from app import db
from datetime import datetime
import uuid

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    from_account_id = db.Column(db.String(36), db.ForeignKey('accounts.id'), nullable=True, index=True)
    to_account_id = db.Column(db.String(36), db.ForeignKey('accounts.id'), nullable=True, index=True)
    
    # Transaction Details
    transaction_type = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='KZA')
    description = db.Column(db.String(255), nullable=True)
    reference_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # Recipient Details
    recipient_name = db.Column(db.String(120), nullable=True)
    recipient_account = db.Column(db.String(50), nullable=True)
    recipient_bank = db.Column(db.String(100), nullable=True)
    recipient_country = db.Column(db.String(50), nullable=True)
    
    # Status
    status = db.Column(db.String(20), default='pending')
    status_reason = db.Column(db.String(255), nullable=True)
    
    # Fees
    fee = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'transaction_type': self.transaction_type,
            'amount': self.amount,
            'currency': self.currency,
            'description': self.description,
            'reference_number': self.reference_number,
            'recipient_name': self.recipient_name,
            'status': self.status,
            'fee': self.fee,
            'total_amount': self.total_amount,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Transaction {self.reference_number}>'