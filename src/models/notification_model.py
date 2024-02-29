
from . import *
from datetime import datetime
from .user_model import user1



class notifications(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.Integer, ForeignKey(user1.id), nullable=False)#converted from string
    apprenticeid = db.Column(db.Integer, nullable=False)
    event = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    allreadyread = db.Column(WAS_READ_COL, db.Boolean, nullable=True)
    numoflinesdisplay=db.Column(db.Integer, nullable=False,default=2)
    details=db.Column(db.String(100), nullable=False,default="")
    frequency=db.Column(db.String(100), nullable=False,default="")

