from sqlalchemy import ARRAY

from . import *
from datetime import datetime
from .user_model import user1


# message class internal (not SMS or WHATAPP
class ContactForm(db.Model):
    __tablename__ = CONTACT_FORMS_TBL

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject = db.Column(db.String(50), nullable=False, default="")
    content = db.Column(db.String(250), nullable=False, default="")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, ForeignKey(user1.id), nullable=False)
    created_for_id = db.Column(db.Integer, ForeignKey(user1.id), nullable=False)
    allreadyread = db.Column(WAS_READ_COL, db.Boolean, nullable=True)
    attachments = db.Column(ARRAY(db.String), nullable=False)
    icon = db.Column(db.String(20), nullable=False, default="")
    type = db.Column("type", db.String(250), nullable=False, default="")
    ent_group = db.Column(db.String(100), nullable=True)
