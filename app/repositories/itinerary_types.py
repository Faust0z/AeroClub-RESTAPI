from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import ItineraryTypes


class ItineraryTypeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return select(ItineraryTypes)

    def get_by_type(self, type: str) -> Optional[ItineraryTypes]:
        return self.db.execute(
            select(ItineraryTypes).where(ItineraryTypes.type == type)
        ).scalar_one_or_none()

    def add(self, it: ItineraryTypes) -> ItineraryTypes:
        self.db.add(it)
        self.db.commit()
        return it

    def update(self, it: ItineraryTypes) -> ItineraryTypes:
        self.db.commit()
        return it

    def delete(self, it: ItineraryTypes) -> None:
        self.db.delete(it)
        self.db.commit()
