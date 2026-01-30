from datetime import datetime, timedelta, timezone

# db
DB_URL = "sqlite:///database_test.db"
SQL_ECHO = False

# user_service
INITIAL_POINTS = 1000

# auth
NOT_SO_SECRET = "sesso"
ALGORITHM = "HS256"
JWT_EXP = datetime.now(timezone.utc) + timedelta(days=1)
