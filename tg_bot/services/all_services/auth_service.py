from database.db import Database
from config.config import settings

class AuthService:
    def __init__(self, db: Database):
        self.db = db
        self.admin_password = settings.ADMIN_PASSWORD

    def login_admin(self, user_id: int, password: str) -> bool:
        if password == self.admin_password:
            self.db.add_admin_session(user_id)
            return True
        return False

    def logout_admin(self, user_id: int):
        return self.db.delete_admin_session(user_id)

    def is_admin(self, user_id: int) -> bool:
        return self.db.get_admin_session(user_id)