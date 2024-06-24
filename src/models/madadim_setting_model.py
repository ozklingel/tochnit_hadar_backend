from src.services import db


# דיוחחים על משתמש או חניך
class MadadimSetting(db.Model):
    __tablename__ = "madadim_setting"

    professionalMeet_madad_date = db.Column("professionalmeet_madad_date", db.DateTime, nullable=False)
    matzbarmeet_madad_date = db.Column("matzbarmeet_madad_date", db.DateTime, nullable=False)
    doForBogrim_madad_date = db.Column("doforbogrim_madad_date", db.DateTime, nullable=False)
    basis_madad_date = db.Column("basis_madad_date", db.DateTime, nullable=False)
    callHorim_madad_date = db.Column("callhorim_madad_date", db.DateTime, nullable=False)
    groupMeet_madad_date = db.Column("groupmeet_madad_date", db.DateTime, nullable=False)
    meet_madad_date = db.Column("meet_madad_date", db.DateTime, nullable=False)
    call_madad_date = db.Column("call_madad_date", db.DateTime, nullable=False)
    cenes_madad_date = db.Column("cenes_madad_date", db.DateTime, nullable=False)
    tochnitMeet_madad_date = db.Column("tochnitmeet_madad_date", db.DateTime, nullable=False)
    eshcolMosadMeet_madad_date = db.Column("eshcolmosadmeet_madad_date", db.DateTime, nullable=False)
    mosadYeshiva_madad_date = db.Column("mosadyeshiva_madad_date", db.DateTime, nullable=False)
    hazana_madad_date = db.Column("hazana_madad_date", db.DateTime, primary_key=True, nullable=False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def to_attributes(self):
        return {
            "doForBogrim_madad_date": self.doForBogrim_madad_date,
            "matzbarmeet_madad_date": self.matzbarmeet_madad_date,
            "professionalMeet_madad_date": self.professionalMeet_madad_date,
            "groupMeet_madad_date": self.groupMeet_madad_date,
            "callHorim_madad_date": self.callHorim_madad_date,
            "basis_madad_date": self.basis_madad_date,
            "cenes_madad_date": self.cenes_madad_date,
            "call_madad_date": self.call_madad_date,
            "meet_madad_date": self.meet_madad_date,
            "eshcolMosadMeet_madad_date": self.eshcolMosadMeet_madad_date,
            "tochnitMeet_madad_date": self.tochnitMeet_madad_date,
            "hazana_madad_date": self.hazana_madad_date,
            "mosadYeshiva_madad_date": self.mosadYeshiva_madad_date,


        }