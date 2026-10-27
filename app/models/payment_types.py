from sqlalchemy import Column, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, relationship

from ..database import Base


class PaymentTypes(Base):
    __tablename__ = 'payment_types'
    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = Column(String, nullable=False, unique=True)
    details: Mapped[str] = Column(Text, nullable=True)

    transactions: Mapped[list["Transactions"]] = relationship(back_populates="payment_type")

    def __repr__(self):
        return f"type=<{self.type} details={self.details}>"
