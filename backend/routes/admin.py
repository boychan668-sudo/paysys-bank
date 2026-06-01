from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models.user import User
from models.account import Account
from models.transaction import Transaction
from models.game import GameSession

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/stats/overview', methods=['GET'])
@jwt_required()
def get_overview_stats():
    """
    Get system overview statistics
    """
    total_users = User.query.count()
    total_accounts = Account.query.count()
    total_transactions = Transaction.query.count()
    total_game_sessions = GameSession.query.count()
    
    total_balance = db.session.query(db.func.sum(Account.balance)).scalar() or 0
    total_gaming_winnings = db.session.query(
        db.func.sum(GameSession.actual_winnings)
    ).filter_by(is_won=True).scalar() or 0
    
    return jsonify({
        'total_users': total_users,
        'total_accounts': total_accounts,
        'total_transactions': total_transactions,
        'total_game_sessions': total_game_sessions,
        'total_balance_in_system': total_balance,
        'total_gaming_winnings': total_gaming_winnings
    }), 200

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def list_users():
    """
    List all users
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    users = User.query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'users': [u.to_dict() for u in users.items],
        'total': users.total,
        'pages': users.pages
    }), 200

@admin_bp.route('/transactions', methods=['GET'])
@jwt_required()
def list_transactions():
    """
    List all transactions
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    transactions = Transaction.query.order_by(
        Transaction.created_at.desc()
    ).paginate(page=page, per_page=per_page)
    
    return jsonify({
        'transactions': [t.to_dict() for t in transactions.items],
        'total': transactions.total,
        'pages': transactions.pages
    }), 200