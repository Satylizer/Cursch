from database.db import Database
from typing import Optional, List
from database.models.models import OnboardingChecklist

class OnboardingService:
    def __init__(self, db: Database):
        self.db = db

    def get_checklist(self, role: str) -> Optional[OnboardingChecklist]:
        return self.db.get_onboarding_checklist(role)

    def get_all_roles(self) -> List[str]:
        return ["разработчик", "менеджер проектов"] 