from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import PlaneStatus


class PlaneStatusRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return select(PlaneStatus)

    def get_by_state(self, state: str) -> Optional[PlaneStatus]:
        return self.db.execute(
            select(PlaneStatus).where(PlaneStatus.state == state)
        ).scalar_one_or_none()

    def add(self, ps: PlaneStatus) -> PlaneStatus:
        self.db.add(ps)
        self.db.commit()
        return ps

    def update(self, ps: PlaneStatus) -> PlaneStatus:
        self.db.commit()
        return ps

    def delete(self, ps: PlaneStatus) -> None:
        self.db.delete(ps)
        self.db.commit()
