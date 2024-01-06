from . import *

class Apprentice(db.Model):
    __tablename__ = APPRENTICES_TBL

    id = db.Column(ID_COL, db.Integer, primary_key=True, autoincrement=True, nullable=True)
    accompany_id = db.Column(ACCOMPANY_ID_COL, db.Integer, ForeignKey(get_forgein_key_source(USERS_TBL, ID_COL)), nullable=True)
    name = db.Column("first_name", db.String(50), nullable=True)
    last_name = db.Column(LAST_NAME_COL, db.String(50), nullable=True)
    phone = db.Column(PHONE_COL, db.String(50), nullable=True)
    email = db.Column(EMAIL_COL, db.String(50), nullable=True)
    birthday = db.Column(BIRTHDAY_COL, db.DateTime, nullable=True)
    marriage_status = db.Column("maritalstatus", db.String(20), nullable=True)
    marriage_date = db.Column(MARRIAGE_DATE_COL, db.DateTime, nullable=True)
    contact1_email =db.Column("contact1_email", db.String(50), nullable=True)
    contact1_first_name=db.Column("contact1_first_name", db.String(50), nullable=True)
    contact1_last_name=db.Column("contact1_last_name", db.String(50), nullable=True)
    contact1_phone=db.Column("contact1_phone", db.String(50), nullable=True)
    contact1_relation=db.Column("contact1_relation", db.String(50), nullable=True)

    contact2_email=db.Column("contact2_email", db.String(50), nullable=True)
    contact2_phone=db.Column("contact2_phone", db.String(50), nullable=True)
    contact2_first_name=db.Column("contact2_first_name", db.String(50), nullable=True)
    contact2_last_name=db.Column("contact2_last_name", db.String(50), nullable=True)
    contact2_relation=db.Column("contact2_relation", db.String(50), nullable=True)

    contact3_phone    =db.Column("contact3_phone", db.String(50), nullable=True)
    contact3_first_name=db.Column("contact3_first_name", db.String(50), nullable=True)
    contact3_last_name=db.Column("contact3_last_name", db.String(50), nullable=True)
    contact3_email=db.Column("contact3_email", db.String(50), nullable=True)
    contact3_relation=db.Column("contact3_relation", db.String(50), nullable=True)

    city_id = db.Column(CITY_ID_COL, db.Integer, ForeignKey(get_forgein_key_source(CITIES_TBL, ID_COL)), nullable=True)
    address = db.Column(ADDRESS_COL, db.String(50), nullable=True)
    high_school_name = db.Column(HIGH_SCHOOL_NAME_COL, db.String(50), nullable=True)
    high_school_teacher = db.Column(HIGH_SCHOOL_TEACHER_COL, db.String(50), nullable=True)
    high_school_teacher_phone = db.Column(HIGH_SCHOOL_TEACHER_PHONE_COL, db.String(50), nullable=True)
    highSchoolInstitution = db.Column("highschoolinstitution", db.String(50), nullable=True)
    teacher_grade_a = db.Column(TEACHER_GRADE_A_COL, db.String(50), nullable=True)
    teacher_grade_a_phone = db.Column(TEACHER_GRADE_A_PHONE_COL, db.String(50), nullable=True)
    teacher_grade_b = db.Column(TEACHER_GRADE_B_COL, db.String(50), nullable=True)
    teacher_grade_b_phone = db.Column(TEACHER_GRADE_B_PHONE_COL, db.String(50), nullable=True)
    institution_id = db.Column(INSTITUTION_ID_COL, db.Integer, ForeignKey(get_forgein_key_source(INSTITUTIONS_TBL, ID_COL)), nullable=True)
    hadar_plan_session = db.Column("thperiod", db.Integer, nullable=True)#mahzor
    base_address = db.Column("militarycompoundid", db.String(50), nullable=True)
    unit_name = db.Column(UNIT_NAME_COL, db.String(50), nullable=True)
    army_role = db.Column(ARMY_ROLE_COL, db.Integer, nullable=True)
    serve_type = db.Column(SERVE_TYPE_COL, db.Integer, nullable=True)
    recruitment_date = db.Column(RECRUITMENT_DATE_COL, db.DateTime, nullable=True)
    release_date = db.Column(RELEASE_DATE_COL, db.DateTime, nullable=True)
    paying = db.Column(PAYING_COL, db.Boolean, nullable=True)
    spirit_status = db.Column("matsber", db.Integer, nullable=True)
    accompany_connect_status = db.Column("onlinestatus", db.Integer, nullable=True)
    workstatus = db.Column(workStatus_COL, db.String(50), nullable=True)
    workplace = db.Column(workPlace_COL, db.String(50), nullable=True)
    worktype = db.Column(workType_COL, db.String(50), nullable=True)
    workoccupation = db.Column(workOccupation_COL, db.String(50), nullable=True)
    educationfaculty = db.Column(educationFaculty_COL, db.String(50), nullable=True)
    educationalinstitution = db.Column(educationalInstitution_COL, db.String(50), nullable=True)
    militarypositionold = db.Column(militaryPositionOld_COL, db.String(50), nullable=True)
    militaryupdateddatetime=db.Column(militaryUpdatedDateTime_COL, db.DateTime, nullable=True)
    high_school_teacher_email=db.Column(high_school_teacher_email_col, db.String(50), nullable=True)
    teacher_grade_a_email=db.Column(teacher_grade_a_email_col, db.String(50), nullable=True)
    teacher_grade_b_email=db.Column(teacher_grade_b_email_col, db.String(50), nullable=True)
    teudatZehut = db.Column("teudatzehut", db.String(20), nullable=True)
    institution_mahzor = db.Column("institution_mahzor", db.String(10), nullable=True)
    photo_path=db.Column("photo_path", db.String(50), nullable=True)
    militaryPositionNew=db.Column("militarypositionnew", db.String(50), nullable=True)
    def __init__(self,contact3_email=None,contact3_last_name=None,contact3_first_name=None,contact3_phone=None,contact2_last_name=None,contact2_first_name=None,contact2_phone=None,contact2_email=None,contact1_phone=None,contact1_last_name=None,contact1_email=None,contact1_first_name=None, id=None,
                 accompany_id=None, name=None, last_name=None, phone=None, email=None, birthday=None, marriage_status=None, marriage_date=None, city_id=None, address=None,
                  high_school_name=None, high_school_teacher=None, high_school_teacher_phone=None, highSchoolInstitution=None, teacher_grade_a=None, teacher_grade_a_phone=None, teacher_grade_b=None,
                 teacher_grade_b_phone=None, institution_id=None, hadar_plan_session=None, base_address=None, unit_name=None, army_role=None, serve_type=None, recruitment_date=None, release_date=None, paying=None, spirit_status=None, accompany_connect_status=None):
        self.id = id
        self.accompany_id = accompany_id
        self.name = name
        self.last_name = last_name
        self.phone = phone
        self.email = email
        self.birthday = birthday
        self.marriage_status = marriage_status
        self.marriage_date = marriage_date
        self.contact1_email = contact1_email
        self.contact1_first_name = contact1_first_name
        self.city_id = city_id
        self.address = address
        self.contact1_last_name = contact1_last_name
        self.contact1_phone = contact1_phone
        self.contact2_email = contact2_email
        self.contact2_phone = contact2_phone
        self.contact2_first_name = contact2_first_name
        self.contact2_last_name = contact2_last_name

        self.contact3_phone = contact3_phone
        self.contact3_first_name = contact3_first_name
        self.contact3_last_name = contact3_last_name
        self.contact3_email = contact3_email

        self.high_school_name = high_school_name
        self.high_school_teacher = high_school_teacher
        self.high_school_teacher_phone = high_school_teacher_phone
        self.highSchoolInstitution = highSchoolInstitution
        self.teacher_grade_a = teacher_grade_a
        self.teacher_grade_a_phone = teacher_grade_a_phone
        self.teacher_grade_b = teacher_grade_b
        self.teacher_grade_b_phone = teacher_grade_b_phone
        self.institution_id = institution_id
        self.hadar_plan_session = hadar_plan_session
        self.base_address = base_address
        self.unit_name = unit_name
        self.army_role = army_role
        self.serve_type = serve_type
        self.recruitment_date = recruitment_date
        self.release_date = release_date
        self.paying = paying
        self.spirit_status = spirit_status
        self.accompany_connect_status = accompany_connect_status