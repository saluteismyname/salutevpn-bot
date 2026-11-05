from sqlalchemy import select
from database.engine import session_maker
from database.models import Order, User
from sqlalchemy.ext.asyncio import AsyncSession
from database.engine import session_maker
from aiogram.types import CallbackQuery, Message

async def get_subscription(order_id: int, session: AsyncSession):
            
    result = await session.execute(
        select(Order, User)
        .join(User, Order.telegram_id == User.telegram_id)
        .where(Order.id == order_id)
        .order_by(Order.id.asc(), Order.created_at.asc())
    )

    order = result.first()

    return order

async def get_subscription_for_friend(order_id: int, session: AsyncSession):
            
    result = await session.execute(
        select(Order)
        .where(Order.id == order_id)
    )

    order = result.scalar_one_or_none()

    return order

async def get_my_subscriptions(telegram_id: int):
    async with session_maker() as session:
        result_without_friends = await session.execute(
            select(Order, User)
            .join(User, Order.telegram_id == User.telegram_id).where(
                Order.telegram_id == telegram_id,
                Order.is_for_friend == False,
                Order.status == "paid"
            ).order_by(Order.vpn_type, Order.created_at.asc())  # 1. Сначала сортируем по протоколу и дате (от старым к новым)
            .distinct(Order.vpn_type)
        )
        orders_without_friends = result_without_friends.all()

        result_with_friends = await session.execute(
            select(Order, User)
            .join(User, Order.telegram_id == User.telegram_id).where(
                Order.telegram_id == telegram_id,
                Order.is_for_friend == True,
                Order.status == "paid"
            ).order_by(Order.created_at.asc(), Order.id.asc())
        )
        orders_with_friends = result_with_friends.all()

        return orders_without_friends, orders_with_friends

async def get_my_subscriptions_from(telegram_id: int):
    async with session_maker() as session:
        result_without_friends = await session.execute(
            select(Order, User)
            .join(User, Order.telegram_id == User.telegram_id).where(
                Order.telegram_id == telegram_id,
                Order.is_for_friend == False,
                Order.status == "paid"
            ).order_by(Order.vpn_type, Order.created_at.asc())  # 1. Сначала сортируем по протоколу и дате (от новых к старым)
            .distinct(Order.vpn_type)
        )
        orders_without_friends = result_without_friends.all()

        result_with_friends = await session.execute(
            select(Order, User)
            .join(User, Order.telegram_id == User.telegram_id).where(
                Order.telegram_id == telegram_id,
                Order.is_for_friend == True,
                Order.status == "paid"
            ).order_by(Order.id.asc(), Order.created_at.asc())
        )
        orders_with_friends = result_with_friends.all()

        return orders_without_friends, orders_with_friends