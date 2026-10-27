import asyncio
from asyncio.log import logger
import datetime
import ipaddress
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
import logging
import aiohttp
from keyboards.keyboards import get_buy_for_friend_kb_vless, get_buy_for_friend_kb_wireguard, get_payment_kb_wireguard, get_payment_kb_vless, get_trial_type_kb
from middlewares.db import ShadowRegistrationMiddleware
import payments.prices as prices
import os
import json
import base64
from random import random
from aiohttp import web
from keyboards import get_start_kb, get_type_buy_kb, get_instruction_kb, get_vless_instruction_kb, get_wireguard_instruction_kb, get_buy_period_kb_vless, get_buy_period_kb_wireguard
from config import config
from aiogram import Bot, Dispatcher
from aiogram import F
from aiogram.filters.command import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message, CallbackQuery
from aiogram import html
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.filters.callback_data import CallbackData
from services import referral_system
from yookassa.domain.notification import WebhookNotificationFactory, WebhookNotification
from dotenv import load_dotenv
from sqlalchemy import select, insert, update
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, async_session, create_async_engine
from database.models import Order, User
from services.yookassa_api import yookassa_webhook_handler
from database.models import Base  # Твой импорт базового класса моделей
from database.engine import engine # Твой импорт асинхронного движка
from aiogram.utils.deep_linking import create_start_link
from database.engine import session_maker
from services.referral_system import referral_system_payment, referral_system_registration

logging.basicConfig(
    level=logging.INFO,  # С какого уровня показывать сообщения (INFO и выше)
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Красивый формат строки
    handlers=[
        logging.StreamHandler(), # Выводить в консоль
        logging.FileHandler("bot.log", encoding="utf-8") # И ОДНОВРЕМЕННО записывать в файл bot.log!
    ]
)
# Подгружаем константы из .env
load_dotenv()

# Объект бота
bot = Bot(
    token=config.bot_token.get_secret_value(),
    default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )
# Диспетчер
dp = Dispatcher()

DATABASE_URL = f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_async_engine(DATABASE_URL, echo=False)
session_maker = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
async def create():
    # Создаем таблицы в БД, если их нет
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

def main():

    dp.update.outer_middleware.register(ShadowRegistrationMiddleware())
    
    dp.startup.register(on_startup)

    app = web.Application()

    app["bot"] = bot
    
    app["db_session_factory"] = session_maker

    webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
   
    webhook_handler.register(app, path="/webhook/telegram")
    
    setup_application(app, dp, bot=bot, allowed_updates=["message", "callback_query"])
  
    app.router.add_post("/webhook/yookassa", yookassa_webhook_handler)
    print("Запуск сервера на порту 8080...")
    web.run_app(app, host="0.0.0.0", port=8080)

async def on_startup(bot: Bot):
    base_webhook_url = config.base_webhook_url

    await bot.delete_webhook()

    await bot.set_webhook(
        f"{base_webhook_url}/webhook/telegram"
    )
    print(f"Лог: Вебхук установлен на: {base_webhook_url}/webhook/telegram")

    for attempt in range(5):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("База данных успешно подключена и таблицы созданы!")
            break
        except Exception as e:
            print(f"Попытка {attempt+1}: База еще не готова, ждем... ({e})")
            await asyncio.sleep(2)

@dp.message(Command("start"))
async def start(message: Message, command: CommandObject, session: AsyncSession):
    user_id = message.from_user.id
    referrer_id = None

    await referral_system_registration(user_id, message, command, session)

    await message.answer(html.bold("Здравствуйте! Вас приветствует SALUTE VPN 👋 \n\n") +
            "🛍️ После приобретения товара Вы получите: \n\n"
            "✅ Персональную ссылку-подписку, передающуюся только в Ваши руки сроком на 6 или 12 месяцев \n"
            "✅ Высокую скорость интернета \n"
            "✅ Низкий пинг! \n"
            "✅ Стабильную работу на всех ваших устройствах: iOS, Android, Windows, MacOS, TV и роутеры (подписка распространяется на 3 устройства) \n"
            "✅ Безлимитный трафик на всех видах VPN\n"
            "✅ Инструкцию к установке и пользованию\n"
            "✅ Полную конфиденциальность, все Ваши действия остаются приватными",
            reply_markup=get_start_kb()
        )

@dp.callback_query(F.data == "to_main_menu")
async def start(callback: CallbackQuery):
    await callback.message.answer(html.bold("Здравствуйте! Вас приветствует SALUTE VPN 👋 \n\n") +
        "🛍️ После приобретения товара Вы получите: \n\n"
        "✅ Персональную ссылку-подписку или конфиг, передающиеся только в Ваши руки сроком на 6 или 12 месяцев \n"
        "✅ Высокую скорость интернета \n"
        "✅ Низкий пинг! \n"
        "✅ Стабильную работу на всех ваших устройствах: iOS, Android, Windows, MacOS, TV и роутеры (подписка распространяется на 3 устройства) \n"
        "✅ Безлимитный трафик на всех видах VPN\n"
        "✅ Инструкцию к установке и пользованию\n"
        "✅ Полную конфиденциальность, все Ваши действия остаются приватными",
        reply_markup=get_start_kb()
        )
    
    await callback.answer()

@dp.message(F.text == "💵 Купить")
async def period_message(message: Message):
    await message.answer(
        "Выберите протокол для покупки: ",
        reply_markup=get_type_buy_kb()
        )
        
@dp.message(F.text == "📜 Инструкция")
async def instruction_message(message: Message):
    await message.answer(
        "Выберите протокол для инструкции: ",
        reply_markup=get_instruction_kb()
    )

@dp.message(F.text == "🎁 Активировать пробную подписку")
async def trial_types(message: Message):
    async with session_maker() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
    
    if not user or not user.is_trial_available:
        await message.answer(
            "Вы уже использовали пробную подписку."
        )
        return
    
    await message.answer(
        "Выберите протокол для активации пробного периода: ",
        reply_markup=get_trial_type_kb()
    )

@dp.callback_query(F.data == "activate_trial_vless")
async def activate_trial_vless(callback: CallbackQuery):
    await callback.message.edit_text(
            "Test Vless",
    )

@dp.callback_query(F.data == "activate_trial_wireguard")
async def activate_trial_wireguard(callback: CallbackQuery):
    await callback.message.edit_text(
            "Test AmneziaWG",
    )

@dp.message(F.text == "🎁 Реферальная система")
async def show_referral_link(message: Message, bot):
    # Создает ссылку вида t.me/bot?start=123456789
    ref_link = await create_start_link(bot, str(message.from_user.id), encode=True)
    
    await message.answer(
        f"🔗 Ваша реферальная ссылка:\n{ref_link}\n\n"
        f"Делитесь ей с друзьями и получайте бонусные рубли, с помощью которых Вы сможете оплатить подписку! 30% с каждой оплаты друга!"
    )

@dp.message(F.text == "💬 Помощь")
async def instruction_message(message: Message):
    await message.answer(
        "<a href='https://t.me/saluteismyname'>Поддержка</a>"
    )

@dp.callback_query(F.data == "buy_type_vless")
async def callback_buy_type_vless(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выберите протокол для покупки: ",
        reply_markup=get_type_buy_kb()
    )
    
@dp.callback_query(F.data == "buy_type_wireguard")
async def callback_buy_type_vless(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выберите протокол для покупки: ",
        reply_markup=get_type_buy_kb()
    )

@dp.callback_query(F.data == "buy_period_vless")
async def callback_period_message(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выберите срок подписки:",
        reply_markup=get_buy_period_kb_vless()
    )
        
@dp.callback_query(F.data == "buy_period_wireguard")
async def callback_period_message(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выберите срок подписки:",
        reply_markup=get_buy_period_kb_wireguard()
    )

@dp.callback_query(F.data == "buy_for_friend_vless")
async def callback_period_message(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выберите срок подписки для друга: \n" \
        "ℹ️ Если Вы хотите продлить имеющуюся подписку друга, нажмите \"Мои подписки\"",
        reply_markup=get_buy_for_friend_kb_vless()
    )

@dp.callback_query(F.data == "buy_for_friend_wireguard")
async def callback_period_message(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выберите срок подписки для друга: \n" \
        "ℹ️ Если Вы хотите продлить имеющуюся подписку друга, нажмите \"Мои подписки\"",
        reply_markup=get_buy_for_friend_kb_wireguard()
    )

@dp.callback_query(F.data == "buy_7_days_vless")
async def callback_buy_7_days(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    days = int(callback.data.split("_")[1])
    kb = await get_payment_kb_vless(telegram_id=telegram_id, days=days)

    await callback.message.edit_text(
        f"Оплатите счёт на сумму {prices.SUBSCRIPTION_PRICES['7_days']}₽",
        reply_markup=kb
    )

@dp.callback_query(F.data == "pay_full_bonuses_7_days_vless")
async def process_pay_full_bonuses(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    days = int(callback.data.split("_")[3])
    price = prices.SUBSCRIPTION_PRICES[f"{days}_days"]
    vpn_type = "vless"

    await referral_system_payment(telegram_id, price, callback, days, vpn_type)

@dp.callback_query(F.data == "buy_7_days_vless_friend")
async def callback_buy_7_days(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    days = int(callback.data.split("_")[1])
    kb = await get_payment_kb_vless(telegram_id=telegram_id, days=days)

    await callback.message.edit_text(
        f"Оплатите счёт на сумму {prices.SUBSCRIPTION_PRICES['7_days']}₽",
        reply_markup=kb
    )

@dp.callback_query(F.data == "buy_30_days_vless")
async def callback_buy_30_days(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    days = int(callback.data.split("_")[1])
    kb = await get_payment_kb_vless(telegram_id=telegram_id, days=days)

    await callback.message.edit_text(
        f"Оплатите счёт на сумму {prices.SUBSCRIPTION_PRICES['30_days']}₽",
        reply_markup=kb
    )

@dp.callback_query(F.data == "pay_full_bonuses_30_days_vless")
async def process_pay_full_bonuses(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    days = int(callback.data.split("_")[3])
    price = prices.SUBSCRIPTION_PRICES[f"{days}_days"]
    vpn_type = "vless"

    await referral_system_payment(telegram_id, price, callback, days, vpn_type)

@dp.callback_query(F.data == "buy_90_days_vless")
async def callback_buy_90_days(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    days = int(callback.data.split("_")[1])
    kb = await get_payment_kb_vless(telegram_id=telegram_id, days=days)

    await callback.message.edit_text(
        f"Оплатите счёт на сумму {prices.SUBSCRIPTION_PRICES['90_days']}₽",
        reply_markup=kb
    )

@dp.callback_query(F.data == "pay_full_bonuses_90_days_vless")
async def process_pay_full_bonuses(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    days = int(callback.data.split("_")[3])
    price = prices.SUBSCRIPTION_PRICES[f"{days}_days"]
    vpn_type = "vless"

    await referral_system_payment(telegram_id, price, callback, days, vpn_type)

@dp.callback_query(F.data == "buy_180_days_vless")
async def callback_buy_180_days(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    days = int(callback.data.split("_")[1])
    kb = await get_payment_kb_vless(telegram_id=telegram_id, days=days)

    await callback.message.edit_text(
        f"Оплатите счёт на сумму {prices.SUBSCRIPTION_PRICES['180_days']}₽",
        reply_markup=kb
    )

@dp.callback_query(F.data == "pay_full_bonuses_180_days_vless")
async def process_pay_full_bonuses(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    days = int(callback.data.split("_")[3])
    price = prices.SUBSCRIPTION_PRICES[f"{days}_days"]
    vpn_type = "vless"

    await referral_system_payment(telegram_id, price, callback, days, vpn_type)
    
@dp.callback_query(F.data == "buy_365_days_vless")
async def callback_buy_365_days(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    days = int(callback.data.split("_")[1])
    kb = await get_payment_kb_vless(telegram_id=telegram_id, days=days)

    await callback.message.edit_text(
        f"Оплатите счёт на сумму {prices.SUBSCRIPTION_PRICES['365_days']}₽",
        reply_markup=kb
    )

@dp.callback_query(F.data == "pay_full_bonuses_365_days_vless")
async def process_pay_full_bonuses(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    days = int(callback.data.split("_")[3])
    price = prices.SUBSCRIPTION_PRICES[f"{days}_days"]
    vpn_type = "vless"

    await referral_system_payment(telegram_id, price, callback, days, vpn_type)

@dp.callback_query(F.data == "buy_7_days_wireguard")
async def callback_buy_7_days(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    days = int(callback.data.split("_")[1])
    kb = await get_payment_kb_wireguard(telegram_id=telegram_id, days=days)

    await callback.message.edit_text(
        f"Оплатите счёт на сумму {prices.SUBSCRIPTION_PRICES[f'{days}_days']}₽",
        reply_markup=kb
    )

@dp.callback_query(F.data == "pay_full_bonuses_7_days_wireguard")
async def process_pay_full_bonuses(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    days = int(callback.data.split("_")[3])
    price = prices.SUBSCRIPTION_PRICES[f"{days}_days"]
    vpn_type = "wireguard"

    await referral_system_payment(telegram_id, price, callback, days, vpn_type)

@dp.callback_query(F.data == "buy_30_days_wireguard")
async def callback_buy_30_days(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    days = int(callback.data.split("_")[1])
    kb = await get_payment_kb_wireguard(telegram_id=telegram_id, days=days)

    await callback.message.edit_text(
        f"Оплатите счёт на сумму {prices.SUBSCRIPTION_PRICES[f'{days}_days']}₽",
        reply_markup=kb
    )

@dp.callback_query(F.data == "pay_full_bonuses_30_days_wireguard")
async def process_pay_full_bonuses(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    days = int(callback.data.split("_")[3])
    price = prices.SUBSCRIPTION_PRICES[f"{days}_days"]
    vpn_type = "wireguard"

    await referral_system_payment(telegram_id, price, callback, days, vpn_type)

@dp.callback_query(F.data == "buy_90_days_wireguard")
async def callback_buy_90_days(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    days = int(callback.data.split("_")[1])
    kb = await get_payment_kb_wireguard(telegram_id=telegram_id, days=days)

    await callback.message.edit_text(
        f"Оплатите счёт на сумму {prices.SUBSCRIPTION_PRICES[f'{days}_days']}₽",
        reply_markup=kb
    )

@dp.callback_query(F.data == "pay_full_bonuses_90_days_wireguard")
async def process_pay_full_bonuses(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    days = int(callback.data.split("_")[3])
    price = prices.SUBSCRIPTION_PRICES[f"{days}_days"]
    vpn_type = "wireguard"

    await referral_system_payment(telegram_id, price, callback, days, vpn_type)

@dp.callback_query(F.data == "buy_180_days_wireguard")
async def callback_buy_180_days(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    days = int(callback.data.split("_")[1])
    kb = await get_payment_kb_wireguard(telegram_id=telegram_id, days=days)

    await callback.message.edit_text(
        f"Оплатите счёт на сумму {prices.SUBSCRIPTION_PRICES[f'{days}_days']}₽",
        reply_markup=kb
    )

@dp.callback_query(F.data == "pay_full_bonuses_180_days_wireguard")
async def process_pay_full_bonuses(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    days = int(callback.data.split("_")[3])
    price = prices.SUBSCRIPTION_PRICES[f"{days}_days"]
    vpn_type = "wireguard"

    await referral_system_payment(telegram_id, price, callback, days, vpn_type)
    
@dp.callback_query(F.data == "buy_365_days_wireguard")
async def callback_buy_365_days(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    days = int(callback.data.split("_")[1])
    kb = await get_payment_kb_wireguard(telegram_id=telegram_id, days=days)

    await callback.message.edit_text(
        f"Оплатите счёт на сумму {prices.SUBSCRIPTION_PRICES[f'{days}_days']}₽",
        reply_markup=kb
    )

@dp.callback_query(F.data == "pay_full_bonuses_365_days_wireguard")
async def process_pay_full_bonuses(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    days = int(callback.data.split("_")[3])
    price = prices.SUBSCRIPTION_PRICES[f"{days}_days"]
    vpn_type = "wireguard"

    await referral_system_payment(telegram_id, price, callback, days, vpn_type)
    
@dp.callback_query(F.data == "vless_instruction")
async def callback_instruction_chosen(callback: CallbackQuery):
    await callback.message.edit_text(
        "1. Скачайте Happ Plus, INCY или V2RayTun\n"
        "2. Скопируйте ссылку-подписку из сообщения о покупке\n"
        "3. В приложении нажмите +, добавить из буфера обмена\n"
        "4. Теперь можете наслаждаться интернетом!👐\n",
        reply_markup=get_vless_instruction_kb()
    )
    
@dp.callback_query(F.data == "wireguard_instruction")
async def callback_instruction_chosen(callback: CallbackQuery):
    await callback.message.edit_text(
        "1. Скачайте WireGuard и убедитесь, что подключение по конфигу есть\n"
        "2. Проверьте интернет-соединение\n"
        "3. Если подключение есть, но интернет не работает - дело в провайдере, на стороне конфига всё хорошо\n"
        "4. Любым текстовым редактором откройте конфиг, и после DNS = 1.1.1.1,8.8.8.8 вставьте следующие значения:\n"

        "<pre>MTU = 1380\n"
        "Jc = 5\n"
        "Jmin = 2\n"
        "Jmax = 9\n"
        "S1 = 0\n"
        "S2 = 0\n"
        "H1 = 1\n"
        "H2 = 2\n"
        "H3 = 3\n"
        "H4 = 4</pre>\n"

        "5. Импортируйте этот конфиг в AmneziaWG (IOS, Android, Windows, Ubuntu)\n"
        "6. Теперь можете наслаждаться интернетом!👐\n",
        reply_markup=get_wireguard_instruction_kb()
    )

if __name__ == "__main__":
    main()
