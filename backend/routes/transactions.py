from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models.account import Account
from models.transaction import Transaction
from datetime import datetime
import uuid

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('/transfer', methods=['POST'])
@jwt_required()
def transfer():
    """
    Transfer money between accounts
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    required_fields = ['from_account_id', 'to_account_number', 'amount', 'recipient_name']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    amount = float(data['amount'])
    from_account_id = data['from_account_id']
    
    from_account = Account.query.filter_by(id=from_account_id, user_id=current_user_id).first()
    if not from_account:
        return jsonify({'error': 'Source account not found'}), 404
    
    if not from_account.is_active:
        return jsonify({'error': 'Source account is inactive'}), 403
    
    if from_account.balance < amount:
        return jsonify({'error': 'Insufficient balance'}), 400
    
    to_account = Account.query.filter_by(account_number=data['to_account_number']).first()
    
    fee = calculate_transfer_fee(amount)
    total_amount = amount + fee
    
    if from_account.balance < total_amount:
        return jsonify({'error': 'Insufficient balance (including fees)'}), 400
    
    from_account.balance -= total_amount
    
    if to_account:
        to_account.balance += amount
    
    transaction = Transaction(
        user_id=current_user_id,
        from_account_id=from_account_id,
        to_account_id=to_account.id if to_account else None,
        transaction_type='transfer',
        amount=amount,
        currency=from_account.currency,
        description=data.get('description', 'Transfer'),
        reference_number=f"TRF{uuid.uuid4().hex[:10].upper()}",
        recipient_name=data['recipient_name'],
        recipient_account=data['to_account_number'],
        recipient_bank=data.get('recipient_bank', 'External Bank'),
        status='completed',
        fee=fee,
        total_amount=total_amount,
        completed_at=datetime.utcnow()
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify({
        'message': 'Transfer completed successfully',
        'transaction': transaction.to_dict(),
        'remaining_balance': from_account.balance
    }), 200

@transactions_bp.route('/history/<account_id>', methods=['GET'])
@jwt_required()
def get_transaction_history(account_id):
    """
    Get transaction history for an account
    """
    current_user_id = get_jwt_identity()
    
    account = Account.query.filter_by(id=account_id, user_id=current_user_id).first()
    if not account:
        return jsonify({'error': 'Account not found'}), 404
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    transactions = Transaction.query.filter(
        (Transaction.from_account_id == account_id) | (Transaction.to_account_id == account_id)
    ).order_by(Transaction.created_at.desc()).paginate(page=page, per_page=per_page)
    
    return jsonify({
        'transactions': [t.to_dict() for t in transactions.items],
        'total': transactions.total,
        'pages': transactions.pages,
        'current_page': page
    }), 200

def calculate_transfer_fee(amount):
    """
    Calculate transfer fee based on amount
    """
    if amount < 1000000:
        return amount * 0.005
    elif amount < 10000000:
        return amount * 0.003
    else:
        return amount * 0.001