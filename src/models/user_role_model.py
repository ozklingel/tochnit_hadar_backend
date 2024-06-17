from sqlalchemy import ForeignKey

from src.services import db
from src.models.models_utils import get_foreign_key_source
from src.models.models_defines import USERS_TBL


class UserRole(db.Model):
    __tablename__ = "user_role"
    id = db.Column("id", nullable=False)
    user = db.Column("user_id", db.Integer, ForeignKey(get_foreign_key_source(USERS_TBL)), nullable=False)
    role= db.Column("role_id", db.Integer, ForeignKey(get_foreign_key_source("role")), nullable=False)