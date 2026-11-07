from asyncio.log import logger
import json

from dotenv import load_dotenv
import httpx
from config import config

from rich import print as rprint

load_dotenv()

remnawave_token = config.remnawave_token.get_secret_value()
remnawave_url = config.remnawave_url

async def get_devices_remnawave(uuid: int | None) -> object:
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

async def delete_devices_remnawave(device_id: int, uuid: str):
    try:
        devices = await get_devices_remnawave(uuid=uuid)
        hwid = devices['response']['devices'][int(device_id) - 1]['hwid']
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{remnawave_url}/api/hwid/devices/delete",
                headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {remnawave_token}"
                },
                json={
                "userUuid": uuid,
                "hwid": hwid
                }   
            )
        if response.status_code >= 400:
            logger.error(f"Remnawave API вернул ошибку {response.status_code}!")
            logger.error(f"Ответ сервера (Body): {response.text}")
        
            return response.json()
    except Exception as e:
        logger.error(f"Ошибка удаления устройств: {e}")