from . import *

from src.services import db


class Base(db.Model):
    __tablename__ = "base"

    id = db.Column(ID_COL, db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(NAME_COL, db.String(50), nullable=False)
    cordinatot = db.Column("cordinatot", db.String(50), nullable=False)

    def __init__(self, id, name, cordinatot):
        self.id = id
        self.name = name
        self.cordinatot = cordinatot
