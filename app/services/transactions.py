import uuid
from datetime import date
from typing import Optional

from app.models import Transactions
from app.repositories import TransactionRepository, UserRepository, BalanceRepository
from app.schemas import TransactionsAdminOut, TransactionsCreate, TransactionsPublicOut
from ..errors import UserNotFound


def get_transactions_srv(
    db: Session,
    email: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    payment_type: Optional[str] = None,
    starting_date: Optional[date] = None,
    limit_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[TransactionsAdminOut]:
    repo = TransactionRepository(db)
    transactions, _total = repo.get_all(
        email=email,
        first_name=first_name,
        last_name=last_name,
        payment_type=payment_type,
        starting_date=starting_date,
        limit_date=limit_date,
        skip=skip,
        limit=limit,
    )
    return [TransactionsAdminOut.model_validate(t) for t in transactions]


def get_user_trans_by_user_id_srv(db: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> list[TransactionsPublicOut]:
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id=user_id)
    if not user:
        raise UserNotFound
    return [TransactionsPublicOut.model_validate(t) for t in user.balance.transactions]


def sum_user_transaction_srv(db: Session, user_id: uuid.UUID, data: dict) -> TransactionsPublicOut:
    from app.models import Transactions

    repo = TransactionRepository(db)
    balance_repo = BalanceRepository(db)
    balance = balance_repo.get_by_user_id(user_id=user_id)
    if not balance:
        raise UserNotFound

    transaction = Transactions(**data)
    transaction.balance = balance
    balance.balance += transaction.amount

    repo.add(transaction)
    return TransactionsPublicOut.model_validate(transaction)


def sub_user_transaction_srv(db: Session, user_id: uuid.UUID, transaction: Transactions) -> TransactionsPublicOut:
    repo = TransactionRepository(db)
    balance_repo = BalanceRepository(db)
    balance = balance_repo.get_by_user_id(user_id=user_id)
    if not balance:
        raise UserNotFound

    transaction.balance = balance
    balance.balance -= transaction.amount

    repo.flush()
    return TransactionsPublicOut.model_validate(transaction)
