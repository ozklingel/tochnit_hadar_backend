from datetime import datetime, timedelta
import uuid
from sqlalchemy import ForeignKey

from src.services import db
from .user_model import User


class Task(db.Model):
    __tablename__ = "task_user_made"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(
        db.Integer, ForeignKey(User.id), nullable=False
    )  # converted from string
    event = db.Column(db.String(100), nullable=False, default="")
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    frequency_weekday = db.Column(
        "frequency_weekday", db.String(20), nullable=True, default=""
    )  # 1,3
    frequency_end = db.Column(db.String(20), nullable=False, default="")  # never/1/date
    frequency_meta = db.Column(db.String(20), nullable=False, default="")  # daily
    details = db.Column(db.String(100), nullable=False, default="")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default="todo")
    subject = db.Column(db.String(20), nullable=False, default="")
    allreadyread = db.Column("already_read", db.Boolean, nullable=True, default=False)

    def to_attributes(self):
        return {
            "id": str(self.id),
            "user_id": str(self.userid),
            "event": self.event,
            "date": self.date.isoformat(),
            "frequency_weekday": self.frequency_weekday,
            "frequency_end": self.frequency_end,
            "frequency_meta": self.frequency_meta,
            "details": self.details,
            "created_at": self.created_at.isoformat(),
            "status": self.status,
            "subject": self.subject,
            "already_read": self.allreadyread,
        }

    def from_attributes(self, data):
        date = data.get("date")
        frequency_meta = data.get("frequency_meta")
        frequency_end = data.get("frequency_end")  # 1,2,3,4 or once or never

        if frequency_end == "once":
            future_date_finish = date
        else:
            if frequency_end.isnumeric():
                if frequency_meta == "daily":
                    days = int(frequency_end)
                if frequency_meta == "weekly":
                    days = 7 * int(frequency_end)
                if frequency_meta == "monthly":
                    days = 30 * int(frequency_end)
                if frequency_meta == "yearly":
                    days = 365 * int(frequency_end)
            else:
                days = 1000
            future_date_finish = datetime.today() + timedelta(days=days)
        return Task(
            id=int(str(uuid.uuid4().int)[:5]),
            userid=data.get("user_id"),
            subject=data.get("subject"),
            event=data.get("event"),
            details=data.get("details"),
            status="private",
            date=date,
            frequency_meta=frequency_meta,
            frequency_end=str(future_date_finish)[:-7],
        )
