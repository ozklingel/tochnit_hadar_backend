from sqlalchemy import ForeignKey
from . import *
from os import sys, path
pth = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(pth)
from app import db
class Institution(db.Model):
    __tablename__ = INSTITUTIONS_TBL

    id = db.Column(ID_COL, db.Integer, primary_key=True, autoincrement=True, nullable=False)
    address = db.Column(ADDRESS_COL, db.String(50), nullable=False)
    city_id = db.Column(CITY_ID_COL, db.Integer, ForeignKey(get_forgein_key_source(CITIES_TBL, ID_COL)), nullable=False)
    phone = db.Column(PHONE_COL, db.String(50), nullable=False)
    contact_name = db.Column(CONTACT_NAME_COL, db.String(50), nullable=False)
    contact_phone = db.Column(CONTACT_PHONE_COL, db.String(50), nullable=False)
    logo_path = db.Column(LOGO_PATH_COL, db.String(50), nullable=False)
    owner_id = db.Column(OWNER_ID_COL, db.Integer, nullable=False)
    name = db.Column(NAME_COL, db.String(20), nullable=False)

    def __init__(self, id, address, city_id, phone, contact_name, contact_phone, logo_path, owner_id):
        self.id = id
        self.address = address
        self.city_id = city_id
        self.phone = phone
        self.contact_name = contact_name
        self.contact_phone = contact_phone
        self.logo_path = logo_path
        self.owner_id = owner_id