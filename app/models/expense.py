from datetime import datetime
from app.extensions import db


class Expense(db.Model):
    __tablename__ = "expenses"

    id           = db.Column(db.Integer, primary_key=True)
    title        = db.Column(db.String(150), nullable=False)
    amount       = db.Column(db.Float, nullable=False)
    category     = db.Column(db.String(100), nullable=False)  # fertilizer, labour, etc.
    date         = db.Column(db.Date, nullable=False)
    notes        = db.Column(db.Text)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign key
    farm_id      = db.Column(db.Integer, db.ForeignKey("farms.id"), nullable=False)

    def __repr__(self):
        return f"<Expense {self.title} - {self.amount}>"