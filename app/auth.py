import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from app.config import JWT_SECRET

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)

def create_access_token(user_id: int, expires_delta: int = 3600):
    payload = {"sub": str(user_id), "exp": datetime.utcnow() + timedelta(seconds=expires_delta)}
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return int(payload.get("sub"))
    except Exception:
        return None
