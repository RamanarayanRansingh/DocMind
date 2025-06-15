from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    DATABASE_URL: str 
    SECRET_KEY: str   
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int 
    GROQ_API_KEY: str
    DATABASE_QUERY_URL: str

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()