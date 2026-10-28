import uuid
from datetime import date
from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from ..models import Balances, PaymentTypes, Transactions, Users


class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        payment_type: Optional[str] = None,
        starting_date: Optional[date] = None,
        limit_date: Optional[date] = None,
    ):
        stmt = select(Transactions)

        if email or first_name or last_name:
            stmt = stmt.join(Transactions.balance).join(Balances.user)
            if email:
                stmt = stmt.where(Users.email.ilike(f"%{email}%"))
            if first_name:
                stmt = stmt.where(Users.first_name.ilike(f"%{first_name}%"))
            if last_name:
                stmt = stmt.where(Users.last_name.ilike(f"%{last_name}%"))
        if payment_type:
            stmt = stmt.join(Transactions.payment_type).where(PaymentTypes.type == payment_type)
        if starting_date and limit_date:
            stmt = stmt.where(and_(Transactions.issued_date >= starting_date, Transactions.issued_date <= limit_date))
        elif starting_date:
            stmt = stmt.where(Transactions.issued_date >= starting_date)
        elif limit_date:
            stmt = stmt.where(Transactions.issued_date <= limit_date)

        return stmt

    def get_by_user_id(self, user_id: uuid.UUID):
        return self.db.execute(
            select(Transactions).join(Balances).where(Balances.user_id == user_id)
        ).scalars().all()

    def add(self, transaction: Transactions) -> Transactions:
        self.db.add(transaction)
        self.db.commit()
        return transaction

    def flush(self) -> None:
        self.db.flush()
