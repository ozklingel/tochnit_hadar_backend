import uuid

from app import db
from sqlalchemy.dialects.postgresql import UUID


class users(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    privatename = db.Column(db.String(100), nullable=False)
    familyname = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    birthday = db.Column(db.String(100), nullable=False)
    eshcol = db.Column(db.String(100), nullable=False)
    apprentice = db.Column(db.String(100), nullable=False)
    mosad = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    creationdate = db.Column(db.String(100), nullable=False)
