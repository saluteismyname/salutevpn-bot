from asyncio.log import logger
import uuid
from config import config
from yookassa import Payment
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Order

async def create_payment(session: AsyncSession, telegram_id: int, days: int, vpn_type: str, amount_value: int, bonuses_spent: int, is_for_friend: bool, friend_number: int | None, remnawave_uuid: str, wg_id: str, wg_panel: str):

    new_order = Order(
        telegram_id=telegram_id,
        vpn_type=vpn_type,
        days=days,
        amount_value=amount_value,
        status="pending",
        bonuses_spent=bonuses_spent,
        is_for_friend=is_for_friend,
        friend_number=friend_number,
        remnawave_uuid=remnawave_uuid,
        wg_id=wg_id,
        wg_panel=wg_panel
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
            "order_id": str(f"{new_order.id}"),
            "is_for_friend": str(f"{is_for_friend}"),
            "remnawave_uuid": str(f"{remnawave_uuid}"),
            "wg_id": str(f"{wg_id}"),
            "friend_number": str(friend_number),
            "wg_panel": str(wg_panel)
        }
    }, uuid.uuid4())
    
    await session.commit()

    return payment