from app.models.balances import Balances
from .users import get_user_by_email_srv
from ..errors import BalanceNotFound
from ..extensions import db


def get_balances_srv(min_balance: float | None = None, max_balance: float | None = None) -> list[Balances]:
    stmt = db.select(Balances)

    if min_balance and max_balance:
        stmt = stmt.where(db.and_(Balances.balance >= min_balance, Balances.balance <= max_balance))
    elif min_balance:
        stmt = stmt.where(Balances.balance >= min_balance)
    elif max_balance:
        stmt = stmt.where(Balances.balance <= max_balance)

    return db.session.execute(stmt).unique().scalars().all()


def get_user_balance_by_email_srv(email: str) -> Balances:
    user = get_user_by_email_srv(email=email)
    if not user.balance:
        raise BalanceNotFound
    return user.balance
