from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models.account import Account
from models.transaction import Transaction
from datetime import datetime
import uuid

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/request', methods=['POST'])
@jwt_required()
def request_payment():
    """
    Request payment via QR code
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data.get('account_id') or not data.get('amount') or not data.get('description'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    account = Account.query.filter_by(id=data['account_id'], user_id=current_user_id).first()
    if not account:
        return jsonify({'error': 'Account not found'}), 404
    
    payment_request = {
        'id': f"PREQ{uuid.uuid4().hex[:10].upper()}",
        'account_number': account.account_number,
        'amount': float(data['amount']),
        'currency': account.currency,
        'description': data['description'],
        'qr_data': f"payment://{account.account_number}/{data['amount']}/PREQ{uuid.uuid4().hex[:10].upper()}",
        'expires_at': datetime.utcnow().isoformat()
    }
    
    return jsonify(payment_request), 201

@payments_bp.route('/confirm', methods=['POST'])
@jwt_required()
def confirm_payment():
    """
    Confirm payment via QR code
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data.get('from_account_id') or not data.get('to_account_number') or not data.get('amount'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    from_account = Account.query.filter_by(id=data['from_account_id'], user_id=current_user_id).first()
    if not from_account:
        return jsonify({'error': 'Source account not found'}), 404
    
    to_account = Account.query.filter_by(account_number=data['to_account_number']).first()
    if not to_account:
        return jsonify({'error': 'Recipient account not found'}), 404
    
    amount = float(data['amount'])
    
    if from_account.balance < amount:
        return jsonify({'error': 'Insufficient balance'}), 400
    
    from_account.balance -= amount
    to_account.balance += amount
    
    transaction = Transaction(
        user_id=current_user_id,
        from_account_id=data['from_account_id'],
        to_account_id=to_account.id,
        transaction_type='payment',
        amount=amount,
        currency=from_account.currency,
        description=data.get('description', 'QR Payment'),
        reference_number=f"QR{uuid.uuid4().hex[:10].upper()}",
        status='completed',
        fee=0,
        total_amount=amount,
        completed_at=datetime.utcnow()
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify({
        'message': 'Payment confirmed successfully',
        'transaction': transaction.to_dict()
    }), 200