import asyncio

from app.auth import hash_password
from app.db import engine, Base, AsyncSessionLocal
from app.models import User, Account


async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # создаём тестового пользователя, счёт и админа, если ещё нет
        from sqlalchemy.future import select
        q = await session.execute(select(User).where(User.email == "user@example.com"))
        if not q.scalars().first():
            u = User(email="user@example.com", password_hash=hash_password("userpass"), full_name="Test User", is_admin=False)
            session.add(u)
            await session.flush()
            a = Account(user_id=u.id, balance=0)
            session.add(a)
        q2 = await session.execute(select(User).where(User.email == "admin@example.com"))
        if not q2.scalars().first():
            admin = User(email="admin@example.com", password_hash=hash_password("adminpass"), full_name="Admin User", is_admin=True)
            session.add(admin)
        await session.commit()

if __name__ == "__main__":
    asyncio.run(init())
