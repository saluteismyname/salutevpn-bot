from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from payments.payments import create_payment
import payments.prices as prices
from database.engine import session_maker

def get_start_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="💵 Купить")
    kb.button(text="📜 Инструкция")
    kb.button(text="💬 Помощь")
    kb.adjust(2, 1)

    return kb.as_markup(resize_keyboard=True)

def get_type_buy_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Vless", callback_data="buy_period_vless")
    kb.button(text="WireGuard / AmneziaWG", callback_data="buy_period_wireguard")

    kb.adjust(1)

    return kb.as_markup()

def get_buy_period_kb_vless() -> InlineKeyboardMarkup:
    one_week = f"1 неделя - {prices.SUBSCRIPTION_PRICES['7_days']}₽"
    one_month = f"1 месяц - {prices.SUBSCRIPTION_PRICES['30_days']}₽"
    three_months = f"3 месяца - {prices.SUBSCRIPTION_PRICES['90_days']}₽"
    six_months = f"6 месяцев - {prices.SUBSCRIPTION_PRICES['180_days']}₽"
    twelve_months = f"12 месяцев - {prices.SUBSCRIPTION_PRICES['365_days']}₽"

    kb = InlineKeyboardBuilder()
    kb.button(text=one_week, callback_data="buy_7_days_vless")
    kb.button(text=one_month, callback_data="buy_30_days_vless")
    kb.button(text=three_months, callback_data="buy_90_days_vless")
    kb.button(text=six_months, callback_data="buy_180_days_vless")
    kb.button(text=twelve_months, callback_data="buy_365_days_vless")
    kb.button(text="🔙 Назад", callback_data="buy_type_vless")
    kb.adjust(1)
    
    return kb.as_markup()

def get_buy_period_kb_wireguard() -> InlineKeyboardMarkup:
    one_week = f"1 неделя - {prices.SUBSCRIPTION_PRICES['7_days']}₽"
    one_month = f"1 месяц - {prices.SUBSCRIPTION_PRICES['30_days']}₽"
    three_months = f"3 месяца - {prices.SUBSCRIPTION_PRICES['90_days']}₽"
    six_months = f"6 месяцев - {prices.SUBSCRIPTION_PRICES['180_days']}₽"
    twelve_months = f"12 месяцев - {prices.SUBSCRIPTION_PRICES['365_days']}₽"

    kb = InlineKeyboardBuilder()
    kb.button(text=one_week, callback_data="buy_7_days_wireguard")
    kb.button(text=one_month, callback_data="buy_30_days_wireguard")
    kb.button(text=three_months, callback_data="buy_90_days_wireguard")
    kb.button(text=six_months, callback_data="buy_180_days_wireguard")
    kb.button(text=twelve_months, callback_data="buy_365_days_wireguard")
    kb.button(text="🔙 Назад", callback_data="buy_type_wireguard")
    kb.adjust(1)
    
    return kb.as_markup()

def get_instruction_kb() -> InlineKeyboardMarkup:

    kb = InlineKeyboardBuilder()
    kb.button(text="Vless", callback_data="vless_instruction")
    kb.button(text="WireGuard / AmneziaWG", callback_data="wireguard_instruction")

    kb.adjust(1)

    return kb.as_markup()

def get_vless_instruction_kb() -> InlineKeyboardMarkup:

    kb = InlineKeyboardBuilder()

    return kb.as_markup()

def get_wireguard_instruction_kb() -> InlineKeyboardMarkup:

    kb = InlineKeyboardBuilder()

    return kb.as_markup()

async def get_payment_7_kb_vless(telegram_id: int) -> InlineKeyboardMarkup:
    
    async with session_maker() as session:
        payment = await create_payment(
            session=session,
            telegram_id = telegram_id,
            days = 7,
            vpn_type = "vless",
            amount_value = prices.SUBSCRIPTION_PRICES["7_days"]
        )
    
    payment_url = payment['confirmation']['confirmation_url']

    kb = InlineKeyboardBuilder()
    kb.button(text="💵 Оплатить", callback_data="payment", url=payment_url)
    kb.button(text="🔙 Назад", callback_data="buy_period_vless")
    kb.adjust(1)

    return kb.as_markup()

async def get_payment_30_kb_vless(telegram_id: int) -> InlineKeyboardMarkup:
    
    async with session_maker() as session:
        payment = await create_payment(
            session=session,
            telegram_id = telegram_id,
            days = 30,
            vpn_type = "vless",
            amount_value = prices.SUBSCRIPTION_PRICES["30_days"]
        )
    
    payment_url = payment['confirmation']['confirmation_url']

    kb = InlineKeyboardBuilder()
    kb.button(text="💵 Оплатить", callback_data="payment", url=payment_url)
    kb.button(text="🔙 Назад", callback_data="buy_period_vless")
    kb.adjust(1)

    return kb.as_markup()

async def get_payment_90_kb_vless(telegram_id: int) -> InlineKeyboardMarkup:
    
    async with session_maker() as session:
        payment = await create_payment(
            session=session,
            telegram_id = telegram_id,
            days = 90,
            vpn_type = "vless",
            amount_value = prices.SUBSCRIPTION_PRICES["90_days"]
        )
    
    payment_url = payment['confirmation']['confirmation_url']

    kb = InlineKeyboardBuilder()
    kb.button(text="💵 Оплатить", callback_data="payment", url=payment_url)
    kb.button(text="🔙 Назад", callback_data="buy_period_vless")
    kb.adjust(1)

    return kb.as_markup()

async def get_payment_180_kb_vless(telegram_id: int) -> InlineKeyboardMarkup:
    
    async with session_maker() as session:
        payment = await create_payment(
            session=session,
            telegram_id = telegram_id,
            days = 180,
            vpn_type = "vless",
            amount_value = prices.SUBSCRIPTION_PRICES["180_days"]
        )
    
    payment_url = payment['confirmation']['confirmation_url']

    kb = InlineKeyboardBuilder()
    kb.button(text="💵 Оплатить", callback_data="payment", url=payment_url)
    kb.button(text="🔙 Назад", callback_data="buy_period_vless")
    kb.adjust(1)

    return kb.as_markup()

async def get_payment_365_kb_vless(telegram_id: int) -> InlineKeyboardMarkup:
    
    async with session_maker() as session:
        payment = await create_payment(
            session=session,
            telegram_id = telegram_id,
            days = 365,
            vpn_type = "vless",
            amount_value = prices.SUBSCRIPTION_PRICES["365_days"]
        )
    
    payment_url = payment['confirmation']['confirmation_url']

    kb = InlineKeyboardBuilder()
    kb.button(text="💵 Оплатить", callback_data="payment", url=payment_url)
    kb.button(text="🔙 Назад", callback_data="buy_period_vless")
    kb.adjust(1)

    return kb.as_markup()

async def get_payment_7_kb_wireguard(telegram_id: int) -> InlineKeyboardMarkup:
    
    async with session_maker() as session:
        payment = await create_payment(
            session=session,
            telegram_id = telegram_id,
            days = 7,
            vpn_type = "wireguard",
            amount_value = prices.SUBSCRIPTION_PRICES["7_days"]
        )

    payment_url = payment['confirmation']['confirmation_url']

    kb = InlineKeyboardBuilder()
    kb.button(text="💵 Оплатить", callback_data="payment", url=payment_url)
    kb.button(text="🔙 Назад", callback_data="buy_period_wireguard")
    kb.adjust(1)

    return kb.as_markup()

async def get_payment_30_kb_wireguard(telegram_id: int) -> InlineKeyboardMarkup:
    
    async with session_maker() as session:
        payment = await create_payment(
            session=session,
            telegram_id = telegram_id,
            days = 30,
            vpn_type = "wireguard",
            amount_value = prices.SUBSCRIPTION_PRICES["30_days"]
        )

    payment_url = payment['confirmation']['confirmation_url']

    kb = InlineKeyboardBuilder()
    kb.button(text="💵 Оплатить", callback_data="payment", url=payment_url)
    kb.button(text="🔙 Назад", callback_data="buy_period_wireguard")
    kb.adjust(1)

    return kb.as_markup()

async def get_payment_90_kb_wireguard(telegram_id: int) -> InlineKeyboardMarkup:
    
    async with session_maker() as session:
        payment = await create_payment(
            session=session,
            telegram_id = telegram_id,
            days = 90,
            vpn_type = "wireguard",
            amount_value = prices.SUBSCRIPTION_PRICES["90_days"]
        )

    payment_url = payment['confirmation']['confirmation_url']

    kb = InlineKeyboardBuilder()
    kb.button(text="💵 Оплатить", callback_data="payment", url=payment_url)
    kb.button(text="🔙 Назад", callback_data="buy_period_wireguard")
    kb.adjust(1)

    return kb.as_markup()

async def get_payment_180_kb_wireguard(telegram_id: int) -> InlineKeyboardMarkup:
    
    async with session_maker() as session:
        payment = await create_payment(
            session=session,
            telegram_id = telegram_id,
            days = 180,
            vpn_type = "wireguard",
            amount_value = prices.SUBSCRIPTION_PRICES["180_days"]
        )

    payment_url = payment['confirmation']['confirmation_url']

    kb = InlineKeyboardBuilder()
    kb.button(text="💵 Оплатить", callback_data="payment", url=payment_url)
    kb.button(text="🔙 Назад", callback_data="buy_period_wireguard")
    kb.adjust(1)

    return kb.as_markup()

async def get_payment_365_kb_wireguard(telegram_id: int) -> InlineKeyboardMarkup:
    
    async with session_maker() as session:
        payment = await create_payment(
            session=session,
            telegram_id = telegram_id,
            days = 365,
            vpn_type = "wireguard",
            amount_value = prices.SUBSCRIPTION_PRICES["365_days"]
        )
    
    payment_url = payment['confirmation']['confirmation_url']

    kb = InlineKeyboardBuilder()
    kb.button(text="💵 Оплатить", callback_data="payment", url=payment_url)
    kb.button(text="🔙 Назад", callback_data="buy_period_wireguard")
    kb.adjust(1)

    return kb.as_markup()