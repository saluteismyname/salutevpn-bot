from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from database.models import User
import payments.prices as prices
from database.engine import session_maker
from sqlalchemy import select

def get_start_kb() -> ReplyKeyboardMarkup:
    
    kb = ReplyKeyboardBuilder()
    kb.button(text="💵 Купить")
    kb.button(text="📜 Инструкция")
    kb.button(text="🎁 Активировать пробную подписку")
    kb.button(text="🎁 Реферальная система")
    kb.button(text="💬 Помощь")
    kb.adjust(2, 1, 1, 1)

    return kb.as_markup(resize_keyboard=True)

def get_buy_type_kb() -> InlineKeyboardMarkup:
   
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
    buy_for_friend = f"🎁 Купить подписку другу"

    kb = InlineKeyboardBuilder()
    kb.button(text=one_week, callback_data="buy_7_days_vless")
    kb.button(text=one_month, callback_data="buy_30_days_vless")
    kb.button(text=three_months, callback_data="buy_90_days_vless")
    kb.button(text=six_months, callback_data="buy_180_days_vless")
    kb.button(text=twelve_months, callback_data="buy_365_days_vless")
    kb.button(text=buy_for_friend, callback_data="buy_for_friend_vless")
    kb.button(text="🔙 Назад", callback_data="buy_type")
    kb.adjust(1)
    
    return kb.as_markup()

def get_buy_period_kb_wireguard() -> InlineKeyboardMarkup:
    
    one_week = f"1 неделя - {prices.SUBSCRIPTION_PRICES['7_days']}₽"
    one_month = f"1 месяц - {prices.SUBSCRIPTION_PRICES['30_days']}₽"
    three_months = f"3 месяца - {prices.SUBSCRIPTION_PRICES['90_days']}₽"
    six_months = f"6 месяцев - {prices.SUBSCRIPTION_PRICES['180_days']}₽"
    twelve_months = f"12 месяцев - {prices.SUBSCRIPTION_PRICES['365_days']}₽"
    buy_for_friend = f"🎁 Купить подписку другу"

    kb = InlineKeyboardBuilder()
    kb.button(text=one_week, callback_data="buy_7_days_wireguard")
    kb.button(text=one_month, callback_data="buy_30_days_wireguard")
    kb.button(text=three_months, callback_data="buy_90_days_wireguard")
    kb.button(text=six_months, callback_data="buy_180_days_wireguard")
    kb.button(text=twelve_months, callback_data="buy_365_days_wireguard")
    kb.button(text=buy_for_friend, callback_data="buy_for_friend_wireguard")
    kb.button(text="🔙 Назад", callback_data="buy_type")
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

def get_buy_for_friend_kb_vless() -> InlineKeyboardMarkup:

    one_week = f"1 неделя - {prices.SUBSCRIPTION_PRICES['7_days']}₽"
    one_month = f"1 месяц - {prices.SUBSCRIPTION_PRICES['30_days']}₽"
    three_months = f"3 месяца - {prices.SUBSCRIPTION_PRICES['90_days']}₽"
    six_months = f"6 месяцев - {prices.SUBSCRIPTION_PRICES['180_days']}₽"
    twelve_months = f"12 месяцев - {prices.SUBSCRIPTION_PRICES['365_days']}₽"

    kb = InlineKeyboardBuilder()
    kb.button(text=one_week, callback_data="buy_7_days_vless_friend")
    kb.button(text=one_month, callback_data="buy_30_days_vless_friend")
    kb.button(text=three_months, callback_data="buy_90_days_vless_friend")
    kb.button(text=six_months, callback_data="buy_180_days_vless_friend")
    kb.button(text=twelve_months, callback_data="buy_365_days_vless_friend")
    kb.button(text="🔙 Назад", callback_data="get_buy_type_kb")
    kb.adjust(1)
    
    return kb.as_markup()

def get_buy_for_friend_kb_wireguard() -> InlineKeyboardMarkup:

    one_week = f"1 неделя - {prices.SUBSCRIPTION_PRICES['7_days']}₽"
    one_month = f"1 месяц - {prices.SUBSCRIPTION_PRICES['30_days']}₽"
    three_months = f"3 месяца - {prices.SUBSCRIPTION_PRICES['90_days']}₽"
    six_months = f"6 месяцев - {prices.SUBSCRIPTION_PRICES['180_days']}₽"
    twelve_months = f"12 месяцев - {prices.SUBSCRIPTION_PRICES['365_days']}₽"

    kb = InlineKeyboardBuilder()
    kb.button(text=one_week, callback_data="buy_7_days_wireguard_friend")
    kb.button(text=one_month, callback_data="buy_30_days_wireguard_friend")
    kb.button(text=three_months, callback_data="buy_90_days_wireguard_friend")
    kb.button(text=six_months, callback_data="buy_180_days_wireguard_friend")
    kb.button(text=twelve_months, callback_data="buy_365_days_wireguard_friend")
    kb.button(text="🔙 Назад", callback_data="buy_type_wireguard")
    kb.adjust(1)
    
    return kb.as_markup()

def get_trial_type_kb():
    
    kb=InlineKeyboardBuilder()
    
    kb.button(
        text="🎁 Активировать пробный период Vless",
        callback_data="activate_trial_vless"
    )
    kb.button(
        text="🎁 Активировать пробный период AmneziaWG",
        callback_data="activate_trial_wireguard"
    )

    kb.adjust(1)

    return kb.as_markup()

def get_payment_kb(days: int, vpn_type: str, payment: object) -> InlineKeyboardMarkup:
    
    kb = InlineKeyboardBuilder()

    if payment["bonuses_to_spend"] > 0 and payment["bonuses_to_spend"] < payment["base_price"]:
        btn_text = f"💵 Списать {payment['bonuses_to_spend']} бонусов + Оплатить {payment['final_amount']}₽."
        kb.button(text=btn_text, url=payment["payment_with_bonuses_url"])
        kb.button(
                    text=f"💳 Оплатить картой",
                    url=payment["payment_without_bonuses_url"]
                )
    elif payment["bonuses_spendable_for_full"] == True:
        kb.button(
                text=f"🎁 Оплатить полностью бонусами ({prices.SUBSCRIPTION_PRICES[f'{days}_days']}₽.)", 
                callback_data=f"pay_full_bonuses_{days}_days_{vpn_type}"
        )
        kb.button(
                    text=f"💳 Оплатить картой",
                    url=payment["payment_without_bonuses_url"]
        )
    else:
        kb.button(
            text=f"💳 Оплатить картой",
            url=payment["payment_without_bonuses_url"]
        )

    kb.button(text="🔙 Назад", callback_data=f"buy_period_{vpn_type}")
    kb.adjust(1)

    return kb.as_markup()