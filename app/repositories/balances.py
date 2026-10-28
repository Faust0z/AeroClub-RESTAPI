import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Balances


class BalanceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self,
        min_balance: Optional[float] = None,
        max_balance: Optional[float] = None,
    ):
        stmt = select(Balances)
        if min_balance and max_balance:
            stmt = stmt.where(Balances.balance >= min_balance, Balances.balance <= max_balance)
        elif min_balance:
            stmt = stmt.where(Balances.balance >= min_balance)
        elif max_balance:
            stmt = stmt.where(Balances.balance <= max_balance)
        return stmt

    def get_by_user_id(self, user_id: uuid.UUID) -> Optional[Balances]:
        return self.db.execute(
            select(Balances).where(Balances.user_id == user_id)
        ).scalar_one_or_none()

    def add(self, balance: Balances) -> Balances:
        self.db.add(balance)
        self.db.commit()
        return balance

    def update(self, balance: Balances) -> Balances:
        self.db.commit()
        return balance

    def delete(self, balance: Balances) -> None:
        self.db.delete(balance)
        self.db.commit()
