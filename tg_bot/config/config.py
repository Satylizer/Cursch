from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    BOT_TOKEN: str = "8179991403:AAEWzRBJsHYjTl1b4vBG86ufd8eZ0vW3BiY"
    ADMIN_PASSWORD: str = "admin123"
    
    class Config:
        env_file = ".env"

settings = Settings()