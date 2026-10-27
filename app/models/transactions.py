from datetime import date

from app.models import FlightSessions
from sqlalchemy import Column, Date, ForeignKey, Integer, Numeric, Text
from sqlalchemy.orm import Mapped, relationship

from ..database import Base


class Transactions(Base):
    __tablename__ = 'transactions'
    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    amount: Mapped[float] = Column(Numeric(10, 2), nullable=False)
    issued_date: Mapped[date] = Column(Date, nullable=False)
    description: Mapped[str] = Column(Text, nullable=True)
    payment_type_id = Column(ForeignKey('payment_types.id'))
    balance_id = Column(ForeignKey('balances.id'))

    balance: Mapped["Balances"] = relationship(back_populates="transactions")
    flight_sessions: Mapped["FlightSessions"] = relationship(back_populates="transactions")
    payment_type: Mapped["PaymentTypes"] = relationship(back_populates="transactions")

    def __repr__(self):
        return f"<Transaction amount={self.amount} issued_date={self.issued_date}>"
