from aiogram.fsm.state import StatesGroup, State

class AdminState(StatesGroup):
    waiting_password = State()
    main_menu = State()
    documents_menu = State()
    employees_menu = State()
    adding_document = State()
    deleting_document = State()
    adding_employee = State()
    deleting_employee = State()