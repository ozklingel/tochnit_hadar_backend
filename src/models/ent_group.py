from sqlalchemy import ForeignKey, ARRAY
from . import *
from os import sys, path
pth = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(pth)
from app import db
class ent_group(db.Model):
    __tablename__ = "ent_group"

    id = db.Column(ID_COL, db.Integer, primary_key=True, autoincrement=True, nullable=False)
    group_name = db.Column("name", db.String(50), nullable=False)
    table_name = db.Column("table_name", db.String(50), nullable=False)
    ent_id_list=db.Column(ARRAY(db.String), nullable=False)
    user_id = db.Column("user_id", db.Integer, nullable=False)

