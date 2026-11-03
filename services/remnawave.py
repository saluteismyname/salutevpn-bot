import asyncio
from asyncio.log import logger
from config import config
from dotenv import load_dotenv
import httpx
from random import randint
import datetime
import random
from rich import print as rprint
# Подгружаем переменные из .env
load_dotenv()

remnawave_token = config.remnawave_token.get_secret_value()
remnawave_url = config.remnawave_url
remnawave_internal_squad = config.remnawave_internal_squad

async def create_user_remnawave(expires_at: str, telegram_id: int, is_for_friend: bool, num_of_friends_vless: int) -> object:
    
    if config.testing == "True" and is_for_friend == False:
        rand_num = random.randint(123456789, 987654321)
        username = f"test_{rand_num}_{telegram_id}"
    elif config.testing == "True" and is_for_friend == True:
        username = f"test_user_{telegram_id}_for_friend_{num_of_friends_vless}"
    elif config.testing == "False" and is_for_friend == True:
        username = f"user_{telegram_id}_for_friend_{num_of_friends_vless}"
    else: 
        username = f"user_{telegram_id}"

    async with httpx.AsyncClient() as client:

        if is_for_friend == True:
            try:
                response = await client.post(f"{remnawave_url}/api/users",
                    
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f'Bearer {remnawave_token}'
                    },
                json={
                    "username": username,
                    "expireAt": expires_at,
                    "status": "ACTIVE",
                    "activeInternalSquads": [
                    f"{remnawave_internal_squad}"
                    ]
                    }
                )

                if response.status_code >= 400:
                    logger.error(f"Remnawave API вернул ошибку {response.status_code}!")
                    logger.error(f"Ответ сервера (Body): {response.text}")
                
                return response.json()
            
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTPStatusError: {e}")
            except Exception as e:
                logger.error(f"Общая ошибка при создании пользователя {e}")
        else:
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

                return response.json()
            
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTPStatusError: {e}")
            except Exception as e:
                logger.error(f"Общая ошибка при создании пользователя {e}")


async def edit_user_remnawave(remnawave_uuid: str, expires_at: datetime):
    async with httpx.AsyncClient() as client:
        await client.patch(f"{remnawave_url}/api/users",
            headers={
            "Content-Type": "application/json",
            "Authorization": f'Bearer {remnawave_token}'
            },
            json={
                "uuid": remnawave_uuid,
                "expireAt": str(expires_at)
            }
        )

async def get_user_remnawave(remnawave_uuid: str):
    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            response = await client.get(f"{remnawave_url}/api/users/{remnawave_uuid}",
                headers={
                "Authorization": f"Bearer {remnawave_token}"
                }
            )
            response.raise_for_status()
            vless_response = response.json()
            resp_data = vless_response['response']
            if not resp_data:
                logger.exception(f"Remnawave вернул странный JSON: {vless_response}")
                return  # или raise кустомное исключение
            
            return response.json()
        except httpx.ConnectTimeout as e:
            logger.exception(
                f"❌ Превышено время ожидания соединения с Remnawave API (ConnectTimeout){e}."
            )
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ Ошибка ответа Remnawave API: {e.response.status_code}")
            return None
        except Exception as e:
            logger.error(f"❌ Непредвиденная ошибка при запросе к Remnawave: {e}")
            return None 