import asyncio
from asyncio.log import logger
import ipaddress
import aiohttp
from config import config
from aiohttp import web
from services.delivery import process_vpn_delivery
from sqlalchemy.ext.asyncio import AsyncSession
from database.engine import session_maker
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
    # Проверка на пренадлежность IP ЮКассе функцией is_yookassa_ip
    if not is_yookassa_ip(client_ip):
        logger.warning(f"Блокировка запроса к вебхуку ЮKassa с левого IP: {client_ip}")
        return web.Response(status=403, text="Forbidden")

    try:
        # Превращаем объект запроса в json
        data = await request.json()
        # Парсим json
        payment_obj = data.get("object", {})
        metadata = payment_obj.get("metadata", {})
        payment_id = payment_obj.get("id")
        telegram_id = metadata.get("telegram_id")
        value = payment_obj.get("amount", {}).get("value")
        vpn_type = metadata.get("vpn_type")
        months = metadata.get("months")

        if not payment_id or not telegram_id:
            return web.Response(status=400, text="Missing ID")
        # Проверяем что платёж прошёл успешно        
        payment_info = await fetch_payment_status(payment_id)
        # Читаемый вывод json
        #pretty_json = json.dumps(data, indent=4, ensure_ascii=False)
        # Проверяем что платёж прошёл успешно
        if payment_info and payment_info.get("status") == "succeeded":
            bot_instance = request.app["bot"]

            try:
                async with session_maker() as session:
                    success = asyncio.create_task(process_vpn_delivery(
                        session=session,
                        bot = bot_instance,
                        payment_id = payment_id,
                    ))

                    return web.Response(status=200)

                if not success:
                    logger.warning(f"Провал выдачи VPN для {payment_id}, просим ЮКассу повторить.")
                    return web.Response(status=500)
            except Exception as e:
                logger.exception("Не удалось запустить выдачу подписки.")
                
        return web.Response(status=200)
    except Exception as e:
        logger.error(f"Ошибка при обработке вебхука ЮKassa: {e}")
        return web.Response(status=400)