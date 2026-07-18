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
from services.remnawave import create_user_remnawave, edit_user_remnawave, get_user_remnawave
from services.wg_easy import create_user_wg_easy, edit_user_wg_easy, get_user_wg_easy
from aiohttp import web
from aiogram.types import BufferedInputFile

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
    days_to_add = relativedelta(days=order.days)
    
    if order.vpn_type == "vless":
        if not user.is_active_vpn or not user.expires_at_vless or user.expires_at_vless < datetime.now(timezone.utc):
            user.expires_at_vless = now + days_to_add
        else:
            user.expires_at_vless += days_to_add

        user.is_active_vpn = True

        try:
            await session.commit()
            logger.info(f"Подписка для пользователя {user.telegram_id} по заказу {payment_id} и типом VPN Vless успешно обновлена!")
        except Exception as e:
            await session.rollback()
            logger.exception(f"Критическая ошибка базы данных при сохранении заказа {payment_id}: {e}")
            return False 

        expires_at = user.expires_at_vless.isoformat() # API запрос принимает только iso формат
        # Создаем пользователя в Remnawave или редактирование
        if not user.remnawave_uuid:
            try:
                response = await create_user_remnawave(expires_at=expires_at, telegram_id=user.telegram_id)
                user.remnawave_uuid = response["response"]["uuid"]
                try:
                    await session.commit()
                except Exception as e:
                    logger.error(f"Ошибка добавления uuid в базу данных")
            except Exception as e:
                logger.error(f"Ошибка создания пользователя в Remnawave: {e}")
                return False
        else:
            try:
                await edit_user_remnawave(remnawave_uuid=user.remnawave_uuid, expires_at=user.expires_at_vless)
            except Exception as e:
                logger.error(f"Ошибка редактирования пользователя: {e}")
        # Отправляем сообщение пользователю
        try:
            moscow_time = user.expires_at_vless + timedelta(hours=3)
            readable_date = moscow_time.strftime("%d.%m.%Y %H:%M")

            vless_response = await get_user_remnawave(remnawave_uuid = user.remnawave_uuid)
            vless_subscription = vless_response['response']['subscriptionUrl']

            if order.days < 30:
                msg = f"✅ <b>Оплата прошла успешно!</b>\n\nВаша подписка на <b>Vless</b> продлена на {order.days} дней\nДействует до: <b>{readable_date} (МСК)</b> 🚀\n\nСпасибо, что выбрали <b>SALUTE VPN!</b>\n\n<b>Vless-подписка:</b><pre>{vless_subscription}</pre>"
            elif order.days == 30:
                msg = f"✅ <b>Оплата прошла успешно!</b>\n\nВаша подписка на <b>Vless</b> продлена на 1 месяц\nДействует до: <b>{readable_date} (МСК)</b> 🚀\n\nСпасибо, что выбрали <b>SALUTE VPN!</b>\n\n<b>Vless-подписка:</b><pre>{vless_subscription}</pre>"
            elif order.days == 90:
                msg = f"✅ <b>Оплата прошла успешно!</b>\n\nВаша подписка на <b>Vless</b> продлена на 3 месяца\nДействует до: <b>{readable_date} (МСК)</b> 🚀\n\nСпасибо, что выбрали <b>SALUTE VPN!</b>\n\n<b>Vless-подписка:</b><pre>{vless_subscription}</pre>"
            elif order.days == 180:
                msg = f"✅ <b>Оплата прошла успешно!</b>\n\nВаша подписка на <b>Vless</b> продлена на полгода\nДействует до: <b>{readable_date} (МСК)</b> 🚀\n\nСпасибо, что выбрали <b>SALUTE VPN!</b>\n\n<b>Vless-подписка:</b><pre>{vless_subscription}</pre>"
            elif order.days == 365:
                msg = f"✅ <b>Оплата прошла успешно!</b>\n\nВаша подписка на <b>Vless</b> продлена на год\nДействует до: <b> {readable_date} (МСК)</b> 🚀\n\nСпасибо, что выбрали <b>SALUTE VPN!</b>\n\n<b>Vless-подписка:</b><pre>{vless_subscription}</pre>"

            await bot.send_message(
                chat_id=user.telegram_id,
                text=msg
            )

            return True
        except Exception as e:
            logger.warning(f"VPN выдан, но не удалось отправить сообщение пользователю {user.telegram_id}: {e}")
            return True
    else:
        if not user.wg_id: # not user.is_active_vpn or not user.expires_at_wireguard or user.expires_at_wireguard < now:
            expires_at_fix = None
            user.expires_at_wireguard = now + days_to_add
            try:
                wg_user = await create_user_wg_easy(user.telegram_id, days_to_add)
                user.wg_id = wg_user
                try:
                    await session.commit()
                except Exception as e:
                    logger.error(f"Ошибка добавления wg_id в базу данных")
            except Exception as e:
                logger.error(f"Ошибка создания пользователя в WG Easy: {e}")
                error_details = traceback.format_exc()
                print("Детали ошибки:")
                print(error_details)
                return False
        else:
            expires_at_fix = user.expires_at_wireguard.strftime("%d.%m.%Y")
            user.expires_at_wireguard += days_to_add
            try:
                await edit_user_wg_easy(user.telegram_id, expires_at_fix, days_to_add)
            except Exception as e:
                logger.error(f"Ошибка создания пользователя в WG Easy: {e}")
                error_details = traceback.format_exc()
                print("Детали ошибки:")
                print(error_details)
                return False

        user.is_active_vpn = True
        
        try:
            await session.commit()
            logger.info(f"Подписка для пользователя {user.telegram_id} по заказу {payment_id} и типом VPN WireGuard успешно обновлена!")
        except Exception as e:
            await session.rollback()
            logger.exception(f"Критическая ошибка базы данных при сохранении заказа {payment_id}: {e}")
            return False
        
        expires_at = user.expires_at_wireguard.strftime("%d.%m.%Y")
            
        # Отправляем сообщение пользователю
        try:
            moscow_time = user.expires_at_wireguard + timedelta(hours=3)
            readable_date = moscow_time.strftime("%d.%m.%Y %H:%M")

            config = await get_user_wg_easy(wg_id = user.wg_id)
            config_file = BufferedInputFile(
                file=config.encode("utf-8"), 
                filename=f"Salute_VPN_{user.telegram_id}.conf"
            )

            if order.days < 30:
                msg = f"✅ <b>Оплата прошла успешно! WG конфиг ☝️</b>\n\nВаша подписка на <b>WireGuard</b> продлена на {order.days} дней\nДействует до: <b>{readable_date} (МСК)</b> 🚀\n\nСпасибо, что выбрали <b>SALUTE VPN!</b>"
            elif order.days == 30:
                msg = f"✅ <b>Оплата прошла успешно! WG конфиг ☝️</b>\n\nВаша подписка на <b>WireGuard</b> продлена на 1 месяц\nДействует до: <b>{readable_date} (МСК)</b> 🚀\n\nСпасибо, что выбрали <b>SALUTE VPN!</b>\n\n"
            elif order.days == 90:
                msg = f"✅ <b>Оплата прошла успешно! WG конфиг ☝️</b>\n\nВаша подписка на <b>WireGuard</b> продлена на 3 месяца\nДействует до: <b>{readable_date} (МСК)</b> 🚀\n\nСпасибо, что выбрали <b>SALUTE VPN!</b>\n\n"
            elif order.days == 180:
                msg = f"✅ <b>Оплата прошла успешно! WG конфиг ☝️</b>\n\nВаша подписка на <b>WireGuard</b> продлена на полгода\nДействует до: <b>{readable_date} (МСК)</b> 🚀\n\nСпасибо, что выбрали <b>SALUTE VPN!</b>\n\n"
            elif order.days == 365:
                msg = f"✅ <b>Оплата прошла успешно! WG конфиг ☝️</b>\n\nВаша подписка на <b>WireGuard</b> продлена на год\nДействует до: <b>{readable_date} (МСК)</b> 🚀\n\nСпасибо, что выбрали <b>SALUTE VPN!</b>\n\n"

            await bot.send_document(
                chat_id=user.telegram_id,
                caption=msg,
                document=config_file
            )

            return True
        except Exception as e:
            logger.warning(f"VPN выдан, но не удалось отправить сообщение пользователю {user.telegram_id}: {e}")
            return False