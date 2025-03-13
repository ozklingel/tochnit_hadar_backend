from src.services import db


class Role(db.Model):
    __tablename__ = "role"
    id = db.Column("id", nullable=False)
    name = db.Column("name", db.String(20), nullable=False)
