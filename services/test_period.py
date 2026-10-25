from datetime import datetime, timedelta, timezone

async def registration_new_user(session, user_id, username):
    # Проверяем, есть ли уже такой пользователь в базе
    user = await session.get(User, user_id)
    
    if not user:
        # Пользователь новый! Вычисляем 3 дня триала
        trial_expires_at = datetime.now(timezone.utc) + timedelta(days=3)
        
        # Создаем пользователя в локальной БД
        user = User(
            telegram_id=user_id,
            username=username,
            is_active_vpn=True,
            expires_at_vless=trial_expires_at,  # Сохраняем дату окончания триала
            # ... остальные поля ...
        )
        session.add(user)
        await session.commit()
        
        return user, True  # True означает, что это новый юзер и ему дали триал
        
    return user, False # Пользователь уже существовал