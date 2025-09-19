from sanic import Blueprint, response
from sanic.request import Request
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.auth import decode_access_token
from app.db import AsyncSessionLocal
from app.models import User

bp = Blueprint("user", url_prefix="/user")

async def get_current_user(request: Request):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth.split(" ", 1)[1]
    user_id = decode_access_token(token)
    if not user_id:
        return None
    async with AsyncSessionLocal() as session:
        q = await session.execute(select(User).where(User.id == user_id))
        return q.scalars().first()

@bp.get("/me")
async def me(request: Request):
    user = await get_current_user(request)
    if not user:
        return response.json({"error": "unauthorized"}, status=401)
    return response.json({"id": user.id, "email": user.email, "full_name": user.full_name})

@bp.get("/accounts")
async def accounts(request: Request):
    user = await get_current_user(request)
    if not user:
        return response.json({"error": "unauthorized"}, status=401)

    # Загрузка аккаунтов вместе с пользователем
    async with AsyncSessionLocal() as session:
        q = await session.execute(select(User).options(joinedload(User.accounts)).where(User.id == user.id))
        user_with_accounts = q.scalars().first()

        if not user_with_accounts:
            return response.json({"error": "user_not_found"}, status=404)

        accounts = [{"id": a.id, "balance": float(a.balance)} for a in user_with_accounts.accounts]
        return response.json({"accounts": accounts})

@bp.get("/payments")
async def payments(request: Request):
    user = await get_current_user(request)
    if not user:
        return response.json({"error": "unauthorized"}, status=401)
    # можно возвращать страницы/фильтры
    payments = []
    for t in user.transactions:
        payments.append({
            "transaction_id": t.transaction_id,
            "account_id": t.account_id,
            "amount": float(t.amount),
            "created_at": t.created_at.isoformat()
        })
    return response.json({"payments": payments})
