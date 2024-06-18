from src.models.models_defines import ID_COL
from src.services import db


class SystemReport(db.Model):
    __tablename__ = "system_report"

    id = db.Column(ID_COL, db.Integer, primary_key=True, autoincrement=True, nullable=False)
    creation_date = db.Column("creation_date", db.DateTime, nullable=False)
    type = db.Column("type", db.String(20), nullable=False)
    related_id = db.Column("related_id", db.Integer, nullable=False)
    value = db.Column("value", db.String(20), nullable=False)

