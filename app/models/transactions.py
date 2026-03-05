from datetime import date

from app.models import FlightSessions
from ..extensions import db


class Transactions(db.Model):
    __tablename__ = 'transactions'
    id: db.Mapped[int] = db.Column(db.Integer, primary_key=True, autoincrement=True)
    amount: db.Mapped[float] = db.Column(db.Numeric(10, 2), nullable=False)
    issued_date: db.Mapped[date] = db.Column(db.Date, nullable=False)
    description: db.Mapped[str] = db.Column(db.Text, nullable=True)
    payment_type_id = db.Column(db.ForeignKey('payment_types.id'))
    balance_id = db.Column(db.ForeignKey('balances.id'))

    balance: db.Mapped["Balances"] = db.relationship(back_populates="transactions")
    flight_sessions: db.Mapped["FlightSessions"] = db.relationship(back_populates="transactions")
    payment_type: db.Mapped["PaymentTypes"] = db.relationship(back_populates="transactions")

    def __repr__(self):
        return f"<Transaction amount={self.amount} issued_date={self.issued_date}>"
