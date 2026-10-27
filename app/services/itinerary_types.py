from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..errors import ItineraryTypeNotFound, ItineraryTypeAlreadyExists
from ..models import ItineraryTypes


def get_itinerary_types_srv(db: Session) -> list[ItineraryTypes]:
    return db.scalars(select(ItineraryTypes)).all()


def get_itinerary_type_by_type_srv(db: Session, type: str) -> ItineraryTypes:
    itinerary_type = db.execute(select(ItineraryTypes).where(ItineraryTypes.type == type)).scalar_one_or_none()
    if not itinerary_type:
        raise ItineraryTypeNotFound
    return itinerary_type


def update_itinerary_type_srv(db: Session, type: str, data: dict) -> ItineraryTypes:
    itinerary_type = get_itinerary_type_by_type_srv(db=db, type=type)
    try:
        for key, value in data.items():
            if hasattr(itinerary_type, key):
                setattr(itinerary_type, key, value)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ItineraryTypeAlreadyExists

    return itinerary_type


def create_itinerary_type_srv(db: Session, type: str, data: dict) -> ItineraryTypes:
    itinerary_type = ItineraryTypes(**data)
    try:
        db.add(itinerary_type)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ItineraryTypeAlreadyExists
    return itinerary_type
