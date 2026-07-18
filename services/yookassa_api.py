import asyncio
from asyncio.log import logger
import ipaddress
import aiohttp
from config import config
from aiohttp import web
from database.models import Order, User
from database.engine import session_maker
from services.delivery import process_vpn_delivery
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from database.engine import session_maker
from sqlalchemy import select
# Проверям принадлежит ли IP серверу, который шлёт вэбхук
def is_yookassa_ip(ip_str: str) -> bool:
    try:
        clean_ip = ip_str.split(':')[0]
        ip = ipaddress.ip_address(clean_ip)
        # config.yookassa_networks уже содержит список объектов ip_network
        return any(ip in net for net in config.yookassa_networks)
    except ValueError:
        return False
# Проверяем статус платежа ЮКассы
async def fetch_payment_status(payment_id: str) -> dict | None:
    url = f"https://api.yookassa.ru/v3/payments/{payment_id}"
    
    # ЮKassa использует Basic Auth (ShopID : SecretKey)
    auth = aiohttp.BasicAuth(
        login=config.yookassa_account_id, 
        password=config.yookassa_secret_key.get_secret_value()
    )
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, auth=auth) as response:
            if response.status == 200:
                return await response.json()
            return None
# Хэндлер вэбхуков ЮКассы
async def yookassa_webhook_handler(request: web.Request) -> web.Response:
    # Извлекаем IP из HTTP-заголовка X-Forwarded-For
    forwarded_for = request.headers.get('X-Forwarded-For')
    client_ip = forwarded_for.split(',')[0].strip() if forwarded_for else request.remote
    
    if not is_yookassa_ip(client_ip):
        logger.warning(f"Блокировка запроса к вебхуку ЮKassa с левого IP: {client_ip}")
        return web.Response(status=403, text="Forbidden")

    try:
        data = await request.json()
        payment_obj = data.get("object", {})
        payment_id = payment_obj.get("id")

        metadata = payment_obj.get("metadata", {})
        internal_order_id = metadata.get("order_id")
        
        if not payment_id:
            return web.Response(status=400, text="Missing Payment ID")

        # Проверяем статус платежа напрямую в API YooKassa для безопасности
        payment_info = await fetch_payment_status(payment_id)
        if not payment_info or payment_info.get("status") != "succeeded":
            return web.Response(status=200, text="Payment not succeeded yet")

        bot_instance = request.config_dict.get("bot")
        session_factory = request.config_dict.get("db_session_factory")

        if not session_factory:
            # На случай, если ключ всё равно не найден, выбросим понятную ошибку для логов
            raise RuntimeError("Не удалось найти 'db_session_factory' в конфигурации aiohttp!")

        async with session_factory() as session:
            if internal_order_id:
                order_query = select(Order).where(Order.id == int(internal_order_id))
            else:
                # Фолбэк на случай, если метаданные не пришли
                order_query = select(Order).where(Order.payment_id == payment_id)
                
            order_result = await session.execute(order_query)
            order = order_result.scalar_one_or_none()

            if not order:
                logger.error(f"Заказ (Внутренний ID: {internal_order_id}, ЮKassa ID: {payment_id}) не найден в БД!")
                return web.Response(status=404, text="Order not found")

            # Если заказ нашли, и у него еще не был сохранен payment_id от ЮКассы, запишем его для истории
            if not order.payment_id:
                order.payment_id = payment_id

            # ИДЕМПОТЕНТНОСТЬ: Если заказ уже был успешно обработан ранее, просто завершаем запрос
            if order.status == "succeeded":
                return web.Response(status=200, text="Already processed")

            # 2. Обновляем статус заказа
            order.status = "succeeded"

            # 3. Находим покупателя
            user_query = select(User).where(User.telegram_id == order.telegram_id)
            user_result = await session.execute(user_query)
            buyer = user_result.scalar_one_or_none()

            if buyer:
                # Списываем бонусы у покупателя, если они использовались
                if order.bonuses_spent > 0:
                    buyer.bonus_balance = max(0, buyer.bonus_balance - order.bonuses_spent)

                # Начисляем 20% пригласителю (рефереру) от РЕАЛЬНО оплаченной суммы
                if buyer.referrer_id:
                    referrer_id = buyer.referrer_id
                    try:
                        actual_amount = float(order.amount_value)
                        bonus_amount = round(actual_amount * 0.30, 2)
                    except (TypeError, ValueError) as e:
                        logger.error(f"Ошибка при конвертации суммы заказа {order.payment_id}: {e}")
                        bonus_amount = 0.0

                    # Находим реферера в БД
                    ref_query = select(User).where(User.telegram_id == referrer_id)
                    ref_result = await session.execute(ref_query)
                    referrer = ref_result.scalar_one_or_none()

                    if referrer:
                        referrer.bonus_balance += bonus_amount
                        
                        # Отправляем уведомление рефереру
                        try:
                            await bot_instance.send_message(
                                chat_id=referrer_id,
                                text=(
                                    f"🎉 **Новое реферальное начисление!**\n\n"
                                    f"Ваш реферал совершил покупку.\n"
                                    f"Вам начислено **30%** от суммы платежа: `+{bonus_amount} руб.`\n"
                                    f"Текущий баланс: `{referrer.bonus_balance} руб.`"
                                ),
                                parse_mode="Markdown"
                            )
                        except Exception as e:
                            logger.error(f"Не удалось отправить уведомление рефереру {referrer_id}: {e}")

            # Сохраняем все изменения в базе данных перед выдачей VPN
            await session.commit()

        # 4. Запускаем фоновую задачу выдачи VPN подписки
        try:
            # Создаем новую чистую сессию для асинхронного процесса доставки, 
            # чтобы избежать конфликтов с закрывающейся сессией вебхука.
            async def run_delivery():
                async with session_maker() as delivery_session:
                    await process_vpn_delivery(
                        session=delivery_session,
                        bot=bot_instance,
                        payment_id=payment_id
                    )

            asyncio.create_task(run_delivery())
            return web.Response(status=200)

        except Exception as e:
            logger.exception(f"Не удалось запустить доставку VPN для платежа {payment_id}: {e}")
            return web.Response(status=500)

    except Exception as e:
        logger.error(f"Ошибка при обработке вебхука ЮKassa: {e}", exc_info=True)
        return web.Response(status=400)