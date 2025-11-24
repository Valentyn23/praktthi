import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from .keyboards import (
    main, topup_amounts_kb, simulate_payment_button,
    catalog_kb, system_detail_kb, order_confirmation_kb
)
from .database.requests import (
    get_or_create_user, get_user_by_tg, get_all_systems,
    get_systems_by_params, get_system_by_id, create_order,
    get_user_orders, update_user_phone, update_balance
)
from .payment import process_simulated_payment

router = Router()

class CatalogSearch(StatesGroup):
    cameras = State()
    area = State()
    budget = State()

class OrderProcess(StatesGroup):
    phone = State()
    confirm = State()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await get_or_create_user(message.from_user.id, message.from_user.full_name)
    await message.answer("Вітаю! Я — помічник з підбору систем відеоспостереження.\nОберіть дію:", reply_markup=main)

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("/start — Початок\n/register — Реєстрація\n/balance — Показати баланс\n/topup — Поповнити баланс (імітація)\n/catalog — Каталог систем\n/orders — Історія замовлень\n/info — Інформація про бот")

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
    try:
        tgid_str, amount_str = payload.split('_')
        amount = float(amount_str)
    except Exception:
        await callback.message.answer("Невірний payload платежу.")
        await callback.answer()
        return
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
            "Команди: /register /balance /topup /catalog /orders /info")
    await message.answer(text)

# Каталог та пошук
@router.message(F.text == 'Каталог')
async def kb_catalog(message: Message, state: FSMContext):
    await message.answer("Оберіть спосіб перегляду:", reply_markup=catalog_kb())

@router.message(Command("catalog"))
async def cmd_catalog(message: Message):
    await message.answer("Оберіть спосіб перегляду:", reply_markup=catalog_kb())

@router.callback_query(F.data == 'catalog_all')
async def show_all_systems(callback: CallbackQuery):
    systems = await get_all_systems()
    if not systems:
        await callback.message.answer("Каталог поки порожній.")
        await callback.answer()
        return
    
    text = "📹 Доступні системи відеоспостереження:\n\n"
    for sys in systems:
        text += f"🔹 {sys.name}\n"
        text += f"   💰 Ціна: {sys.price}$\n"
        text += f"   📷 Камер: {sys.cameras_count}\n"
        text += f"   📐 Площа: {sys.coverage_area}м²\n\n"
    
    from .keyboards import systems_list_kb
    await callback.message.answer(text, reply_markup=systems_list_kb(systems))
    await callback.answer()

@router.callback_query(F.data == 'catalog_search')
async def start_search(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CatalogSearch.cameras)
    await callback.message.answer("🔍 Підбір системи за параметрами\n\nСкільки камер вам потрібно? (введіть число)")
    await callback.answer()

@router.message(CatalogSearch.cameras)
async def process_cameras(message: Message, state: FSMContext):
    try:
        cameras = int(message.text)
        if cameras < 1 or cameras > 50:
            await message.answer("Введіть коректне число камер (1-50)")
            return
        await state.update_data(cameras=cameras)
        await state.set_state(CatalogSearch.area)
        await message.answer("Яка площа потребує покриття? (введіть площу в м²)")
    except ValueError:
        await message.answer("Будь ласка, введіть число")

@router.message(CatalogSearch.area)
async def process_area(message: Message, state: FSMContext):
    try:
        area = int(message.text)
        if area < 1 or area > 10000:
            await message.answer("Введіть коректну площу (1-10000 м²)")
            return
        await state.update_data(area=area)
        await state.set_state(CatalogSearch.budget)
        await message.answer("Який ваш максимальний бюджет? (введіть суму в $)")
    except ValueError:
        await message.answer("Будь ласка, введіть число")

@router.message(CatalogSearch.budget)
async def process_budget(message: Message, state: FSMContext):
    try:
        budget = float(message.text)
        if budget < 0:
            await message.answer("Бюджет не може бути від'ємним")
            return
        
        data = await state.get_data()
        cameras = data['cameras']
        area = data['area']
        
        systems = await get_systems_by_params(cameras, area, budget)
        
        if not systems:
            await message.answer(
                f"На жаль, не знайдено систем за вашими параметрами:\n"
                f"📷 Камер: від {cameras}\n"
                f"📐 Площа: від {area}м²\n"
                f"💰 Бюджет: до {budget}$\n\n"
                f"Спробуйте змінити параметри пошуку."
            )
        else:
            text = f"✅ Знайдено {len(systems)} систем за вашими параметрами:\n\n"
            for sys in systems:
                text += f"🔹 {sys.name}\n"
                text += f"   💰 Ціна: {sys.price}$\n"
                text += f"   📷 Камер: {sys.cameras_count}\n"
                text += f"   📐 Площа: {sys.coverage_area}м²\n\n"
            
            from .keyboards import systems_list_kb
            await message.answer(text, reply_markup=systems_list_kb(systems))
        
        await state.clear()
    except ValueError:
        await message.answer("Будь ласка, введіть коректну суму")

@router.callback_query(F.data.startswith('system_'))
async def show_system_detail(callback: CallbackQuery):
    system_id = int(callback.data.split('_')[1])
    system = await get_system_by_id(system_id)
    
    if not system:
        await callback.answer("Систему не знайдено", show_alert=True)
        return
    
    text = f"📹 {system.name}\n\n"
    text += f"📝 {system.description}\n\n"
    text += f"💰 Ціна: {system.price}$\n"
    text += f"📷 Кількість камер: {system.cameras_count}\n"
    text += f"📐 Площа покриття: {system.coverage_area}м²\n"
    if system.features:
        text += f"\n✨ Особливості:\n{system.features}\n"
    
    await callback.message.answer(text, reply_markup=system_detail_kb(system_id))
    await callback.answer()

@router.callback_query(F.data.startswith('order_'))
async def start_order(callback: CallbackQuery, state: FSMContext):
    system_id = int(callback.data.split('_')[1])
    system = await get_system_by_id(system_id)
    user = await get_user_by_tg(callback.from_user.id)
    
    if not system:
        await callback.answer("Систему не знайдено", show_alert=True)
        return
    
    if not user:
        await callback.message.answer("Спочатку зареєструйтесь командою /register")
        await callback.answer()
        return
    
    if user.balance < system.price:
        await callback.message.answer(
            f"❌ Недостатньо коштів!\n\n"
            f"Ціна системи: {system.price}$\n"
            f"Ваш баланс: {user.balance}$\n"
            f"Не вистачає: {system.price - user.balance}$\n\n"
            f"Поповніть баланс командою /topup або натисніть кнопку 'Поповнити баланс'"
        )
        await callback.answer()
        return
    
    await state.update_data(system_id=system_id, system_price=system.price)
    
    if user.phone:
        await state.set_state(OrderProcess.confirm)
        await callback.message.answer(
            f"📦 Оформлення замовлення\n\n"
            f"Система: {system.name}\n"
            f"Ціна: {system.price}$\n"
            f"Телефон: {user.phone}\n\n"
            f"Підтвердити замовлення?",
            reply_markup=order_confirmation_kb()
        )
    else:
        await state.set_state(OrderProcess.phone)
        await callback.message.answer(
            f"📦 Оформлення замовлення\n\n"
            f"Система: {system.name}\n"
            f"Ціна: {system.price}$\n\n"
            f"Будь ласка, введіть ваш номер телефону для зв'язку:"
        )
    
    await callback.answer()

@router.message(OrderProcess.phone)
async def process_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    
    if len(phone) < 10:
        await message.answer("Введіть коректний номер телефону (мінімум 10 цифр)")
        return
    
    await update_user_phone(message.from_user.id, phone)
    await state.update_data(phone=phone)
    await state.set_state(OrderProcess.confirm)
    
    data = await state.get_data()
    system = await get_system_by_id(data['system_id'])
    
    await message.answer(
        f"📦 Оформлення замовлення\n\n"
        f"Система: {system.name}\n"
        f"Ціна: {system.price}$\n"
        f"Телефон: {phone}\n\n"
        f"Підтвердити замовлення?",
        reply_markup=order_confirmation_kb()
    )

@router.callback_query(F.data == 'confirm_order')
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    system_id = data['system_id']
    system_price = data['system_price']
    
    user = await get_user_by_tg(callback.from_user.id)
    system = await get_system_by_id(system_id)
    
    if user.balance < system_price:
        await callback.message.answer("❌ Недостатньо коштів! Поповніть баланс.")
        await callback.answer()
        await state.clear()
        return
    
    # Створюємо замовлення
    order = await create_order(user.tg_id, system_id, user.phone, system_price)
    
    # Списуємо кошти
    new_balance = user.balance - system_price
    await update_balance(user.tg_id, new_balance)
    
    await callback.message.answer(
        f"✅ Замовлення успішно оформлено!\n\n"
        f"Номер замовлення: #{order.id}\n"
        f"Система: {system.name}\n"
        f"Сума: {system_price}$\n"
        f"Новий баланс: {new_balance}$\n\n"
        f"З вами зв'яжуться за номером: {user.phone}\n\n"
        f"Дякуємо за покупку! 🎉"
    )
    
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == 'cancel_order')
async def cancel_order(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Замовлення скасовано.")
    await state.clear()
    await callback.answer()

# Історія замовлень
@router.message(F.text == 'Мої замовлення')
async def kb_orders(message: Message):
    await show_orders(message)

@router.message(Command("orders"))
async def cmd_orders(message: Message):
    await show_orders(message)

async def show_orders(message: Message):
    orders = await get_user_orders(message.from_user.id)
    
    if not orders:
        await message.answer("У вас поки немає замовлень.")
        return
    
    text = "📋 Ваші замовлення:\n\n"
    for order in orders:
        system = await get_system_by_id(order.system_id)
        text += f"🔹 Замовлення #{order.id}\n"
        text += f"   Система: {system.name if system else 'Невідома'}\n"
        text += f"   Сума: {order.total_price}$\n"
        text += f"   Статус: {order.status}\n"
        text += f"   Дата: {order.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
    
    await message.answer(text)
