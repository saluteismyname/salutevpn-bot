from asyncio.log import logger
from datetime import datetime, timedelta, timezone
import logging
import traceback
from zoneinfo import ZoneInfo
from dateutil.relativedelta import relativedelta
from aiogram import Bot
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Order, User
from payments import prices
from services.remnawave import create_user_remnawave
from services.wg_easy import create_user_wg_easy
from aiohttp import web

from services.wg_easy import create_user_wg_easy

logger = logging.getLogger(__name__)

async def process_vpn_delivery(
        session: AsyncSession,
        bot: Bot, 
        payment_id: str
    ) -> bool:
    query = select(Order).where(Order.payment_id == payment_id)
    result = await session.execute(query)
    order = result.scalar_one_or_none()

    if not order:
        logger.error(f"Заказ с payment_id {payment_id} не найден в Базе Данных!")
        return False
    
    if order.status == "paid":
        logger.info(f"Заказ с payment_id {payment_id} уже был обработан ранее.")
        return True

    order.status = "paid"

    user_query = select(User).where(User.telegram_id == order.telegram_id)
    user_result = await session.execute(user_query)
    user = user_result.scalar_one()

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    months_to_add = relativedelta(months=order.months)
    
    if order.vpn_type == "vless":
        if not user.is_active_vpn or not user.expires_at_vless or user.expires_at_vless < now:
            user.expires_at_vless = now + months_to_add
        else:
            user.expires_at_vless += months_to_add

        user.is_active_vpn = True

        try:
            await session.commit()
            logger.info(f"Подписка для пользователя {user.telegram_id} по заказу {payment_id} и типом VPN Vless успешно обновлена!")
        except Exception as e:
            await session.rollback()
            logger.exception(f"Критическая ошибка базы данных при сохранении заказа {payment_id}: {e}")
            return False 

        expires_at = user.expires_at_vless.isoformat() # API запрос принимает только iso формат
        # Создаем пользователя в Remnawave
        try:
            await create_user_remnawave(expires_at=expires_at, telegram_id=user.telegram_id)
        except Exception as e:
            logger.error(f"Ошибка создания пользователя в Remnawave: {e}")
            return False
        # Отправляем сообщение пользователю
        try:
            moscow_time = user.expires_at_vless + timedelta(hours=3)
            readable_date = moscow_time.strftime("%d.%m.%Y %H:%M")

            await bot.send_message(
                chat_id=user.telegram_id,
                text=(
                    f"✅ <b>Оплата прошла успешно!</b>\n\n"
                    f"Ваша подписка на <b>Vless</b> продлена на {order.months} мес.\n"
                    f"Действует до: <b>{readable_date} (МСК)</b>. 🚀\n\n"
                    f"Спасибо, что выбрали Salute VPN!"
                ),
            )

            return True
        except Exception as e:
            logger.warning(f"VPN выдан, но не удалось отправить сообщение пользователю {user.telegram_id}: {e}")
            return True
    else:
        if not user.is_active_vpn or not user.expires_at_wireguard or user.expires_at_wireguard < now:
            expires_at_fix = None
            user.expires_at_wireguard = now + months_to_add
            firstly = True
        else:
            expires_at_fix = user.expires_at_wireguard.strftime("%d.%m.%Y")
            user.expires_at_wireguard += months_to_add
            firstly = False

        user.is_active_vpn = True
        
        try:
            await session.commit()
            logger.info(f"Подписка для пользователя {user.telegram_id} по заказу {payment_id} и типом VPN WireGuard успешно обновлена!")
        except Exception as e:
            await session.rollback()
            logger.exception(f"Критическая ошибка базы данных при сохранении заказа {payment_id}: {e}")
            return False
        
        expires_at = user.expires_at_wireguard.strftime("%d.%m.%Y")

        # Создаём пользователя в WG Easy
        try:
            await create_user_wg_easy(user.telegram_id, expires_at_fix, months_to_add, firstly)
        except Exception as e:
            logger.error(f"Ошибка создания пользователя в WG Easy: {e}")
            error_details = traceback.format_exc()
            print("Детали ошибки:")
            print(error_details)
            return False
        # Отправляем сообщение пользователю
        try:
            moscow_time = user.expires_at_wireguard + timedelta(hours=3)
            readable_date = moscow_time.strftime("%d.%m.%Y %H:%M")

            await bot.send_message(
                chat_id=user.telegram_id,
                text=(
                    f"✅ <b>Оплата прошла успешно!</b>\n\n"
                    f"Ваша подписка на <b>WireGuard</b> продлена на {order.months} мес.\n"
                    f"Действует до: <b>{readable_date} (МСК)</b>. 🚀\n\n"
                    f"Спасибо, что выбрали Salute VPN!"
                ),
            )

            return True
        except Exception as e:
            logger.warning(f"VPN выдан, но не удалось отправить сообщение пользователю {user.telegram_id}: {e}")
            return False