from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models.user import User
from models.account import Account
from models.game import GameSession
from models.transaction import Transaction
from datetime import datetime
import random
import uuid

game_bp = Blueprint('game', __name__)

MULTIPLIER = 1000000

@game_bp.route('/play', methods=['POST'])
@jwt_required()
def play_game():
    """
    Play the number game
    Even number (2, 4, 6...) x 1,000,000 KZA = potential winnings
    50% chance to win
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data.get('account_id') or not data.get('even_number') or not data.get('bet_amount'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    even_number = int(data['even_number'])
    bet_amount = float(data['bet_amount'])
    account_id = data['account_id']
    
    if even_number % 2 != 0 or even_number < 2:
        return jsonify({'error': 'Number must be even and >= 2'}), 400
    
    account = Account.query.filter_by(id=account_id, user_id=current_user_id).first()
    if not account:
        return jsonify({'error': 'Account not found'}), 404
    
    if not account.is_active:
        return jsonify({'error': 'Account is inactive'}), 403
    
    if account.balance < bet_amount:
        return jsonify({'error': 'Insufficient balance'}), 400
    
    potential_winnings = bet_amount * (even_number * MULTIPLIER)
    
    account.balance -= bet_amount
    account.available_balance = account.balance
    
    game_session = GameSession(
        user_id=current_user_id,
        even_number=even_number,
        multiplier=MULTIPLIER,
        bet_amount=bet_amount,
        potential_winnings=potential_winnings
    )
    
    is_won = random.random() < 0.5
    game_session.is_won = is_won
    
    if is_won:
        game_session.status = 'won'
        game_session.actual_winnings = potential_winnings
        
        account.balance += potential_winnings
        account.available_balance = account.balance
        
        transaction = Transaction(
            user_id=current_user_id,
            from_account_id=None,
            to_account_id=account_id,
            transaction_type='game_win',
            amount=potential_winnings,
            currency=account.currency,
            description=f'Game Win - {even_number}x Multiplier',
            reference_number=f"GAME{uuid.uuid4().hex[:10].upper()}",
            status='completed',
            fee=0,
            total_amount=potential_winnings,
            completed_at=datetime.utcnow()
        )
        db.session.add(transaction)
    else:
        game_session.status = 'lost'
        
        transaction = Transaction(
            user_id=current_user_id,
            from_account_id=account_id,
            to_account_id=None,
            transaction_type='game_loss',
            amount=bet_amount,
            currency=account.currency,
            description=f'Game Loss - Number {even_number}',
            reference_number=f"GAME{uuid.uuid4().hex[:10].upper()}",
            status='completed',
            fee=0,
            total_amount=bet_amount,
            completed_at=datetime.utcnow()
        )
        db.session.add(transaction)
    
    game_session.completed_at = datetime.utcnow()
    
    db.session.add(game_session)
    db.session.commit()
    
    return jsonify({
        'message': 'Game completed',
        'game_session': game_session.to_dict(),
        'result': 'WON' if is_won else 'LOST',
        'account_balance': account.balance
    }), 200

@game_bp.route('/sessions', methods=['GET'])
@jwt_required()
def get_game_sessions():
    """
    Get all game sessions for current user
    """
    current_user_id = get_jwt_identity()
    sessions = GameSession.query.filter_by(user_id=current_user_id).order_by(
        GameSession.created_at.desc()
    ).all()
    
    return jsonify({
        'sessions': [session.to_dict() for session in sessions]
    }), 200

@game_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_game_stats():
    """
    Get game statistics for current user
    """
    current_user_id = get_jwt_identity()
    sessions = GameSession.query.filter_by(user_id=current_user_id).all()
    
    total_games = len(sessions)
    total_wins = len([s for s in sessions if s.is_won])
    total_losses = total_games - total_wins
    total_winnings = sum([s.actual_winnings for s in sessions if s.is_won])
    total_bets = sum([s.bet_amount for s in sessions])
    
    win_rate = (total_wins / total_games * 100) if total_games > 0 else 0
    
    return jsonify({
        'total_games': total_games,
        'total_wins': total_wins,
        'total_losses': total_losses,
        'win_rate': f"{win_rate:.2f}%",
        'total_winnings': total_winnings,
        'total_bets': total_bets,
        'net_profit': total_winnings - total_bets
    }), 200