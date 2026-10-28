from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Planes, PlaneStatus


class PlaneRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self,
        brand: Optional[str] = None,
        registration: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
    ):
        stmt = select(Planes)

        if brand:
            stmt = stmt.where(Planes.brand.ilike(f"%{brand}%"))
        if registration:
            stmt = stmt.where(Planes.registration.ilike(f"%{registration}%"))
        if category:
            stmt = stmt.where(Planes.category.ilike(f"%{category}%"))
        if status:
            stmt = stmt.join(Planes.plane_status).where(PlaneStatus.state.ilike(f"%{status}%"))

        return stmt

    def get_by_registration(self, registration: str) -> Optional[Planes]:
        return self.db.execute(
            select(Planes).where(Planes.registration == registration)
        ).scalar_one_or_none()

    def add(self, plane: Planes) -> Planes:
        self.db.add(plane)
        self.db.commit()
        return plane

    def update(self, plane: Planes) -> Planes:
        self.db.commit()
        return plane

    def delete(self, plane: Planes) -> None:
        self.db.delete(plane)
        self.db.commit()
