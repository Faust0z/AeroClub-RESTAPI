from sqlalchemy import Column, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, relationship

from ..database import Base


class Balances(Base):
    __tablename__ = 'balances'
    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    balance: Mapped[float] = Column(Numeric(10, 2), nullable=False)
    user_id: Mapped[int] = Column(ForeignKey('users.id'), nullable=False)

    user: Mapped["Users"] = relationship(back_populates="balance")
    transactions: Mapped[list["Transactions"]] = relationship(back_populates="balance")

    def __repr__(self):
        return f"<balance={self.balance}>"
