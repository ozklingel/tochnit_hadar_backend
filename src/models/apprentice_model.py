from . import *

class Apprentice(db.Model):
    __tablename__ = APPRENTICES_TBL

    id = db.Column(ID_COL, db.Integer, primary_key=True, autoincrement=True, nullable=False)
    accompany_id = db.Column(ACCOMPANY_ID_COL, db.Integer, ForeignKey(get_forgein_key_source(USERS_TBL, ID_COL)), nullable=False)
    name = db.Column("first_name", db.String(50), nullable=False,default="")
    last_name = db.Column(LAST_NAME_COL, db.String(50), nullable=False,default="")
    phone = db.Column(PHONE_COL, db.String(50), nullable=False,default="")
    email = db.Column(EMAIL_COL, db.String(50), nullable=False,default="")
    birthday = db.Column(BIRTHDAY_COL, db.DateTime, nullable=False)
    marriage_status = db.Column("maritalstatus", db.String(20), nullable=False,default="")
    marriage_date = db.Column(MARRIAGE_DATE_COL, db.DateTime, nullable=False,default="2022-01-01")
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
    hadar_plan_session = db.Column("thperiod", db.Integer, nullable=False,default=0)#mahzor
    base_address = db.Column("militarycompoundid", db.String(50), nullable=False,default="")
    unit_name = db.Column(UNIT_NAME_COL, db.String(50), nullable=False,default="")
    army_role = db.Column(ARMY_ROLE_COL, db.Integer, nullable=False,default=0)
    serve_type = db.Column(SERVE_TYPE_COL, db.String(50), nullable=False,default=0)
    recruitment_date = db.Column(RECRUITMENT_DATE_COL, db.DateTime, nullable=False,default="2022-01-01")
    release_date = db.Column(RELEASE_DATE_COL, db.DateTime, nullable=False,default="2022-01-01")
    paying = db.Column(PAYING_COL, db.Boolean, nullable=False,default=False)
    spirit_status = db.Column("matsber", db.Integer, nullable=False,default=0)
    accompany_connect_status = db.Column("onlinestatus", db.Integer, nullable=False,default=0)
    workstatus = db.Column(workStatus_COL, db.String(50), nullable=False,default="")
    workplace = db.Column(workPlace_COL, db.String(50), nullable=False,default="")
    worktype = db.Column(workType_COL, db.String(50), nullable=False,default="")
    workoccupation = db.Column(workOccupation_COL, db.String(50), nullable=False,default="")
    educationfaculty = db.Column(educationFaculty_COL, db.String(50), nullable=False,default="")
    educationalinstitution = db.Column(educationalInstitution_COL, db.String(50), nullable=False,default="")
    militarypositionold = db.Column(militaryPositionOld_COL, db.String(50), nullable=False,default="")
    militaryupdateddatetime=db.Column(militaryUpdatedDateTime_COL, db.DateTime, nullable=False,default="2022-01-01")
    high_school_teacher_email=db.Column(high_school_teacher_email_col, db.String(50), nullable=False,default="")
    teacher_grade_a_email=db.Column(teacher_grade_a_email_col, db.String(50), nullable=False,default="")
    teacher_grade_b_email=db.Column(teacher_grade_b_email_col, db.String(50), nullable=False,default="")
    teudatZehut = db.Column("teudatzehut", db.String(20), nullable=False,default="")
    institution_mahzor = db.Column("institution_mahzor", db.String(10), nullable=False,default="")
    photo_path=db.Column("photo_path", db.String(50), nullable=False,default="")
    militaryPositionNew=db.Column("militarypositionnew", db.String(50), nullable=False,default="")
