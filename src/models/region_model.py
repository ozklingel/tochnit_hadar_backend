from src.services import db
from src.models.models_defines import CLUSTERS_TBL, ID_COL, NAME_COL


# region where the entity is in Israel
class Region(db.Model):
    __tablename__ = "regions"

    id = db.Column(ID_COL, db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(NAME_COL, db.String(50), nullable=False)

    def __init__(self, id, name):
        self.id = id
        self.name = name
