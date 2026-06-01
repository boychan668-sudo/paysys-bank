from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models.user import User
from models.account import Account
import uuid

accounts_bp = Blueprint('accounts', __name__)

@accounts_bp.route('/', methods=['POST'])
@jwt_required()
def create_account():
    """
    Create a new bank account
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    account_number = f"ACC{uuid.uuid4().hex[:12].upper()}"
    
    account = Account(
        user_id=current_user_id,
        account_number=account_number,
        account_type=data.get('account_type', 'checking'),
        currency=data.get('currency', 'KZA'),
        balance=data.get('initial_balance', 0.0)
    )
    
    db.session.add(account)
    db.session.commit()
    
    return jsonify({
        'message': 'Account created successfully',
        'account': account.to_dict()
    }), 201

@accounts_bp.route('/', methods=['GET'])
@jwt_required()
def get_accounts():
    """
    Get all accounts for current user
    """
    current_user_id = get_jwt_identity()
    accounts = Account.query.filter_by(user_id=current_user_id).all()
    
    return jsonify({
        'accounts': [acc.to_dict() for acc in accounts]
    }), 200

@accounts_bp.route('/<account_id>', methods=['GET'])
@jwt_required()
def get_account(account_id):
    """
    Get specific account
    """
    current_user_id = get_jwt_identity()
    account = Account.query.filter_by(id=account_id, user_id=current_user_id).first()
    
    if not account:
        return jsonify({'error': 'Account not found'}), 404
    
    return jsonify(account.to_dict()), 200

@accounts_bp.route('/<account_id>/balance', methods=['GET'])
@jwt_required()
def get_balance(account_id):
    """
    Get account balance
    """
    current_user_id = get_jwt_identity()
    account = Account.query.filter_by(id=account_id, user_id=current_user_id).first()
    
    if not account:
        return jsonify({'error': 'Account not found'}), 404
    
    return jsonify({
        'account_number': account.account_number,
        'balance': account.balance,
        'available_balance': account.available_balance,
        'currency': account.currency
    }), 200