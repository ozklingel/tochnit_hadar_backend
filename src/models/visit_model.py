from . import *
from .apprentice_model import Apprentice
from .user_model import user1


class Visit(db.Model):
    __tablename__ = VISITS_TBL

    id = db.Column(ID_COL, db.Integer, primary_key=True, autoincrement=True, nullable=False)
    apprentice_id = db.Column(APPRENTICE_ID_COL, db.Integer, ForeignKey(Apprentice.id), nullable=False)
    visit_date = db.Column(VISIT_DATE_COL, db.DateTime, nullable=False)
    user_id = db.Column(USER_ID_COL, db.Integer, ForeignKey(user1.id), nullable=False)
    visit_in_army = db.Column(VISIT_IN_ARMY_COL, db.Boolean, nullable=False)
    note = db.Column(NOTE_COL, db.String(50), nullable=True)
    title = db.Column(NOTE_COL, db.String(50), nullable=True)
    allreadyread=db.Column(ALLREADYREAD, db.Boolean, nullable=True)

    def __init__(self, id, apprentice_id, visit_date, user_id, visit_in_army, note,allreadyread,title):
        self.id = id
        self.apprentice_id = apprentice_id
        self.visit_date = visit_date
        self.user_id = user_id
        self.visit_in_army = visit_in_army
        self.note = note
        self.allreadyread = allreadyread
        self.title = title
