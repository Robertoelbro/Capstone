import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / '.env')
DATABASE_URL = os.getenv('DATABASE_URL', '')
SECRET_KEY = os.getenv('SECRET_KEY', '')
CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',')
DATA_ENCRYPTION_KEY = os.getenv('DATA_ENCRYPTION_KEY', '')
