from . import *
from datetime import datetime

class ContactForm(db.Model):
    __tablename__ = CONTACT_FORMS_TBL

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(250), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, ForeignKey(get_forgein_key_source(USERS_TBL, ID_COL)), nullable=False)

    def __init__(self, id, subject, content, created_at, created_by_id):
        self.id = id
        self.subject = subject
        self.content = content
        self.created_at = created_at
        self.created_by_id = created_by_id
