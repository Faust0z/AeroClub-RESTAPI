from sqlalchemy.exc import IntegrityError

from ..errors import ItineraryTypeNotFound, ItineraryTypeAlreadyExists
from ..extensions import db
from ..models import ItineraryTypes


def get_itinerary_types_srv() -> list[ItineraryTypes]:
    return db.session.scalars(db.select(ItineraryTypes)).all()


def get_itinerary_type_by_type_srv(type: str) -> ItineraryTypes:
    itinerary_type = db.session.execute(db.select(ItineraryTypes).where(ItineraryTypes.type == type)).scalar_one_or_none()
    if not itinerary_type:
        raise ItineraryTypeNotFound
    return itinerary_type


def update_itinerary_type_srv(type: str, data: dict) -> ItineraryTypes:
    itinerary_type = get_itinerary_type_by_type_srv(type=type)
    try:
        for key, value in data.items():
            if hasattr(itinerary_type, key):
                setattr(itinerary_type, key, value)
        db.session.commit()
    except IntegrityError:
        raise ItineraryTypeAlreadyExists

    return itinerary_type
