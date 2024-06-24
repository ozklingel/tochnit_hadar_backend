from sqlalchemy import ForeignKey
from src.services import db

from src.models.models_utils import get_foreign_key_source
from src.models.models_defines import CITIES_TBL, CLUSTER_ID_COL, CLUSTERS_TBL, ID_COL, NAME_COL


class City(db.Model):
    __tablename__ = CITIES_TBL

    id = db.Column(ID_COL, db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(NAME_COL, db.String(50), nullable=False)
    region_id = db.Column(CLUSTER_ID_COL, db.Integer, ForeignKey(get_foreign_key_source("regions", ID_COL)),
                           nullable=False)

    def __init__(self, id, name, region_id):
        self.id = id
        self.name = name
        self.region_id = region_id
