from datetime import datetime
from sqlalchemy import ARRAY, ForeignKey, Enum

from src.services import db
from src.models.models_defines import WAS_READ_COL

from .user_model import User
from enum import Enum as PyEnum


class IconTypeEnum(PyEnum):
    INTERNAL = 1
    SMS = 2
    WHATSAPP = 3


class MessageTypeEnum(PyEnum):
    INCOMING = 1
    OUTGOING = 2
    DRAFT = 3


# message class internal (not SMS or WHATAPP
class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject = db.Column(db.String(50), nullable=False, default="")
    content = db.Column(db.String(250), nullable=False, default="")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, ForeignKey(User.id), nullable=False)
    created_for_id = db.Column(db.Integer, nullable=False)
    allreadyread = db.Column(WAS_READ_COL, db.Boolean, nullable=True)
    attachments = db.Column(ARRAY(db.String), nullable=False)
    icon = db.Column(Enum(IconTypeEnum), nullable=False, default="")
    type = db.Column(Enum(MessageTypeEnum), nullable=False, default="")
    ent_group = db.Column(db.String(100), nullable=True)

    def to_attributes(self, mess_type, to, date_, ent_group):
        return {
            "id": str(self.id),
            "title": str(self.subject),
            "content": self.content,
            "date": date_,
            "from": str(self.created_by_id),
            "to": to,
            "allreadyread": str(self.allreadyread),
            "attachments": self.attachments,
            "icon": self.icon.name,
            "ent_group": ent_group,
            "type": mess_type,
        }
