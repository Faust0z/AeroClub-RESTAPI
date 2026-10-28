from typing import Optional

from sqlalchemy.exc import IntegrityError
from typing import Optional

from app.repositories import PlaneStatusRepository
from app.schemas import PlaneStatusCreate, PlaneStatusOut, PlaneStatusUpdate
from ..errors import PlaneStatusAlreadyExists, PlaneStatusNotFound


def get_planes_status_srv(db, skip: int = 0, limit: int = 100) -> list[PlaneStatusOut]:
    repo = PlaneStatusRepository(db)
    pss, _total = repo.get_all(skip=skip, limit=limit)
    return [PlaneStatusOut.model_validate(p) for p in pss]


def get_plane_status_by_name_srv(db, name: str) -> PlaneStatusOut:
    repo = PlaneStatusRepository(db)
    ps = repo.get_by_state(state=name)
    if not ps:
        raise PlaneStatusNotFound
    return PlaneStatusOut.model_validate(ps)


def create_plane_status_srv(db, ps_data: PlaneStatusCreate) -> PlaneStatusOut:
    repo = PlaneStatusRepository(db)
    from app.models import PlaneStatus
    plane_status = PlaneStatus(**ps_data.model_dump())
    try:
        repo.add(plane_status)
    except IntegrityError:
        repo.db.rollback()
        raise PlaneStatusAlreadyExists
    return PlaneStatusOut.model_validate(plane_status)


def update_plane_status_srv(db, name: str, ps_data: PlaneStatusUpdate) -> PlaneStatusOut:
    repo = PlaneStatusRepository(db)
    plane_status = repo.get_by_state(state=name)
    if not plane_status:
        raise PlaneStatusNotFound
    try:
        for key, value in ps_data.model_dump(exclude_unset=True).items():
            if hasattr(plane_status, key):
                setattr(plane_status, key, value)
        repo.update(plane_status)
    except IntegrityError:
        repo.db.rollback()
        raise PlaneStatusAlreadyExists
    return PlaneStatusOut.model_validate(plane_status)
