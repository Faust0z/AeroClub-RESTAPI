from ..extensions import db


class Planes(db.Model):
    __tablename__ = 'planes'
    id: db.Mapped[int] = db.mapped_column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    brand: db.Mapped[str] = db.mapped_column(db.String, nullable=False)
    model: db.Mapped[str] = db.mapped_column(db.String, nullable=False)
    registration: db.Mapped[str] = db.mapped_column(db.String, nullable=False, unique=True)
    category: db.Mapped[str] = db.mapped_column(db.String, nullable=False)
    acquisition_date: db.Mapped[db.Date] = db.mapped_column(db.Date, nullable=False)
    consumption_per_hour: db.Mapped[int] = db.mapped_column(db.Integer, nullable=False)
    fare: db.Mapped[float] = db.mapped_column(db.Numeric(10, 2), nullable=False)
    description: db.Mapped[str] = db.mapped_column(db.Text)
    plane_status_id: db.Mapped[int] = db.mapped_column(db.ForeignKey('plane_status.id'))

    itinerary: db.Mapped[list["Itineraries"]] = db.relationship(back_populates="plane")
    plane_status: db.Mapped["PlaneStatus"] = db.relationship(back_populates="plane")

    def __repr__(self):
        return (f"<Plane "
                f"id={self.id} "
                f"model='{self.model}' "
                f"consumption_per_hour={self.consumption_per_hour}>")
