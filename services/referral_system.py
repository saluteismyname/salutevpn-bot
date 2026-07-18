import asyncio
import base64
import time
from aiogram.filters import CommandObject
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Order, User
from database.engine import session_maker
from services.delivery import process_vpn_delivery

async def referral_system_registration(user_id: int, message: Message, command: CommandObject, session: AsyncSession):
    # 1. Проверяем реферальный аргумент
    if command.args:
        try:
            # ИСПРАВЛЕНО: Декодируем строку из Base64 обратно в обычный текст
            # К тексту добавляем "==", чтобы избежать ошибок заполнения (padding) в Base64
            padded_args = command.args + "=="
            decoded_bytes = base64.urlsafe_b64decode(padded_args.encode('utf-8'))
            decoded_str = decoded_bytes.decode('utf-8')
            
            potential_referrer = int(decoded_str)

            if potential_referrer != user_id:
                referrer_id = potential_referrer
        except (ValueError, Exception):
            # Если это была не Base64 строка или не число, просто игнорируем
            pass

    query = select(User).where(User.telegram_id == user_id)
    result = await session.execute(query)
    current_user = result.scalar_one_or_none()

    # 3. Если пользователя вообще нет в БД (Middleware его не создал)
    if not current_user:
        new_user = User(telegram_id=user_id, referrer_id=referrer_id)
        session.add(new_user)
        
        if referrer_id:
                try:
                    await message.bot.send_message(
                        chat_id=referrer_id,
                        text=f"🎉 По вашей ссылке зарегистрировался новый пользователь!"
                    )

                except Exception:
                    pass
            
        await session.commit()
    # 4. ИСПРАВЛЕНО: Если пользователь есть (создан Middleware), но у него нет реферера
    else:
        if referrer_id and current_user.referrer_id is None:
            current_user.referrer_id = referrer_id  # Дописываем реферера!
            try:
                await message.bot.send_message(
                        chat_id=referrer_id,
                        text=f"🎉 По вашей ссылке зарегистрировался новый пользователь!"
                    )

            except Exception:
                pass

        await session.commit()

async def referral_system_payment(telegram_id: int, price: int, callback: CallbackQuery, days: int, vpn_type: str):
    async with session_maker() as session:
        user_query = select(User).where(User.telegram_id == telegram_id)
        user_result = await session.execute(user_query)
        user = user_result.scalar_one()
        
        if user.bonus_balance >= price:
            # 1. Списываем бонусы
            user.bonus_balance -= price
            
            # 2. Создаем заказ со статусом сразу "succeeded" без YooKassa
            new_order = Order(
                telegram_id=telegram_id,
                payment_id=f"internal_bonus_{telegram_id}_{int(time.time())}",
                vpn_type=vpn_type,
                days=days,
                amount_value=0, # Рублей картой списано ноль
                bonuses_spent=price,
                status="succeeded"
            )
            session.add(new_order)
            
            await session.flush()
            await callback.message.edit_text(f"🎉 Подписка успешно оплачена бонусами и активирована на {days} дней!")
            
            async def run_delivery():
                async with session_maker() as delivery_session:
                    await process_vpn_delivery(
                        session=delivery_session,
                        bot=callback.bot,
                        payment_id=new_order.payment_id
                    )

            await session.commit()
            asyncio.create_task(run_delivery())
            
        else:
            await callback.answer("Недостаточно бонусов для полной оплаты!", show_alert=True)