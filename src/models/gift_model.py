import uuid
from sqlalchemy.dialects.postgresql import UUID

from src.models.models_defines import ID_COL
from src.services import db


class Gift(db.Model):
    __tablename__ = "gift"
    id = db.Column(ID_COL, UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = db.Column("code", db.String(20), primary_key=True, nullable=False)
    was_used = db.Column("was_used", db.Boolean, nullable=False, default=False)
