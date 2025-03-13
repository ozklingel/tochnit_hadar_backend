import uuid
from src.services import db
from sqlalchemy.dialects.postgresql import UUID


class SystemReport(db.Model):
    __tablename__ = "system_report"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creation_date = db.Column("creation_date", db.DateTime, nullable=False)
    type = db.Column("type", db.String(20), nullable=False)
    related_id = db.Column("related_id", db.Integer, nullable=False)
    value = db.Column("value", db.String(20), nullable=False)


###################דוחות################

# melave
visitmeets_melave_avg = "meets_melave_avg"
visitcalls_melave_avg = "calls_melave_avg"
forgotenApprentice_cnt_melave = "forgoten_apprentice_melave_cnt"
proffesionalMeet_presence_melave = "professional_meet_melave_presence"
cenes_presence_melave = "cenes_melave_presence"
melave_Score = "melave_Score"
basis_meeting_melave = "basis_meeting_melave_cnt"  # num of meeting per year
horim_meeting_melave = "horim_meeting_melave_cnt"  # num of meeting per year
# mosad
visitmeets_mosad_avg = "meets_mosad_avg"
visitcalls_mosad_avg = "calls_mosad_avg"
proffesionalMeet_presence_mosad = "professional_meet_presence_mosad"
matzbarMeeting_gap_mosad = "matzbar_meeting_gap_mosad"
matzbar_apprentice_status_mosad = "matzbar_apprentice_status_mosad"
avg_groupMeeting_gap = "avg_group_meeting_gap"
apprenticeCall_gap_mosad = "apprentice_call_gap_mosad"
apprenticeMeeting_gap_mosad = "apprentice_meeting_gap_mosad"
forgotenApprentice_cnt_mosad_rivony = "forgoten_apprentice_cnt_mosad_rivony"
apprentice_forgoten_cnt_mosad_monthly = "apprentice_forgoten_cnt_mosad_monthly"
# eshcol
mosad_eshcol_meeting = "mosad_eshcol_meeting"
forgotenApprentice_cnt_eshcol = "forgoten_apprentice_cnt_eshcol"
# tochnit
spirit_status_tochnit = "spirit_status_tochnit"
# madadim
lowScoreApprentice_tochnit_csv = "low_score_apprentice_tochnit_csv"
# מוסד,פערי מפגש,פערי שיחה,ציון נמוך,כמות חניכים
# לוד,0,0,0,0
# יתיר,0,0,0,0
lowScoreApprentice_mosad_csv = "low_score_apprentice_mosad_csv"
# מוסד,פערי מפגש,פערי שיחה,ציון נמוך,כמות חניכים
# בני דוד - עלי,544,0,544,544
eshcol_corrdintors_score_csv = "eshcol_corrdintors_score_csv"
# שם,ציון
# ינון שטינפלד,40
forgotenApprentice_mosad_csv = "forgoten_apprentice_mosad_csv"
# שם,שם מוסד,
# אבגי הראל,בני דוד - עלי
forgotenApprentice_tochnit_scv = "forgoten_apprentice_tochnit_scv"
# שם,כמות
# בני דוד - עלי,544
melave_score_csv = "melave_score_csv"
# שם,מוסד,ציון
# טל גופר,בני דוד - עלי,20
mosad_melavim_cnt_csv = "mosad_melavim_cnt_csv"
# מוסד,כמות
# בני דוד - עלי,22
mosad_corrdintors_score_csv = "mosad_corrdintors_score_csv"
# שם,ציון,פלאפון
# לירן גרובס,506795170,36.0

mosadot_score = "mosadot_score"


forgotenApprentice_list = "דוח דו שבועי-חניכים נשכחים"
melave_Score_list = "דוח  חודשי- ציון מלווים"
low_score_65_list = "דוח רכזים תחת ציון 65"
mosdot_score_list = "עידכון חודשי-ציון מוסדות"
