from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TELEGRAM_TOKEN: str
    DATABASE_URL: str
    CHROMA_PATH: str = "./chroma_db"
    TELEGRAM_CHAT_ID: str | None = None

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()