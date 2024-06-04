
from . import *


class user_role(db.Model):
    __tablename__ = "user_role"
    id = db.Column("id", nullable=False)
    user = db.Column("user_id", db.Integer, ForeignKey(get_forgein_key_source(USERS_TBL)), nullable=False)
    role= db.Column("role_id", db.Integer, ForeignKey(get_forgein_key_source("role")), nullable=False)