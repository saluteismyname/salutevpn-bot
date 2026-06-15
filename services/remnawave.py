import asyncio
from config import config
from dotenv import load_dotenv
import httpx
from random import randint
import datetime
# Подгружаем переменные из .env
load_dotenv()

remnawave_token = config.remnawave_token.get_secret_value()
# Обязательно пишем str(), так как API ожидает в json от нас str, а randint возвращает int

async def create_user_remnawave(expires_at: datetime, telegram_id: int):
    async with httpx.AsyncClient() as client:
        username = (f"{str(randint(123456789, 987654321))}_{telegram_id})")
        await client.post("https://test-site-for-development.site/api/users",
            headers={
                "Content-Type": "application/json",
                "Authorization": f'Bearer {remnawave_token}'
            },
            json={
                "username": username,
                "expireAt": expires_at,
                "telegramId": telegram_id,
                "status": "ACTIVE",
                "activeInternalSquads": [
                    "2f7d0688-bd6e-4048-9f47-93df38139dcb"
                ]
            }
        )

async def edit_user_remnawave(expires_at: datetime, telegram_id: int):
    async with httpx.AsyncClient() as client:
        await client.patch("https://test-site-for-development.site/api/users",
            headers={
            "Content-Type": "application/json",
            "Authorization": f'Bearer {remnawave_token}'
            },
            json={
                "telegram_id": telegram_id
            }
        )