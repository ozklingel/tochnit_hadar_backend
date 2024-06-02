from . import *
from datetime import datetime
from .user_model import user1


# user made task.will be use by naster only
class task_user_made(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.Integer, ForeignKey(user1.id), nullable=False)  # converted from string
    event = db.Column(db.String(100), nullable=False, default="")
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    frequency_weekday = db.Column("frequency_weekday", db.String(20), nullable=True, default="")  # 1,3
    frequency_end = db.Column(db.String(20), nullable=False, default="")  # never/1/date
    frequency_meta = db.Column(db.String(20), nullable=False, default="")  # daily
    details = db.Column(db.String(100), nullable=False, default="")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default="todo")
