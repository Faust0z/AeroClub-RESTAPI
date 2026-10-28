from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import PaymentTypes


class PaymentTypeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return select(PaymentTypes)

    def get_by_name(self, name: str) -> Optional[PaymentTypes]:
        return self.db.execute(
            select(PaymentTypes).where(PaymentTypes.type == name)
        ).scalar_one_or_none()

    def add(self, pt: PaymentTypes) -> PaymentTypes:
        self.db.add(pt)
        self.db.commit()
        return pt

    def update(self, pt: PaymentTypes) -> PaymentTypes:
        self.db.commit()
        return pt

    def delete(self, pt: PaymentTypes) -> None:
        self.db.delete(pt)
        self.db.commit()
