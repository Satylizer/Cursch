import sys
import os
import sqlite3
from enum import Enum
from pathlib import Path

current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
sys.path.append(str(project_root))

# Теперь импортируем наши классы
try:
    from tg_bot.database.models.models import DocumentType, Document, Employee, OnboardingChecklist
    from database.db import Database
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    print("Проверьте структуру проекта и sys.path")
    sys.exit(1)

def test_database():
    print("="*50)
    print("НАЧАЛО ТЕСТИРОВАНИЯ БАЗЫ ДАННЫХ")
    print("="*50)
    
    # Инициализация базы данных в памяти
    db = Database(db_path=":memory:")
    
    try:
        # Тестирование документов
        print("\n=== ТЕСТИРОВАНИЕ ДОКУМЕНТОВ ===")
        
        # Создание документов
        doc1 = Document(name="Политика компании", content="Содержание политики...", type=DocumentType.PDF)
        doc2 = Document(name="Руководство сотрудника", content="Инструкции для сотрудников...", type=DocumentType.DOCX)
        
        doc1_id = db.add_document(doc1)
        doc2_id = db.add_document(doc2)
        print(f"Добавлены документы: ID {doc1_id}, ID {doc2_id}")
        
        # Чтение документов
        documents = db.get_all_documents()
        print(f"Всего документов: {len(documents)}")
        for doc in documents:
            print(f"  - {doc.name} ({doc.type.value})")
        
        # Удаление документа
        deleted = db.delete_document_by_name("Политика компании")
        print(f"Удаление документа 'Политика компании': {'Успешно' if deleted else 'Неудачно'}")
        
        documents = db.get_all_documents()
        print(f"Осталось документов: {len(documents)}")
        
        # Тестирование сотрудников
        print("\n=== ТЕСТИРОВАНИЕ СОТРУДНИКОВ ===")
        
        # Создание сотрудников
        # In your test_database() function:
        emp1 = Employee()
        emp1.email = "ivanov@example.com"
        emp1.name = "Иван Иванов"
        emp1.role = "разработчик"

        emp2 = Employee()
        emp2.email = "petrova@example.com"
        emp2.name = "Мария Петрова"
        emp2.role = "менеджер"
        
        emp1_id = db.add_employee(emp1)
        emp2_id = db.add_employee(emp2)
        print(f"Добавлены сотрудники: ID {emp1_id}, ID {emp2_id}")
        
        # Чтение сотрудника
        emp = db.get_employee("ivanov@example.com")
        print(f"Найден сотрудник: {emp.name} ({emp.role})" if emp else "Сотрудник не найден")
        
        # Удаление сотрудника
        deleted = db.delete_employee("petrova@example.com")
        print(f"Удаление сотрудника 'petrova@example.com': {'Успешно' if deleted else 'Неудачно'}")
        
        # Тестирование сессий администратора
        print("\n=== ТЕСТИРОВАНИЕ АДМИН-СЕССИЙ ===")
        
        # Добавление сессий
        db.add_admin_session(12345)
        db.add_admin_session(67890)
        
        # Проверка сессий
        session_exists = db.get_admin_session(12345)
        print(f"Сессия для 12345: {'Существует' if session_exists else 'Отсутствует'}")
        
        # Удаление сессии
        deleted = db.delete_admin_session(67890)
        print(f"Удаление сессии 67890: {'Успешно' if deleted else 'Неудачно'}")
        
        session_exists = db.get_admin_session(67890)
        print(f"Сессия для 67890: {'Существует' if session_exists else 'Отсутствует'}")
        
        # Тестирование чек-листов онбординга
        print("\n=== ТЕСТИРОВАНИЕ ЧЕК-ЛИСТОВ ОНБОРДИНГА ===")
        
        # Получение чек-листа
        checklist = db.get_onboarding_checklist("разработчик")
        if checklist:
            print(f"Чек-лист для разработчика:")
            print(f"  Документы: {checklist.documents}")
            print(f"  Контакты: {checklist.contacts}")
            print(f"  Мероприятия: {checklist.events}")
            print(f"  Материалы: {checklist.materials}")
        else:
            print("Чек-лист для разработчика не найден")
        
        # Добавление нового чек-листа
        new_checklist = OnboardingChecklist(
            role="дизайнер",
            documents=["Гайдлайн бренда", "Инструкция по инструментам"],
            contacts=["Руководитель: design@example.com"],
            events=["Обучение Figma", "Введение в продукт"],
            materials=["https://example.com/design-onboarding"]
        )
        db.add_onboarding_checklist(new_checklist)
        
        checklist = db.get_onboarding_checklist("дизайнер")
        print(f"Чек-лист для дизайнера: {'Найден' if checklist else 'Не найден'}")
        
        print("\n" + "="*50)
        print("ТЕСТИРОВАНИЕ УСПЕШНО ЗАВЕРШЕНО!")
        print("="*50)
        
    except Exception as e:
        print(f"\n!!! ОШИБКА ПРИ ТЕСТИРОВАНИИ: {str(e)}")
        import traceback
        traceback.print_exc()
        print("="*50)
        print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО С ОШИБКАМИ!")
        print("="*50)
    finally:
        db.close()

if __name__ == "__main__":
    test_database()