from sqlalchemy import ForeignKey

from src.models.models_defines import (
    INSTITUTIONS_TBL,
    ID_COL,
    ADDRESS_COL,
    CITY_ID_COL,
    PHONE_COL,
    CONTACT_NAME_COL,
    LOGO_PATH_COL,
    OWNER_ID_COL,
    NAME_COL,
    CONTACT_PHONE_COL,
    CITIES_TBL,
)
from src.models.models_utils import get_foreign_key_source
from src.services import db


class Institution(db.Model):
    __tablename__ = INSTITUTIONS_TBL

    id = db.Column(
        ID_COL, db.Integer, primary_key=True, autoincrement=True, nullable=False
    )
    address = db.Column(ADDRESS_COL, db.String(50), nullable=False, default="")
    city_id = db.Column(
        CITY_ID_COL,
        db.Integer,
        ForeignKey(get_foreign_key_source(CITIES_TBL, ID_COL)),
        nullable=False,
    )
    phone = db.Column(PHONE_COL, db.String(50), nullable=False, default="")
    contact_name = db.Column(
        CONTACT_NAME_COL, db.String(50), nullable=False, default=""
    )
    contact_phone = db.Column(
        CONTACT_PHONE_COL, db.String(50), nullable=False, default=""
    )
    logo_path = db.Column(LOGO_PATH_COL, db.String(50), nullable=False, default="")
    owner_id = db.Column(OWNER_ID_COL, db.String(50), nullable=False, default=0)
    name = db.Column(NAME_COL, db.String(20), nullable=False, default="")
    admin_name = db.Column("admin_name", db.String(50), nullable=False, default="")
    admin_phone = db.Column("admin_phone", db.String(50), nullable=False, default="")
    roshYeshiva_name = db.Column(
        "roshyeshiva_name", db.String(50), nullable=False, default=""
    )
    roshYeshiva_phone = db.Column(
        "roshyeshiva_phone", db.String(50), nullable=False, default=""
    )
    cluster_id = db.Column("cluster_id", db.Integer, nullable=False)
    shluha = db.Column("shluha", db.String(50), nullable=False, default="")

    def to_attributes(
        self, city, region, melave_List, apprenticeList, owner_details, mosad_score
    ):
        return {
            "racaz_firstName": owner_details.name if owner_details else "no owner",
            "racaz_lastName": owner_details.last_name if owner_details else "no owner",
            "score": int(mosad_score) if type(mosad_score)==int  else -1,
            "apprenticeList": [str(row.id) for row in apprenticeList],
            "melave_List": [str(row.id) for row in melave_List],
            "admin_name": self.admin_name,
            "name": self.name,
            "owner_id": str(self.owner_id),
            "logo_path": self.logo_path,
            "contact_phone": self.contact_phone,
            "contact_name": self.contact_name,
            "phone": self.phone,
            "city_id": self.city_id,
            "address": self.address,
            "id": str(self.id),
            "admin_phone": self.admin_phone,
            "roshYeshiva_name": self.roshYeshiva_name,
            "roshYeshiva_phone": self.roshYeshiva_phone,
            "cluster": str(self.cluster_id),
            "shluha": self.shluha,
            "address": {
                "country": "IL",
                "city": city.name if city else "",
                "cityId": city.id,
                "street": self.address,
                "houseNumber": "1",
                "apartment": "1",
                "shluha": self.shluha,
                "region": region.name if region else "",
                "entrance": "a",
                "floor": "1",
                "postalCode": "12131",
                "lat": 32.04282620026557,
                "lng": 34.75186193813887,
            },
        }


front_end_dict = {
    "id": "id",
    "name": "name",
    "racaz_id": "owner_id",
    "contact_phone": "owner_id",
    "address": "city",
    "contact_name": "contact_name",
    "phone": "phone",
    "avatar": "logo_path",
    "cluster": "cluster_id",
    "roshYeshiva_phone": "roshYeshiva_phone",
    "roshYeshiva_name": "roshYeshiva_name",
    "admin_phone": "admin_phone",
    "shluha": "shluha",
    "admin_name": "admin_name",
}
