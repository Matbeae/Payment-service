from sanic import Blueprint, response
from sanic.request import Request
from app.config import WEBHOOK_SECRET
from hashlib import sha256
from sqlalchemy.future import select
from app.db import AsyncSessionLocal
from app.models import User, Account, Transaction
from decimal import Decimal

bp = Blueprint("webhook", url_prefix="/webhook")

def make_signature(payload: dict, secret: str):
    # порядок по алфавиту ключей: account_id, amount, transaction_id, user_id, secret_key
    s = f"{payload['account_id']}{payload['amount']}{payload['transaction_id']}{payload['user_id']}{secret}"
    return sha256(s.encode('utf-8')).hexdigest()

@bp.post("/payment")
async def payment_hook(request: Request):
    data = request.json or {}
    required = {"transaction_id", "account_id", "user_id", "amount", "signature"}
    if not required.issubset(data.keys()):
        return response.json({"error": "bad_request"}, status=400)

    expected_sig = make_signature(data, WEBHOOK_SECRET)
    if expected_sig != data["signature"]:
        return response.json({"error": "bad_signature"}, status=400)

    txid = data["transaction_id"]
    uid = int(data["user_id"])
    aid = int(data["account_id"])
    amount = Decimal(str(data["amount"]))

    async with AsyncSessionLocal() as session:
        # Проверяем, не существует ли уже транзакция с таким transaction_id
        qtx = await session.execute(select(Transaction).where(Transaction.transaction_id == txid))
        existing = qtx.scalars().first()
        if existing:
            return response.json({"status": "already_processed"}, status=200)

        # Убедимся, что пользователь существует
        qu = await session.execute(select(User).where(User.id == uid))
        user = qu.scalars().first()
        if not user:
            return response.json({"error": "user_not_found"}, status=404)

        # Проверим, существует ли счет — если нет, создаём
        qacc = await session.execute(select(Account).where(Account.id == aid))
        account = qacc.scalars().first()
        if not account:
            account = Account(id=aid, user_id=uid, balance=0)
            session.add(account)
            await session.flush()  # чтобы получить id (если авто)
        # Создаём транзакцию и начисляем баланс
        tx = Transaction(transaction_id=txid, user_id=uid, account_id=account.id, amount=amount)
        session.add(tx)
        # увеличиваем баланс
        account.balance = account.balance + amount
        await session.commit()
        return response.json({"status": "ok"})
