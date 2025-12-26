# services/service_manager.py
from database.db import Database
from services.all_services.auth_service import AuthService
from services.all_services.document_service import DocumentService
from services.all_services.employee_service import EmployeeService
from services.all_services.onboarding_service import OnboardingService

class ServiceManager:
    def __init__(self, db: Database):
        self.db = db
        self._initialize_services()
        
    def _initialize_services(self):
        self.auth_service = AuthService(self.db)
        self.document_service = DocumentService(self.db)
        self.employee_service = EmployeeService(self.db)
        self.onboarding_service = OnboardingService(self.db)
        
    def close(self):
        self.db.close()