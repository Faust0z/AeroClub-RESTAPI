from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.plane_status import PlaneStatus
from ..errors import PlaneStatusAlreadyExists, PlaneStatusNotFound


def get_planes_status_srv(db: Session) -> list[PlaneStatus]:
    return db.scalars(select(PlaneStatus)).all()


def get_plane_status_by_name_srv(db: Session, name: str) -> PlaneStatus:
    plane_status = db.execute(select(PlaneStatus).where(PlaneStatus.state == name)).scalar_one_or_none()
    if not plane_status:
        raise PlaneStatusNotFound
    return plane_status


def update_plane_status_srv(db: Session, name: str, data: dict) -> PlaneStatus:
    plane_status = get_plane_status_by_name_srv(db=db, name=name)
    try:
        for key, value in data.items():
            if hasattr(plane_status, key):
                setattr(plane_status, key, value)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise PlaneStatusAlreadyExists

    return plane_status


def create_plane_status_srv(db: Session, name: str, data: dict) -> PlaneStatus:
    plane_status = PlaneStatus(**data)
    try:
        db.add(plane_status)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise PlaneStatusAlreadyExists
    return plane_status
