from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Каталог')],
        [KeyboardButton(text='Баланс'), KeyboardButton(text='Мої замовлення')],
        [KeyboardButton(text='Поповнити баланс')],
        [KeyboardButton(text='Web App', web_app=WebAppInfo(url='https://example.com'))],  # Замінити на реальний URL
    ],
    resize_keyboard=True,
    input_field_placeholder='Оберіть дію...'
)

def topup_amounts_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Поповнити 50$', callback_data='pay_50')],
        [InlineKeyboardButton(text='Поповнити 100$', callback_data='pay_100')],
        [InlineKeyboardButton(text='Поповнити 200$', callback_data='pay_200')],
        [InlineKeyboardButton(text='Поповнити 500$', callback_data='pay_500')],
    ])
    return kb

def simulate_payment_button(payload: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='✅ Імітувати оплату', callback_data=f"simulate_{payload}")],
        [InlineKeyboardButton(text='❌ Скасувати', callback_data='payment_cancel')]
    ])

def catalog_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='📋 Всі системи', callback_data='catalog_all')],
        [InlineKeyboardButton(text='🔍 Підбір за параметрами', callback_data='catalog_search')],
    ])

def systems_list_kb(systems):
    builder = InlineKeyboardBuilder()
    for system in systems:
        builder.add(InlineKeyboardButton(
            text=f"{system.name} - {system.price}$",
            callback_data=f"system_{system.id}"
        ))
    builder.adjust(1)
    return builder.as_markup()

def system_detail_kb(system_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🛒 Замовити', callback_data=f"order_{system_id}")],
        [InlineKeyboardButton(text='◀️ Назад до каталогу', callback_data='catalog_all')],
    ])

def order_confirmation_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='✅ Підтвердити', callback_data='confirm_order')],
        [InlineKeyboardButton(text='❌ Скасувати', callback_data='cancel_order')],
    ])
