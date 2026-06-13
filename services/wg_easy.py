from datetime import datetime, timedelta, timezone
import json

import httpx
import asyncio

from dotenv import load_dotenv
from sqlalchemy import Select
from dateutil.relativedelta import relativedelta

from config import config
from database.engine import session_maker
from database.models import User
from sqlalchemy import select, insert, update

load_dotenv()

password = config.wg_easy_password.get_secret_value()

url = "https://wg01.test-site-for-development.ru:8443"

async def create_user_wg_easy(telegram_id: int, expires_at_fix: datetime, months_to_add: datetime, firstly: bool):
    async with httpx.AsyncClient(base_url=url) as client:
        # Авторизация
        login_response = await client.post(
            "/api/session",
            json={"password": password}
        )

        if login_response.status_code >= 400:
            print("Ошибка логина в WG Easy")
            return None
        
        if expires_at_fix:
            name = f"{expires_at_fix}_{telegram_id}"
        else:
            now_pre = datetime.now(timezone.utc).replace(tzinfo=None)
            expires_at_fix = now_pre + months_to_add
            expires_at_fix = expires_at_fix.strftime("%d.%m.%Y")
            name = f"{expires_at_fix}_{telegram_id}"

        if firstly:
            create_response = await client.post(
                "/api/wireguard/client",
                json={"name": name}
            )
 
        get_response = await client.get("/api/wireguard/client")

        clients = get_response.json()
        
        pointed_user = None

        if not firstly:
            for pointed_client in clients:
                if pointed_client['name'] == name:
                    pointed_user = pointed_client

        if pointed_user and expires_at_fix:
            expires_at_fix = datetime.strptime(expires_at_fix, "%d.%m.%Y")
            time_left = relativedelta(expires_at_fix, datetime.now())
            time_calculated = time_left + months_to_add
            time_plus_now = time_calculated + datetime.now()
            time = time_plus_now.strftime("%d.%m.%Y")
            put_response = await client.put(
                f"/api/wireguard/client/{pointed_user['id']}/name",
                json={"name": f"{time}_{telegram_id}"}
            )