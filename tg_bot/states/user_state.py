from aiogram.fsm.state import StatesGroup, State

class OnboardingState(StatesGroup):
    waiting_for_role = State()

class VacationState(StatesGroup):
    waiting_for_name = State()
    waiting_for_start_date = State()
    waiting_for_end_date = State()
    waiting_for_type = State()

class UserState(StatesGroup):
    user_documents_menu = State()
    waiting_for_question = State()
    waiting_document_name = State()
    waiting_for_question_type = State()