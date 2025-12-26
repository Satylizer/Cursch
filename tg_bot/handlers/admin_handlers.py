from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from states.admin_state import AdminState
from services.service_manager import ServiceManager
from config.logging import logger
from typing import Optional
from keyboards.admin_kb import *
from states.admin_state import *
from keyboards.user_kb import main_menu_kb

def setup_admin_handlers(router: Router, service_manager: ServiceManager):
    admin_router = Router()
    router.include_router(admin_router)

    @admin_router.message(F.text == "/admin")
    async def admin_start(message: types.Message, state: FSMContext):
        await state.set_state(AdminState.waiting_password)
        await message.answer("🔐 Введите пароль:", reply_markup=cancel_kb())

    @admin_router.message(AdminState.waiting_password)
    async def check_password(message: types.Message, state: FSMContext):
        if message.text == "❌ Отмена":
            await state.clear()
            await message.answer("Действие отменено")
            return
            
        if service_manager.auth_service.login_admin(message.from_user.id, message.text): # type: ignore
            await state.set_state(AdminState.main_menu)
            await message.answer("Доступ разрешен", reply_markup=admin_menu_kb())
        else:
            await message.answer("Неверный пароль", reply_markup=cancel_kb())

    @admin_router.message(F.text == "🔙 Назад", AdminState.main_menu)
    @admin_router.message(F.text == "❌ Отмена")
    async def to_main_menu(message: types.Message, state: FSMContext):
        await state.set_state(AdminState.main_menu)
        await message.answer("Главное меню:", reply_markup=admin_menu_kb())

    @admin_router.message(F.text == "🔙 Выйти")
    async def admin_logout(message: types.Message, state: FSMContext):
        try:
            await state.clear()
            await message.answer(
                "Вы успешно вышли из админ-панели",
                reply_markup=types.ReplyKeyboardRemove()
            )

            await message.answer(
                "Выберите действие:",
                reply_markup=main_menu_kb()
            )
        except Exception as e:
            logger.error(f"Ошибка при выходе из админ-панели: {e}")
            await message.answer("Произошла ошибка при выходе, попробуйте еще раз")

    @admin_router.message(F.text == "📂 Документы")
    async def docs_menu(message: types.Message, state: FSMContext):
        await state.set_state(AdminState.documents_menu)
        await message.answer("Управление документами:", reply_markup=documents_menu_kb())

    @admin_router.message(F.text == "🔙 Назад", AdminState.documents_menu)
    async def back_from_docs(message: types.Message, state: FSMContext):
        await state.set_state(AdminState.main_menu)
        await message.answer("Главное меню:", reply_markup=admin_menu_kb())

    @admin_router.message(F.text == "📄 Список", AdminState.documents_menu)
    async def list_doсs(message: types.Message):
        try:
            documents = service_manager.document_service.get_all_documents()
            
            if not documents:
                await message.answer(
                    "В базе нет документов", 
                    reply_markup=documents_menu_kb()
                )
                return
                
            await message.answer(
                "Доступные документы:",
                reply_markup=documents_list_kb(documents) # type: ignore
            )
            
        except Exception as e:
            logger.error(f"Ошибка получения документов: {e}")
            await message.answer(
                "⚠️ Произошла ошибка при загрузке документов",
                reply_markup=documents_menu_kb()
        )

    @admin_router.message(F.text == "➕ Добавить", AdminState.documents_menu)
    async def add_doc_start(message: types.Message, state: FSMContext):
        await state.set_state(AdminState.adding_document)
        await message.answer(
            "Отправьте файл",
            reply_markup=back_kb())

    @admin_router.message(AdminState.adding_document)
    async def add_doc_process(message: types.Message, state: FSMContext):
        if message.text == "🔙 Назад":
            await state.set_state(AdminState.documents_menu)
            await message.answer("Действие отменено", reply_markup=documents_menu_kb())
            return
            
        success, response = await service_manager.document_service.add_document(message, message.from_user.id) # type: ignore
        await message.answer(response, reply_markup=documents_menu_kb())
        await state.set_state(AdminState.documents_menu)

    @admin_router.message(F.text == "👥 Сотрудники")
    async def employees_menu(message: types.Message, state: FSMContext):
        await state.set_state(AdminState.employees_menu)
        await message.answer("Управление сотрудниками:", reply_markup=employees_menu_kb())

    @admin_router.message(F.text == "🔙 Назад", AdminState.employees_menu)
    async def back_from_employees(message: types.Message, state: FSMContext):
        await state.set_state(AdminState.main_menu)
        await message.answer("Главное меню:", reply_markup=admin_menu_kb())

    @admin_router.message(F.text == "👤 Список", AdminState.employees_menu)
    async def list_employees(message: types.Message):
        emps = service_manager.employee_service.get_all_employees()
        if not emps:
            await message.answer("Сотрудники не найдены", reply_markup=employees_menu_kb())
            return
        
        response = "👥 Сотрудники:\n" + "\n".join(
            f"{i+1}. {emp.name} ({emp.email}) - {emp.role}"
            for i, emp in enumerate(emps))
        await message.answer(response, reply_markup=employees_menu_kb())

    @admin_router.message(F.text == "➕ Добавить", AdminState.employees_menu)
    async def add_emp_start(message: types.Message, state: FSMContext):
        await state.set_state(AdminState.adding_employee)
        await message.answer(
            "Введите данные в формате:\nEmail, ФИО, Должность",
            reply_markup=back_kb())

    @admin_router.message(AdminState.adding_employee)
    async def add_emp_process(message: types.Message, state: FSMContext):
        if message.text == "🔙 Назад":
            await state.set_state(AdminState.employees_menu)
            await message.answer("Действие отменено", reply_markup=employees_menu_kb())
            return
            
        try:
            email, name, role = map(str.strip, message.text.split(",", 2)) # type: ignore
            success, response = service_manager.employee_service.add_employee(email, name, role)
            await message.answer(response, reply_markup=employees_menu_kb())
            await state.set_state(AdminState.employees_menu)
        except ValueError:
            await message.answer(
                "Неверный формат. Требуется: Email, ФИО, Должность",
                reply_markup=back_kb())
            
    @admin_router.message(F.text == "🗑 Удалить", AdminState.documents_menu)
    async def delete_doc_start(message: types.Message, state: FSMContext):
        docs = service_manager.document_service.get_all_documents()
        if not docs:
            await message.answer("Нет документов для удаления", reply_markup=documents_menu_kb())
            return
        
        builder = ReplyKeyboardBuilder()
        for doc in docs:
            builder.button(text=doc.name)
        builder.button(text="🔙 Назад")
        builder.adjust(2)
        
        await state.set_state(AdminState.deleting_document)
        await message.answer(
            "Выберите документ для удаления:",
            reply_markup=builder.as_markup(resize_keyboard=True)
        )
        
    @admin_router.message(AdminState.deleting_document) # type: ignore
    async def delete_doc_process(message: types.Message, state: FSMContext):
        if message.text == "🔙 Назад":
            await state.set_state(AdminState.documents_menu)
            await message.answer("Действие отменено", reply_markup=documents_menu_kb())
            return
            
        success, response = service_manager.document_service.delete_document(message.text) # type: ignore
        await message.answer(response, reply_markup=documents_menu_kb())
        await state.set_state(AdminState.documents_menu)

    @admin_router.message(F.text == "🗑 Удалить", AdminState.employees_menu)
    async def delete_emp_start(message: types.Message, state: FSMContext):
        emps = service_manager.employee_service.get_all_employees()
        if not emps:
            await message.answer("Нет сотрудников для удаления", reply_markup=employees_menu_kb())
            return
        
        builder = ReplyKeyboardBuilder()
        for emp in emps:
            builder.button(text=emp.email)
        builder.button(text="🔙 Назад")
        builder.adjust(2)
        
        await state.set_state(AdminState.deleting_employee)
        await message.answer(
            "Выберите email сотрудника для удаления:",
            reply_markup=builder.as_markup(resize_keyboard=True))
    
    @admin_router.message(AdminState.deleting_employee)
    async def delete_emp_process(message: types.Message, state: FSMContext):
        if message.text == "🔙 Назад":
            await state.set_state(AdminState.employees_menu)
            await message.answer("Действие отменено", reply_markup=employees_menu_kb())
            return
            
        success, response = service_manager.employee_service.delete_employee(message.text) # type: ignore
        await message.answer(response, reply_markup=employees_menu_kb())
        await state.set_state(AdminState.employees_menu)