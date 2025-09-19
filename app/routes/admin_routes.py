from sanic import Blueprint, response
from sanic.request import Request
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select

from app.auth import decode_access_token, hash_password
from app.db import AsyncSessionLocal
from app.models import User

bp = Blueprint("admin", url_prefix="/admin")

async def get_current_admin(request: Request):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth.split(" ", 1)[1]
    user_id = decode_access_token(token)
    if not user_id:
        return None
    async with AsyncSessionLocal() as session:
        q = await session.execute(select(User).where(User.id == user_id))
        u = q.scalars().first()
        if u and u.is_admin:
            return u
    return None

@bp.get("/me")
async def me(request: Request):
    admin = await get_current_admin(request)
    if not admin:
        return response.json({"error": "unauthorized"}, status=401)
    return response.json({"id": admin.id, "email": admin.email, "full_name": admin.full_name})

@bp.post("/users")
async def create_user(request: Request):
    admin = await get_current_admin(request)
    if not admin:
        return response.json({"error": "unauthorized"}, status=401)
    data = request.json or {}
    async with AsyncSessionLocal() as session:
        user = User(email=data["email"], password_hash=hash_password(data["password"]), full_name=data.get("full_name"))
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return response.json({"id": user.id, "email": user.email})

@bp.put("/users/<user_id:int>")
async def update_user(request: Request, user_id: int):
    admin = await get_current_admin(request)
    if not admin:
        return response.json({"error": "unauthorized"}, status=401)
    data = request.json or {}
    async with AsyncSessionLocal() as session:
        q = await session.execute(select(User).where(User.id == user_id))
        user = q.scalars().first()
        if not user:
            return response.json({"error": "not_found"}, status=404)
        if "email" in data: user.email = data["email"]
        if "full_name" in data: user.full_name = data["full_name"]
        if "password" in data: user.password_hash = hash_password(data["password"])
        await session.commit()
        return response.json({"ok": True})

@bp.delete("/users/<user_id:int>")
async def delete_user(request: Request, user_id: int):
    admin = await get_current_admin(request)
    if not admin:
        return response.json({"error": "unauthorized"}, status=401)
    async with AsyncSessionLocal() as session:
        q = await session.execute(select(User).where(User.id == user_id))
        user = q.scalars().first()
        if not user:
            return response.json({"error": "not_found"}, status=404)
        await session.delete(user)
        await session.commit()
        return response.json({"ok": True})


@bp.get("/users")
async def list_users(request: Request):
    # Предположим, что у вас есть функция, которая возвращает текущего админа.
    admin = await get_current_admin(request)

    if not admin:
        return response.json({"error": "unauthorized"}, status=401)

    # Используем асинхронную сессию и выполняем запрос
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).options(selectinload(User.accounts))  # Загрузка аккаунтов пользователя
        )
        users = result.scalars().all()

        users_list = []
        for user in users:
            accounts = [{"id": a.id, "balance": float(a.balance)} for a in user.accounts]
            users_list.append({
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "accounts": accounts
            })

        return response.json({"users": users_list})
