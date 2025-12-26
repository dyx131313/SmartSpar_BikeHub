from app import db
from datetime import datetime, timedelta

class VerificationCode(db.Model):
    """Verification Code Model"""
    __tablename__ = 'verification_codes'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, index=True)
    code = db.Column(db.String(6), nullable=False)
    type = db.Column(db.Enum('bind_email', 'reset_password', name='verification_type'), nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    def __init__(self, email, code, type, expires_in_minutes=1):
        self.email = email
        self.code = code
        self.type = type
        self.expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)

    @property
    def is_valid(self):
        return not self.is_used and datetime.utcnow() < self.expires_at

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'type': self.type,
            'is_used': self.is_used,
            'expires_at': self.expires_at.isoformat(),
            'created_at': self.created_at.isoformat()
        }

