from datetime import datetime

from app.models import db


class Payment(db.Model):
    __tablename__ = 'Payments'

    id = db.Column('Id', db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column('UserId', db.BigInteger, db.ForeignKey('Users.Id'), nullable=False)
    course_id = db.Column('CourseId', db.Integer, db.ForeignKey('Courses.Id'), nullable=False)
    amount = db.Column('Amount', db.Numeric(12, 2), nullable=False, default=0)
    va_account_number = db.Column('VaAccountNumber', db.String(64), nullable=False, unique=True)
    bank_code = db.Column('BankCode', db.String(32), nullable=False)
    status = db.Column('Status', db.String(20), nullable=False, default='PENDING')
    transaction_id = db.Column('TransactionId', db.String(128))
    payment_code = db.Column('PaymentCode', db.String(64), unique=True)
    paid_at = db.Column('PaidAt', db.DateTime)
    created_at = db.Column('CreatedAt', db.DateTime, default=datetime.utcnow, nullable=False)
