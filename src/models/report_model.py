import uuid
from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from src.models.models_defines import (
    VISIT_DATE_COL,
    USER_ID_COL,
    VISIT_IN_ARMY_COL,
    NOTE_COL,
    TITLE_COL,
    ALREADY_READ,
)
from src.services import db
from . import to_iso
from .user_model import User


# דיוחחים על משתמש או חניך
class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ent_reported = db.Column("ent_reported", db.Integer, nullable=False)
    visit_date = db.Column(VISIT_DATE_COL, db.DateTime, nullable=False)
    user_id = db.Column(USER_ID_COL, db.Integer, ForeignKey(User.id), nullable=False)
    visit_in_army = db.Column(
        VISIT_IN_ARMY_COL, db.Boolean, nullable=False, default=False
    )
    note = db.Column(NOTE_COL, db.String(50), nullable=True, default="")
    title = db.Column(TITLE_COL, db.String(50), nullable=True, default="")
    allreadyread = db.Column(ALREADY_READ, db.Boolean, nullable=True, default=False)
    attachments = db.Column("attachments", nullable=True, default=[])
    description = db.Column("description", db.String(100), nullable=True, default="")
    ent_group = db.Column(db.String(100), nullable=True, default="")
    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.now().strftime("%Y%m%d %H%M%S")
    )

    def to_attributes(self, search_token, reported_on):
        return {
            "reported_on": reported_on,
            "search": search_token,
            "id": str(self.id),
            "date": to_iso(self.visit_date),
            "user_id": str(self.user_id),
            "title": self.title,
            "allreadyread": str(self.allreadyread),
            "attachments": self.attachments,
            "description": self.description,
            "ent_group": self.ent_group,
            "creation_date": str(self.created_at),
        }


call_report = "שיחה טלפונית"
zoom_report = "פגישה מקוונת"
fiveMess_report = "5 הודעות"
failCall_report = "נסיון כושל"
personalMeet_report = "פגישה פיזית"
groupMeet_report = "מפגש קבוצתי"
basis_report = "ביקור בבסיס"
HorimCall_report = "שיחה להורים"

matzbar_report = "ישיבת מצב”ר"  # 3 חודשים
hazanatMachzor_report = "הזנת מחזור"
mahzorMeeting_report = "מפגש מחזור"
mahzorShabat_report = "שבת מחזור"
doForBogrim_report = "עשייה לבוגרים"
professional_report = "כנס מלווים מקצועי חודשי"  # 2 חודשים
MelavimMeeting_report = "ישיבה מוסדית"  # 1 חודשים

MOsadEshcolMeeting_report = "ישיבה עם רכז"
tochnitMeeting_report = "ישיבת רכזים ומלווים באשכול"
cenes_report = "כנס מלווים שנתי"

mosad_reports = [
    MelavimMeeting_report,
    matzbar_report,
    hazanatMachzor_report,
    doForBogrim_report,
    professional_report,
]
eshcol_reports = [MOsadEshcolMeeting_report, tochnitMeeting_report, cenes_report]
reports_as_call = [call_report, zoom_report, fiveMess_report]
report_as_meet = [personalMeet_report, groupMeet_report, basis_report]
report_as_DoForBogrim = [mahzorShabat_report, mahzorMeeting_report, doForBogrim_report]
report_as_group = [
    MelavimMeeting_report,
    hazanatMachzor_report,
    doForBogrim_report,
    professional_report,
    tochnitMeeting_report,
    groupMeet_report,
    basis_report,
    mahzorShabat_report,
    mahzorMeeting_report,
    doForBogrim_report,
]
all_reports = [
    tochnitMeeting_report,
    cenes_report,
    MOsadEshcolMeeting_report,
    doForBogrim_report,
    hazanatMachzor_report,
    matzbar_report,
    professional_report,
    mahzorMeeting_report,
    mahzorShabat_report,
    MelavimMeeting_report,
    zoom_report,
    call_report,
    HorimCall_report,
    basis_report,
    groupMeet_report,
    personalMeet_report,
    failCall_report,
    fiveMess_report,
]
