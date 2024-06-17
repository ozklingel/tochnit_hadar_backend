import datetime
from sqlalchemy import ForeignKey

from src.models.models_defines import *
from src.models.models_utils import to_iso
from src.services import db

from .city_model import City
from .cluster_model import Cluster
from .institution_model import Institution


class User(db.Model):
    __tablename__ = USERS_TBL
    role_ids = db.Column("role_ids", nullable=False)
    id = db.Column(ID_COL, db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column("first_name", db.String(50), nullable=False, default="")
    last_name = db.Column(LAST_NAME_COL, db.String(50), nullable=False, default="")
    role_id = db.Column(ROLE_ID_COL, db.String(10), nullable=False, default="0")
    teudatZehut = db.Column("teudatzehut", db.String(50), nullable=False, default="")
    email = db.Column(EMAIL_COL, db.String(50), nullable=False, default="")
    birthday = db.Column(BIRTHDAY_COL, db.DateTime, nullable=False, default="2022-01-01")
    city_id = db.Column(CITY_ID_COL, db.Integer, ForeignKey(City.id), nullable=False, default=313)
    address = db.Column(ADDRESS_COL, db.String(50), nullable=False, default="")
    institution_id = db.Column(INSTITUTION_ID_COL, db.Integer, ForeignKey(Institution.id), nullable=False, default=0)
    cluster_id = db.Column(CLUSTER_ID_COL, db.Integer, ForeignKey(Cluster.id), nullable=False, default=0)
    photo_path = db.Column(PHOTO_PATH_COL, db.String(50), nullable=False, default="https://www.gravatar.com/avatar")
    notifyStartWeek = db.Column(NOTIFY_START_WEEK_COL, db.Boolean, nullable=False, default=True)
    notifyDayBefore = db.Column(NOTIFY_DAY_BEFORE_COL, db.Boolean, nullable=False, default=True)
    notifyMorning = db.Column(NOTIFY_MORNING_COL, db.Boolean, nullable=False, default=True)
    notifyStartWeek_sevev = db.Column("notifystartweek_sevev", db.Boolean, nullable=False, default=True)
    notifyDayBefore_sevev = db.Column("notifydaybefore_sevev", db.Boolean, nullable=False, default=True)
    notifyMorning_sevev = db.Column("notifymorning_sevev", db.Boolean, nullable=False, default=True)
    notifyMorning_weekly_report = db.Column("notifymorning_weekly_report", db.Boolean, nullable=False, default=True)
    eshcol = db.Column("eshcol", db.String(50), nullable=False, default="")
    association_date = db.Column("association_date", db.DateTime, nullable=False, default=datetime.date.today())

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    

    def to_attributes(self, city: str, region: str, apprentice_list):
        return {
                "id": str(self.id),
                "name": self.name,
                "last_name": self.last_name,
                "birthday": to_iso(self.birthday),
                "email": self.email,
                "city": city,
                "cluster_id": region,
                "role_ids": [int(r) for r in self.role_ids.split(",")],
                "institution": str(self.institution_id),
                "eshcol": str(self.eshcol),
                "apprentices": apprentice_list,
                "phone": str(self.id),
                "teudatZehut": str(self.teudatZehut),
                "photo_path": self.photo_path if self.photo_path is not None else 'https://www.gravatar.com/avatar'
                }

