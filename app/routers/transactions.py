from datetime import date
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_admin, require_active_user
from app.database import get_db
from app.errors import UserNotFound
from app.models import Users
from app.schemas import TransactionsAdminOut, TransactionsCreate, TransactionsPublicOut
from app.services.transactions import (
    get_transactions_srv,
    get_user_trans_by_email_srv,
    sum_user_transaction_srv,
)

router = APIRouter(prefix="/v1/transactions", tags=["transactions"])


@router.get("/", response_model=List[TransactionsAdminOut])
def list_transactions(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[TransactionsAdminOut, Depends(require_admin)],
    email: Optional[str] = Query(None),
    first_name: Optional[str] = Query(None),
    last_name: Optional[str] = Query(None),
    payment_type: Optional[str] = Query(None),
    starting_date: Optional[date] = Query(None),
    limit_date: Optional[date] = Query(None),
):
    transactions = get_transactions_srv(
        db=db,
        email=email,
        first_name=first_name,
        last_name=last_name,
        payment_type=payment_type,
        starting_date=starting_date,
        limit_date=limit_date,
    )
    return transactions


@router.get("/me", response_model=List[TransactionsPublicOut])
def get_my_transactions(
    current_user: Annotated[Users, Depends(require_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    transactions = get_user_trans_by_email_srv(db=db, email=current_user.email)
    return transactions


@router.get("/{email}", response_model=List[TransactionsAdminOut])
def get_user_transactions(
    email: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_admin)],
):
    try:
        transactions = get_user_trans_by_email_srv(db=db, email=email)
    except UserNotFound:
        raise HTTPException(status_code=404, detail="No user found with the given email")
    return transactions


@router.post("/{email}", response_model=TransactionsPublicOut, status_code=status.HTTP_201_CREATED)
def create_user_transaction(
    email: str,
    transaction_data: TransactionsCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_admin)],
):
    try:
        transaction = sum_user_transaction_srv(
            db=db, email=email, data=transaction_data.model_dump()
        )
    except UserNotFound:
        raise HTTPException(status_code=404, detail="No user found with the given email")
    return transaction
