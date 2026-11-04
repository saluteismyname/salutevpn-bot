from payments import prices
from database.engine import session_maker
from database.models import User
from sqlalchemy import select

from payments.payments import create_payment

async def get_payment_data(telegram_id: int, days: int, vpn_type: str, is_for_friend: bool, friend_number: int | None):
   
    if is_for_friend == True or is_for_friend == "True":
        base_price = prices.SUBSCRIPTION_PRICES_FOR_FRIEND[f"{days}_days"]
    else:
        base_price = prices.SUBSCRIPTION_PRICES[f"{days}_days"]

    async with session_maker() as session:        

        user_query = select(User).where(User.telegram_id == telegram_id)
        user_result = await session.execute(user_query)
        user = user_result.scalar_one_or_none()

        bonus_balance = user.bonus_balance 


    if bonus_balance == 0:
    
        payment_without_bonuses = await create_payment(
            session=session,
            telegram_id=telegram_id,
            days=days,
            vpn_type=vpn_type,
            amount_value=base_price,
            bonuses_spent=0,
            friend_number=friend_number,
            is_for_friend=is_for_friend,
            remnawave_uuid=None,
            wg_id=None
        )

        payment_without_bonuses_url = payment_without_bonuses['confirmation']['confirmation_url']

        return {
            "payment_without_bonuses_url": payment_without_bonuses_url, 
            "bonuses_to_spend": 0,
            "bonuses_spendable_for_full": False,
            "payment_id": payment_without_bonuses["metadata"]["order_id"]
        }
        
    elif bonus_balance > 0 and bonus_balance < base_price:
        final_amount = base_price - int(bonus_balance) # сколько бонусов спишем (все доступные)

        payment_with_bonuses = await create_payment(
            session=session,
            telegram_id=telegram_id,
            days=days,
            vpn_type=vpn_type,
            amount_value=final_amount,
            bonuses_spent=bonus_balance,
            friend_number=friend_number,
            is_for_friend=is_for_friend,
            remnawave_uuid=None,
            wg_id=None
        )

        payment_without_bonuses = await create_payment(
            session=session,
            telegram_id=telegram_id,
            days=days,
            vpn_type=vpn_type,
            amount_value=base_price,
            bonuses_spent=0,
            friend_number=friend_number,
            is_for_friend=is_for_friend,
            remnawave_uuid=None,
            wg_id=None
        )
        
        payment_with_bonuses_url = payment_with_bonuses['confirmation']['confirmation_url']
        payment_without_bonuses_url = payment_without_bonuses['confirmation']['confirmation_url']

        return {
            "payment_with_bonuses_url": payment_with_bonuses_url,
            "payment_without_bonuses_url": payment_without_bonuses_url,
            "bonuses_to_spend": bonus_balance,
            "final_amount": final_amount,
            "base_price": base_price,
            "bonuses_spendable_for_full": False,
            "payment_id": payment_without_bonuses["metadata"]["order_id"]
        }

    elif bonus_balance > 0 and bonus_balance >= base_price:

        payment_without_bonuses = await create_payment(
            session=session,
            telegram_id=telegram_id,
            days=days,
            vpn_type=vpn_type,
            amount_value=base_price,
            bonuses_spent=0,
            friend_number=friend_number,
            is_for_friend=is_for_friend,
            remnawave_uuid=None,
            wg_id=None
        )

        payment_without_bonuses_url = payment_without_bonuses['confirmation']['confirmation_url']

        return {
            "payment_without_bonuses_url": payment_without_bonuses_url,
            "bonuses_to_spend": 0,
            "base_price": base_price,
            "bonuses_spendable_for_full": True,
            "payment_id": payment_without_bonuses["metadata"]["order_id"]
        }