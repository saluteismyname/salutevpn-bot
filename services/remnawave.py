import asyncio
from asyncio.log import logger
from config import config
from dotenv import load_dotenv
import httpx
from random import randint
import datetime
# Подгружаем переменные из .env
load_dotenv()

remnawave_token = config.remnawave_token.get_secret_value()
remnawave_url = config.remnawave_url
remnawave_internal_squad = config.remnawave_internal_squad
# Обязательно пишем str(), так как API ожидает в json от нас str, а randint возвращает int

async def create_user_remnawave(expires_at: datetime, telegram_id: int):
    username = (f"{str(randint(123456789, 987654321))}_{telegram_id}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{remnawave_url}/api/users",
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
                f"{remnawave_internal_squad}"
            ]
            }
        )

            if response.status_code >= 400:
                logger.error(f"Remnawave API вернул ошибку {response.status_code}!")
                logger.error(f"Ответ сервера (Body): {response.text}")
            
            response.raise_for_status()
            user_data = response.json()
        
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTPStatusError: {e}")
        except Exception as e:
            logger.exception("Общая ошибка при создании пользователя")

        return response.json()

async def edit_user_remnawave(remnawave_uuid: str, expires_at: datetime):
    async with httpx.AsyncClient() as client:
        await client.patch(f"{remnawave_url}/api/users",
            headers={
            "Content-Type": "application/json",
            "Authorization": f'Bearer {remnawave_token}'
            },
            json={
                "uuid": remnawave_uuid,
                "expireAt": expires_at.isoformat()
            }
        )

async def get_user_remnawave(remnawave_uuid: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{remnawave_url}/api/users/{remnawave_uuid}",
            headers={
            "Authorization": f"Bearer {remnawave_token}"
            }
        )

        response.raise_for_status()

        vless_response = response.json()

        resp_data = vless_response.get('response')
        if not resp_data:
            logger.error(f"Remnawave вернул странный JSON: {vless_response}")
            return  # или raise кустомное исключение

        return response.json()