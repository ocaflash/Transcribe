import os
from dotenv import load_dotenv

load_dotenv()  # Загружаем переменные из .env файла

DATABASE_URL = os.getenv("DATABASE_URL")
