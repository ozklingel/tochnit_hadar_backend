from datetime import datetime
from sqlalchemy import ForeignKey

from src.models.models_defines import VISITS_TBL, ID_COL, VISIT_DATE_COL, USER_ID_COL, \
    VISIT_IN_ARMY_COL, NOTE_COL, TITLE_COL, ALREADY_READ
from src.services import db
from .user_model import User


# דיוחחים על משתמש או חניך
class Report(db.Model):
    __tablename__ = VISITS_TBL

    id = db.Column(ID_COL, db.Integer, primary_key=True, autoincrement=True, nullable=False)
    ent_reported = db.Column("ent_reported", db.Integer, nullable=False)
    visit_date = db.Column(VISIT_DATE_COL, db.DateTime, nullable=False)
    user_id = db.Column(USER_ID_COL, db.Integer, ForeignKey(User.id), nullable=False)
    visit_in_army = db.Column(VISIT_IN_ARMY_COL, db.Boolean, nullable=False, default=False)
    note = db.Column(NOTE_COL, db.String(50), nullable=True, default="")
    title = db.Column(TITLE_COL, db.String(50), nullable=True, default="")
    allreadyread = db.Column(ALREADY_READ, db.Boolean, nullable=True, default=False)
    attachments = db.Column("attachments", nullable=True, default=[])
    description = db.Column("description", db.String(100), nullable=True, default="")
    ent_group = db.Column(db.String(100), nullable=True, default="")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def to_attributes(self):
        return {
            "id": str(self.id),
            "ent_reported": str(self.ent_reported),
            "visit_date": self.visit_date,
            "user_id": str(self.user_id),
            "visit_in_army": self.visit_in_army,
            "note": self.note,
            "title": self.title,
            "allreadyread": self.allreadyread,
            "attachments": self.attachments,
            "description": self.description,
            "ent_group": self.ent_group,
            "created_at": self.created_at,

        }