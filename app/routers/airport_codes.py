from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_admin, require_active_user
from app.database import get_db
from app.errors import AirportCodeAlreadyExists, AirportCodeNotFound
from app.models import Users
from app.schemas import AirportCodesCreate, AirportCodesOut, AirportCodesUpdate
from app.services.airport_codes import (
    create_airport_code_srv,
    get_airport_code_by_code_srv,
    get_airport_codes_srv,
    update_airport_code_srv,
)

router = APIRouter(prefix="/v1/airport_codes", tags=["airport_codes"])


@router.get("/", response_model=List[AirportCodesOut])
def list_airport_codes(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_active_user)],
):
    return get_airport_codes_srv(db=db)


@router.get("/{code}", response_model=AirportCodesOut)
def get_airport_code(
    code: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_active_user)],
):
    try:
        return get_airport_code_by_code_srv(db=db, code=code)
    except AirportCodeNotFound:
        raise HTTPException(status_code=404, detail="Airport code not found")


@router.post("/", response_model=AirportCodesOut, status_code=status.HTTP_201_CREATED)
def create_airport_code(
    code_data: AirportCodesCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_admin)],
):
    try:
        return create_airport_code_srv(db=db, code=code_data.code, data={"code": code_data.code})
    except AirportCodeAlreadyExists:
        raise HTTPException(status_code=409, detail="Airport code already exists")


@router.patch("/{code}", response_model=AirportCodesOut)
def update_airport_code(
    code: str,
    code_data: AirportCodesUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_admin)],
):
    try:
        return update_airport_code_srv(db=db, code=code, data=code_data.model_dump(exclude_unset=True))
    except AirportCodeNotFound:
        raise HTTPException(status_code=404, detail="Airport code not found")
    except AirportCodeAlreadyExists:
        raise HTTPException(status_code=409, detail="Airport code already exists")
