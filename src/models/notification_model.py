import uuid

from app import db
from sqlalchemy.dialects.postgresql import UUID
from . import *
from datetime import datetime

from .user_model import user1



class notifications(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.Integer, ForeignKey(user1.id), nullable=False)#converted from string
    apprenticeid = db.Column(db.Integer, ForeignKey(user1.id), nullable=False)
    event = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    timefromnow = db.Column(db.String(100), nullable=False)
    allreadyread = db.Column(WAS_READ_COL, db.Boolean, nullable=True)

