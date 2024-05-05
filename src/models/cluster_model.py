from . import *

from src.services import db
#region where the entity is in Israel
class Cluster(db.Model):
    __tablename__ = CLUSTERS_TBL

    id = db.Column(ID_COL, db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(NAME_COL, db.String(50), nullable=False)

    def __init__(self, id, name):
        self.id = id
        self.name = name