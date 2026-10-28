from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Planes, PlaneStatus
from app.repositories import PlaneRepository, PlaneStatusRepository
from app.schemas import PlanesCreate, PlanesOut, PlanesUpdate
from ..errors import PlaneNotFound, PlaneRegistrationAlreadyExists, PlaneStatusNotFound


def get_planes_srv(
    db: Session,
    brand: Optional[str] = None,
    registration: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[PlanesOut]:
    stmt = select(Planes)
    if brand:
        stmt = stmt.where(Planes.brand.ilike(f"%{brand}%"))
    if registration:
        stmt = stmt.where(Planes.registration.ilike(f"%{registration}%"))
    if category:
        stmt = stmt.where(Planes.category.ilike(f"%{category}%"))
    if status:
        stmt = stmt.join(Planes.plane_status).where(PlaneStatus.state.ilike(f"%{status}%"))
    stmt = stmt.offset(skip).limit(limit)
    planes = db.execute(stmt).unique().scalars().all()
    return [PlanesOut.model_validate(p) for p in planes]


def get_plane_by_registration_srv(db: Session, registration: str) -> Planes:
    repo = PlaneRepository(db)
    plane = repo.get_by_registration(registration=registration)
    if not plane:
        raise PlaneNotFound
    return plane


def create_plane_srv(db: Session, data: PlanesCreate) -> PlanesOut:
    repo = PlaneRepository(db)
    status_repo = PlaneStatusRepository(db)
    plane = Planes(**data.model_dump())
    plane.plane_status = status_repo.get_by_state(state="Active")

    try:
        repo.add(plane)
    except IntegrityError:
        repo.db.rollback()
        raise PlaneRegistrationAlreadyExists
    return PlanesOut.model_validate(plane)


def update_plane_srv(db: Session, registration: str, data: PlanesUpdate) -> PlanesOut:
    repo = PlaneRepository(db)
    plane = repo.get_by_registration(registration=registration)
    if not plane:
        raise PlaneNotFound

    try:
        for key, value in data.model_dump(exclude_unset=True).items():
            if hasattr(plane, key):
                setattr(plane, key, value)
        repo.update(plane)
    except IntegrityError:
        repo.db.rollback()
        raise PlaneRegistrationAlreadyExists
    return PlanesOut.model_validate(plane)


def update_plane_status_srv(db: Session, registration: str, plane_status_name: str) -> PlanesOut:
    repo = PlaneRepository(db)
    status_repo = PlaneStatusRepository(db)
    plane = repo.get_by_registration(registration=registration)
    if not plane:
        raise PlaneNotFound
    plane_status = status_repo.get_by_state(state=plane_status_name)
    if not plane_status:
        raise PlaneStatusNotFound

    plane.plane_status = plane_status
    repo.update(plane)
    return PlanesOut.model_validate(plane)
