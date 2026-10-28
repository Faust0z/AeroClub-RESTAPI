from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_admin, require_active_user
from app.database import get_db
from app.errors import PaymentTypeAlreadyExists, PaymentTypeNotFound
from app.models import Users
from app.schemas import PaymentTypesCreate, PaymentTypesOut, PaymentTypesUpdate, Page
from app.services.payment_types import (
    create_payment_type_srv,
    get_payment_type_by_name_srv,
    get_payment_types_srv,
    update_payment_type_srv,
)

router = APIRouter(prefix="/v1/payment_types", tags=["payment_types"])


@router.get("/", response_model=Page[PaymentTypesOut])
def list_payment_types(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_active_user)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    pts, total = get_payment_types_srv(db=db, skip=skip, limit=limit)
    return Page[PaymentTypesOut](items=pts, total=total, skip=skip, limit=limit)


@router.get("/{name}", response_model=PaymentTypesOut)
def get_payment_type(
    name: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_active_user)],
):
    try:
        return get_payment_type_by_name_srv(db=db, name=name)
    except PaymentTypeNotFound:
        raise HTTPException(status_code=404, detail="Payment type not found")


@router.post("/", response_model=PaymentTypesOut, status_code=status.HTTP_201_CREATED)
def create_payment_type(
    pt_data: PaymentTypesCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_admin)],
):
    try:
        return create_payment_type_srv(db=db, pt_data=pt_data)
    except PaymentTypeAlreadyExists:
        raise HTTPException(status_code=409, detail="Payment type already exists")


@router.patch("/{name}", response_model=PaymentTypesOut)
def update_payment_type(
    name: str,
    pt_data: PaymentTypesUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_admin)],
):
    try:
        return update_payment_type_srv(db=db, name=name, pt_data=pt_data)
    except PaymentTypeNotFound:
        raise HTTPException(status_code=404, detail="Payment type not found")
    except PaymentTypeAlreadyExists:
        raise HTTPException(status_code=409, detail="Payment type already exists")
