from sqlalchemy import ForeignKey
from . import *
from os import sys, path
from .city_model import City
from .cluster_model import Cluster
from .institution_model import Institution
from .gift import gift
pth = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(pth)
from app import db
class user1(db.Model):
    __tablename__ = USERS_TBL

    id = db.Column(ID_COL, db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column("first_name", db.String(50), nullable=False,default="")
    last_name = db.Column(LAST_NAME_COL, db.String(50), nullable=False,default="")
    role_id = db.Column(ROLE_ID_COL, db.String(10),  nullable=False,default="0")
    teudatZehut = db.Column("teudatzehut", db.String(50), nullable=False,default="")
    email = db.Column(EMAIL_COL, db.String(50), nullable=False,default="")
    birthday = db.Column(BIRTHDAY_COL, db.DateTime, nullable=False,default="2022-01-01")
    city_id = db.Column(CITY_ID_COL, db.Integer, ForeignKey(City.id), nullable=False,default=313)
    address = db.Column(ADDRESS_COL, db.String(50), nullable=False,default="")
    institution_id = db.Column(INSTITUTION_ID_COL, db.Integer, ForeignKey(Institution.id), nullable=False,default=0)
    cluster_id = db.Column(CLUSTER_ID_COL, db.Integer, ForeignKey(Cluster.id), nullable=False,default=0)
    photo_path = db.Column(PHOTO_PATH_COL, db.String(50), nullable=False,default="https://www.gravatar.com/avatar")
    notifyStartWeek = db.Column(notifyStartWeek_COL, db.Boolean, nullable=False,default=True)
    notifyDayBefore = db.Column(notifyDayBefore_COL, db.Boolean, nullable=False,default=True)
    notifyMorning = db.Column(notifyMorning_COL, db.Boolean, nullable=False,default=True)
    notifyStartWeek_sevev = db.Column("notifystartweek_sevev", db.Boolean, nullable=False,default=True)
    notifyDayBefore_sevev = db.Column("notifydaybefore_sevev", db.Boolean, nullable=False,default=True)
    notifyMorning_sevev = db.Column("notifymorning_sevev", db.Boolean, nullable=False,default=True)
    notifyMorning_weekly_report = db.Column("notifymorning_weekly_report", db.Boolean, nullable=False,default=True)


    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}