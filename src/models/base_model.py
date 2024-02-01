from sqlalchemy import ForeignKey
from . import *
from os import sys, path
pth = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(pth)
from app import db
class Base(db.Model):
    __tablename__ = "base"

    id = db.Column(ID_COL, db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(NAME_COL, db.String(50), nullable=False)
    cordinatot = db.Column("cordinatot", db.String(50), nullable=False)

    def __init__(self, id, name, cordinatot):
        self.id = id
        self.name = name
        self.cordinatot = cordinatot