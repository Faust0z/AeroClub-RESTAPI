import uuid
from typing import Optional

from app.repositories import BalanceRepository, UserRepository
from app.schemas import BalancesOut, BalancesUpdate
from ..errors import BalanceNotFound, UserNotFound


def get_balances_srv(
    db: Session,
    min_balance: Optional[float] = None,
    max_balance: Optional[float] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[BalancesOut]:
    repo = BalanceRepository(db)
    balances, _total = repo.get_all(
        min_balance=min_balance, max_balance=max_balance, skip=skip, limit=limit
    )
    return [BalancesOut.model_validate(b) for b in balances]


def get_user_balance_by_user_id_srv(db: Session, user_id: uuid.UUID) -> BalancesOut:
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id=user_id)
    if not user:
        raise UserNotFound
    if not user.balance:
        raise BalanceNotFound
    return BalancesOut.model_validate(user.balance)
