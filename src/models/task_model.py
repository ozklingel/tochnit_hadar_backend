from datetime import datetime
from sqlalchemy import ForeignKey

from src.services import db
from .user_model import User


# user made task.will be use by naster only
class Task(db.Model):
    __tablename__ = "task_user_made"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.Integer, ForeignKey(User.id), nullable=False)  # converted from string
    event = db.Column(db.String(100), nullable=False, default="")
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    frequency_weekday = db.Column("frequency_weekday", db.String(20), nullable=True, default="")  # 1,3
    frequency_end = db.Column(db.String(20), nullable=False, default="")  # never/1/date
    frequency_meta = db.Column(db.String(20), nullable=False, default="")  # daily
    details = db.Column(db.String(100), nullable=False, default="")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default="todo")
    subject = db.Column(db.String(20), nullable=False, default="")
    allreadyread = db.Column("already_read", db.Boolean, nullable=True, default=False)
