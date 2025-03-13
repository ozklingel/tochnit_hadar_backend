from src.services import db


# דיוחחים על משתמש או חניך
class MadadimSetting(db.Model):
    __tablename__ = "madadim_setting"

    professionalMeet_madad_date = db.Column(
        "professionalmeet_madad_date", db.DateTime, nullable=False
    )
    matzbarmeet_madad_date = db.Column(
        "matzbarmeet_madad_date", db.DateTime, nullable=False
    )
    doForBogrim_madad_date = db.Column(
        "doforbogrim_madad_date", db.DateTime, nullable=False
    )
    basis_madad_date = db.Column("basis_madad_date", db.DateTime, nullable=False)
    callHorim_madad_date = db.Column(
        "callhorim_madad_date", db.DateTime, nullable=False
    )
    groupMeet_madad_date = db.Column(
        "groupmeet_madad_date", db.DateTime, nullable=False
    )
    meet_madad_date = db.Column("meet_madad_date", db.DateTime, nullable=False)
    call_madad_date = db.Column("call_madad_date", db.DateTime, nullable=False)
    cenes_madad_date = db.Column("cenes_madad_date", db.DateTime, nullable=False)
    tochnitMeet_madad_date = db.Column(
        "tochnitmeet_madad_date", db.DateTime, nullable=False
    )
    eshcolMosadMeet_madad_date = db.Column(
        "eshcolmosadmeet_madad_date", db.DateTime, nullable=False
    )
    mosadYeshiva_madad_date = db.Column(
        "mosadyeshiva_madad_date", db.DateTime, nullable=False
    )
    hazana_madad_date = db.Column(
        "hazana_madad_date", db.DateTime, primary_key=True, nullable=False
    )
