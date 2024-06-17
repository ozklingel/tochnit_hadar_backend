from datetime import datetime
from sqlalchemy import ARRAY, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from src.services import db
from src.models.models_defines import ID_COL, WAS_READ_COL

from .user_model import User


# message class internal (not SMS or WHATAPP)
class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(ID_COL,UUID(as_uuid=True), primary_key=True)
    subject = db.Column(db.String(50), nullable=False, default="")
    content = db.Column(db.String(250), nullable=False, default="")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_by_id = db.Column(UUID(as_uuid=True), ForeignKey(User.id), nullable=False)
    created_for_id = db.Column(UUID(as_uuid=True), ForeignKey(User.id), nullable=False)
    allreadyread = db.Column(WAS_READ_COL, db.Boolean, nullable=True)
    attachments = db.Column(ARRAY(db.String), nullable=False)
    icon = db.Column(db.String(20), nullable=False, default="")
    type = db.Column("type", db.String(250), nullable=False, default="")
    ent_group = db.Column(db.String(100), nullable=True)
