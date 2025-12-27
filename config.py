from pydantic_settings import SettingsConfigDict,BaseSettings
from typing import List
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Settings(BaseSettings):
    #Database settings
    DATABASE_URL:str
    model_config=SettingsConfigDict(env_file=".env",case_sensitive=True)
    
    #Media settings
    MEDIA_ROOT:Path = BASE_DIR/"uploads"
    MEDIA_URL:str = "/uploads"
    BASE_URL:str = "http://localhost:8000"
    
    

settings = Settings()
    

