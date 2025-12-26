import sqlite3
from pathlib import Path
from database.models.models import *
from typing import List

class Database:
    def __init__(self, db_path: str = "D:/Practice App/practice_project/tg_bot/database/db.db"):
        self.db_path = Path(db_path)
        self.conn = None
        self._initialize_db()

    def _initialize_db(self):
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            content TEXT NOT NULL,
            type TEXT NOT NULL
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            password TEXT NOT NULL DEFAULT 'default123'
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_sessions (
            user_id INTEGER NOT NULL UNIQUE
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS onboarding_checklists (
            role TEXT PRIMARY KEY,
            documents_json TEXT NOT NULL,
            contacts_json TEXT NOT NULL,
            events_json TEXT NOT NULL,
            materials_json TEXT NOT NULL
        )
        ''')
        
        self.conn.commit()
        self._seed_initial_data()

    def _seed_initial_data(self):
        checklists = [
            OnboardingChecklist(
                role="разработчик",
                documents=["Трудовой договор", "NDA", "Политика безопасности"],
                contacts=["HR: hr@example.com", "Руководитель: dev_lead@example.com"],
                events=["1 день: Введение в компанию", "2 день: Обучение инструментам"],
                materials=["https://example.com/dev-onboarding"]
            ),
            OnboardingChecklist(
                role="менеджер проектов",
                documents=["Трудовой договор", "NDA", "Политика работы с клиентами"],
                contacts=["HR: hr@example.com", "Руководитель: pm_lead@example.com"],
                events=["1 день: Введение в компанию", "2 день: Обучение процессам"],
                materials=["https://example.com/pm-onboarding"]
            )
        ]
        
        for checklist in checklists:
            self.add_onboarding_checklist(checklist)
            
    def add_onboarding_checklist(self, checklist: OnboardingChecklist):
        cursor = self.conn.cursor() # type: ignore
        cursor.execute('''
        INSERT OR REPLACE INTO onboarding_checklists 
        (role, documents_json, contacts_json, events_json, materials_json)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            checklist.role,
            ','.join(checklist.documents),
            ','.join(checklist.contacts),
            ','.join(checklist.events),
            ','.join(checklist.materials)
        ))
        self.conn.commit() # type: ignore

    def add_document(self, document: Document) -> int:
        cursor = self.conn.cursor() # type: ignore
        cursor.execute('''
        INSERT INTO documents (name, content, type)
        VALUES (?, ?, ?)
        ''', (document.name, document.content, document.type.value))
        doc_id = cursor.lastrowid
        self.conn.commit() # type: ignore
        return doc_id # type: ignore

    def get_all_documents(self) -> List[Document]: # type: ignore
        try:
            cursor = self.conn.cursor() # type: ignore
            cursor.execute('SELECT * FROM documents')
            documents = []
            
            for row in cursor.fetchall():
                document = Document(
                    id=row[0],
                    name=row[1],
                    content=row[2],
                    type=DocumentType(row[3])
                )
                documents.append(document)
                
            return documents
        except sqlite3.Error as e:
            print(f"Ошибка при получении документов: {e}")
            return []
        
    def get_document_by_name(self, name: str) -> Optional[Document]:
        try:
            cursor = self.conn.cursor() # type: ignore
            cursor.execute(
                'SELECT id, name, content, type FROM documents WHERE name = ?',
                (name,)
            )
            row = cursor.fetchone()
            
            if row:
                return Document(
                    id=row[0],
                    name=row[1],
                    content=row[2],
                    type=DocumentType(row[3])
                )
            return None
        except sqlite3.Error as e:
            print(f"Ошибка при поиске документа: {e}")
            return None
    
    def delete_document_by_name(self, name: str) -> bool:
        try:
            cursor = self.conn.cursor() # type: ignore
            cursor.execute('DELETE FROM documents WHERE name = ?', (name,))
            self.conn.commit() # type: ignore
            return cursor.rowcount > 0
        except sqlite3.Error:
            return False

    def add_employee(self, employee: Employee) -> int:
        cursor = self.conn.cursor() # type: ignore
        cursor.execute('''
        INSERT INTO employees (email, name, role)
        VALUES (?, ?, ?)
        ''', (employee.email, employee.name, employee.role))
        emp_id = cursor.lastrowid
        self.conn.commit() # type: ignore
        return emp_id # type: ignore

    def get_employee(self, email: str) -> Optional[Employee]:
        cursor = self.conn.cursor() # type: ignore
        cursor.execute('SELECT * FROM employees WHERE email = ?', (email,))
        row = cursor.fetchone()
        if row:
            return Employee(
                id=row[0],
                email=row[1],
                name=row[2],
                role=row[3]
            )
        return None
    
    def get_all_employees(self) -> List[Employee]:
        try:
            cursor = self.conn.cursor() # type: ignore
            cursor.execute('SELECT id, email, name, role FROM employees')
            employees = []
            
            for row in cursor.fetchall():
                employee = Employee(
                    id=row[0],
                    email=row[1],
                    name=row[2],
                    role=row[3]
                )
                employees.append(employee)
                
            return employees
        except sqlite3.Error as e:
            print(f"Ошибка при получении списка сотрудников: {e}")
            return []
    
    def get_all_documents(self) -> List[Document]:
        try:
            cursor = self.conn.cursor() # type: ignore
            cursor.execute('SELECT * FROM documents')
            documents = []
            
            for row in cursor.fetchall():
                document = Document(
                    id=row[0],
                    name=row[1],
                    content=row[2],
                    type=DocumentType(row[3])
                )
                documents.append(document)
                
            return documents
        except sqlite3.Error as e:
            print(f"Ошибка при получении документов: {e}")
            return []
    
    def delete_employee(self, email: str) -> bool:
        try:
            cursor = self.conn.cursor() # type: ignore
            cursor.execute('DELETE FROM employees WHERE email = ?', (email,))
            self.conn.commit() # type: ignore
            return cursor.rowcount > 0
        except sqlite3.Error:
            self.conn.rollback() # type: ignore
            return False

    def add_admin_session(self, user_id: int) -> int:
        cursor = self.conn.cursor() # type: ignore
        cursor.execute('''
        INSERT OR REPLACE INTO admin_sessions (user_id)
        VALUES (?)
        ''', (user_id,))
        session_id = cursor.lastrowid
        self.conn.commit() # type: ignore
        return session_id # type: ignore

    def get_admin_session(self, user_id: int) -> bool:
        cursor = self.conn.cursor() # type: ignore
        cursor.execute('SELECT 1 FROM admin_sessions WHERE user_id = ?', (user_id,))
        return cursor.fetchone() is not None

    def delete_admin_session(self, user_id: int) -> bool:
        cursor = self.conn.cursor() # type: ignore
        cursor.execute('DELETE FROM admin_sessions WHERE user_id = ?', (user_id,))
        self.conn.commit() # type: ignore
        return cursor.rowcount > 0
    
    def get_onboarding_checklist(self, role: str) -> Optional[OnboardingChecklist]:
        try:
            cursor = self.conn.cursor() # type: ignore
            cursor.execute(
                'SELECT role, documents_json, contacts_json, events_json, materials_json '
                'FROM onboarding_checklists WHERE role = ?', 
                (role,)
            )
            row = cursor.fetchone()
            
            if row:
                return OnboardingChecklist(
                    role=row[0],
                    documents=row[1].split(','),
                    contacts=row[2].split(','),
                    events=row[3].split(','),
                    materials=row[4].split(',')
                )
            return None
        except sqlite3.Error as e:
            print(f"Ошибка при получении чек-листа: {e}")
            return None

    def close(self):
        if self.conn:
            self.conn.close()