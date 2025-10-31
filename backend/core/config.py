# /backend/core/config.py

from passlib.context import CryptContext
import os
from dotenv import load_dotenv
from pathlib import Path


env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# IMPORTANT: Keep SECRET_KEY in .env file
# or environment variable in production!
# Use env var or a default
SECRET_KEY = os.getenv("SECRET_KEY", "Ihet6eJMLfDf7IAo9stPiHsUPq7Z8xQX")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token validity period

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
