from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_admin, require_active_user
from app.database import get_db
from app.errors import ItineraryTypeAlreadyExists, ItineraryTypeNotFound
from app.models import Users
from app.schemas import ItineraryTypesCreate, ItineraryTypesOut, ItineraryTypesUpdate, Page
from app.services.itinerary_types import (
    create_itinerary_type_srv,
    get_itinerary_type_by_type_srv,
    get_itinerary_types_srv,
    update_itinerary_type_srv,
)

router = APIRouter(prefix="/v1/itinerary_types", tags=["itinerary_types"])


@router.get("/", response_model=Page[ItineraryTypesOut])
def list_itinerary_types(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_active_user)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    its, total = get_itinerary_types_srv(db=db, skip=skip, limit=limit)
    return Page[ItineraryTypesOut](items=its, total=total, skip=skip, limit=limit)


@router.get("/{type}", response_model=ItineraryTypesOut)
def get_itinerary_type(
    type: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_active_user)],
):
    try:
        return get_itinerary_type_by_type_srv(db=db, type=type)
    except ItineraryTypeNotFound:
        raise HTTPException(status_code=404, detail="Itinerary type not found")


@router.post("/", response_model=ItineraryTypesOut, status_code=status.HTTP_201_CREATED)
def create_itinerary_type(
    it_data: ItineraryTypesCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_admin)],
):
    try:
        return create_itinerary_type_srv(db=db, it_data=it_data)
    except ItineraryTypeAlreadyExists:
        raise HTTPException(status_code=409, detail="Itinerary type already exists")


@router.patch("/{type}", response_model=ItineraryTypesOut)
def update_itinerary_type(
    type: str,
    it_data: ItineraryTypesUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_admin)],
):
    try:
        return update_itinerary_type_srv(db=db, type=type, it_data=it_data)
    except ItineraryTypeNotFound:
        raise HTTPException(status_code=404, detail="Itinerary type not found")
    except ItineraryTypeAlreadyExists:
        raise HTTPException(status_code=409, detail="Itinerary type already exists")
