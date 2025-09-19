from sanic import Sanic
from app.routes.auth_routes import bp as auth_bp
from app.routes.user_routes import bp as user_bp
from app.routes.admin_routes import bp as admin_bp
from app.routes.webhook_routes import bp as webhook_bp
from app.config import INIT_DB
import asyncio
from app.init_db import init as init_db

app = Sanic("payment_service")
app.blueprint(auth_bp)
app.blueprint(user_bp)
app.blueprint(admin_bp)
app.blueprint(webhook_bp)

if __name__ == "__main__":
    if INIT_DB == "1":
        asyncio.run(init_db())
    app.run(host="0.0.0.0", port=8000, access_log=True)
