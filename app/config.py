import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    BOT_TOKEN: str
    BASE_SITE: str
    ADMIN_ID: int
    ZULIP_API_KEY: str
    ZULIP_EMAIL: str
    ZULIP_SITE: str
    ZULIP_ALLOW_INSECURE: bool
    ZULIP_STAFF_IDS: list[int]

    RABBIT_USER: str
    RABBIT_USER_PSW: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    )

    def get_webhook_url(self) -> str:
        """Возвращает URL вебхука с кодированием специальных символов."""
        return f"{self.BASE_SITE}/webhook"


settings = Settings()
