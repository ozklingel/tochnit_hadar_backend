import uuid

from sqlalchemy.dialects.postgresql import UUID
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class user1(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    privatename= db.Column(db.String(100), nullable=False)
    familyname= db.Column(db.String(100), nullable=False)
    image= db.Column(db.String(100), nullable=False)
    phone= db.Column(db.String(100), nullable=False)
    birthday= db.Column(db.String(100), nullable=False)
    eshcol= db.Column(db.String(100), nullable=False)
    apprentice= db.Column(db.String(100), nullable=False)
    mosad= db.Column(db.String(100), nullable=False)
    address= db.Column(db.String(100), nullable=False)
    creationdate= db.Column(db.String(100), nullable=False)

class Apprentice(db.Model):
    id= db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    privatename= db.Column(db.String(100), nullable=False)
    familyname= db.Column(db.String(100), nullable=False)
    image= db.Column(db.String(100), nullable=False)
    phone= db.Column(db.String(100), nullable=False)
    mail= db.Column(db.String(100), nullable=False)
    birthday= db.Column(db.DateTime(), nullable=False)
    eshcol= db.Column(db.String(100), nullable=False)
    HighschoolName= db.Column(db.String(100), nullable=False)
    YeshivaName= db.Column(db.String(100), nullable=False)
    HomeAddress= db.Column(db.String(100), nullable=False)
    BasisAddress= db.Column(db.String(100), nullable=False)
    startArmyDate= db.Column(db.DateTime(), nullable=False)
    Yehida= db.Column(db.String(100), nullable=False)
    lastvisitdate= db.Column(db.DateTime(), nullable=False)
    lastconatctdate= db.Column(db.DateTime(), nullable=False)
    familystatus= db.Column(db.String(100), nullable=False)
    fatherName= db.Column(db.String(100), nullable=False)
    fatherphone= db.Column(db.String(100), nullable=False)
    fatherMail= db.Column(db.String(100), nullable=False)
    motherName= db.Column(db.String(100), nullable=False)
    motherPhone= db.Column(db.String(100), nullable=False)
    mothermail= db.Column(db.String(100), nullable=False)
    yeshivamahzore= db.Column(db.String(100), nullable=False)
    ramName= db.Column(db.String(100), nullable=False)
    ramPhone= db.Column(db.String(100), nullable=False)
    melavename= db.Column(db.String(100), nullable=False)
    creationDate= db.Column(db.DateTime(), nullable=False)
    weddingDate= db.Column(db.DateTime(), nullable=False)

class Interaction(db.Model):
    ID= db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    apprenticeId= db.Column(db.String(100), nullable=False)
    userId= db.Column(db.String(100), nullable=False)
    type= db.Column(db.String(100), nullable=False)
    creationDate= db.Column(db.String(100), nullable=False)

    def get_json_data(self):
        return {
            "email": self.email,
        }
