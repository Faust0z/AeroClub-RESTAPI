import uuid
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination import Page, paginate
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_admin, require_active_user
from app.database import get_db
from app.errors import BalanceNotFound, UserNotFound
from app.models import Users
from app.schemas import BalancesOut, BalancesUpdate, Page
from app.services.balances import get_balances_srv, get_user_balance_by_user_id_srv

router = APIRouter(prefix="/v1/balances", tags=["balances"])


@router.get("/", response_model=Page[BalancesOut])
def list_balances(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_admin)],
    min_balance: Optional[float] = Query(None),
    max_balance: Optional[float] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    balances, total = get_balances_srv(db=db, min_balance=min_balance, max_balance=max_balance, skip=skip, limit=limit)
    return Page[BalancesOut](items=balances, total=total, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=BalancesOut)
def get_user_balance(
    user_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_admin)],
):
    try:
        balance = get_user_balance_by_user_id_srv(db=db, user_id=user_id)
    except UserNotFound:
        raise HTTPException(status_code=404, detail="User not found")
    except BalanceNotFound:
        raise HTTPException(status_code=404, detail="Balance not found for this user")
    return balance


@router.get("/me", response_model=BalancesOut)
def get_my_balance(
    current_user: Annotated[Users, Depends(require_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    try:
        balance = get_user_balance_by_user_id_srv(db=db, user_id=current_user.uuid)
    except BalanceNotFound:
        raise HTTPException(status_code=404, detail="Balance not found for this user")
    return balance
