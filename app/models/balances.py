from ..extensions import db


class Balances(db.Model):
    __tablename__ = 'balances'
    id: db.Mapped[int] = db.Column(db.Integer, primary_key=True, autoincrement=True)
    balance: db.Mapped[float] = db.Column(db.Numeric(10, 2), nullable=False)
    user_id: db.Mapped[int] = db.Column(db.ForeignKey('users.id'), nullable=False)

    user: db.Mapped["Users"] = db.relationship(back_populates="balance")
    transactions: db.Mapped[list["Transactions"]] = db.relationship(back_populates="balance")

    def __repr__(self):
        return f"<balance={self.balance}>"
