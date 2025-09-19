from sanic import Blueprint, response
from sanic.request import Request
from sqlalchemy.future import select

from app.auth import verify_password, create_access_token
from app.db import AsyncSessionLocal
from app.models import User

bp = Blueprint("auth", url_prefix="/auth")

@bp.post("/login")
async def login(request: Request):
    data = request.json or {}
    email = data.get("email")
    password = data.get("password")
    async with AsyncSessionLocal() as session:
        q = await session.execute(select(User).where(User.email == email))
        user = q.scalars().first()
        if not user or not verify_password(password, user.password_hash):
            return response.json({"error": "invalid_credentials"}, status=401)
        token = create_access_token(user.id)
        return response.json({"access_token": token, "user": {"id": user.id, "email": user.email, "full_name": user.full_name}})
