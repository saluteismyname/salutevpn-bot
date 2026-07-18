from asyncio.log import logger
import uuid
from config import config
from yookassa import Payment
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Order

async def create_payment(session: AsyncSession, telegram_id: int, days: int, vpn_type: str, amount_value: int, bonuses_spent: int):

    new_order = Order(
        telegram_id=telegram_id,
        vpn_type=vpn_type,
        days=days,
        amount_value=amount_value,
        status="pending",
        bonuses_spent=bonuses_spent
    )

    session.add(new_order)

    await session.flush()

    payment = Payment.create({
        "amount": {
            "value": int(f"{amount_value}"),
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/salutevpnbot"
        },
        "test": True,
        "capture": True,
        "description": f"Оплата заказа №{new_order.id}",
        "metadata" : {
            "telegram_id": str(f"{telegram_id}"),
            "vpn_type": str(f"{vpn_type}"),
            "days": str(f"{days}"),
            "order_id": str(f"{new_order.id}")
        }
    }, uuid.uuid4())
    
    await session.commit()

    return payment