from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_admin, require_active_user
from app.database import get_db
from app.errors import PlaneNotFound, PlaneRegistrationAlreadyExists
from app.models import Users
from app.schemas import PlanesCreate, PlanesOut, PlanesUpdate
from app.services.planes import (
    create_plane_srv,
    get_planes_srv,
    get_plane_by_registration_srv,
    update_plane_srv,
    update_plane_status_srv,
)

router = APIRouter(prefix="/v1/planes", tags=["planes"])


@router.get("/", response_model=List[PlanesOut])
def list_planes(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_active_user)],
    brand: Optional[str] = Query(None),
    registration: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
):
    planes = get_planes_srv(db=db, brand=brand, registration=registration, category=category, status=status)
    return planes


@router.get("/{registration}", response_model=PlanesOut)
def get_plane(
    registration: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_active_user)],
):
    try:
        plane = get_plane_by_registration_srv(db=db, registration=registration)
    except PlaneNotFound:
        raise HTTPException(status_code=404, detail="Plane not found")
    return plane


@router.post("/", response_model=PlanesOut, status_code=status.HTTP_201_CREATED)
def create_plane(
    plane_data: PlanesCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_admin)],
):
    try:
        plane = create_plane_srv(db=db, data=plane_data.model_dump())
    except PlaneRegistrationAlreadyExists:
        raise HTTPException(status_code=409, detail="Plane's registration already exists")
    return plane


@router.patch("/{registration}", response_model=PlanesOut)
def update_plane(
    registration: str,
    plane_data: PlanesUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_admin)],
):
    try:
        plane = update_plane_srv(db=db, registration=registration, data=plane_data.model_dump(exclude_unset=True))
    except PlaneNotFound:
        raise HTTPException(status_code=404, detail="Plane not found")
    except PlaneRegistrationAlreadyExists:
        raise HTTPException(status_code=409, detail="Plane's registration already exists")
    return plane


@router.patch("/{registration}/status", response_model=PlanesOut)
def update_plane_status_endpoint(
    registration: str,
    plane_status: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_admin)],
):
    try:
        plane = update_plane_status_srv(db=db, registration=registration, plane_status_name=plane_status)
    except PlaneNotFound:
        raise HTTPException(status_code=404, detail="Plane not found")
    return plane
