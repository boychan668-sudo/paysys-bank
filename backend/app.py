from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
import logging
import os
from datetime import datetime

from config import config

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

def create_app(config_name='development'):
    """
    Application factory pattern
    """
    app = Flask(__name__)
    
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    from routes.auth import auth_bp
    from routes.users import users_bp
    from routes.accounts import accounts_bp
    from routes.transactions import transactions_bp
    from routes.game import game_bp
    from routes.payments import payments_bp
    from routes.qrcode import qrcode_bp
    from routes.admin import admin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(users_bp, url_prefix='/api/v1/users')
    app.register_blueprint(accounts_bp, url_prefix='/api/v1/accounts')
    app.register_blueprint(transactions_bp, url_prefix='/api/v1/transactions')
    app.register_blueprint(game_bp, url_prefix='/api/v1/game')
    app.register_blueprint(payments_bp, url_prefix='/api/v1/payments')
    app.register_blueprint(qrcode_bp, url_prefix='/api/v1/qrcode')
    app.register_blueprint(admin_bp, url_prefix='/api/v1/admin')
    
    setup_logging(app)
    register_error_handlers(app)
    
    with app.app_context():
        db.create_all()
    
    return app

def setup_logging(app):
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    handler = logging.FileHandler('logs/payment_system.log')
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

def register_error_handlers(app):
    
    @app.errorhandler(400)
    def bad_request(error):
        return {'error': 'Bad Request', 'message': str(error)}, 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return {'error': 'Unauthorized', 'message': 'Authentication required'}, 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return {'error': 'Forbidden', 'message': 'Access denied'}, 403
    
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not Found', 'message': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Internal Server Error', 'message': 'Something went wrong'}, 500

if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    app.run(host='0.0.0.0', port=5000, debug=True)