from app import db
from datetime import datetime
import uuid

class Account(db.Model):
    __tablename__ = 'accounts'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Account Details
    account_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    account_type = db.Column(db.String(20), default='checking')
    currency = db.Column(db.String(3), default='KZA')
    balance = db.Column(db.Float, default=0.0)
    available_balance = db.Column(db.Float, default=0.0)
    
    # Bank Routing
    bank_code = db.Column(db.String(10), nullable=False, default='PAYSYS')
    branch_code = db.Column(db.String(10), nullable=False, default='MAIN')
    swift_code = db.Column(db.String(11), nullable=True)
    iban = db.Column(db.String(34), nullable=True)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_blocked = db.Column(db.Boolean, default=False)
    block_reason = db.Column(db.String(255), nullable=True)
    
    # Limits
    daily_transfer_limit = db.Column(db.Float, default=50000000)
    monthly_transfer_limit = db.Column(db.Float, default=500000000)
    daily_transfer_used = db.Column(db.Float, default=0.0)
    monthly_transfer_used = db.Column(db.Float, default=0.0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transactions_sent = db.relationship(
        'Transaction',
        foreign_keys='Transaction.from_account_id',
        backref='from_account',
        lazy=True
    )
    transactions_received = db.relationship(
        'Transaction',
        foreign_keys='Transaction.to_account_id',
        backref='to_account',
        lazy=True
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'account_number': self.account_number,
            'account_type': self.account_type,
            'currency': self.currency,
            'balance': self.balance,
            'available_balance': self.available_balance,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Account {self.account_number}>'