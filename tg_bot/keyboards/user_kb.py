from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup
from typing import List

def main_menu_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="📌 Онбординг")
    builder.button(text="🏖 Оформить отпуск")
    builder.button(text="❓ Задать вопрос")
    builder.button(text="📄 Документы")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def question_type_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="🤖 LLM (общие вопросы)")
    builder.button(text="📚 RAG (по документам)")
    builder.button(text="❌ Отмена")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def roles_kb(roles: List[str]) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    
    for role in roles:
        builder.button(text=role.capitalize())
    
    builder.button(text="❌ Отмена")
    
    builder.adjust(1)
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True
    )

def vacation_type_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="Оплачиваемый")
    builder.button(text="Неоплачиваемый")
    builder.button(text="❌ Отмена")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def user_documents_menu_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="📋 Список документов")
    builder.button(text="🔍 Поиск по названию") 
    builder.button(text="◀️ Вернуться")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def document_view_kb(doc_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🔙 Назад к списку",
        callback_data="back_to_docs"
    )
    builder.adjust(1)
    return builder.as_markup()

def cancel_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="❌ Отмена")
    return builder.as_markup(resize_keyboard=True)

def user_back_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="◀️ Вернуться")
    return builder.as_markup(resize_keyboard=True)

