from sqlalchemy import ForeignKey
from . import *
from os import sys, path
from .city_model import City
from .cluster_model import Cluster
from .institution_model import Institution
from .role_model import Role
pth = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(pth)
from app import db
class user1(db.Model):
    __tablename__ = USERS_TBL

    id = db.Column(ID_COL, db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(NAME_COL, db.String(50), nullable=False)
    last_name = db.Column(LAST_NAME_COL, db.String(50), nullable=False)
    role_id = db.Column(ROLE_ID_COL, db.Integer, ForeignKey(Role.id), nullable=False)
    phone = db.Column(PHONE_COL, db.String(50), nullable=False)
    email = db.Column(EMAIL_COL, db.String(50), nullable=False)
    birthday = db.Column(BIRTHDAY_COL, db.DateTime, nullable=False)
    city_id = db.Column(CITY_ID_COL, db.Integer, ForeignKey(City.id), nullable=False)
    address = db.Column(ADDRESS_COL, db.String(50), nullable=False)
    institution_id = db.Column(INSTITUTION_ID_COL, db.Integer, ForeignKey(Institution.id), nullable=False)
    cluster_id = db.Column(CLUSTER_ID_COL, db.Integer, ForeignKey(Cluster.id), nullable=False)
    photo_path = db.Column(PHOTO_PATH_COL, db.String(50), nullable=False)

    def __init__(self, id, name, last_name, role_id, phone, email, birthday, city_id, address, institution_id, cluster_id, photo_path):
        self.id = id
        self.name = name
        self.last_name = last_name
        self.role_id = role_id
        self.phone = phone
        self.email = email
        self.birthday = birthday
        self.city_id = city_id
        self.address = address
        self.institution_id = institution_id
        self.cluster_id = cluster_id
        self.photo_path = photo_path

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}