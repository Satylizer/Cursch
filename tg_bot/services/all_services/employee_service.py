from typing import Tuple, List, Optional
from database.models.models import Employee
from database.db import Database
import sqlite3
import re

class EmployeeService:
    def __init__(self, db: Database):
        self.db = db
        self.ADMIN_EMAIL = "admin@example.com"

    def _validate_email(self, email: str) -> bool:
        return bool(re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email))

    def _validate_input(self, email: str, name: str, role: str) -> Optional[Tuple[bool, str]]:
        if not all([email, name, role]):
            return False, "Все поля должны быть заполнены"
        if not self._validate_email(email):
            return False, "Неверный формат email"
        if email == self.ADMIN_EMAIL:
            return False, "Этот email зарезервирован для администратора"
        return None

    def add_employee(self, email: str, name: str, role: str) -> Tuple[bool, str]:
        validation_result = self._validate_input(email, name, role)
        if validation_result:
            return validation_result

        employee = Employee(
            email=email.strip(),
            name=name.strip(),
            role=role.strip()
        )
        
        try:
            self.db.add_employee(employee)
            return True, f"Сотрудник {name} успешно добавлен"
        except sqlite3.IntegrityError:
            return False, "Сотрудник с таким email уже существует"
        except sqlite3.Error as e:
            return False, f"Ошибка базы данных: {str(e)}"

    def get_all_employees(self) -> List[Employee]:
        try:
            return self.db.get_all_employees()
        except sqlite3.Error as e:
            print(f"Ошибка базы данных: {e}")
            return []

    def get_employee(self, email: str) -> Optional[Employee]:
        try:
            return self.db.get_employee(email.strip())
        except sqlite3.Error as e:
            print(f"Ошибка базы данных: {e}")
            return None

    def delete_employee(self, email: str) -> Tuple[bool, str]:
        if not email:
            return False, "Email не может быть пустым"
            
        email = email.strip()
        
        if email == self.ADMIN_EMAIL:
            return False, "Нельзя удалить аккаунт администратора"
        
        employee = self.get_employee(email)
        if not employee:
            return False, f"Сотрудник с email {email} не найден"
        
        try:
            if self.db.delete_employee(email):
                return True, f"Сотрудник {employee.name} ({email}) успешно удалён"
            return False, f"Не удалось удалить сотрудника {email}"
        except sqlite3.Error as e:
            return False, f"Ошибка базы данных: {str(e)}"