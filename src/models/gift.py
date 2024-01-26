from sqlalchemy import ForeignKey
from . import *
from os import sys, path
pth = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(pth)
from app import db
class gift(db.Model):
    __tablename__ = "gift"

    code = db.Column("code", db.String(20), primary_key=True, nullable=False)
    was_used = db.Column("was_used", db.Boolean, nullable=False,default=False)


