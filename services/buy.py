from sqlalchemy import desc, select

from database.engine import session_maker
from database.models import Order, User

async def buy_days(telegram_id: int):
    async with session_maker() as session:

        result = await session.execute(
            select(User)
            .where(User.telegram_id == telegram_id)
        )

        user_check = result.scalar_one_or_none()

        result_not_first = await session.execute(
            select(Order)
            .where(Order.telegram_id == telegram_id) #, Order.vpn_type == vpn_type
            .order_by(
                desc(Order.id)
            )
            .limit(1)
        )
    
        order = result_not_first.scalar_one_or_none()

        return {
            "user_check": user_check,
            "order": order
        }