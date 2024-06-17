from src.services import db


class Gift(db.Model):
    __tablename__ = "gift"

    code = db.Column("code", db.String(20), primary_key=True, nullable=False)
    was_used = db.Column("was_used", db.Boolean, nullable=False, default=False)
