from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_admin, require_active_user
from app.database import get_db
from app.errors import PaymentTypeAlreadyExists, PaymentTypeNotFound
from app.models import Users
from app.schemas import PaymentTypesCreate, PaymentTypesOut, PaymentTypesUpdate
from app.services.payment_types import (
    create_payment_type_srv,
    get_payment_type_by_name_srv,
    get_payment_types_srv,
    update_payment_type_srv,
)

router = APIRouter(prefix="/v1/payment_types", tags=["payment_types"])


@router.get("/", response_model=List[PaymentTypesOut])
def list_payment_types(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_active_user)],
):
    return get_payment_types_srv(db=db)


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
        return create_payment_type_srv(db=db, name=pt_data.type, data={"type": pt_data.type, "details": pt_data.details})
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
        return update_payment_type_srv(db=db, name=name, data=pt_data.model_dump(exclude_unset=True))
    except PaymentTypeNotFound:
        raise HTTPException(status_code=404, detail="Payment type not found")
    except PaymentTypeAlreadyExists:
        raise HTTPException(status_code=409, detail="Payment type already exists")
