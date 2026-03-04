from datetime import datetime
from app.extensions import db


class Income(db.Model):
    __tablename__ = "income"

    id           = db.Column(db.Integer, primary_key=True)
    title        = db.Column(db.String(150), nullable=False)
    amount       = db.Column(db.Float, nullable=False)
    source       = db.Column(db.String(100))   # coffee sale, subsidy, etc.
    date         = db.Column(db.Date, nullable=False)
    notes        = db.Column(db.Text)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign key
    farm_id      = db.Column(db.Integer, db.ForeignKey("farms.id"), nullable=False)

    # Relationship ← THIS WAS MISSING
    farm         = db.relationship("Farm", backref="incomes")

    def __repr__(self):
        return f"<Income {self.title} - {self.amount}>"