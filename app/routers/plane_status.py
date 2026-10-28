from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_admin, require_active_user
from app.database import get_db
from app.errors import PlaneStatusAlreadyExists, PlaneStatusNotFound
from app.models import Users
from app.schemas import PlaneStatusCreate, PlaneStatusOut, PlaneStatusUpdate, Page
from app.services.plane_status import (
    create_plane_status_srv,
    get_plane_status_by_name_srv,
    get_planes_status_srv,
    update_plane_status_srv,
)

router = APIRouter(prefix="/v1/plane_status", tags=["plane_status"])


@router.get("/", response_model=Page[PlaneStatusOut])
def list_plane_status(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_active_user)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    pss, total = get_planes_status_srv(db=db, skip=skip, limit=limit)
    return Page[PlaneStatusOut](items=pss, total=total, skip=skip, limit=limit)


@router.get("/{state}", response_model=PlaneStatusOut)
def get_plane_status(
    state: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_active_user)],
):
    try:
        return get_plane_status_by_name_srv(db=db, name=state)
    except PlaneStatusNotFound:
        raise HTTPException(status_code=404, detail="Plane status not found")


@router.post("/", response_model=PlaneStatusOut, status_code=status.HTTP_201_CREATED)
def create_plane_status(
    ps_data: PlaneStatusCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_admin)],
):
    try:
        return create_plane_status_srv(db=db, ps_data=ps_data)
    except PlaneStatusAlreadyExists:
        raise HTTPException(status_code=409, detail="Plane Status already exists")


@router.patch("/{state}", response_model=PlaneStatusOut)
def update_plane_status(
    state: str,
    ps_data: PlaneStatusUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_admin)],
):
    try:
        return update_plane_status_srv(db=db, name=state, ps_data=ps_data)
    except PlaneStatusNotFound:
        raise HTTPException(status_code=404, detail="Plane status not found")
    except PlaneStatusAlreadyExists:
        raise HTTPException(status_code=409, detail="Plane Status already exists")
