from sqlalchemy.exc import IntegrityError
from typing import Optional

from app.models import Planes, PlaneStatus
from .plane_status import get_plane_status_by_name_srv
from ..errors import PlaneRegistrationAlreadyExists, PlaneNotFound
from ..extensions import db


def get_planes_srv(brand: Optional[str] = None, registration: Optional[str] = None, category: Optional[str] = None,
                   status: Optional[str] = None) -> list[Planes]:
    stmt = db.select(Planes)

    if brand:
        stmt = stmt.where(Planes.brand.ilike(f"%{brand}%"))
    if registration:
        stmt = stmt.where(Planes.registration.ilike(f"%{registration}%"))
    if category:
        stmt = stmt.where(Planes.category.ilike(f"%{category}%"))
    if status:
        stmt = stmt.join(Planes.status).where(PlaneStatus.state.ilike(f"%{status}%"))

    return db.session.execute(stmt).unique().scalars().all()


def get_plane_by_registration_srv(registration: str) -> Planes:
    plane = db.session.execute(db.select(Planes).where(Planes.registration == registration)).scalar_one_or_none()
    if not plane:
        raise PlaneNotFound
    return plane


def create_plane_srv(plane: Planes) -> Planes:
    plane.plane_status = get_plane_status_by_name_srv("Active")

    try:
        db.session.add(plane)
        db.session.commit()
    except IntegrityError:
        raise PlaneRegistrationAlreadyExists

    return plane


def update_plane_srv(registration: str, data: dict) -> Planes:
    plane = get_plane_by_registration_srv(registration=registration)

    try:
        for key, value in data.items():
            if hasattr(plane, key):
                setattr(plane, key, value)
        db.session.commit()
    except IntegrityError:
        raise PlaneRegistrationAlreadyExists
    return plane


def update_plane_status_srv(registration: str, plane_status: str) -> Planes:
    plane = get_plane_by_registration_srv(registration=registration)
    plane_status = get_plane_status_by_name_srv(name=plane_status)

    plane.plane_status = plane_status
    db.session.commit()
    return plane
