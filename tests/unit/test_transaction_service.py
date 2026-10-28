"""Unit tests for transactions service with mocked repository."""

from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4

import pytest

from app.models import Transactions, Balances, Users
from app.repositories import TransactionRepository, BalanceRepository, UserRepository
from app.services.transactions import (
    get_transactions_srv,
    get_user_trans_by_user_id_srv,
    sum_user_transaction_srv,
    sub_user_transaction_srv,
)
from app.errors import UserNotFound


def _make_user(user_id: UUID = None) -> Users:
    return Users(
        uuid=user_id or uuid4(),
        email="test@example.com",
        first_name="Test",
        last_name="User",
        phone_number="+1234567890",
        password="hashed",
        created_at=date.today(),
        status=True,
    )


def _make_balance(user_id: UUID = None, amount: Decimal = Decimal("100.00")) -> Balances:
    return Balances(
        id=user_id or uuid4(),
        user_id=user_id or uuid4(),
        balance=amount,
    )


def _make_transaction(transaction_id: UUID = None, amount: Decimal = Decimal("50.00")) -> Transactions:
    return Transactions(
        id=transaction_id or uuid4(),
        amount=amount,
        issued_date=date.today(),
        description="Test transaction",
        payment_type_id=uuid4(),
        balance_id=uuid4(),
    )


class TestGetTransactionsSrv:
    def test_list(self):
        db = MagicMock()
        transactions = [_make_transaction(UUID("11111111-1111-1111-1111-111111111111")), _make_transaction(UUID("22222222-2222-2222-2222-222222222222"))]
        with patch.object(TransactionRepository, "get_all", return_value=(transactions, 2)):
            result = get_transactions_srv(db=db)
        assert len(result) == 2
        assert result[0].amount == Decimal("50.00")


class TestGetUserTransByUserIdSrv:
    def test_found(self):
        db = MagicMock()
        user = _make_user()
        balance = _make_balance(user_id=user.uuid, amount=Decimal("100.00"))
        transactions = [_make_transaction(UUID("11111111-1111-1111-1111-111111111111")), _make_transaction(UUID("22222222-2222-2222-2222-222222222222"))]
        user.balance = balance
        balance.transactions = transactions
        with patch.object(UserRepository, "get_by_id", return_value=user):
            result = get_user_trans_by_user_id_srv(db=db, user_id=user.uuid)
        assert len(result) == 2


class TestSumUserTransactionSrv:
    def test_add(self):
        db = MagicMock()
        user = _make_user()
        balance = _make_balance(user_id=user.uuid, amount=Decimal("100.00"))
        transaction_data = {
            "amount": Decimal("50.00"),
            "issued_date": date.today(),
            "description": "Test deposit",
            "payment_type_id": 1,
            "balance_id": balance.id,
        }
        created_txn = _make_transaction(UUID("11111111-1111-1111-1111-111111111111"), Decimal("50.00"))
        with patch.object(UserRepository, "get_by_id", return_value=user):
            with patch.object(BalanceRepository, "get_by_user_id", return_value=balance):
                with patch.object(TransactionRepository, "add", return_value=created_txn):
                    result = sum_user_transaction_srv(db=db, user_id=user.uuid, data=transaction_data)
        assert result.amount == Decimal("50.00")
        assert balance.balance == Decimal("150.00")
