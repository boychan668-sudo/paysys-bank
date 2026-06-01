from app import db
from datetime import datetime
import uuid

class GameSession(db.Model):
    __tablename__ = 'game_sessions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Game Details
    even_number = db.Column(db.Integer, nullable=False)
    multiplier = db.Column(db.Float, default=1000000)
    bet_amount = db.Column(db.Float, nullable=False)
    potential_winnings = db.Column(db.Float, nullable=False)
    
    # Result
    is_won = db.Column(db.Boolean, default=False)
    actual_winnings = db.Column(db.Float, default=0.0)
    
    # Status
    status = db.Column(db.String(20), default='pending')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'even_number': self.even_number,
            'bet_amount': self.bet_amount,
            'potential_winnings': self.potential_winnings,
            'is_won': self.is_won,
            'actual_winnings': self.actual_winnings,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<GameSession {self.id}>'