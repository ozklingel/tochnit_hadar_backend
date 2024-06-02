from . import *

from src.services import db


class City(db.Model):
    __tablename__ = CITIES_TBL

    id = db.Column(ID_COL, db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(NAME_COL, db.String(50), nullable=False)
    cluster_id = db.Column(CLUSTER_ID_COL, db.Integer, ForeignKey(get_forgein_key_source(CLUSTERS_TBL, ID_COL)),
                           nullable=False)

    def __init__(self, id, name, cluster_id):
        self.id = id
        self.name = name
        self.cluster_id = cluster_id
