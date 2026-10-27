from typing import Optional

from app.models.balances import Balances
from sqlalchemy import select
from sqlalchemy.orm import Session

from .users import get_user_by_email_srv
from ..errors import BalanceNotFound


def get_balances_srv(db: Session, min_balance: Optional[float] = None, max_balance: Optional[float] = None) -> list[Balances]:
    stmt = select(Balances)

    if min_balance and max_balance:
        stmt = stmt.where(Balances.balance >= min_balance, Balances.balance <= max_balance)
    elif min_balance:
        stmt = stmt.where(Balances.balance >= min_balance)
    elif max_balance:
        stmt = stmt.where(Balances.balance <= max_balance)

    return db.execute(stmt).unique().scalars().all()


def get_user_balance_by_email_srv(db: Session, email: str) -> Balances:
    user = get_user_by_email_srv(db=db, email=email)
    if not user.balance:
        raise BalanceNotFound
    return user.balance
