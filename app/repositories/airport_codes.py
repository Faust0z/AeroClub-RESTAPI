from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import AirportCodes


class AirportCodeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return select(AirportCodes)

    def get_by_code(self, code: str) -> Optional[AirportCodes]:
        return self.db.execute(
            select(AirportCodes).where(AirportCodes.code == code)
        ).scalar_one_or_none()

    def add(self, code: AirportCodes) -> AirportCodes:
        self.db.add(code)
        self.db.commit()
        return code

    def update(self, code: AirportCodes) -> AirportCodes:
        self.db.commit()
        return code

    def delete(self, code: AirportCodes) -> None:
        self.db.delete(code)
        self.db.commit()
