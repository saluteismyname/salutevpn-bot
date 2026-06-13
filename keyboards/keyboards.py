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
    six_months = f"6 месяцев - {prices.SUBSCRIPTION_PRICES['6_months']}₽"
    twelve_months = f"12 месяцев - {prices.SUBSCRIPTION_PRICES['12_months']}₽"

    kb = InlineKeyboardBuilder()
    kb.button(text=six_months, callback_data="buy_6_months_vless")
    kb.button(text=twelve_months, callback_data="buy_12_months_vless")
    kb.button(text="🔙 Назад", callback_data="buy_type_vless")
    kb.adjust(2)
    
    return kb.as_markup()

def get_buy_period_kb_wireguard() -> InlineKeyboardMarkup:
    six_months = f"6 месяцев - {prices.SUBSCRIPTION_PRICES['6_months']}₽"
    twelve_months = f"12 месяцев - {prices.SUBSCRIPTION_PRICES['12_months']}₽"
    
    kb = InlineKeyboardBuilder()
    kb.button(text=six_months, callback_data="buy_6_months_wireguard")
    kb.button(text=twelve_months, callback_data="buy_12_months_wireguard")
    kb.button(text="🔙 Назад", callback_data="buy_type_wireguard")
    kb.adjust(2)
    
    return kb.as_markup()

def get_instruction_kb() -> InlineKeyboardMarkup:

    kb = InlineKeyboardBuilder()
    kb.button(text="Vless", callback_data="vless_instruction")
    kb.button(text="WireGuard / AmneziaWG", callback_data="wireguard_instruction")

    kb.adjust(1)

    return kb.as_markup()

def get_vless_instruction_kb() -> InlineKeyboardMarkup:

    kb = InlineKeyboardBuilder()
    kb.button(text="🔙 Назад", callback_data="choose_the_type_instruction")

    return kb.as_markup()

def get_wireguard_instruction_kb() -> InlineKeyboardMarkup:

    kb = InlineKeyboardBuilder()
    kb.button(text="🔙 Назад", callback_data="choose_the_type_instruction")

    return kb.as_markup()

async def get_payment_6_kb_vless(telegram_id: int) -> InlineKeyboardMarkup:
    
    async with session_maker() as session:
        payment = await create_payment(
            session=session,
            telegram_id = telegram_id,
            months = 6,
            vpn_type = "vless",
            amount_value = prices.SUBSCRIPTION_PRICES["6_months"]
        )
    
    payment_url = payment['confirmation']['confirmation_url']

    kb = InlineKeyboardBuilder()
    kb.button(text="💵 Оплатить", callback_data="payment", url=payment_url)
    kb.button(text="🔙 Назад", callback_data="buy_period_vless")
    kb.adjust(1)

    return kb.as_markup()

async def get_payment_12_kb_vless(telegram_id: int) -> InlineKeyboardMarkup:
    
    async with session_maker() as session:
        payment = await create_payment(
            session=session,
            telegram_id = telegram_id,
            months = 12,
            vpn_type = "vless",
            amount_value = prices.SUBSCRIPTION_PRICES["12_months"]
        )
    
    payment_url = payment['confirmation']['confirmation_url']

    kb = InlineKeyboardBuilder()
    kb.button(text="💵 Оплатить", callback_data="payment", url=payment_url)
    kb.button(text="🔙 Назад", callback_data="buy_period_vless")
    kb.adjust(1)

    return kb.as_markup()

async def get_payment_6_kb_wireguard(telegram_id: int) -> InlineKeyboardMarkup:
    
    async with session_maker() as session:
        payment = await create_payment(
            session=session,
            telegram_id = telegram_id,
            months = 6,
            vpn_type = "wireguard",
            amount_value = prices.SUBSCRIPTION_PRICES["6_months"]
        )

    payment_url = payment['confirmation']['confirmation_url']

    kb = InlineKeyboardBuilder()
    kb.button(text="💵 Оплатить", callback_data="payment", url=payment_url)
    kb.button(text="🔙 Назад", callback_data="buy_period_wireguard")
    kb.adjust(1)

    return kb.as_markup()

async def get_payment_12_kb_wireguard(telegram_id: int) -> InlineKeyboardMarkup:
    
    async with session_maker() as session:
        payment = await create_payment(
            session=session,
            telegram_id = telegram_id,
            months = 12,
            vpn_type = "wireguard",
            amount_value = prices.SUBSCRIPTION_PRICES["12_months"]
        )
    
    payment_url = payment['confirmation']['confirmation_url']

    kb = InlineKeyboardBuilder()
    kb.button(text="💵 Оплатить", callback_data="payment", url=payment_url)
    kb.button(text="🔙 Назад", callback_data="buy_period_wireguard")
    kb.adjust(1)

    return kb.as_markup()