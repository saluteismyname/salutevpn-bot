from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Update
from sqlalchemy import select, insert, update

from database.engine import session_maker
from database.models import User

class ShadowRegistrationMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        telegram_user = data.get("event_from_user")

        # Открываем единую сессию для всего запроса
        async with session_maker() as session:
            # Кладем сессию в data, чтобы хэндлеры могли принимать аргумент `session: AsyncSession`
            data["session"] = session

            if telegram_user and not telegram_user.is_bot:
                user_id = telegram_user.id
                current_username = telegram_user.username

                query = select(
                    User.telegram_id,
                    User.username,
                    User.is_active_vpn
                ).where(User.telegram_id == user_id)
                
                result = await session.execute(query)
                user_row = result.mappings().first()

                if user_row is None:
                    stmt = insert(User).values(
                        telegram_id = user_id,
                        username = current_username,
                        is_active_vpn = False
                    )
                    await session.execute(stmt)
                    await session.commit()

                    user_data = {
                        "telegram_id": user_id,
                        "username": current_username,
                        "is_active_vpn": False
                    }

                    print(f"Лог [Middleware]: Пользователь {user_id} автоматически зарегистрирован в базе данных.")
                else:
                    db_username = user_row["username"]
                    if db_username != current_username:
                        upd_stmt = update(User).where(User.telegram_id == user_id).values(
                            username = current_username
                        )
                        await session.execute(upd_stmt)
                        await session.commit()
                        print(f"Лог [Middleware]: Юзернейм пользователя {user_id} обновлен на {current_username}")
                    
                    user_data = dict(user_row)
                    user_data["username"] = current_username

                data["db_user"] = user_data

            # Передаем обработку хэндлеру внутри контекста активной сессии
            return await handler(event, data)