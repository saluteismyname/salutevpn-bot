import uuid
from config import config
from yookassa import Payment
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Order

async def create_payment(session: AsyncSession, telegram_id: int, months: int, vpn_type: str, amount_value: int):

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
        "description": "Оплата заказа №1",
        "metadata" : {
            "telegram_id": str(f"{telegram_id}"),
            "vpn_type": str(f"{vpn_type}"),
            "months": str(f"{months}")
        }
    }, uuid.uuid4())

    new_order = Order(
        telegram_id=telegram_id,
        payment_id=payment.id,
        vpn_type=vpn_type,
        months=months,
        amount_value=amount_value,
        status="pending"
    )
    session.add(new_order)
    await session.commit()

    return payment