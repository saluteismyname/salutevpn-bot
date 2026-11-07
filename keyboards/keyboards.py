from datetime import datetime, timezone

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from database.models import User
import payments.prices as prices
from database.engine import session_maker
from sqlalchemy import select
from dateutil.relativedelta import relativedelta
from rich import print as rprint

def get_start_kb() -> ReplyKeyboardMarkup:
    
    kb = ReplyKeyboardBuilder()
    kb.button(text="💵 Купить")
    kb.button(text="📋 Мои подписки")
    kb.button(text="📜 Инструкция")
    kb.button(text="💬 Помощь")
    kb.button(text="🎁 Активировать пробную подписку")
    kb.button(text="🎁 Реферальная система")
    
    kb.adjust(2, 2, 1, 1)

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
    kb.button(text=buy_for_friend, callback_data="buy_for_friend_menu_vless")
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
    kb.button(text=buy_for_friend, callback_data="buy_for_friend_menu_wireguard")
    kb.button(text="🔙 Назад", callback_data="buy_type")
    kb.adjust(1)
    
    return kb.as_markup()

def get_buy_for_friend_kb_vless() -> InlineKeyboardMarkup:

    one_week = f"1 неделя - {int(prices.SUBSCRIPTION_PRICES_FOR_FRIEND['7_days'])}₽"
    one_month = f"1 месяц - {int(prices.SUBSCRIPTION_PRICES_FOR_FRIEND['30_days'])}₽"
    three_months = f"3 месяца - {int(prices.SUBSCRIPTION_PRICES_FOR_FRIEND['90_days'])}₽"
    six_months = f"6 месяцев - {int(prices.SUBSCRIPTION_PRICES_FOR_FRIEND['180_days'])}₽"
    twelve_months = f"12 месяцев - {int(prices.SUBSCRIPTION_PRICES_FOR_FRIEND['365_days'])}₽"

    kb = InlineKeyboardBuilder()
    kb.button(text=one_week, callback_data="buy_7_days_vless_for_friend")
    kb.button(text=one_month, callback_data="buy_30_days_vless_for_friend")
    kb.button(text=three_months, callback_data="buy_90_days_vless_for_friend")
    kb.button(text=six_months, callback_data="buy_180_days_vless_for_friend")
    kb.button(text=twelve_months, callback_data="buy_365_days_vless_for_friend")
    kb.button(text="🔙 Назад", callback_data="buy_period_vless")
    kb.adjust(1)
    
    return kb.as_markup()

def get_buy_for_friend_kb_wireguard() -> InlineKeyboardMarkup:

    one_week = f"1 неделя - {int(prices.SUBSCRIPTION_PRICES_FOR_FRIEND['7_days'])}₽"
    one_month = f"1 месяц - {int(prices.SUBSCRIPTION_PRICES_FOR_FRIEND['30_days'])}₽"
    three_months = f"3 месяца - {int(prices.SUBSCRIPTION_PRICES_FOR_FRIEND['90_days'])}₽"
    six_months = f"6 месяцев - {int(prices.SUBSCRIPTION_PRICES_FOR_FRIEND['180_days'])}₽"
    twelve_months = f"12 месяцев - {int(prices.SUBSCRIPTION_PRICES_FOR_FRIEND['365_days'])}₽"

    kb = InlineKeyboardBuilder()
    kb.button(text=one_week, callback_data="buy_7_days_wireguard_for_friend")
    kb.button(text=one_month, callback_data="buy_30_days_wireguard_for_friend")
    kb.button(text=three_months, callback_data="buy_90_days_wireguard_for_friend")
    kb.button(text=six_months, callback_data="buy_180_days_wireguard_for_friend")
    kb.button(text=twelve_months, callback_data="buy_365_days_wireguard_for_friend")
    kb.button(text="🔙 Назад", callback_data="buy_period_wireguard")
    kb.adjust(1)
    
    return kb.as_markup()

def get_type_subscriptions_kb() -> InlineKeyboardMarkup:

    kb = InlineKeyboardBuilder()

    kb.button(text="Vless", callback_data="vless_instruction")
    kb.button(text="WireGuard / AmneziaWG", callback_data="wireguard_instruction")

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

def get_payment_kb(days: int, vpn_type: str, payment: object, is_for_friend: bool) -> InlineKeyboardMarkup:
    
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

    if is_for_friend == True:
        kb.button(text="🔙 Назад", callback_data=f"buy_for_friend_menu_{vpn_type}")
    else:
        kb.button(text="🔙 Назад", callback_data=f"buy_period_{vpn_type}")


    kb.adjust(1)

    return kb.as_markup()

def subscription_menu_kb(vpn_type: str, page: int, order_id: str, uuid: str):
    kb = InlineKeyboardBuilder()

    kb.button(
        text="📱Редактировать устройства",
        callback_data=f"edit_devices_{uuid}_{order_id}"
    )

    kb.button(
        text="🔙 Назад",
        callback_data=f"friends_subs_page_{vpn_type}_{page}"
    )

    kb.adjust(1)

    return kb.as_markup()

def subscription_devices_menu_kb(devices: object, order_id: int, uuid: str):
    kb = InlineKeyboardBuilder()   
    count = 0

    for device in devices['response']['devices']:
        count += 1
        kb.button(
            text=f"📱{count}: {device['userAgent']}",
            callback_data=f"select_device:_{count}_{uuid}_{order_id}"
        )    
    kb.button(
        text="🔙 Назад",
        callback_data=f"select_order:_{order_id}"
    )

    kb.adjust(1)

    return kb.as_markup()

def subscription_device_menu_kb(uuid: str, order_id: int, device_id: str):
    kb = InlineKeyboardBuilder()   

    if uuid:
        kb.button(
            text="❌Удалить устройство",
            callback_data=f"delete_device_{device_id}_{uuid}"
        )
    
    kb.button(
        text="🔙 Назад",
        callback_data=f"edit_devices_{uuid}_{order_id}"
    )

    kb.adjust(1)

    return kb.as_markup()

def get_subscriptions_kb(orders_with_friends: list, orders_without_friends: list, page: int = 1):
    kb = InlineKeyboardBuilder()
    now = datetime.now(timezone.utc)
    buttons_count = 0
    user_has_orders_for_friends = False

    # 1. Рендерим личные подписки (они выводятся всегда целиком: 1 или 2 штуки)
    if orders_without_friends:
        for order, user in orders_without_friends:
            vpn_info = {
                "vless": ("Vless", user.expires_at_vless),
                "wireguard": ("WireGuard", user.expires_at_wireguard)
            }
            
            pretty_name, expire_date = vpn_info.get(order.vpn_type, (order.vpn_type, None))
            
            if expire_date:
                remaining_days = (expire_date - now).days
                remaining_hours = (expire_date - now).seconds // 3600
                if remaining_days > 0:
                    days_text = f"{format_days(remaining_days)}"
                elif remaining_hours > 0:
                    days_text = f"{format_hours(remaining_hours)}"
                else:
                    days_text = "Подписка истекла"
            else:
                days_text = f"{format_days(order.days)}"

            btn_text = f"📦 {pretty_name} | {days_text}"
            kb.button(
                text=btn_text,
                callback_data=f"select_order:_{order.id}"
            )
            buttons_count += 1

            if user.num_of_friends_vless > 0 or user.num_of_friends_wireguard > 0:
                user_has_orders_for_friends = True 

    # 2. Кнопка-разделитель «Подписки друзей» (выводится только если есть друзья)
    if user_has_orders_for_friends:
        kb.button(
            text='Подписки друзей 🔽',
            callback_data='ignore'
        )

    # 3. Пагинация для подписок друзей (по 4 штуки на страницу)
    if orders_with_friends:
        per_page = 4
        total_items = len(orders_with_friends)
        total_pages = (total_items + per_page - 1) // per_page
        page = max(1, min(page, total_pages))
        
        start = (page - 1) * per_page
        end = start + per_page
        current_friends_orders = orders_with_friends[start:end]

        for order, user in current_friends_orders:
            vpn_info = {
                "vless": "Vless",
                "wireguard": "WireGuard"
            }
            pretty_name = vpn_info.get(order.vpn_type, order.vpn_type)
            expire_date = order.created_at + relativedelta(days=order.days)
            
            if expire_date:
                remaining_days = (expire_date - now).days
                remaining_hours = (expire_date - now).seconds // 3600
                if remaining_days > 0:
                    days_text = f"{format_days(remaining_days)}"
                elif remaining_hours > 0:
                    days_text = f"{format_hours(remaining_hours)}"
                else:
                    days_text = "Подписка истекла"
            else:
                days_text = f"{format_days(order.days)}"

            btn_text = f"📦 {pretty_name} | {days_text}"
            kb.button(
                text=btn_text,
                callback_data=f"select_order:_{order.id}_{page}"
            )

    # Настройка сетки для основных кнопок (личные подписки, разделитель и подписки друзей)
    if buttons_count > 1:
        kb.adjust(2, 1, 2)
    else:
        kb.adjust(1, 1, 2)

    # 4. Блок пагинации в самом низу (индикатор на отдельной строке, стрелки ниже)
    if orders_with_friends and total_pages > 1:
        # Первая строка пагинации: Индикатор текущей страницы (строго 1 в ряд)
        kb.row(
            InlineKeyboardButton(
                text=f"📄 {page} из {total_pages}", 
                callback_data="ignore"
            )
        )
        
        # Вторая строка пагинации: Кнопки «Назад» и «Вперед» (по 2 в ряд)
        nav_buttons = []
        if page > 1:
            nav_buttons.append(
                InlineKeyboardButton(text="⬅️ Назад", callback_data=f"friends_subs_page_{page - 1}")
            )
        if page < total_pages:
            nav_buttons.append(
                InlineKeyboardButton(text="Вперед ➡️", callback_data=f"friends_subs_page_{page + 1}")
            )
            
        if nav_buttons:
            kb.row(*nav_buttons)

    return kb.as_markup()

def get_paginated_subscriptions_kb(prices_dict: dict, page: int, per_page: int, vpn_type: str, for_friend: bool):
    kb = InlineKeyboardBuilder()
    
    # Превращаем словарь в список словарей: [{'days': 7, 'price': 69}, {'days': 30, 'price': 129}, ...]
    tariffs = [
        {"days": int(key.split("_")[0]), "price": price}
        for key, price in prices_dict.items()
    ]
    
    # Расчет пагинации
    total_pages = (len(tariffs) + per_page - 1) // per_page
    page = max(1, min(page, total_pages))
    
    start = (page - 1) * per_page
    end = start + per_page
    current_tariffs = tariffs[start:end]
    
    # 1. Кнопки тарифов текущей страницы
    for tariff in current_tariffs:
        days = tariff["days"]
        price = tariff["price"]
        friend_suffix = "_for" if for_friend else ""
        
        kb.row(
            InlineKeyboardButton(
                text=f"🗓 {days} дней — {price}₽",
                callback_data=f"buy_{days}_days_{vpn_type}{friend_suffix}"
            )
        )
    
    # 2. Ряд навигации (если страниц больше одной)
    if total_pages > 1:
        nav_buttons = []
        
        if page > 1:
            nav_buttons.append(
                InlineKeyboardButton(
                    text="⬅️ Назад", 
                    callback_data=f"sub_page_{page - 1}_{vpn_type}_{1 if for_friend else 0}"
                )
            )
            
        nav_buttons.append(
            InlineKeyboardButton(text=f"📄 {page} / {total_pages}", callback_data="ignore")
        )
        
        if page < total_pages:
            nav_buttons.append(
                InlineKeyboardButton(
                    text="Вперед ➡️", 
                    callback_data=f"sub_page_{page + 1}_{vpn_type}_{1 if for_friend else 0}"
                )
            )
            
        kb.row(*nav_buttons)
        
    # 3. Кнопка возврата в меню
    kb.row(
        InlineKeyboardButton(text="« Назад", callback_data="back_to_menu")
    )
    
    return kb.as_markup()

def format_days(n: int) -> str:
    if n % 10 == 1 and n % 100 != 11:
        return f"{n} день"
    elif 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20):
        return f"{n} дня"
    else:
        return f"{n} дней"

def format_hours(n: int) -> str:
    if n % 10 == 1 and n % 100 != 11:
        return f"{n} час"
    elif 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20):
        return f"{n} часа"
    else:
        return f"{n} часов"