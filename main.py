import asyncio
from asyncio.log import logger
import ipaddress
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
import logging
import aiohttp
from middlewares.db import ShadowRegistrationMiddleware
import payments.prices as prices
import os
import json
from random import random
from aiohttp import web
from keyboards import get_start_kb, get_type_buy_kb, get_instruction_kb, get_vless_instruction_kb, get_wireguard_instruction_kb, get_buy_period_kb_vless, get_buy_period_kb_wireguard, get_payment_6_kb_vless, get_payment_12_kb_vless, get_payment_6_kb_wireguard, get_payment_12_kb_wireguard
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
from yookassa.domain.notification import WebhookNotificationFactory, WebhookNotification
from dotenv import load_dotenv
from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from database.engine import create_db, session_maker
from database.models import User
from services.yookassa_api import yookassa_webhook_handler

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

def main():

    dp.update.outer_middleware.register(ShadowRegistrationMiddleware())
    
    dp.startup.register(on_startup)

    app = web.Application()

    app["bot"] = bot
    
    webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
   
    webhook_handler.register(app, path="/webhook/telegram")
    
    setup_application(app, dp, bot=bot, allowed_updates=["message", "callback_query"])
  
    app.router.add_post("/webhook/yookassa", yookassa_webhook_handler)
    print("Запуск сервера на порту 8080...")
    web.run_app(app, host="127.0.0.1", port=8080)

async def on_startup(bot: Bot):
    base_webhook_url = config.base_webhook_url

    await bot.delete_webhook(drop_pending_updates=True)

    await bot.set_webhook(
        f"{base_webhook_url}/webhook/telegram",
        allowed_updates=["message", "callback_query"]
    )
    print(f"Лог: Вебхук установлен на: {base_webhook_url}/webhook/telegram")

    await create_db()
    print("Лог: База данных проверена и готова к работе!")
    
@dp.message(Command("start"))
async def start(message: Message):
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
        "✅ Персональную ссылку-подписку, передающуюся только в Ваши руки сроком на 6 или 12 месяцев \n"
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
        "Выберите вид продукта покупки: ",
        reply_markup=get_type_buy_kb()
        )
        
@dp.message(F.text == "📜 Инструкция")
async def instruction_message(message: Message):
    await message.answer(
        "Выберите вид продукта инструкции: ",
        reply_markup=get_instruction_kb()
    )

@dp.message(F.text == "💬 Помощь")
async def instruction_message(message: Message):
    await message.answer(
        "<a href='https://t.me/saluteismyname'>Поддержка</a>"
    )

@dp.callback_query(F.data == "buy_type_vless")
async def callback_buy_type_vless(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выберите вид продукта покупки: ",
        reply_markup=get_type_buy_kb()
    )
    
@dp.callback_query(F.data == "buy_type_wireguard")
async def callback_buy_type_vless(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выберите вид продукта покупки: ",
        reply_markup=get_type_buy_kb()
    )

@dp.callback_query(F.data == "buy_period_vless")
async def callback_period_message(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выберите срок подписки: ",
        reply_markup=get_buy_period_kb_vless()
    )
        
@dp.callback_query(F.data == "buy_period_wireguard")
async def callback_period_message(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выберите срок подписки: ",
        reply_markup=get_buy_period_kb_wireguard()
    )
        
@dp.callback_query(F.data == "buy_6_months_vless")
async def callback_buy_6_months(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    kb = await get_payment_6_kb_vless(telegram_id=telegram_id)

    await callback.message.edit_text(
        f"Оплатите счёт на сумму {prices.SUBSCRIPTION_PRICES['6_months']}₽",
        reply_markup=kb
    )
    
@dp.callback_query(F.data == "buy_12_months_vless")
async def callback_buy_12_months(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    kb = await get_payment_12_kb_vless(telegram_id=telegram_id)

    await callback.message.edit_text(
        f"Оплатите счёт на сумму {prices.SUBSCRIPTION_PRICES['12_months']}₽",
        reply_markup=kb
    )
    
@dp.callback_query(F.data == "buy_6_months_wireguard")
async def callback_buy_6_months(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    kb = await get_payment_6_kb_wireguard(telegram_id=telegram_id)

    await callback.message.edit_text(
        f"Оплатите счёт на сумму {prices.SUBSCRIPTION_PRICES['6_months']}₽",
        reply_markup=kb
    )
    
@dp.callback_query(F.data == "buy_12_months_wireguard")
async def callback_buy_12_months(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    kb = await get_payment_12_kb_wireguard(telegram_id=telegram_id)

    await callback.message.edit_text(
        f"Оплатите счёт на сумму {prices.SUBSCRIPTION_PRICES['12_months']}₽",
        reply_markup=kb
    )
    
@dp.callback_query(F.data == "vless_instruction")
async def callback_instruction_chosen(callback: CallbackQuery):
    await callback.message.edit_text(
        "1. Скачайте Happ Plus, V2RayTun, Streisand или V2RayNG\n"
        "2. Скопируйте ссылку-подписку из сообщения о покупке\n"
        "3. Нажмите +, добавить из буфера обмена\n"
        "4. Готово!\n",
        reply_markup=get_vless_instruction_kb()
    )
    
@dp.callback_query(F.data == "wireguard_instruction")
async def callback_instruction_chosen(callback: CallbackQuery):
    await callback.message.edit_text(
        "1. Скачайте WireGuard и убедитесь, что подключение по конфигу есть\n"
        "2. Проверьте интернет-соединение\n"
        "3. Если подключение есть, но интернет не работает - дело в провайдере, на стороне конфига всё хорошо\n"
        "4. Любым текстовым редактором откройте конфиг, и после DNS = 1.1.1.1,8.8.8.8 вставьте следующие значения: (нажмите, что бы скопировать)\n"

        "<code>MTU = 1380\n"
        "Jc = 5\n"
        "Jmin = 2\n"
        "Jmax = 9\n"
        "S1 = 0\n"
        "S2 = 0\n"
        "H1 = 1\n"
        "H2 = 2\n"
        "H3 = 3\n"
        "H4 = 4</code>\n"

        "5. Импортируйте этот конфиг в AmneziaWG (IOS, Android, Windows, Ubuntu)\n"
        "6. Теперь можете наслаждаться интернетом!👐\n",
        reply_markup=get_wireguard_instruction_kb()
    )

if __name__ == "__main__":
    main()