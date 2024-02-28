from . import *

from app import db
#לא בשימוש###########
class Eshcol(db.Model):
    __tablename__ = "eshcol"

    id = db.Column(ID_COL, db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(NAME_COL, db.String(50), nullable=False)

    def __init__(self, id, name):
        self.id = id
        self.name = name