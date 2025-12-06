from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup


def build_main_menu() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Баланс")
    kb.button(text="Оплата по QR")
    kb.button(text="Правила бота")
    kb.button(text="Правила школы")
    kb.button(text="Кибероны")
    kb.button(text="Финансы")
    kb.button(text="Написать директору")
    kb.adjust(3, 3, 1)
    return kb.as_markup(resize_keyboard=True)
