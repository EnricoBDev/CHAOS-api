import os

from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

# db
DB_URL = "sqlite:///data/database.db"
SQL_ECHO = bool(os.getenv("SQL_ECO"))

# user_service
INITIAL_POINTS = int(os.getenv("INITIAL_POINTS"))  # ty:ignore[invalid-argument-type]

# auth
SECRET = str(os.getenv("SECRET"))
ALGORITHM = str(os.getenv("ALGORITHM"))
JWT_EXP_DAYS = int(os.getenv("JWT_EXP_DAYS"))  # ty:ignore[invalid-argument-type]
