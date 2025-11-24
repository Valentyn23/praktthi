import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram import Router

from .keyboards import main, topup_amounts_kb, simulate_payment_button
from .database.requests import get_or_create_user, get_user_by_tg
from .payment import process_simulated_payment

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await get_or_create_user(message.from_user.id, message.from_user.full_name)
    await message.answer("Вітаю! Я — помічник з підбору систем відеоспостереження.\nОберіть дію:", reply_markup=main)

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("/start — Початок\n/register — Реєстрація\n/balance — Показати баланс\n/topup — Поповнити баланс (імітація)\n/info — Інформація про бот")

@router.message(Command("register"))
async def cmd_register(message: Message):
    user = await get_or_create_user(message.from_user.id, message.from_user.full_name)
    await message.answer(f"Ви зареєстровані: {user.name} (tg_id={user.tg_id}). Баланс: {user.balance}$")

@router.message(Command("balance"))
async def cmd_balance(message: Message):
    user = await get_user_by_tg(message.from_user.id)
    if not user:
        await message.answer("Ви не зареєстровані. Виконайте /register")
        return
    await message.answer(f"Ваш баланс: {user.balance}$")

@router.message(F.text == 'Баланс')
async def kb_balance(message: Message):
    await cmd_balance(message)

@router.message(F.text == 'Поповнити баланс')
async def kb_topup(message: Message):
    await message.answer("Оберіть суму для поповнення:", reply_markup=topup_amounts_kb())

@router.callback_query(F.data.startswith('pay_'))
async def on_select_amount(callback: CallbackQuery):
    amount_str = callback.data.split('_')[1]
    amount = float(amount_str)
    payload = f"{callback.from_user.id}_{int(amount)}"
    await callback.message.answer(f"Ви обрали поповнення {amount}$.\nНатисніть нижче, щоб імітувати оплату.", reply_markup=simulate_payment_button(payload))
    await callback.answer()

@router.callback_query(F.data.startswith('simulate_'))
async def on_simulate_payment(callback: CallbackQuery):
    payload = callback.data.split('_', 1)[1]
    # payload format: "{tgid}_{amount}"
    try:
        tgid_str, amount_str = payload.split('_')
        amount = float(amount_str)
    except Exception:
        await callback.message.answer("Невірний payload платежу.")
        await callback.answer()
        return
    # process simulated payment for the *caller*
    user = await process_simulated_payment(callback.from_user.id, amount)
    if user:
        await callback.message.answer(f"Оплата успішна! Поповнено {amount}$. Новий баланс: {user.balance}$")
    else:
        await callback.message.answer("Користувача не знайдено. Зробіть /register")
    await callback.answer()

@router.callback_query(F.data == 'payment_cancel')
async def on_payment_cancel(callback: CallbackQuery):
    await callback.message.answer("Платіж скасовано.")
    await callback.answer()

@router.message(Command("info"))
async def cmd_info(message: Message):
    text = ("Бот допомагає обрати систему відеоспостереження за базовими параметрами.\n"
            "Це практична робота — оплата імітована.\n"
            "Команди: /register /balance /topup /info")
    await message.answer(text)
