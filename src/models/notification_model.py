from datetime import datetime
from sqlalchemy import ForeignKey

from src.models.models_defines import WAS_READ_COL
from src.services import db

from .user_model import User


# התראןת
class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.Integer, ForeignKey(User.id), nullable=False)  # converted from string
    subject = db.Column(db.String(20), nullable=False)
    event = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    allreadyread = db.Column(WAS_READ_COL, db.Boolean, nullable=True)
    numoflinesdisplay = db.Column(db.Integer, nullable=False, default=2)
    details = db.Column(db.String(100), nullable=False, default="")
    frequency = db.Column(db.String(100), nullable=False, default="")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def to_attributes(self):
        return {
            "id": str(self.id),
            "userid": str(self.userid),
            "subject": self.subject,
            "event": self.event,
            "date": self.date,
            "allreadyread": self.allreadyread,
            "details": self.details,
            "frequency": self.frequency,
            "created_at": self.created_at,

        }