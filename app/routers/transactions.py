import uuid
from datetime import date
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination import Page, paginate
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_admin, require_active_user
from app.database import get_db
from app.errors import UserNotFound
from app.models import Users
from app.schemas import TransactionsAdminOut, TransactionsCreate, TransactionsPublicOut, Page
from app.services.transactions import (
    get_transactions_srv,
    get_user_trans_by_user_id_srv,
    sum_user_transaction_srv,
)

router = APIRouter(prefix="/v1/transactions", tags=["transactions"])


@router.get("/", response_model=Page[TransactionsAdminOut])
def list_transactions(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_admin)],
    email: Optional[str] = Query(None),
    first_name: Optional[str] = Query(None),
    last_name: Optional[str] = Query(None),
    payment_type: Optional[str] = Query(None),
    starting_date: Optional[date] = Query(None),
    limit_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    transactions, total = get_transactions_srv(
        db=db,
        email=email,
        first_name=first_name,
        last_name=last_name,
        payment_type=payment_type,
        starting_date=starting_date,
        limit_date=limit_date,
        skip=skip,
        limit=limit,
    )
    return Page[TransactionsAdminOut](items=transactions, total=total, skip=skip, limit=limit)


@router.get("/me", response_model=List[TransactionsPublicOut])
def get_my_transactions(
    current_user: Annotated[Users, Depends(require_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    transactions = get_user_trans_by_user_id_srv(db=db, user_id=current_user.uuid)
    return transactions


@router.get("/{user_id}", response_model=Page[TransactionsAdminOut])
def get_user_transactions(
    user_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_admin)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    try:
        transactions, total = get_user_trans_by_user_id_srv(db=db, user_id=user_id, skip=skip, limit=limit)
    except UserNotFound:
        raise HTTPException(status_code=404, detail="User not found")
    return Page[TransactionsAdminOut](items=transactions, total=total, skip=skip, limit=limit)


@router.post("/", response_model=TransactionsPublicOut, status_code=status.HTTP_201_CREATED)
def create_user_transaction(
    transaction_data: TransactionsCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_admin)],
):
    try:
        transaction = sum_user_transaction_srv(
            db=db, user_id=transaction_data.user_id, data=transaction_data.model_dump(exclude={"user_id"})
        )
    except UserNotFound:
        raise HTTPException(status_code=404, detail="User not found")
    return transaction
