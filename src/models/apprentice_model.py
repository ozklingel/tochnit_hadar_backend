import datetime

from . import *

class Apprentice(db.Model):
    __tablename__ = APPRENTICES_TBL

    id = db.Column(ID_COL, db.Integer, primary_key=True, autoincrement=True, nullable=False)
    accompany_id = db.Column(ACCOMPANY_ID_COL, db.Integer, ForeignKey(get_forgein_key_source(USERS_TBL, ID_COL)), nullable=False)
    name = db.Column("first_name", db.String(50), nullable=False,default="")
    last_name = db.Column(LAST_NAME_COL, db.String(50), nullable=False,default="")
    phone = db.Column(PHONE_COL, db.String(50), nullable=False,default="")
    email = db.Column(EMAIL_COL, db.String(50), nullable=False,default="")
    birthday = db.Column(BIRTHDAY_COL, db.DateTime, nullable=True)
    eshcol = db.Column("eshcol", db.String(20), nullable=False,default="")
    marriage_status = db.Column("maritalstatus", db.String(20), nullable=False,default="")
    marriage_date = db.Column(MARRIAGE_DATE_COL, db.DateTime, nullable=True)
    contact1_email =db.Column("contact1_email", db.String(50), nullable=False,default="")
    contact1_first_name=db.Column("contact1_first_name", db.String(50), nullable=False,default="")
    contact1_last_name=db.Column("contact1_last_name", db.String(50), nullable=False,default="")
    contact1_phone=db.Column("contact1_phone", db.String(50), nullable=False,default="")
    contact1_relation=db.Column("contact1_relation", db.String(50), nullable=False,default="")

    contact2_email=db.Column("contact2_email", db.String(50), nullable=False,default="")
    contact2_phone=db.Column("contact2_phone", db.String(50), nullable=False,default="")
    contact2_first_name=db.Column("contact2_first_name", db.String(50), nullable=False,default="")
    contact2_last_name=db.Column("contact2_last_name", db.String(50), nullable=False,default="")
    contact2_relation=db.Column("contact2_relation", db.String(50), nullable=False,default="")

    contact3_phone    =db.Column("contact3_phone", db.String(50), nullable=False,default="")
    contact3_first_name=db.Column("contact3_first_name", db.String(50), nullable=False,default="")
    contact3_last_name=db.Column("contact3_last_name", db.String(50), nullable=False,default="")
    contact3_email=db.Column("contact3_email", db.String(50), nullable=False,default="")
    contact3_relation=db.Column("contact3_relation", db.String(50), nullable=False,default="")

    city_id = db.Column(CITY_ID_COL, db.Integer, ForeignKey(get_forgein_key_source(CITIES_TBL, ID_COL)), nullable=False,default=313)
    address = db.Column(ADDRESS_COL, db.String(50), nullable=False,default="")
    high_school_name = db.Column(HIGH_SCHOOL_NAME_COL, db.String(50), nullable=False,default="")
    high_school_teacher = db.Column(HIGH_SCHOOL_TEACHER_COL, db.String(50), nullable=False,default="")
    high_school_teacher_phone = db.Column(HIGH_SCHOOL_TEACHER_PHONE_COL, db.String(50), nullable=False,default="")
    highSchoolInstitution = db.Column("highschoolinstitution", db.String(50), nullable=False,default="")
    teacher_grade_a = db.Column(TEACHER_GRADE_A_COL, db.String(50), nullable=False,default="")
    teacher_grade_a_phone = db.Column(TEACHER_GRADE_A_PHONE_COL, db.String(50), nullable=False,default="")
    teacher_grade_b = db.Column(TEACHER_GRADE_B_COL, db.String(50), nullable=False,default="")
    teacher_grade_b_phone = db.Column(TEACHER_GRADE_B_PHONE_COL, db.String(50), nullable=False,default="")
    institution_id = db.Column(INSTITUTION_ID_COL, db.Integer, ForeignKey(get_forgein_key_source(INSTITUTIONS_TBL, ID_COL)), nullable=False,default=0)
    hadar_plan_session = db.Column("thperiod", db.String(10), nullable=False,default=0)#mahzor
    base_address = db.Column("militarycompoundid", db.Integer, nullable=False,default=14509)
    unit_name = db.Column(UNIT_NAME_COL, db.String(50), nullable=False,default="")
    army_role = db.Column(ARMY_ROLE_COL, db.String(50), nullable=False,default="")
    serve_type = db.Column(SERVE_TYPE_COL, db.String(50), nullable=False,default="")
    recruitment_date = db.Column(RECRUITMENT_DATE_COL, db.DateTime, nullable=True)
    release_date = db.Column(RELEASE_DATE_COL, db.DateTime, nullable=True)
    paying = db.Column(PAYING_COL, db.String(50), nullable=False,default="")
    spirit_status = db.Column("matsber", db.String(50), nullable=False,default="")
    accompany_connect_status = db.Column("onlinestatus", db.Integer, nullable=False,default=0)
    workstatus = db.Column(workStatus_COL, db.String(50), nullable=False,default="")
    workplace = db.Column(workPlace_COL, db.String(50), nullable=False,default="")
    worktype = db.Column(workType_COL, db.String(50), nullable=False,default="")
    workoccupation = db.Column(workOccupation_COL, db.String(50), nullable=False,default="")
    educationfaculty = db.Column(educationFaculty_COL, db.String(50), nullable=False,default="")
    educationalinstitution = db.Column(educationalInstitution_COL, db.String(50), nullable=False,default="")
    militaryPositionOld = db.Column(militaryPositionOld_COL, db.String(50), nullable=False,default="")
    militaryupdateddatetime=db.Column(militaryUpdatedDateTime_COL, db.DateTime, nullable=False,default="2022-01-01")
    high_school_teacher_email=db.Column(high_school_teacher_email_col, db.String(50), nullable=False,default="")
    teacher_grade_a_email=db.Column(teacher_grade_a_email_col, db.String(50), nullable=False,default="")
    teacher_grade_b_email=db.Column(teacher_grade_b_email_col, db.String(50), nullable=False,default="")
    teudatZehut = db.Column("teudatzehut", db.String(50), nullable=False,default="")
    institution_mahzor = db.Column("institution_mahzor", db.String(10), nullable=False,default="")
    photo_path=db.Column("photo_path", db.String(50), nullable=False,default="https://www.gravatar.com/avatar")
    militaryPositionNew=db.Column("militarypositionnew", db.String(50), nullable=False,default="")
    association_date=db.Column("association_date", db.DateTime, nullable=False, default=datetime.date.today())
    birthday_ivry=db.Column("birthday_ivry", db.String(50), nullable=False,default="ה' בטבת")
    marriage_date_ivry=db.Column("marriage_date_ivry", db.DateTime, nullable=True)


front_end_dict={
"address": "address",

"highSchoolRavMelamed_phone": "high_school_teacher_phone"
,"highSchoolRavMelamed_name":"high_school_teacher",
"highSchoolRavMelamed_email":"high_school_teacher_email",

"thRavMelamedYearA_name":"teacher_grade_a",
"thRavMelamedYearA_phone":"teacher_grade_a_phone",
"thRavMelamedYearA_email":"teacher_grade_a_email",

"thRavMelamedYearB_name":"teacher_grade_b",
"thRavMelamedYearB_phone":"teacher_grade_b_phone",
"thRavMelamedYearB_email":"teacher_grade_b_email",
"thMentor_id": "thMentor_id",
"contact1_first_name":"contact1_first_name",
"contact1_last_name":"contact1_last_name",
"contact1_phone":"contact1_phone",
"contact1_email":"contact1_email",
"contact1_relation":"contact1_relation",
"contact2_first_name":"contact2_first_name",
"contact2_last_name":"contact2_last_name",
"contact2_phone":"contact2_phone",
"contact2_email":"contact2_email",
"contact2_relation":"contact2_relation",
"contact3_first_name":"contact3_first_name",
"contact3_last_name":"contact3_last_name",
"contact3_phone":"contact3_phone",
"contact3_email":'contact3_email',
"contact3_relation":"contact3_relation",
"activity_score":"reportList",
"id":"id",
"thMentor_id":"thMentor_id",
"militaryPositionNew":"militaryPositionNew"
,"avatar":"photo_path",
"name":"name",
"last_name":"last_name",
"institution_id":"institution_id",
"thPeriod":"hadar_plan_session",
"serve_type":"serve_type",
"marriage_status":"marriage_status",
"militaryCompoundId":"base_id",
"phone":'id',"email":"email",
"teudatZehut":"teudatZehut",
"birthday":"birthday",
"marriage_date":"marriage_date",
"highSchoolInstitution":"highSchoolInstitution",
"army_role":"army_role",
"militaryUnit":"unit_name",
"matsber":"spirit_status",
"militaryDateOfDischarge":"release_date",
"militaryDateOfEnlistment":"recruitment_date"
,"militaryUpdatedDateTime":"militaryupdateddatetime",
"militaryPositionOld":"militaryPositionOld",
"educationalInstitution":"educationalinstitution"
,"educationFaculty":"educationfaculty",
"workOccupation":"workoccupation",
"workType":"worktype",
"workPlace":"workplace",
"workStatus":"workstatus",
"paying":"paying"
}