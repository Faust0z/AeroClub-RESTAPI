from typing import Optional

from sqlalchemy.exc import IntegrityError
from typing import Optional

from app.repositories import ItineraryTypeRepository
from app.schemas import ItineraryTypesCreate, ItineraryTypesOut, ItineraryTypesUpdate
from ..errors import ItineraryTypeAlreadyExists, ItineraryTypeNotFound


def get_itinerary_types_srv(db, skip: int = 0, limit: int = 100) -> list[ItineraryTypesOut]:
    repo = ItineraryTypeRepository(db)
    its, _total = repo.get_all(skip=skip, limit=limit)
    return [ItineraryTypesOut.model_validate(i) for i in its]


def get_itinerary_type_by_type_srv(db, type: str) -> ItineraryTypesOut:
    repo = ItineraryTypeRepository(db)
    it = repo.get_by_type(type=type)
    if not it:
        raise ItineraryTypeNotFound
    return ItineraryTypesOut.model_validate(it)


def create_itinerary_type_srv(db, it_data: ItineraryTypesCreate) -> ItineraryTypesOut:
    repo = ItineraryTypeRepository(db)
    from app.models import ItineraryTypes
    itinerary_type = ItineraryTypes(**it_data.model_dump())
    try:
        repo.add(itinerary_type)
    except IntegrityError:
        repo.db.rollback()
        raise ItineraryTypeAlreadyExists
    return ItineraryTypesOut.model_validate(itinerary_type)


def update_itinerary_type_srv(db, type: str, it_data: ItineraryTypesUpdate) -> ItineraryTypesOut:
    repo = ItineraryTypeRepository(db)
    itinerary_type = repo.get_by_type(type=type)
    if not itinerary_type:
        raise ItineraryTypeNotFound
    try:
        for key, value in it_data.model_dump(exclude_unset=True).items():
            if hasattr(itinerary_type, key):
                setattr(itinerary_type, key, value)
        repo.update(itinerary_type)
    except IntegrityError:
        repo.db.rollback()
        raise ItineraryTypeAlreadyExists
    return ItineraryTypesOut.model_validate(itinerary_type)
