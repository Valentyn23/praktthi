from app.database.requests import get_user_by_tg, update_balance

async def process_simulated_payment(tg_id: int, amount: float):
    user = await get_user_by_tg(tg_id)
    if not user:
        return None
    new_balance = (user.balance or 0) + amount
    user = await update_balance(tg_id, new_balance)
    return user
