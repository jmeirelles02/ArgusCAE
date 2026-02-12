from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GEMINI_API_KEY: str
    TELEGRAM_TOKEN: str
    DATABASE_URL: str 
    CHROMA_PATH: str = "./chroma_db" 

    class Config:
        env_file = ".env"
        extra = "ignore" 

settings = Settings()