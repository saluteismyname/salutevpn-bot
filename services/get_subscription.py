from sqlalchemy import select
from database.engine import session_maker
from database.models import Order, User
from sqlalchemy.ext.asyncio import AsyncSession

async def get_subscription(order_id: int, session: AsyncSession):
    async with session_maker() as session:
            
        result = await session.execute(
            select(Order, User)
            .join(User, Order.telegram_id == User.telegram_id)
            .order_by(Order.vpn_type, Order.created_at.desc())  # 1. Сначала сортируем по протоколу и дате (от новых к старым)
            .distinct(Order.vpn_type)
            .where(Order.id == order_id)
        )

        order = result.first()

        return order