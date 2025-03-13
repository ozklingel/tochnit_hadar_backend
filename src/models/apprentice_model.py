import datetime

from sqlalchemy import ForeignKey

from src.models.models_defines import *
from src.models.models_utils import get_foreign_key_source, to_iso
from src.services import db


class Apprentice(db.Model):
    __tablename__ = APPRENTICES_TBL

    id = db.Column(
        ID_COL, db.Integer, primary_key=True, autoincrement=True, nullable=False
    )
    accompany_id = db.Column(
        ACCOMPANY_ID_COL,
        db.Integer,
        ForeignKey(get_foreign_key_source(USERS_TBL, ID_COL)),
        nullable=False,
    )
    name = db.Column("first_name", db.String(50), nullable=False, default="")
    last_name = db.Column(LAST_NAME_COL, db.String(50), nullable=False, default="")
    phone = db.Column(PHONE_COL, db.String(50), nullable=False, default="")
    email = db.Column(EMAIL_COL, db.String(50), nullable=False, default="")
    birthday = db.Column(BIRTHDAY_COL, db.DateTime, nullable=True)
    marriage_status = db.Column(
        "maritalstatus", db.String(20), nullable=False, default=""
    )
    marriage_date = db.Column(MARRIAGE_DATE_COL, db.DateTime, nullable=True)
    contact1_email = db.Column(
        "contact1_email", db.String(50), nullable=False, default=""
    )
    contact1_first_name = db.Column(
        "contact1_first_name", db.String(50), nullable=False, default=""
    )
    contact1_last_name = db.Column(
        "contact1_last_name", db.String(50), nullable=False, default=""
    )
    contact1_phone = db.Column(
        "contact1_phone", db.String(50), nullable=False, default=""
    )
    contact1_relation = db.Column(
        "contact1_relation", db.String(50), nullable=False, default=""
    )
    contact2_email = db.Column(
        "contact2_email", db.String(50), nullable=False, default=""
    )
    contact2_phone = db.Column(
        "contact2_phone", db.String(50), nullable=False, default=""
    )
    contact2_first_name = db.Column(
        "contact2_first_name", db.String(50), nullable=False, default=""
    )
    contact2_last_name = db.Column(
        "contact2_last_name", db.String(50), nullable=False, default=""
    )
    contact2_relation = db.Column(
        "contact2_relation", db.String(50), nullable=False, default=""
    )
    contact3_phone = db.Column(
        "contact3_phone", db.String(50), nullable=False, default=""
    )
    contact3_first_name = db.Column(
        "contact3_first_name", db.String(50), nullable=False, default=""
    )
    contact3_last_name = db.Column(
        "contact3_last_name", db.String(50), nullable=False, default=""
    )
    contact3_email = db.Column(
        "contact3_email", db.String(50), nullable=False, default=""
    )
    contact3_relation = db.Column(
        "contact3_relation", db.String(50), nullable=False, default=""
    )
    city_id = db.Column(
        CITY_ID_COL,
        db.Integer,
        ForeignKey(get_foreign_key_source(CITIES_TBL, ID_COL)),
        nullable=True,
    )
    address = db.Column(ADDRESS_COL, db.String(50), nullable=False, default="")
    high_school_name = db.Column(  ###not in use?
        HIGH_SCHOOL_NAME_COL, db.String(50), nullable=False, default=""
    )
    high_school_teacher = db.Column(
        HIGH_SCHOOL_TEACHER_COL, db.String(50), nullable=False, default=""
    )
    high_school_teacher_phone = db.Column(
        HIGH_SCHOOL_TEACHER_PHONE_COL, db.String(50), nullable=False, default=""
    )
    teacher_grade_a = db.Column(
        TEACHER_GRADE_A_COL, db.String(50), nullable=False, default=""
    )
    teacher_grade_a_phone = db.Column(
        TEACHER_GRADE_A_PHONE_COL, db.String(50), nullable=False, default=""
    )
    teacher_grade_b = db.Column(
        TEACHER_GRADE_B_COL, db.String(50), nullable=False, default=""
    )
    teacher_grade_b_phone = db.Column(
        TEACHER_GRADE_B_PHONE_COL, db.String(50), nullable=False, default=""
    )
    institution_id = db.Column(
        INSTITUTION_ID_COL,
        db.Integer,
        ForeignKey(get_foreign_key_source(INSTITUTIONS_TBL, ID_COL)),
        nullable=False,
    )
    hadar_plan_session = db.Column("thperiod", db.String(10), nullable=False)  # mahzor
    base_address = db.Column(
        "militarycompoundid",
        db.Integer,
        nullable=True,
    )
    recruitment_date = db.Column(RECRUITMENT_DATE_COL, db.DateTime, nullable=True)
    release_date = db.Column(RELEASE_DATE_COL, db.DateTime, nullable=True)
    paying = db.Column(PAYING_COL, db.Boolean, nullable=False, default=False)
    spirit_status = db.Column("matsber", db.String(50), nullable=False, default="")
    accompany_connect_status = db.Column(
        "onlinestatus", db.Integer, nullable=False, default=0
    )
    workstatus = db.Column(WORK_STATUS_COL, db.String(50), nullable=False, default="")
    workplace = db.Column(WORK_PLACE_COL, db.String(50), nullable=False, default="")
    worktype = db.Column(WORK_TYPE_COL, db.String(50), nullable=False, default="")
    workoccupation = db.Column(
        WORK_OCCUPATION_COL, db.String(50), nullable=False, default=""
    )
    educationfaculty = db.Column(
        EDUCATION_FACULTY_COL, db.String(50), nullable=False, default=""
    )
    educationalinstitution = db.Column(
        EDUCATIONAL_INSTITUTION_COL, db.String(50), nullable=False, default=""
    )
    militaryPositionOld = db.Column(
        MILITARY_POSITION_OLD_COL, db.String(50), nullable=False, default=""
    )
    militaryupdateddatetime = db.Column(
        MILITARY_UPDATED_DATETIME_COL,
        db.DateTime,
        nullable=True,
    )
    high_school_teacher_email = db.Column(
        HIGH_SCHOOL_TEACHER_EMAIL_COL, db.String(50), nullable=False, default=""
    )
    teacher_grade_a_email = db.Column(
        TEACHER_GRADE_A_EMAIL_COL, db.String(50), nullable=False, default=""
    )
    teacher_grade_b_email = db.Column(
        TEACHER_GRADE_B_EMAIL_COL, db.String(50), nullable=False, default=""
    )
    teudatZehut = db.Column("teudatzehut", db.String(50), nullable=False, default="")
    institution_mahzor = db.Column(
        "institution_mahzor", db.String(10), nullable=False, default=""
    )
    photo_path = db.Column(
        "photo_path",
        db.String(50),
        nullable=False,
        default="https://www.gravatar.com/avatar",
    )
    association_date = db.Column(
        "association_date", db.DateTime, nullable=False, default=datetime.date.today()
    )
    birthday_ivry = db.Column("birthday_ivry", db.String(50), nullable=True)
    marriage_date_ivry = db.Column("marriage_date_ivry", db.String(50), nullable=True)
    militaryPositionNew = db.Column(
        "militarypositionnew", db.String(50), nullable=True, default=""
    )  # מפקד כיתה
    serve_type = db.Column(
        SERVE_TYPE_COL, db.String(50), nullable=True, default=""
    )  # קבע
    army_role = db.Column(
        ARMY_ROLE_COL, db.String(50), nullable=True, default=""
    )  # סיירות
    unit_name = db.Column(
        UNIT_NAME_COL, db.String(50), nullable=True, default=""
    )  # צנחנים
    cluster_id = db.Column("cluster_id", db.Integer, nullable=False)
    house_number = db.Column("house_number", db.Integer, nullable=False)
