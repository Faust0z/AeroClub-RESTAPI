from sqlalchemy import Column, ForeignKey, Integer, Numeric, UUID
from sqlalchemy.orm import Mapped, relationship
import uuid

from ..database import Base


class Balances(Base):
    __tablename__ = 'balances'
    id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    balance: Mapped[float] = Column(Numeric(10, 2), nullable=False)
    user_id: Mapped[uuid.UUID] = Column(ForeignKey('users.uuid'), nullable=False)

    user: Mapped["Users"] = relationship(back_populates="balance")
    transactions: Mapped[list["Transactions"]] = relationship(back_populates="balance")

    def __repr__(self):
        return f"<balance={self.balance}>"
