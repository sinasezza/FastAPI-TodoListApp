import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")

JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM")


BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=f"{BASE_DIR}/templates")
