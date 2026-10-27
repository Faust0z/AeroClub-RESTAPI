from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_admin, require_active_user
from app.database import get_db
from app.errors import BalanceNotFound, UserNotFound
from app.models import Users
from app.schemas import BalancesOut, BalancesUpdate
from app.services.balances import get_balances_srv, get_user_balance_by_email_srv

router = APIRouter(prefix="/v1/balances", tags=["balances"])


@router.get("/", response_model=List[BalancesOut])
def list_balances(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[BalancesOut, Depends(require_admin)],
    min_balance: Optional[float] = Query(None),
    max_balance: Optional[float] = Query(None),
):
    balances = get_balances_srv(db=db, min_balance=min_balance, max_balance=max_balance)
    return balances


@router.get("/{email}", response_model=BalancesOut)
def get_user_balance(
    email: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_admin)],
):
    try:
        balance = get_user_balance_by_email_srv(db=db, email=email)
    except UserNotFound:
        raise HTTPException(status_code=404, detail="No user found with the given email")
    except BalanceNotFound:
        raise HTTPException(status_code=404, detail="Balance not found for this user")
    return balance


@router.get("/me", response_model=BalancesOut)
def get_my_balance(
    current_user: Annotated[Users, Depends(require_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    try:
        balance = get_user_balance_by_email_srv(db=db, email=current_user.email)
    except BalanceNotFound:
        raise HTTPException(status_code=404, detail="Balance not found for this user")
    return balance
