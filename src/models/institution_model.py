from sqlalchemy import ForeignKey

from src.models.models_defines import INSTITUTIONS_TBL, ID_COL, ADDRESS_COL, CITY_ID_COL, PHONE_COL, \
    CONTACT_NAME_COL, LOGO_PATH_COL, OWNER_ID_COL, NAME_COL, CONTACT_PHONE_COL, CITIES_TBL
from src.models.models_utils import get_foreign_key_source
from src.services import db


class Institution(db.Model):
    __tablename__ = INSTITUTIONS_TBL

    id = db.Column(ID_COL, db.Integer, primary_key=True, autoincrement=True, nullable=False)
    address = db.Column(ADDRESS_COL, db.String(50), nullable=False, default="")
    city_id = db.Column(CITY_ID_COL, db.Integer, ForeignKey(get_foreign_key_source(CITIES_TBL, ID_COL)), nullable=False)
    phone = db.Column(PHONE_COL, db.String(50), nullable=False, default="")
    contact_name = db.Column(CONTACT_NAME_COL, db.String(50), nullable=False, default="")
    contact_phone = db.Column(CONTACT_PHONE_COL, db.String(50), nullable=False, default="")
    logo_path = db.Column(LOGO_PATH_COL, db.String(50), nullable=False, default="")
    owner_id = db.Column(OWNER_ID_COL, db.String(50), nullable=False, default=0)
    name = db.Column(NAME_COL, db.String(20),  nullable=False, default="")
    admin_name = db.Column("admin_name", db.String(50), nullable=False, default="")
    admin_phone = db.Column("admin_phone", db.String(50), nullable=False, default="")
    roshYeshiva_name = db.Column("roshyeshiva_name", db.String(50), nullable=False, default="")
    roshYeshiva_phone = db.Column("roshyeshiva_phone", db.String(50), nullable=False, default="")
    cluster_id = db.Column("eshcol_id", db.String(50), nullable=False, default="")

front_end_dict = {
    "id": "id",
    "name": "name",
    "racaz_id": "owner_id",
    "contact_phone": "owner_id",
    "address": "city",
    "contact_name": "contact_name",
    "phone": "phone",
    "avatar": "logo_path",
    "eshcol": "cluster_id",
    "roshYeshiva_phone": "roshYeshiva_phone",
    "roshYeshiva_name": "roshYeshiva_name",
    "admin_phone": "admin_phone",
    "admin_name": "admin_name"
}
