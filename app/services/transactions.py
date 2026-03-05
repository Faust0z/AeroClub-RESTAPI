from datetime import date
from typing import Optional

from .balances import get_user_balance_by_email_srv
from .users import get_user_by_email_srv
from ..extensions import db
from ..models import Balances, PaymentTypes, Transactions, Users


def get_transactions_srv(email: Optional[str] = None, first_name: Optional[str] = None, last_name: Optional[str] = None,
                         payment_type: Optional[str] = None, starting_date: Optional[date] = None, limit_date: Optional[date] = None) -> \
        list[Transactions]:
    stmt = db.select(Transactions)

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
        stmt = stmt.where(db.and_(Transactions.issued_date >= starting_date, Transactions.issued_date <= limit_date))
    elif starting_date:
        stmt = stmt.where(Transactions.issued_date >= starting_date)
    elif limit_date:
        stmt = stmt.where(Transactions.issued_date <= limit_date)

    return db.session.execute(stmt).unique().scalars().all()


def get_user_trans_by_email_srv(email: str) -> list[Transactions]:
    user = get_user_by_email_srv(email=email)
    return user.balance.transactions


def sum_user_transaction_srv(email: str, transaction: Transactions) -> Transactions:
    """
    These kind of transactions are only to add money to the user's balance
    :param email: user's email
    :param transaction: the transaction to sum
    :return: the transaction with the payment type and user's balance attached
    """
    balance = get_user_balance_by_email_srv(email=email)
    transaction.balance = balance
    balance.balance += transaction.amount

    db.session.add(transaction)
    db.session.commit()

    return transaction


def sub_user_transaction_srv(email: str, transaction: Transactions) -> Transactions:
    """
    These kind of transactions are only to subtract to the user's balance. Called by new flight sessions being created and
    *flushes* instead of commiting to avoid session issues
    :param email: user's email
    :param transaction: the user's transaction
    :return: the transaction with the payment type and user's balance attached
    """
    balance = get_user_balance_by_email_srv(email=email)
    transaction.balance = balance
    balance.balance -= transaction.amount

    db.session.add(transaction)
    db.session.flush()

    return transaction
