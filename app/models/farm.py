from datetime import datetime
from app.extensions import db


class Farm(db.Model):
    __tablename__ = "farms"

    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(100), nullable=False)
    location     = db.Column(db.String(200))
    area_acres   = db.Column(db.Float, nullable=False)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign key
    user_id      = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Relationships
    expenses     = db.relationship("Expense", backref="farm", lazy=True)

    def __repr__(self):
        return f"<Farm {self.name}>"