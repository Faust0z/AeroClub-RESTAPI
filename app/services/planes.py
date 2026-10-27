from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import Optional

from app.models import Planes, PlaneStatus
from .plane_status import get_plane_status_by_name_srv
from ..errors import PlaneRegistrationAlreadyExists, PlaneNotFound


def get_planes_srv(db: Session, brand: Optional[str] = None, registration: Optional[str] = None, category: Optional[str] = None,
                   status: Optional[str] = None) -> list[Planes]:
    stmt = select(Planes)

    if brand:
        stmt = stmt.where(Planes.brand.ilike(f"%{brand}%"))
    if registration:
        stmt = stmt.where(Planes.registration.ilike(f"%{registration}%"))
    if category:
        stmt = stmt.where(Planes.category.ilike(f"%{category}%"))
    if status:
        stmt = stmt.join(Planes.plane_status).where(PlaneStatus.state.ilike(f"%{status}%"))

    return db.execute(stmt).unique().scalars().all()


def get_plane_by_registration_srv(db: Session, registration: str) -> Planes:
    plane = db.execute(select(Planes).where(Planes.registration == registration)).scalar_one_or_none()
    if not plane:
        raise PlaneNotFound
    return plane


def create_plane_srv(db: Session, data: dict) -> Planes:
    plane = Planes(**data)
    plane.plane_status = get_plane_status_by_name_srv(db=db, name="Active")

    try:
        db.add(plane)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise PlaneRegistrationAlreadyExists

    return plane


def update_plane_srv(db: Session, registration: str, data: dict) -> Planes:
    plane = get_plane_by_registration_srv(db=db, registration=registration)

    try:
        for key, value in data.items():
            if hasattr(plane, key):
                setattr(plane, key, value)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise PlaneRegistrationAlreadyExists
    return plane


def update_plane_status_srv(db: Session, registration: str, plane_status_name: str) -> Planes:
    plane = get_plane_by_registration_srv(db=db, registration=registration)
    plane_status = get_plane_status_by_name_srv(db=db, name=plane_status_name)

    plane.plane_status = plane_status
    db.commit()
    return plane
