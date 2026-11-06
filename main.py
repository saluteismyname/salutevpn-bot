import asyncio
from datetime import datetime, timezone
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
import logging
from keyboards.keyboards import subscription_devices_menu_kb, subscription_menu_kb, get_buy_for_friend_kb_vless, get_buy_for_friend_kb_wireguard, get_buy_type_kb, get_paginated_subscriptions_kb, get_payment_kb, get_subscriptions_kb, get_trial_type_kb
from middlewares.db import ShadowRegistrationMiddleware
import payments.prices as prices
import os
from aiohttp import web
from keyboards import get_start_kb, get_instruction_kb, get_vless_instruction_kb, get_wireguard_instruction_kb, get_buy_period_kb_vless, get_buy_period_kb_wireguard
from config import config
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters.command import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BufferedInputFile, Message, CallbackQuery
from aiogram import html
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.filters.callback_data import CallbackData
from services import referral_system
from yookassa.domain.notification import WebhookNotificationFactory, WebhookNotification
from dotenv import load_dotenv
from sqlalchemy import desc, select, insert, update
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, async_session, create_async_engine
from database.models import Order, User
from services.buy import buy_days
from services.devices_remnawave import get_devices_remnawave
from services.payment import get_payment_data
from services.remnawave import get_user_remnawave
from services.trial_delivery import process_trial_vpn_delivery
from services.wg_easy import get_user_wg_easy
from services.yookassa_api import yookassa_webhook_handler
from database.models import Base  # Твой импорт базового класса моделей
from database.engine import engine # Твой импорт асинхронного движка
from aiogram.utils.deep_linking import create_start_link
from database.engine import session_maker
from services.referral_system import referral_system_payment, referral_system_registration
from rich import print as rprint
from services.get_subscription import get_my_subscriptions, get_subscription
from dateutil.relativedelta import relativedelta

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

# Роутер
router = Router()

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
            "✅ Персональную ссылку-подписку, передающуюся только в Ваши руки с удобным для Вас сроком\n"
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
        reply_markup=get_buy_type_kb()
        )
        
@dp.message(F.text == "📜 Инструкция")
async def instruction_message(message: Message):
    
    await message.answer(
        "Выберите протокол для инструкции: ",
        reply_markup=get_instruction_kb()
    )

@dp.message(F.text == "📋 Мои подписки")
async def subscriptions_message(message: Message):
    telegram_id = message.from_user.id
    orders_without_friends, orders_with_friends = await get_my_subscriptions(telegram_id=telegram_id)

    if orders_without_friends or orders_with_friends:
        text = "Выберите подписку: "
    else:
        text = "У Вас ещё нет активных подписок."

    await message.answer(
        text=text,
        reply_markup=get_subscriptions_kb(
            orders_with_friends=orders_with_friends, 
            orders_without_friends=orders_without_friends,
            page=1
        )
    )

@dp.callback_query(F.data.startswith("friends_subs_page_"))
async def process_friends_subs_pagination(callback: CallbackQuery):
    # Пример callback_data: "friends_subs_page_2"
    # Разбиваем по подчеркиванию и берем последний элемент (номер страницы)
    page = int(callback.data.split("_")[-1])
    vpn_type = str(callback.data.split("_")[-2])

    telegram_id = callback.from_user.id
    
    # Получаем актуальные данные подписок из базы
    orders_without_friends, orders_with_friends = await get_my_subscriptions(telegram_id=telegram_id)

    # Генерируем клавиатуру для новой страницы
    kb = get_subscriptions_kb(
        orders_with_friends=orders_with_friends, 
        orders_without_friends=orders_without_friends,
        page=page
    )

    if vpn_type == "wireguard":
        await callback.message.delete()
    # Обновляем клавиатуру в сообщении
        await callback.message.answer(
            text="Выберите подписку:",
            reply_markup=kb
            )
    else:
        await callback.message.edit_text(
            text="Выберите подписку: ",
            reply_markup=kb
        )
    
    # Обязательно гасим анимацию загрузки на кнопке
    await callback.answer()

@dp.callback_query(F.data.startswith("sub_page_"))
async def process_sub_pagination(callback: CallbackQuery):
    # Парсим: sub_page_<page>_<vpn_type>_<for_friend_flag>
    parts = callback.data.split("_")
    page = int(parts[2])
    vpn_type = parts[3]
    for_friend = bool(int(parts[4]))
    
    # Передаем ваш словарь цен
    kb = get_paginated_subscriptions_kb(
        prices_dict=prices.SUBSCRIPTION_PRICES, # или SUBSCRIPTION_PRICES_FOR_FRIEND, если нужно
        page=page,
        per_page=2, # Количество тарифов на одной странице
        vpn_type=vpn_type,
        for_friend=for_friend
    )
    
    await callback.message.edit_text(
        text="Выберите подписку: ",
        reply_markup=kb
        )
    await callback.answer()

@dp.callback_query(F.data.startswith("select_order:_"))
async def select_order(callback: CallbackQuery, session: AsyncSession):

    subscription = await get_subscription(int(callback.data.split("_")[2]), session)
    now = datetime.now(timezone.utc)
    order, user = subscription
    parts = callback.data.split("_")
    if len(parts) >= 4:
        page = int(parts[3]) # Берем самый последний элемент (например, номер страницы)
    else:
        page = 1

    if order.vpn_type == "vless":
        expires_at = user.expires_at_vless if user.expires_at_vless else "Бессрочно"
        vless_get = await get_user_remnawave(user.remnawave_uuid)
        vless_key = vless_get['response']['subscriptionUrl']
        vpn_name = "Vless"
        num_of_friend = order.friend_number
        vless_user_uuid = vless_get["response"]["uuid"]
        vless_total_devices = 3 if vless_get["response"]["hwidDeviceLimit"] == None else vless_get["response"]["hwidDeviceLimit"]
        vless_connected_devices_pre = await get_devices_remnawave(uuid=vless_user_uuid)
        vless_connected_devices = vless_connected_devices_pre["response"]["total"]
        
        if order.is_for_friend == True:
            is_for_friend = f" для друга №{num_of_friend}"
            expires_at = order.created_at + relativedelta(days=order.days)
            vless_get = await get_user_remnawave(order.remnawave_uuid)
            vless_key = vless_get["response"]["subscriptionUrl"]
        else:
            is_for_friend = ""

        if expires_at > now:
            is_active = "🟢 Активна\n"
            lasts_to = "Действует до:"
        else:
            is_active = "🔴 Истекла\n"
            lasts_to = "Действовала до:"

        await callback.message.edit_text(
            f"📱 Подписка {vpn_name}{is_for_friend}\n"
            f"Статус: {is_active}\n"
            f"Дата приобретения: {order.created_at.strftime('%d.%m.%Y')}\n"
            f"{lasts_to} {expires_at.strftime('%d.%m.%Y')}\n\n"
            "───────────────────\n"
            "⚡ Скорость: До 1 Gbps (без ограничений)\n"
            f"👥 Подключенных устройств: {vless_connected_devices} из {vless_total_devices}\n\n"
            "💡 Скопируйте ключ ниже и вставьте в ваше приложение:\n"
            f"<pre>{vless_key}</pre>",
            parse_mode="HTML",
            reply_markup=subscription_menu_kb(vpn_type="vless", page=page, order_id=order.id, uuid=vless_user_uuid)
        )

    else:
        expires_at = user.expires_at_wireguard if user.expires_at_wireguard else "Бессрочно"
        vpn_name = "WireGuard"
        config = await get_user_wg_easy(order.wg_id)
        config_file = BufferedInputFile(
            file=config.encode("utf-8"), 
            filename=f"Salute_VPN_{user.telegram_id}.conf"
        )

        num_of_friend = order.friend_number

        if order.is_for_friend == True:
            is_for_friend = f" для друга №{num_of_friend}"
            expires_at = order.created_at + relativedelta(days=order.days)
        else:
            is_for_friend = ""
        
        if expires_at > now:
            is_active = "🟢 Активна\n"
            lasts_to = "Действует до:"
        else:
            is_active = "🔴 Истекла\n"
            lasts_to = "Действовала до:"

        msg = f"📱 Подписка {vpn_name}{is_for_friend}\n"\
            f"Статус: {is_active}\n"\
            f"Дата приобретения: {order.created_at.strftime('%d.%m.%Y')}\n"\
            f"{lasts_to} {expires_at.strftime('%d.%m.%Y')}\n\n"\
            "───────────────────\n"\
            "⚡ Скорость: До 1 Gbps (без ограничений)\n"\
            "💡 Скачайте конфиг выше ☝️ и вставьте в ваше приложение:\n"\

        await callback.message.delete()
        
        await callback.bot.send_document(
            chat_id=user.telegram_id,
            caption=msg,
            document=config_file,
            parse_mode="HTML",
            reply_markup=subscription_menu_kb(vpn_type="wireguard", page=page)
        )

    await callback.answer()

@dp.callback_query(F.data.startswith("edit_devices_"))
async def edit_devices(callback: CallbackQuery):
    user_id = callback.data.split("_")[-1] 
    user_uuid = callback.data.split("_")[-2] 
    devices = await get_devices_remnawave(uuid=user_uuid)
    
    await callback.message.answer(
        "Редактировать список устройств:",
        reply_markup=subscription_devices_menu_kb(devices=devices, order_id=user_id)
    )

    await callback.answer()

@dp.message(F.text == "🎁 Активировать пробную подписку")
async def trial_types(message: Message):
    async with session_maker() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()

    if not user:
        await message.answer(
            "Вы ещё не зарегистрированы!"
        )
        return
    
    await message.answer(
        "Выберите протокол для активации пробного периода: ",
        reply_markup=get_trial_type_kb()
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

@dp.callback_query(F.data.startswith("activate_trial_"))
async def activate_trial(callback: CallbackQuery):
    await callback.answer()
    vpn_type = callback.data.split("_")[-1]

    async with session_maker() as session:
        
        result = await session.execute(
            select(User).where(User.telegram_id == callback.from_user.id)
        )

        user = result.scalar_one_or_none()

    if not user:
        await callback.message.answer(
            "Вы ещё не зарегистрировались."
        )

        return
    
    if vpn_type == "vless":

        if not user.is_trial_available_vless:
                await callback.message.answer(
                    "Вы уже использовали пробную подписку Vless."
                )
                
                return
        else:
            
            data = await process_trial_vpn_delivery(telegram_id=callback.from_user.id, vpn_type="vless", session=session, bot=bot)
            
            await callback.message.answer(
                f"✅ <b>Активация пробного периода прошло успешно!</b>\n\nВаша подписка на <b>Vless</b> активирована на 3 дня\nДействует до: <b>{data['readable_date']} (МСК)</b> 🚀\n\nСпасибо, что выбрали <b>SALUTE VPN!</b>\n\n<b>Vless-подписка:</b><pre>{data['vless_subscription']}</pre>"
            )

            return
        
    elif vpn_type == "wireguard":
    
        if not user.is_trial_available_wireguard:
            await callback.message.answer(
                "Вы уже использовали пробную подписку WireGuard."
            )
            
            return
        else:

            await process_trial_vpn_delivery(telegram_id=callback.from_user.id, vpn_type="wireguard", session=session, bot=bot)

            return

@dp.callback_query(F.data == "buy_type")
async def callback_buy_type_vless(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выберите протокол для покупки: ",
        reply_markup=get_buy_type_kb()
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("buy_period_"))
async def callback_period_message(callback: CallbackQuery):

    vpn_type = str(callback.data.split("_")[2])

    if vpn_type == "vless":
        await callback.message.edit_text(
            "Выберите срок подписки Vless:",
            reply_markup=get_buy_period_kb_vless()
        )
    elif vpn_type == "wireguard":
        await callback.message.edit_text(
            "Выберите срок подписки WireGuard:",
            reply_markup=get_buy_period_kb_wireguard()
        )
    await callback.answer()

@dp.callback_query(F.data.startswith("buy_for_friend_menu_"))
async def callback_period_message(callback: CallbackQuery):
    vpn_type = str(callback.data.split("_")[4])

    if vpn_type == "vless":
        await callback.message.edit_text(
            "Выберите срок подписки Vless для друга: \n" \
            "ℹ️ Если Вы хотите продлить имеющуюся подписку друга, нажмите \"Мои подписки\"",
            reply_markup=get_buy_for_friend_kb_vless()
        )
    elif vpn_type == "wireguard":
        await callback.message.edit_text(
                "Выберите срок подписки WireGuard для друга: \n" \
                "ℹ️ Если Вы хотите продлить имеющуюся подписку друга, нажмите \"Мои подписки\"",
                reply_markup=get_buy_for_friend_kb_wireguard()
        )
    await callback.answer()

@dp.callback_query(F.data.startswith("buy_"))
async def callback_buy_days(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    days = int(callback.data.split("_")[1])
    vpn_type = str(callback.data.split("_")[3])
    price = prices.SUBSCRIPTION_PRICES[f"{days}_days"]
    price_for_friend = prices.SUBSCRIPTION_PRICES_FOR_FRIEND[f"{days}_days"]
    parts = callback.data.split("_")
    for_friend = parts[4] if len(parts) > 4 else False
    order = None

    holder = await buy_days(telegram_id=telegram_id)
    user_check = holder["user_check"]
    order = holder["order"]

    if for_friend == "for":

        if user_check.is_active_vpn is not False:
            if order.vpn_type == "vless" and for_friend == "for":
                if user_check.num_of_friends_vless is None:
                    friend_number = 1
                else:
                    friend_number = user_check.num_of_friends_vless + user_check.num_of_friends_wireguard + 1

            if order.vpn_type == "wireguard" and for_friend == "for":
                if user_check.num_of_friends_wireguard is None:
                    friend_number = 1
                else:
                    friend_number = user_check.num_of_friends_wireguard + user_check.num_of_friends_vless + 1
        else:
            await callback.message.edit_text("Вы не можете купить подписку для друга не имея своей.")
            return
        
        payment = await get_payment_data(telegram_id=telegram_id, days=days, vpn_type=vpn_type, is_for_friend=True, friend_number=friend_number)
        kb = get_payment_kb(days=days, vpn_type=vpn_type, payment=payment, is_for_friend=True)
    
        await callback.message.edit_text(
            f"Оплатите счёт на сумму {price_for_friend}₽",
            reply_markup=kb
        )
    else:
        payment = await get_payment_data(telegram_id=telegram_id, days=days, vpn_type=vpn_type, is_for_friend=False, friend_number=None)
        kb = get_payment_kb(days=days, vpn_type=vpn_type, payment=payment, is_for_friend=False)
        await callback.message.edit_text(
            f"Оплатите счёт на сумму {price}₽",
            reply_markup=kb
        )

    await callback.answer()

@dp.callback_query(F.data.startswith("pay_full_bonuses_"))
async def process_pay_full_bonuses(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    days = int(callback.data.split("_")[3])
    vpn_type = str(callback.data.split("_")[5])
    price = prices.SUBSCRIPTION_PRICES[f"{days}_days"]
    await callback.answer()

    await referral_system_payment(telegram_id, price, callback, days, vpn_type=vpn_type, is_for_friend=False)
    
@dp.callback_query(F.data.startswith("instruction_"))
async def callback_instruction_chosen(callback: CallbackQuery):
    vpn_type = callback.data.split("_")[1]
    if vpn_type:
        await callback.message.edit_text(
            "1. Скачайте Happ Plus, INCY или V2RayTun\n"
            "2. Скопируйте ссылку-подписку из сообщения о покупке\n"
            "3. В приложении нажмите +, добавить из буфера обмена\n"
            "4. Теперь можете наслаждаться интернетом!👐\n",
            reply_markup=get_vless_instruction_kb()
        )
    else:
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
    await callback.answer()

if __name__ == "__main__":
    main()