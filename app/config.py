import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@db:5432/payments")
JWT_SECRET = os.getenv("JWT_SECRET", "changeme")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "gfdmhghif38yrf9ew0jkf32")
INIT_DB = os.getenv("INIT_DB", "1")  # "1" чтобы при старте инициализировать тестовую БД
