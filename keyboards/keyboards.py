from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from database.models import User
from payments.payments import create_payment
import payments.prices as prices
from database.engine import session_maker
from sqlalchemy import select

def get_start_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="💵 Купить")
    kb.button(text="📜 Инструкция")
    kb.button(text="🎁 Реферальная система")
    kb.button(text="💬 Помощь")
    kb.adjust(2, 1, 1)

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
    buy_for_friend = f"🎁 Купить подписку другу"

    kb = InlineKeyboardBuilder()
    kb.button(text=one_week, callback_data="buy_7_days_vless")
    kb.button(text=one_month, callback_data="buy_30_days_vless")
    kb.button(text=three_months, callback_data="buy_90_days_vless")
    kb.button(text=six_months, callback_data="buy_180_days_vless")
    kb.button(text=twelve_months, callback_data="buy_365_days_vless")
    kb.button(text=buy_for_friend, callback_data="buy_for_friend_vless")
    kb.button(text="🔙 Назад", callback_data="buy_type_vless")
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
    kb.button(text="🔙 Назад", callback_data="buy_type_vless")
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

async def get_payment_kb_vless(telegram_id: int, days: int) -> InlineKeyboardMarkup:
    
    base_price = prices.SUBSCRIPTION_PRICES[f"{days}_days"]

    async with session_maker() as session:        

        user_query = select(User).where(User.telegram_id == telegram_id)
        user_result = await session.execute(user_query)
        user = user_result.scalar_one()
        
        bonus_balance = user.bonus_balance
    
    kb = InlineKeyboardBuilder()

    # Сценарий А: Бонусов хватает на полную оплату
    if bonus_balance >= base_price:

        async with session_maker() as session:
                    # Создаем платеж в YooKassa на оставшуюся сумму (final_amount)
                    # В metadata передаем id заказа, чтобы связать его при получении вебхука
                    payment = await create_payment(
                        session=session,
                        telegram_id=telegram_id,
                        days=days,
                        vpn_type="vless",
                        amount_value=base_price,
                        bonuses_spent=0,
                    )

        payment_url = payment['confirmation']['confirmation_url']
        
        kb.button(
            text=f"💳 Оплатить картой",
            url=payment_url
        )

        # Здесь вместо ссылки на оплату YooKassa мы ведем на callback-хэндлер полной оплаты бонусами

        kb.button(
            text=f"🎁 Оплатить полностью бонусами ({base_price}₽.)", 
            callback_data=f"pay_full_bonuses_{days}_days_vless"
        )
    else:
        # Сценарий Б: Бонусов не хватает, делаем частичную скидку (или бонусов 0)
        bonuses_to_spend = int(bonus_balance) # сколько бонусов спишем (все доступные)
        final_amount = base_price - bonuses_to_spend # сколько останется доплатить картой
        
        async with session_maker() as session:
            # Создаем платеж в YooKassa на оставшуюся сумму (final_amount)
            # В metadata передаем id заказа, чтобы связать его при получении вебхука
            payment = await create_payment(
                session=session,
                telegram_id=telegram_id,
                days=days,
                vpn_type="vless",
                amount_value=final_amount,
                bonuses_spent=bonuses_to_spend,
                )
        
        payment_url = payment['confirmation']['confirmation_url']
        
        if bonuses_to_spend > 0:
            btn_text = f"💳 Списать {bonuses_to_spend} бонусов + Оплатить {final_amount}₽."
        else:
            btn_text = f"💵 Оплатить ({final_amount}₽.)"
            
        kb.button(text=btn_text, url=payment_url)

    kb.button(text="🔙 Назад", callback_data="buy_period_vless")
    kb.adjust(1)

    return kb.as_markup()

async def get_payment_kb_wireguard(telegram_id: int, days: int) -> InlineKeyboardMarkup:
    
    base_price = prices.SUBSCRIPTION_PRICES[f"{days}_days"]

    async with session_maker() as session:        

        user_query = select(User).where(User.telegram_id == telegram_id)
        user_result = await session.execute(user_query)
        user = user_result.scalar_one()
        
        bonus_balance = user.bonus_balance
    
    kb = InlineKeyboardBuilder()

    # Сценарий А: Бонусов хватает на полную оплату
    if bonus_balance >= base_price:
        # Здесь вместо ссылки на оплату YooKassa мы ведем на callback-хэндлер полной оплаты бонусами
        kb.button(
            text=f"🎁 Оплатить полностью бонусами ({base_price}₽.)", 
            callback_data=f"pay_full_bonuses_{days}_days_wireguard"
        )
    else:
        # Сценарий Б: Бонусов не хватает, делаем частичную скидку (или бонусов 0)
        bonuses_to_spend = int(bonus_balance) # сколько бонусов спишем (все доступные)
        final_amount = base_price - bonuses_to_spend # сколько останется доплатить картой
        
        async with session_maker() as session:
            # Создаем платеж в YooKassa на оставшуюся сумму (final_amount)
            # В metadata передаем id заказа, чтобы связать его при получении вебхука
            payment = await create_payment(
                session=session,
                telegram_id=telegram_id,
                days=days,
                vpn_type="wireguard",
                amount_value=final_amount,
                bonuses_spent=bonuses_to_spend,
                )
        
        payment_url = payment['confirmation']['confirmation_url']
        
        if bonuses_to_spend > 0:
            btn_text = f"💳 Списать {bonuses_to_spend} бонусов + Оплатить {final_amount}₽."
        else:
            btn_text = f"💵 Оплатить ({final_amount} ₽.)"
            
        kb.button(text=btn_text, url=payment_url)

    kb.button(text="🔙 Назад", callback_data="buy_period_wireguard")
    kb.adjust(1)

    return kb.as_markup()