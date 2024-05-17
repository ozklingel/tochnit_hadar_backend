from . import *
from .city_model import City
from .cluster_model import Cluster
from .institution_model import Institution

from src.services import db
import datetime

class user1(db.Model):
    __tablename__ = USERS_TBL
    role_ids = db.Column("role_ids", nullable=False)

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
    eshcol = db.Column("eshcol", db.String(50), nullable=False,default="")
    association_date=db.Column("association_date", db.DateTime, nullable=False, default=datetime.date.today())


    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}




front_end_dict={
"cluster": "eshcol"
,"avatar":"photo_path",
"region":"cluster_id",
"institution":"institution_id",
"address":"address",
"city_id":"city_id",
"date_of_birth":"birthday",
"email":"email",
"teudatZehut":"teudatZehut",
"role": "role_ids",
"last_name":"last_name",
"firstName":"name",
"city":"city",


}