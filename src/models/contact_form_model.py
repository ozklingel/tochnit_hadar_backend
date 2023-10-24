from . import *
from datetime import datetime
from .user_model import user1


class ContactForm(db.Model):
    __tablename__ = CONTACT_FORMS_TBL

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(250), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, ForeignKey(user1.id), nullable=False)
    created_for_id = db.Column(db.Integer, ForeignKey(user1.id), nullable=False)
    allreadyread=db.Column(WAS_READ_COL, db.Boolean, nullable=True)
    def __init__(self, id, subject, content, created_at, created_by_id,created_for_id,allreadyread):
        self.id = id
        self.subject = subject
        self.content = content
        self.created_at = created_at
        self.created_by_id = created_by_id
        self.created_for_id=created_for_id
        self.allreadyread=allreadyread
