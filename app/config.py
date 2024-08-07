import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    GOOGLE_APPLICATION_CREDENTIALS: str
    GOOGLE_DRIVE_FOLDER_ID: str
    TEMP_FILE_PATH: str = "/tmp"

    class Config:
        env_file = ".env"

settings = Settings()