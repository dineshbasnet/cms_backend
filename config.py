from pydantic_settings import SettingsConfigDict,BaseSettings
from typing import List
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Settings(BaseSettings):
    #Database settings
    DATABASE_URL:str
    SECRET_KEY:str
    ALGORITHM:str
    ACCESS_TOKEN_EXPIRE_MINUTES:int
    REFRESH_TOKEN_EXPIRE_DAYS:int
    model_config=SettingsConfigDict(env_file=".env",case_sensitive=True)
    
    #Media settings
    MEDIA_ROOT:Path = BASE_DIR/"uploads"
    MEDIA_URL:str = "/uploads"
    BASE_URL:str = "http://localhost:8000"
    
    #Mail settings
    MAIL_SERVER: str
    MAIL_PORT: int
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str

    
    

settings = Settings()
    

