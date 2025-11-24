from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Каталог')],
        [KeyboardButton(text='Баланс')],
        [KeyboardButton(text='Поповнити баланс')],
        [KeyboardButton(text='Контакти'), KeyboardButton(text='Про нас')]
    ],
    resize_keyboard=True
)

def topup_amounts_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Поповнити 5$', callback_data='pay_5')],
        [InlineKeyboardButton(text='Поповнити 10$', callback_data='pay_10')],
        [InlineKeyboardButton(text='Поповнити 20$', callback_data='pay_20')],
    ])
    return kb

def simulate_payment_button(payload: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Імітувати оплату', callback_data=f"simulate_{payload}")],
        [InlineKeyboardButton(text='Скасувати', callback_data='payment_cancel')]
    ])
