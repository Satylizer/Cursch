from typing import List
from xml.dom.minidom import Document
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from telegram import InlineKeyboardMarkup

def admin_menu_kb():
    builder = ReplyKeyboardBuilder()
    builder.button(text="📂 Документы")
    builder.button(text="👥 Сотрудники")
    builder.button(text="🔙 Выйти")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def documents_menu_kb():
    builder = ReplyKeyboardBuilder()
    builder.button(text="📄 Список")
    builder.button(text="➕ Добавить")
    builder.button(text="🗑 Удалить")
    builder.button(text="🔙 Назад")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def employees_menu_kb():
    builder = ReplyKeyboardBuilder()
    builder.button(text="👤 Список")
    builder.button(text="➕ Добавить")
    builder.button(text="🗑 Удалить") 
    builder.button(text="🔙 Назад")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def cancel_kb():
    builder = ReplyKeyboardBuilder()
    builder.button(text="❌ Отмена")
    return builder.as_markup(resize_keyboard=True)

def back_kb():
    builder = ReplyKeyboardBuilder()
    builder.button(text="🔙 Назад")
    return builder.as_markup(resize_keyboard=True)


def documents_list_kb(documents: List[Document]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for doc in documents:
        builder.button(
            text=f"📄 {doc.name}", # type: ignore
            callback_data=f"view_doc:{doc.id}" # type: ignore
        )
    builder.adjust(1)
    return builder.as_markup() # type: ignore