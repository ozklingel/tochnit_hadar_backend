import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from src.models.models_defines import *
from src.models.models_utils import to_iso
from src.services import db

from .city_model import City
from .region_model import Region
from .institution_model import Institution


class User(db.Model):
    __tablename__ = USERS_TBL
    role_ids = db.Column("role_ids", nullable=False)
    id = db.Column(
        ID_COL, db.Integer, primary_key=True, autoincrement=True, nullable=False
    )
    name = db.Column("first_name", db.String(50), nullable=False, default="")
    last_name = db.Column(LAST_NAME_COL, db.String(50), nullable=False, default="")
    teudatZehut = db.Column("teudatzehut", db.String(50), nullable=False, default="")
    email = db.Column(EMAIL_COL, db.String(50), nullable=False, default="")
    birthday = db.Column(BIRTHDAY_COL, db.DateTime, nullable=True)
    city_id = db.Column(CITY_ID_COL, db.Integer, ForeignKey(City.id), nullable=True)
    address = db.Column(ADDRESS_COL, db.String(50), nullable=False, default="")
    fcmToken = db.Column("fcmToken", db.String(50), nullable=True, default="")

    institution_id = db.Column(
        INSTITUTION_ID_COL, db.Integer, ForeignKey(Institution.id), nullable=True
    )
    region_id = db.Column(
        "region_id", db.Integer, ForeignKey(Region.id), nullable=False, default=0
    )
    photo_path = db.Column(
        PHOTO_PATH_COL,
        db.String(50),
        nullable=True,
        default="https://www.gravatar.com/avatar",
    )
    notifyStartWeek = db.Column(
        NOTIFY_START_WEEK_COL, db.Boolean, nullable=False, default=True
    )
    notifyDayBefore = db.Column(
        NOTIFY_DAY_BEFORE_COL, db.Boolean, nullable=False, default=True
    )
    notifyMorning = db.Column(
        NOTIFY_MORNING_COL, db.Boolean, nullable=False, default=True
    )
    notifyStartWeek_sevev = db.Column(
        "notifystartweek_sevev", db.Boolean, nullable=False, default=True
    )
    notifyDayBefore_sevev = db.Column(
        "notifydaybefore_sevev", db.Boolean, nullable=False, default=True
    )
    notifyMorning_sevev = db.Column(
        "notifymorning_sevev", db.Boolean, nullable=False, default=True
    )
    notifyMorning_weekly_report = db.Column(
        "notifymorning_weekly_report", db.Boolean, nullable=False, default=True
    )
    cluster_id = db.Column("cluster_id", db.Integer, nullable=True)
    association_date = db.Column(
        "association_date", db.DateTime, nullable=False, default=datetime.date.today()
    )
    house_number = db.Column("house_number", db.Integer, nullable=False)

    tasks = relationship("Task", back_populates="user")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def to_attributes(self, city: str, region: str):
        return {
            "id": str(self.id),
            "name": self.name if self.name else "",
            "last_name": self.last_name if self.last_name else "",
            "birthday": to_iso(self.birthday) if self.birthday else "",
            "email": self.email,
            "city": city,
            "region": region,
            "role_ids": [int(r) for r in self.role_ids.split(",")],
            "institution": str(self.institution_id) if self.institution_id else "",
            "cluster_id": int(self.cluster_id) if self.cluster_id else "",
            "phone": str(self.id) if self.id else "",
            "fcmToken": str(self.fcmToken) if self.fcmToken else "",
            "teudatZehut": str(self.teudatZehut) if self.teudatZehut else "",
            "apprentices":[],
            "photo_path": (
                self.photo_path
                if self.photo_path is not None
                else "https://www.gravatar.com/avatar"
            ),
        }
