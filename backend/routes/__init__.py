from routes.auth import auth_bp
from routes.users import users_bp
from routes.accounts import accounts_bp
from routes.transactions import transactions_bp
from routes.game import game_bp
from routes.payments import payments_bp
from routes.qrcode import qrcode_bp
from routes.admin import admin_bp

__all__ = [
    'auth_bp', 'users_bp', 'accounts_bp', 'transactions_bp',
    'game_bp', 'payments_bp', 'qrcode_bp', 'admin_bp'
]