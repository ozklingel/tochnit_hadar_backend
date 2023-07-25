import uuid

from app import db
from sqlalchemy.dialects.postgresql import UUID


class interactions(db.Model):
    ID = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    apprenticeId = db.Column(db.String(100), nullable=False)
    userId = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    creationDate = db.Column(db.String(100), nullable=False)

    def get_json_data(self):
        return {
            "email": self.email,
        }
