import datetime

from sqlalchemy import ForeignKey

from src.models.models_defines import *
from src.models.models_utils import get_foreign_key_source, to_iso
from src.services import db


class Apprentice(db.Model):
    __tablename__ = APPRENTICES_TBL

    id = db.Column(ID_COL, db.Integer, primary_key=True, autoincrement=True, nullable=False)
    accompany_id = db.Column(ACCOMPANY_ID_COL, db.Integer, ForeignKey(get_foreign_key_source(USERS_TBL, ID_COL)),nullable=False)
    name = db.Column("first_name", db.String(50), nullable=False, default="")
    last_name = db.Column(LAST_NAME_COL, db.String(50), nullable=False, default="")
    phone = db.Column(PHONE_COL, db.String(50), nullable=False, default="")
    email = db.Column(EMAIL_COL, db.String(50), nullable=False, default="")
    birthday = db.Column(BIRTHDAY_COL, db.DateTime, nullable=True)
    cluster_id = db.Column("eshcol", db.String(20), nullable=False, default="")
    marriage_status = db.Column("maritalstatus", db.String(20), nullable=False, default="")
    marriage_date = db.Column(MARRIAGE_DATE_COL, db.DateTime, nullable=True)
    contact1_email = db.Column("contact1_email", db.String(50), nullable=False, default="")
    contact1_first_name = db.Column("contact1_first_name", db.String(50), nullable=False, default="")
    contact1_last_name = db.Column("contact1_last_name", db.String(50), nullable=False, default="")
    contact1_phone = db.Column("contact1_phone", db.String(50), nullable=False, default="")
    contact1_relation = db.Column("contact1_relation", db.String(50), nullable=False, default="")
    contact2_email = db.Column("contact2_email", db.String(50), nullable=False, default="")
    contact2_phone = db.Column("contact2_phone", db.String(50), nullable=False, default="")
    contact2_first_name = db.Column("contact2_first_name", db.String(50), nullable=False, default="")
    contact2_last_name = db.Column("contact2_last_name", db.String(50), nullable=False, default="")
    contact2_relation = db.Column("contact2_relation", db.String(50), nullable=False, default="")
    contact3_phone = db.Column("contact3_phone", db.String(50), nullable=False, default="")
    contact3_first_name = db.Column("contact3_first_name", db.String(50), nullable=False, default="")
    contact3_last_name = db.Column("contact3_last_name", db.String(50), nullable=False, default="")
    contact3_email = db.Column("contact3_email", db.String(50), nullable=False, default="")
    contact3_relation = db.Column("contact3_relation", db.String(50), nullable=False, default="")
    city_id = db.Column(CITY_ID_COL, db.Integer, ForeignKey(get_foreign_key_source(CITIES_TBL, ID_COL)), nullable=True)
    address = db.Column(ADDRESS_COL, db.String(50), nullable=False, default="")
    high_school_name = db.Column(HIGH_SCHOOL_NAME_COL, db.String(50), nullable=False, default="")
    high_school_teacher = db.Column(HIGH_SCHOOL_TEACHER_COL, db.String(50), nullable=False, default="")
    high_school_teacher_phone = db.Column(HIGH_SCHOOL_TEACHER_PHONE_COL, db.String(50), nullable=False, default="")
    highSchoolInstitution = db.Column("highschoolinstitution", db.String(50), nullable=False, default="")
    teacher_grade_a = db.Column(TEACHER_GRADE_A_COL, db.String(50), nullable=False, default="")
    teacher_grade_a_phone = db.Column(TEACHER_GRADE_A_PHONE_COL, db.String(50), nullable=False, default="")
    teacher_grade_b = db.Column(TEACHER_GRADE_B_COL, db.String(50), nullable=False, default="")
    teacher_grade_b_phone = db.Column(TEACHER_GRADE_B_PHONE_COL, db.String(50), nullable=False, default="")
    institution_id = db.Column(INSTITUTION_ID_COL, db.Integer,ForeignKey(get_foreign_key_source(INSTITUTIONS_TBL, ID_COL)), nullable=False, default=0)
    hadar_plan_session = db.Column("thperiod", db.String(10), nullable=False, default=0)  # mahzor
    base_address = db.Column("militarycompoundid", db.Integer, nullable=False, default=14509)
    recruitment_date = db.Column(RECRUITMENT_DATE_COL, db.DateTime, nullable=True)
    release_date = db.Column(RELEASE_DATE_COL, db.DateTime, nullable=True)
    paying = db.Column(PAYING_COL, db.String(50), nullable=False, default="")
    spirit_status = db.Column("matsber", db.String(50), nullable=False, default="")
    accompany_connect_status = db.Column("onlinestatus", db.Integer, nullable=False, default=0)
    workstatus = db.Column(WORK_STATUS_COL, db.String(50), nullable=False, default="")
    workplace = db.Column(WORK_PLACE_COL, db.String(50), nullable=False, default="")
    worktype = db.Column(WORK_TYPE_COL, db.String(50), nullable=False, default="")
    workoccupation = db.Column(WORK_OCCUPATION_COL, db.String(50), nullable=False, default="")
    educationfaculty = db.Column(EDUCATION_FACULTY_COL, db.String(50), nullable=False, default="")
    educationalinstitution = db.Column(EDUCATIONAL_INSTITUTION_COL, db.String(50), nullable=False, default="")
    militaryPositionOld = db.Column(MILITARY_POSITION_OLD_COL, db.String(50), nullable=False, default="")
    militaryupdateddatetime = db.Column(MILITARY_UPDATED_DATETIME_COL, db.DateTime, nullable=False, default="2022-01-01")
    high_school_teacher_email = db.Column(HIGH_SCHOOL_TEACHER_EMAIL_COL, db.String(50), nullable=False, default="")
    teacher_grade_a_email = db.Column(TEACHER_GRADE_A_EMAIL_COL, db.String(50), nullable=False, default="")
    teacher_grade_b_email = db.Column(TEACHER_GRADE_B_EMAIL_COL, db.String(50), nullable=False, default="")
    teudatZehut = db.Column("teudatzehut", db.String(50), nullable=False, default="")
    institution_mahzor = db.Column("institution_mahzor", db.String(10), nullable=False, default="")
    photo_path = db.Column("photo_path", db.String(50), nullable=False, default="https://www.gravatar.com/avatar")
    association_date = db.Column("association_date", db.DateTime, nullable=False, default=datetime.date.today())
    birthday_ivry = db.Column("birthday_ivry", db.String(50), nullable=False, default="ה' בטבת")
    marriage_date_ivry = db.Column("marriage_date_ivry", db.DateTime, nullable=True)
    militaryPositionNew = db.Column("militarypositionnew", db.String(50), nullable=False, default="")  # מפקד כיתה
    serve_type = db.Column(SERVE_TYPE_COL, db.String(50), nullable=False, default="")  # קבע
    army_role = db.Column(ARMY_ROLE_COL, db.String(50), nullable=False, default="")  # סיירות
    unit_name = db.Column(UNIT_NAME_COL, db.String(50), nullable=False, default="")  # צנחנים

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def to_attributes(self):
        return {
            "id": str(self.id),
            "contact1_email": self.contact1_email,
            "marriage_date": self.marriage_date,
            "marriage_status": self.marriage_status,
            "cluster_id": self.cluster_id,
            "birthday": self.birthday,
            "email": self.email,
            "phone": self.phone,
            "last_name": self.last_name,
            "name": self.name,
            "accompany_id": self.accompany_id,
            "contact3_phone": self.contact3_phone,
            "contact2_relation": self.contact2_relation,
            "contact2_last_name": self.contact2_last_name,
            "contact2_first_name": self.contact2_first_name,
            "contact2_phone": self.contact2_phone,
            "contact2_email": self.contact2_email,
            "contact1_relation": self.contact1_relation,
            "contact1_phone": self.contact1_phone,
            "contact1_last_name": self.contact1_last_name,
            "contact1_first_name": self.contact1_first_name,
            "highSchoolInstitution": self.highSchoolInstitution,
            "high_school_teacher_phone": self.high_school_teacher_phone,
            "high_school_teacher": self.high_school_teacher,
            "high_school_name": self.high_school_name,
            "address": self.address,
            "city_id": self.city_id,
            "contact3_relation": self.contact3_relation,
            "contact3_email": self.contact3_email,
            "contact3_last_name": self.contact3_last_name,
            "contact3_first_name": self.contact3_first_name,
            "paying": self.paying,
            "release_date": self.release_date,
            "recruitment_date": self.recruitment_date,
            "base_address": self.base_address,
            "hadar_plan_session": self.hadar_plan_session,
            "institution_id": self.institution_id,
            "teacher_grade_b_phone": self.teacher_grade_b_phone,
            "teacher_grade_b": self.teacher_grade_b,
            "teacher_grade_a_phone": self.teacher_grade_a_phone,
            "teacher_grade_a": self.teacher_grade_a,
            "high_school_teacher_email": self.high_school_teacher_email,
            "militaryupdateddatetime": self.militaryupdateddatetime,
            "militaryPositionOld": self.militaryPositionOld,
            "educationalinstitution": self.educationalinstitution,
            "educationfaculty": self.educationfaculty,
            "workoccupation": self.workoccupation,
            "worktype": self.worktype,
            "workplace": self.workplace,
            "workstatus": self.workstatus,
            "accompany_connect_status": self.accompany_connect_status,
            "serve_type": self.serve_type,
            "militaryPositionNew": self.militaryPositionNew,
            "marriage_date_ivry": self.marriage_date_ivry,
            "birthday_ivry": self.birthday_ivry,
            "association_date": self.association_date,
            "photo_path": self.photo_path,
            "institution_mahzor": self.institution_mahzor,
            "teudatZehut": self.teudatZehut,
            "teacher_grade_b_email": self.teacher_grade_b_email,
            "teacher_grade_a_email": self.teacher_grade_a_email,
            "army_role": self.army_role,
            "unit_name": self.unit_name,

        }
front_end_dict = {
    "address": "address",

    "highSchoolRavMelamed_phone": "high_school_teacher_phone",
    "highSchoolRavMelamed_name": "high_school_teacher",
    "highSchoolRavMelamed_email": "high_school_teacher_email",

    "thRavMelamedYearA_name": "teacher_grade_a",
    "thRavMelamedYearA_phone": "teacher_grade_a_phone",
    "thRavMelamedYearA_email": "teacher_grade_a_email",

    "thRavMelamedYearB_name": "teacher_grade_b",
    "thRavMelamedYearB_phone": "teacher_grade_b_phone",
    "thRavMelamedYearB_email": "teacher_grade_b_email",
    "thMentor_id": "thMentor_id",
    "contact1_first_name": "contact1_first_name",
    "contact1_last_name": "contact1_last_name",
    "contact1_phone": "contact1_phone",
    "contact1_email": "contact1_email",
    "contact1_relation": "contact1_relation",
    "contact2_first_name": "contact2_first_name",
    "contact2_last_name": "contact2_last_name",
    "contact2_phone": "contact2_phone",
    "contact2_email": "contact2_email",
    "contact2_relation": "contact2_relation",
    "contact3_first_name": "contact3_first_name",
    "contact3_last_name": "contact3_last_name",
    "contact3_phone": "contact3_phone",
    "contact3_email": 'contact3_email',
    "contact3_relation": "contact3_relation",
    "activity_score": "reportList",
    "id": "id",
    "militaryPositionNew": "militaryPositionNew",
    "avatar": "photo_path",
    "name": "name",
    "last_name": "last_name",
    "institution_id": "institution_id",
    "thPeriod": "hadar_plan_session",
    "serve_type": "serve_type",
    "marriage_status": "marriage_status",
    "militaryCompoundId": "base_address",
    "phone": 'id',
    "email": "email",
    "teudatZehut": "teudatZehut",
    "birthday": "birthday",
    "marriage_date": "marriage_date",
    "highSchoolInstitution": "highSchoolInstitution",
    "army_role": "army_role",
    "militaryUnit": "unit_name",
    "matsber": "spirit_status",
    "militaryDateOfDischarge": "release_date",
    "militaryDateOfEnlistment": "recruitment_date",
    "militaryUpdatedDateTime": "militaryupdateddatetime",
    "militaryPositionOld": "militaryPositionOld",
    "educationalInstitution": "educationalinstitution",
    "educationFaculty": "educationfaculty",
    "workOccupation": "workoccupation",
    "workType": "worktype",
    "workPlace": "workplace",
    "workStatus": "workstatus",
    "paying": "paying"
}