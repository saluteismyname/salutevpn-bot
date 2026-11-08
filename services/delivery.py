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
import httpx
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

    #Ветвление подписки для пользователя
    if order.vpn_type == "vless" and order.is_for_friend == False:
        if not user.is_active_vpn or not user.expires_at_vless or user.expires_at_vless < datetime.now(timezone.utc):
            user.expires_at_vless = now + days_to_add
        else:
            user.expires_at_vless += days_to_add

        user.is_active_vpn = True
        user.is_first_time = False

        try:
            await session.commit()
            logger.info(f"Подписка для пользователя {user.telegram_id} по заказу {payment_id} и типом VPN Vless успешно обновлена!")
        except Exception as e:
            await session.rollback()
            logger.exception(f"Критическая ошибка базы данных при сохранении заказа {payment_id}: {e}")
            return False 

        expires_at = user.expires_at_vless.isoformat()
        # Создаем пользователя в Remnawave если его нет
        if not user.remnawave_uuid:
            try:
                response = await create_user_remnawave(expires_at=expires_at, telegram_id=user.telegram_id, is_for_friend=False, num_of_friends_vless=user.num_of_friends_vless)
                if response:
                    user.remnawave_uuid = response["response"]["uuid"]
                    try:
                        await session.commit()
                    except Exception as e:
                        logger.error(f"Ошибка добавления uuid в базу данных")
            except httpx.HTTPStatusError as e:
                # Выведет точный текст ошибки от сервера Remnawave
                logger.error(f"Код: {e.response.status_code}, Ответ: {e.response.text}")
            except Exception as e:
                logger.exception(f"Общая ошибка:")
        else:
            expires_at = user.expires_at_vless + relativedelta(days=order.days)
            try:
                await edit_user_remnawave(remnawave_uuid=user.remnawave_uuid, expires_at=expires_at.isoformat())
            except Exception as e:
                logger.error(f"Ошибка редактирования пользователя: {e}")
        # Отправляем сообщение пользователю
        try:
            moscow_time = user.expires_at_vless + timedelta(hours=3)
            readable_date = moscow_time.strftime("%d.%m.%Y %H:%M")

            if user.remnawave_uuid:
                vless_response = await get_user_remnawave(remnawave_uuid = user.remnawave_uuid)
                if vless_response:
                    vless_subscription = vless_response["response"]["subscriptionUrl"]

            if order.days < 30:
                msg = f"✅ <b>Оплата прошла успешно!</b>\n\nВаша подписка на <b>Vless</b> продлена на {order.days} дней\nДействует до: <b>{readable_date} (МСК)</b> 🚀\n\nСпасибо, что выбрали <b>SALUTE VPN!</b>\n\n<b>Vless-подписка:</b><pre>{vless_subscription}</pre>"
            elif order.days == 30:
                msg = f"✅ <b>Оплата прошла успешно!</b>\n\nВаша подписка на <b>Vless</b> продлена на 1 месяц\nДействует до: <b>{readable_date} (МСК)</b> 🚀\n\nСпасибо, что выбрали <b>SALUTE VPN!</b>\n\n<b>Vless-подписка:</b><pre>{vless_subscription}</pre>"
            elif order.days == 90:
                msg = f"✅ <b>Оплата прошла успешно!</b>\n\nВаша подписка на <b>Vless</b> продлена на 3 месяца\nДействует до: <b>{readable_date} (МСК)</b> 🚀\n\nСпасибо, что выбрали <b>SALUTE VPN!</b>\n\n<b>Vless-подписка:</b><pre>{vless_subscription}</pre>"
            elif order.days == 180:
                msg = f"✅ <b>Оплата прошла успешно!</b>\n\nВаша подписка на <b>Vless</b> продлена на 6 месяцев\nДействует до: <b>{readable_date} (МСК)</b> 🚀\n\nСпасибо, что выбрали <b>SALUTE VPN!</b>\n\n<b>Vless-подписка:</b><pre>{vless_subscription}</pre>"
            elif order.days == 365:
                msg = f"✅ <b>Оплата прошла успешно!</b>\n\nВаша подписка на <b>Vless</b> продлена на 1 год\nДействует до: <b> {readable_date} (МСК)</b> 🚀\n\nСпасибо, что выбрали <b>SALUTE VPN!</b>\n\n<b>Vless-подписка:</b><pre>{vless_subscription}</pre>"

            try:
                await bot.send_message(
                    chat_id=user.telegram_id,
                    text=msg
                )
            except Exception as e:
                logger.exception(f"Не удалось отправить уведомление об оплате: {e}")

            return True
        except httpx.HTTPStatusError as e:
            # Выведет точный текст ошибки от сервера Remnawave
            logger.error(f"Код: {e.response.status_code}, Ответ: {e.response.text}") 
        except Exception as e:
            # Метод .exception запишет в логи не просто имя ошибки, 
            # а конкретный файл и номер строки, где она упала.
            logger.exception("Произошел сбой при обработке запроса к Remnawave")

    elif order.vpn_type == "wireguard" and order.is_for_friend == False:
        if not user.wg_id: 
            expires_at_fix = None
            user.expires_at_wireguard = now + days_to_add
            try:
                wg_user = await create_user_wg_easy(user.telegram_id, days_to_add, is_for_friend=False, num_of_friends_wireguard=None, wg_panel=order.wg_panel)
                user.wg_id = wg_user
                user.is_first_time = False
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
                await edit_user_wg_easy(user.telegram_id, expires_at_fix, days_to_add, wg_panel=order.wg_panel)
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

            config = await get_user_wg_easy(wg_id = user.wg_id, wg_panel=order.wg_panel)
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
                msg = f"✅ <b>Оплата прошла успешно! WG конфиг ☝️</b>\n\nВаша подписка на <b>WireGuard</b> продлена на 6 месяцев\nДействует до: <b>{readable_date} (МСК)</b> 🚀\n\nСпасибо, что выбрали <b>SALUTE VPN!</b>\n\n"
            elif order.days == 365:
                msg = f"✅ <b>Оплата прошла успешно! WG конфиг ☝️</b>\n\nВаша подписка на <b>WireGuard</b> продлена на 1 год\nДействует до: <b>{readable_date} (МСК)</b> 🚀\n\nСпасибо, что выбрали <b>SALUTE VPN!</b>\n\n"

            try:
                await bot.send_document(
                    chat_id=user.telegram_id,
                    document=config_file,
                    caption=msg,
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.exception(f"Не удалось отправить уведомление об оплате: {e}")

            return True
        except Exception as e:
            logger.warning(f"VPN выдан, но не удалось отправить сообщение пользователю {user.telegram_id}: {e}")
            return False

    elif order.vpn_type == "vless" and order.is_for_friend == True:

        expires_at = now + relativedelta(days=order.days)
        expires_at = expires_at.isoformat()
        # Создаем пользователя в Remnawave или редактирование
        
        expires_at_date = now + timedelta(days=order.days)
        if isinstance(expires_at, datetime):
            expires_at = str(expires_at.isoformat())
        else:
            expires_at = str(expires_at)
        try:
            user.num_of_friends_vless += 1
            order.friend_number_vless = user.num_of_friends_vless
            response = await create_user_remnawave(expires_at=expires_at, telegram_id=user.telegram_id, is_for_friend=True, num_of_friends_vless=user.num_of_friends_vless)
            order.remnawave_uuid = response["response"]["uuid"]
            
            moscow_time = expires_at_date + timedelta(hours=3)
            readable_date = moscow_time.strftime("%d.%m.%Y %H:%M")
            vless_subscription = response["response"]["subscriptionUrl"]
            try:
                await session.commit()
                logger.info(f"Подписка для пользователя {user.telegram_id} и его друга №{user.num_of_friends_vless} по заказу {payment_id} и типом VPN Vless успешно обновлена!")
            except Exception as e:
                await session.rollback()
                logger.exception(f"Критическая ошибка базы данных при сохранении заказа {payment_id}: {e}")
                return False 
                
            if order.days < 30:
                msg = f"✅ <b>Оплата прошла успешно!</b>\n\nВаша подписка на <b>Vless</b> продлена на {order.days} дней\nДействует до: <b>{readable_date} (МСК)</b> 🚀\n\nСпасибо, что выбрали <b>SALUTE VPN!</b>\n\n<b>Vless-подписка:</b><pre>{vless_subscription}</pre>"
            elif order.days == 30:
                msg = f"✅ <b>Оплата прошла успешно!</b>\n\nВаша подписка на <b>Vless</b> продлена на 1 месяц\nДействует до: <b>{readable_date} (МСК)</b> 🚀\n\nСпасибо, что выбрали <b>SALUTE VPN!</b>\n\n<b>Vless-подписка:</b><pre>{vless_subscription}</pre>"
            elif order.days == 90:
                msg = f"✅ <b>Оплата прошла успешно!</b>\n\nВаша подписка на <b>Vless</b> продлена на 3 месяца\nДействует до: <b>{readable_date} (МСК)</b> 🚀\n\nСпасибо, что выбрали <b>SALUTE VPN!</b>\n\n<b>Vless-подписка:</b><pre>{vless_subscription}</pre>"
            elif order.days == 180:
                msg = f"✅ <b>Оплата прошла успешно!</b>\n\nВаша подписка на <b>Vless</b> продлена на 6 месяцев\nДействует до: <b>{readable_date} (МСК)</b> 🚀\n\nСпасибо, что выбрали <b>SALUTE VPN!</b>\n\n<b>Vless-подписка:</b><pre>{vless_subscription}</pre>"
            elif order.days == 365:
                msg = f"✅ <b>Оплата прошла успешно!</b>\n\nВаша подписка на <b>Vless</b> продлена на 1 год\nДействует до: <b> {readable_date} (МСК)</b> 🚀\n\nСпасибо, что выбрали <b>SALUTE VPN!</b>\n\n<b>Vless-подписка:</b><pre>{vless_subscription}</pre>"

            try:
                await bot.send_message(
                    chat_id=user.telegram_id,
                    text=msg
                )
            except Exception as e:
                logger.exception(f"Не удалось отправить уведомление об оплате: {e}")

            return True
        except httpx.HTTPStatusError as e:
            # Выведет точный текст ошибки от сервера Remnawave
            logger.error(f"Код: {e.response.status_code}, Ответ: {e.response.text}") 
        except Exception as e:
            logger.exception(f"Ошибка создания пользователя {e}")

    elif order.vpn_type == "wireguard" and order.is_for_friend == True:
        expires_at_fix = None
        expires_at_wireguard = now + days_to_add
        user.num_of_friends_wireguard += 1
        order.friend_number_vless = user.num_of_friends_vless
        num_of_friends_wireguard = user.num_of_friends_wireguard
        try:
            wg_user = await create_user_wg_easy(user.telegram_id, days_to_add, is_for_friend=True, num_of_friends_wireguard=num_of_friends_wireguard)
            order.wg_id = wg_user
            try:
                await session.commit()
            except Exception as e:
                logger.error(f"Ошибка добавления wg_id в базу данных при покупке для друга")
        except Exception as e:
            logger.error(f"Ошибка создания пользователя в WG Easy: {e}")
            error_details = traceback.format_exc()
            print("Детали ошибки:")
            print(error_details)
            return False
        
        expires_at = expires_at_wireguard.strftime("%d.%m.%Y")
            
        # Отправляем сообщение пользователю
        try:
            moscow_time = order.created_at + relativedelta(days=order.days) + timedelta(hours=3)
            readable_date = moscow_time.strftime("%d.%m.%Y %H:%M")

            config = await get_user_wg_easy(wg_id = order.wg_id, wg_panel=order.wg_panel)
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
                msg = f"✅ <b>Оплата прошла успешно! WG конфиг ☝️</b>\n\nВаша подписка на <b>WireGuard</b> продлена на 6 месяцев\nДействует до: <b>{readable_date} (МСК)</b> 🚀\n\nСпасибо, что выбрали <b>SALUTE VPN!</b>\n\n"
            elif order.days == 365:
                msg = f"✅ <b>Оплата прошла успешно! WG конфиг ☝️</b>\n\nВаша подписка на <b>WireGuard</b> продлена на 1 год\nДействует до: <b>{readable_date} (МСК)</b> 🚀\n\nСпасибо, что выбрали <b>SALUTE VPN!</b>\n\n"

            try:
                await bot.send_document(
                    chat_id=user.telegram_id,
                    document=config_file,
                    caption=msg,
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.exception(f"Не удалось отправить уведомление об оплате при окупке для друга: {e}")

            return True
        except Exception as e:
            logger.warning(f"VPN выдан, но не удалось отправить сообщение пользователю {user.telegram_id} при покупке для друга: {e}")
            return False