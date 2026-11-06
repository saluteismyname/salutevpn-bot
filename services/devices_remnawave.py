from asyncio.log import logger
import json

from dotenv import load_dotenv
import httpx
from config import config

load_dotenv()

remnawave_token = config.remnawave_token.get_secret_value()
remnawave_url = config.remnawave_url

async def get_devices_remnawave(uuid: int) -> object:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{remnawave_url}/api/hwid/devices/{uuid}",
                headers={
                "Authorization": f"Bearer {remnawave_token}"
                }
            )
            return response.json()
    except Exception as e:
        logger.error(f"Ошибка получения устройств: {e}",)
        return False



async def delete_devices_remnawave(user_id: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{remnawave_url}/api/hwid/devices/delete",
                headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {remnawave_token}"
                },
                json={
                "userId": user_id,
                "hwid": ""
                }   
            )
            return response.json()
    except Exception as e:
        logger.error(f"Ошибка удаления устройств: {e}")

    