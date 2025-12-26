from aiogram import F, Router, types
from aiogram.types import Message
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from datetime import datetime, date, timedelta
import asyncio
from keyboards.user_kb import *
from states.user_state import OnboardingState, VacationState, UserState
from services.service_manager import ServiceManager
from config.logging import logger
from typing import Tuple, Optional
from requests.llm_request import ask_llm
from requests.rag_request import ask_rag

def setup_user_handlers(router: Router, service_manager: ServiceManager):
    user_router = Router()
    router.include_router(user_router)
       
    @user_router.message(Command("start"))
    async def send_welcome(message: types.Message):
        """Приветственное сообщение с главным меню"""
        try:
            await message.answer(
                "👋 Добро пожаловать в HR-консультант!\n"
                "Для доступа к админ-панели используйте команду /admin\n\n"
                "Выберите нужный раздел:",
                reply_markup=main_menu_kb()
            )
        except Exception as e:
            logger.error(f"Error in send_welcome: {e}")
            await message.answer("Произошла ошибка при загрузке меню")

    @user_router.message(F.text == "❌ Отмена")
    async def user_cancel_handler(message: types.Message, state: FSMContext):
        try:
            current_state = await state.get_state()
            
            if current_state:
                if current_state.startswith("VacationState"):
                    await message.answer("Оформление отпуска отменено", reply_markup=main_menu_kb())
                elif current_state.startswith("OnboardingState"):
                    await message.answer("Процесс онбординга прерван", reply_markup=main_menu_kb())
                else:
                    await message.answer("Действие отменено", reply_markup=main_menu_kb())
                
                await state.clear()
            else:
                await message.answer("Главное меню:", reply_markup=main_menu_kb())
                
        except Exception as e:
            logger.error(f"Ошибка в user_cancel_handler: {e}")
            await message.answer("Произошла ошибка при отмене действия", reply_markup=main_menu_kb())

    @user_router.message(F.text == "❓ Задать вопрос")
    async def ask_question(message: types.Message, state: FSMContext):
        try:
            await message.answer(
                "Выберите тип вопроса:",
                reply_markup=question_type_kb()
            )
            await state.set_state(UserState.waiting_for_question_type)
        except Exception as e:
            logger.error(f"Error in ask_question: {e}")
            await message.answer("Произошла ошибка", reply_markup=main_menu_kb())
            
    @user_router.message(UserState.waiting_for_question_type)
    async def handle_question_type(message: types.Message, state: FSMContext):
        try:
            if not message.text or message.text == "❌ Отмена":
                await state.clear()
                await message.answer("Действие отменено", reply_markup=main_menu_kb())
                return
                
            if message.text not in ["🤖 LLM (общие вопросы)", "📚 RAG (по документам)"]:
                await message.answer("Пожалуйста, выберите тип вопроса из меню:")
                return
                
            await state.update_data(question_type="llm" if "LLM" in message.text else "rag")
            
            await message.answer(
                "Введите ваш вопрос:",
                reply_markup=cancel_kb()
            )
            await state.set_state(UserState.waiting_for_question)
            
        except Exception as e:
            logger.error(f"Error in handle_question_type: {e}")
            await state.clear()
            await message.answer("Ошибка", reply_markup=main_menu_kb())
    
    @user_router.message(UserState.waiting_for_question)
    async def handle_question(message: types.Message, state: FSMContext):
        try:
            if not message.text or message.text == "❌ Отмена":
                await state.clear()
                await message.answer("Вопрос отменён", reply_markup=main_menu_kb())
                return
                
            # Получаем сохранённый тип вопроса
            data = await state.get_data()
            question_type = data.get("question_type", "llm")
            
            # Обработка в зависимости от типа
            if question_type == "llm":
                answer = await ask_llm(message.text.strip())
            else:
                answer = await ask_rag(message.text.strip(), service_manager)
                
            await message.answer(answer, reply_markup=main_menu_kb())
            
        except Exception as e:
            logger.error(f"Error in handle_question: {e}")
            await message.answer("Ошибка обработки", reply_markup=main_menu_kb())
        finally:
            await state.clear()

    @user_router.message(F.text == "◀️ Вернуться")
    async def back_handler(message: types.Message, state: FSMContext):
        current_state = await state.get_state()
        
        if current_state == UserState.user_documents_menu:
            await state.clear()
            await message.answer("Главное меню:", reply_markup=main_menu_kb())
        elif current_state == UserState.waiting_document_name:
            await state.set_state(UserState.user_documents_menu)
            await message.answer("Меню документов:", reply_markup=user_documents_menu_kb())
        else:
            await state.clear()
            await message.answer("Главное меню:", reply_markup=main_menu_kb())

    @user_router.message(F.text == "📄 Документы")
    async def handle_documents_menu(message: types.Message, state: FSMContext):
        await state.set_state(UserState.user_documents_menu)
        await message.answer(
            "Меню документов. Выберите действие:", 
            reply_markup=user_documents_menu_kb()
        )
    
    @user_router.message(F.text == "📋 Список документов", UserState.user_documents_menu)
    async def handle_list_docs(message: types.Message):
        docs = service_manager.document_service.get_all_documents()
        if not docs:
            await message.answer("Документы не найдены", reply_markup=user_documents_menu_kb())
            return
        
        response = "Документы:\n" + "\n".join(
            f"{i+1}. {doc.name}" 
            for i, doc in enumerate(docs))
        await message.answer(response, reply_markup=user_documents_menu_kb())

    @user_router.message(F.text == "🔍 Поиск по названию", UserState.user_documents_menu)  
    async def start_document_search(message: types.Message, state: FSMContext):
        await state.set_state(UserState.waiting_document_name)
        await message.answer(
            "🔍 Введите название документа:",
            reply_markup=user_back_kb()
    )

    @user_router.message(UserState.waiting_document_name, F.text)
    async def handle_document_search(message: types.Message, state: FSMContext):
        if message.text == "◀️ Вернуться":
            await state.set_state(UserState.user_documents_menu)
            await message.answer("Меню документов:", reply_markup=user_documents_menu_kb())
            return

        try:
            document = service_manager.document_service.get_document_by_name(message.text.strip()) # type: ignore
            if not document:
                await message.answer(f"❌ Документ '{message.text}' не найден.")
                return

            content = document.content

            if isinstance(content, str):
                text = content
            elif isinstance(content, bytes):
                text = content.decode('utf-8', errors='replace')
            else:
                text = str(content)

            if len(text) > 3900:
                preview = text[:3900] + "..."
            else:
                preview = text

            await message.answer(f"📄 <b>{document.name}</b>:\n\n{preview}", parse_mode="HTML")

        except Exception as e:
            logger.error(f"Ошибка при показе документа: {e}")
            await message.answer("❌ Произошла ошибка при загрузке документа.")

        finally:
            await state.set_state(UserState.user_documents_menu)
            await message.answer("Меню документов:", reply_markup=user_documents_menu_kb())

    @user_router.message(F.text == "📌 Онбординг")
    async def start_onboarding(message: types.Message, state: FSMContext):
        try:
            roles = service_manager.onboarding_service.get_all_roles()
            if not roles:
                await message.answer("В данный момент нет доступных программ онбординга")
                return
            await message.answer(
                "Выберите вашу роль:",
                reply_markup=roles_kb(roles)
            )
            await state.set_state(OnboardingState.waiting_for_role)
        except Exception as e:
            logger.error(f"Error in start_onboarding: {e}")
            await message.answer("Произошла ошибка при запуске онбординга")

    @user_router.message(OnboardingState.waiting_for_role)
    async def process_role(message: types.Message, state: FSMContext):
        try:
            if not message.text:
                await message.answer("Пожалуйста, введите корректную роль.")
                return

            role = message.text.strip().lower()

            available_roles = service_manager.onboarding_service.get_all_roles()
            if role not in available_roles:
                await message.answer(
                    "Пожалуйста, выберите роль из предложенных:",
                    reply_markup=roles_kb(available_roles)
                )
                return

            checklist = service_manager.onboarding_service.get_checklist(role)
            if not checklist:
                await message.answer(
                    f"Для роли '{role}' нет информации по онбордингу",
                    reply_markup=main_menu_kb()
                )
                await state.clear()
                return

            response = (
                f"📋 План онбординга для {role.capitalize()}:\n"
                f"📄 Необходимые документы:\n" +
                "\n".join(f"• {doc}" for doc in checklist.documents) + "\n"
                f"📞 Контакты:\n" +
                "\n".join(f"• {contact}" for contact in checklist.contacts) + "\n"
                f"🗓 Мероприятия:\n" +
                "\n".join(f"• {event}" for event in checklist.events) + "\n"
                f"📚 Обучающие материалы:\n" +
                "\n".join(f"• {material}" for material in checklist.materials)
            )

            await message.answer(response, reply_markup=main_menu_kb())
            await state.clear()
        except Exception as e:
            logger.error(f"Error in process_role: {e}")
            await message.answer(
                "Произошла ошибка при обработке вашего выбора",
                reply_markup=main_menu_kb()
            )
            await state.clear()

    @user_router.message(F.text == "🏖 Оформить отпуск")
    async def start_vacation(message: types.Message, state: FSMContext):
        await message.answer(
            "Введите ваше ФИО:",
            reply_markup=cancel_kb()
        )
        await state.set_state(VacationState.waiting_for_name)

    @user_router.message(VacationState.waiting_for_name)
    async def process_name(message: types.Message, state: FSMContext):
        if not message.text or not message.text.strip():
            await message.answer("Пожалуйста, введите корректное ФИО:")
            return
        await state.update_data(name=message.text.strip())
        await message.answer(
            "Введите дату начала отпуска (ДД.ММ.ГГГГ):",
            reply_markup=cancel_kb()
        )
        await state.set_state(VacationState.waiting_for_start_date)

    @user_router.message(VacationState.waiting_for_start_date)
    async def process_start_date(message: types.Message, state: FSMContext):
        is_valid, start_date = _validate_date(message.text) # type: ignore
        if not is_valid or not start_date:
            await message.answer("Неверный формат даты. Введите в формате ДД.ММ.ГГГГ:")
            return
        today = date.today()
        if start_date < today:
            await message.answer("Дата начала не может быть в прошлом. Введите корректную дату:")
            return
        if not _is_within_one_month(start_date):
            await message.answer("Дата начала должна быть в пределах 1 месяца от текущей даты:")
            return
        await state.update_data(start_date=start_date)
        await message.answer(
            "Введите дату окончания отпуска (ДД.ММ.ГГГГ):",
            reply_markup=cancel_kb()
        ) 
        await state.set_state(VacationState.waiting_for_end_date) 

    @user_router.message(VacationState.waiting_for_end_date)
    async def process_end_date(message: types.Message, state: FSMContext):
        is_valid, end_date = _validate_date(message.text) # type: ignore
        data = await state.get_data()
        start_date = data.get('start_date')
        if not is_valid or not end_date:
            await message.answer("Неверный формат даты. Введите в формате ДД.ММ.ГГГГ:")
            return
        if not start_date:
            await message.answer("Ошибка данных. Начните процесс заново.")
            await state.clear()
            return
        if end_date < start_date:
            await message.answer("Дата окончания не может быть раньше даты начала. Введите корректную дату:")
            return
        if not _is_within_one_month(end_date):
            await message.answer("Дата окончания должна быть в пределах 1 месяцев от текущей даты:")
            return
        await state.update_data(end_date=end_date)
        await message.answer(
            "Выберите тип отпуска:",
            reply_markup=vacation_type_kb()
        )
        await state.set_state(VacationState.waiting_for_type)

    @user_router.message(VacationState.waiting_for_type)
    async def process_vacation_type(message: types.Message, state: FSMContext):
        if not message.text or message.text.lower() not in ["оплачиваемый", "неоплачиваемый"]:
            await message.answer("Пожалуйста, выберите тип отпуска из предложенных:")
            return
        data = await state.get_data()
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        name = data.get('name')
        if not all([start_date, end_date, name]):
            await message.answer("Ошибка данных. Начните процесс заново.", reply_markup=main_menu_kb())
            await state.clear()
            return
        days = (end_date - start_date).days + 1 # type: ignore
        vacation_application = (
            f"📄 Заявление на отпуск\n"
            f"Я, {name}, прошу предоставить мне {message.text.lower()} отпуск "
            f"с {start_date.strftime('%d.%m.%Y')} по {end_date.strftime('%d.%m.%Y')} "  # type: ignore
            f"({days} {'день' if days == 1 else 'дня' if 1 < days < 5 else 'дней'})."
        )
        instructions = (
            f"📌 Инструкция:\n"
            f"1. Распечатайте заявление\n"
            f"2. Подпишите его\n"
            f"3. Отправьте на почту hr@example.com\n"
            f"4. Уведомите руководителя"
        )
        await message.answer(vacation_application)
        await message.answer(instructions, reply_markup=main_menu_kb())
        await state.clear()

    def _validate_date(date_str: str) -> Tuple[bool, Optional[date]]:
        try:
            return True, datetime.strptime(date_str, "%d.%m.%Y").date()
        except ValueError:
            return False, None

    def _is_within_one_month(check_date: date, reference_date: date = None) -> bool: # type: ignore
        reference_date = reference_date or date.today()
        max_date = reference_date + timedelta(days=31)
        return reference_date <= check_date <= max_date
    
    @user_router.message(Command("stop"))
    async def stop_bot_command(message: Message, bot: Bot):
        try:
            await message.answer(
                "Бот остановлен",
                reply_markup=types.ReplyKeyboardRemove()
            )
            await asyncio.sleep(2)
            logger.info(f"Бот остановлен пользователем {message.from_user.id}") # type: ignore
            await bot.close()
        except Exception as e:
            logger.error(f"Ошибка при остановке бота: {e}")
            await message.answer("Не удалось остановить бота")