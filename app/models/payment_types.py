from sqlalchemy import Column, ForeignKey, Integer, Numeric, String, Text, UUID
from sqlalchemy.orm import Mapped, relationship
import uuid

from ..database import Base


class PaymentTypes(Base):
    __tablename__ = 'payment_types'
    id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type: Mapped[str] = Column(String, nullable=False, unique=True)
    details: Mapped[str] = Column(Text, nullable=True)

    transactions: Mapped[list["Transactions"]] = relationship(back_populates="payment_type")

    def __repr__(self):
        return f"type=<{self.type} details={self.details}>"
