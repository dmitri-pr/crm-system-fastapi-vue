from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os


class Settings(BaseSettings):
    app_name: str = "CRM FastAPI Vue"
    secret_key: str = "super-secret-key-change-in-production-please-use-env"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 1 day
    database_url: str = "sqlite+aiosqlite:///./crm.db"
    # Для PostgreSQL используйте: postgresql+asyncpg://user:password@localhost:5432/crm_db
    media_root: str = "./media"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def model_post_init(self, __context):
        # Абсолютный путь для media
        if self.media_root == "./media":
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
            self.media_root = os.path.join(base_dir, "media")
        # Для SQLite делаем путь абсолютным, чтобы не зависеть от cwd
        # Только для точного дефолта, чтобы не перезатирать пользовательский абсолютный путь
        if not self.database_url:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
            abs_db = os.path.join(base_dir, "crm.db")
            abs_db_posix = abs_db.replace("\\", "/")
            self.database_url = f"sqlite+aiosqlite:///{abs_db_posix}"
        elif self.database_url == "sqlite+aiosqlite:///./crm.db":
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
            abs_db = os.path.join(base_dir, "crm.db")
            abs_db_posix = abs_db.replace("\\", "/")
            self.database_url = f"sqlite+aiosqlite:///{abs_db_posix}"
        # Защита от продакшена с дефолтным ключом
        if self.secret_key.startswith("super-secret") and os.getenv("ENV") == "production":
            raise RuntimeError("SECRET_KEY должен быть переопределён в production via ENV")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
