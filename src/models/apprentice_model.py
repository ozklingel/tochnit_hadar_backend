from . import *

class Apprentice(db.Model):
    __tablename__ = APPRENTICES_TBL

    id = db.Column(APPRENTICE_ID_COL, db.Integer, primary_key=True, autoincrement=True, nullable=False)
    accompany_id = db.Column(ACCOMPANY_ID_COL, db.Integer, ForeignKey(get_forgein_key_source(USERS_TBL, ID_COL)), nullable=False)
    name = db.Column(NAME_COL, db.String(50), nullable=False)
    last_name = db.Column(LAST_NAME_COL, db.String(50), nullable=False)
    phone = db.Column(PHONE_COL, db.String(50), nullable=False)
    email = db.Column(EMAIL_COL, db.String(50), nullable=False)
    birthday = db.Column(BIRTHDAY_COL, db.DateTime, nullable=False)
    marriage_status = db.Column(MARRIAGE_STATUS_COL, db.Boolean, nullable=False)
    marriage_date = db.Column(MARRIAGE_DATE_COL, db.DateTime, nullable=True)
    wife_name = db.Column(WIFE_NAME_COL, db.String(50), nullable=True)
    wife_phone = db.Column(WIFE_PHONE_COL, db.String(50), nullable=True)
    city_id = db.Column(CITY_ID_COL, db.Integer, ForeignKey(get_forgein_key_source(CITIES_TBL, ID_COL)), nullable=False)
    address = db.Column(ADDRESS_COL, db.String(50), nullable=False)
    father_name = db.Column(FATHER_NAME_COL, db.String(50), nullable=True)
    father_phone = db.Column(FATHER_PHONE_COL, db.String(50), nullable=True)
    father_email = db.Column(FATHER_EMAIL_COL, db.String(50), nullable=True)
    mother_name = db.Column(MOTHER_NAME_COL, db.String(50), nullable=True)
    mother_phone = db.Column(MOTHER_PHONE_COL, db.String(50), nullable=True)
    mother_email = db.Column(MOTHER_EMAIL_COL, db.String(50), nullable=True)
    high_school_name = db.Column(HIGH_SCHOOL_NAME_COL, db.String(50), nullable=True)
    high_school_teacher = db.Column(HIGH_SCHOOL_TEACHER_COL, db.String(50), nullable=True)
    high_school_teacher_phone = db.Column(HIGH_SCHOOL_TEACHER_PHONE_COL, db.String(50), nullable=True)
    pre_army_institution = db.Column(PRE_ARMY_INSTITUTION_COL, db.String(50), nullable=True)
    teacher_grade_a = db.Column(TEACHER_GRADE_A_COL, db.String(50), nullable=True)
    teacher_grade_a_phone = db.Column(TEACHER_GRADE_A_PHONE_COL, db.String(50), nullable=True)
    teacher_grade_b = db.Column(TEACHER_GRADE_B_COL, db.String(50), nullable=True)
    teacher_grade_b_phone = db.Column(TEACHER_GRADE_B_PHONE_COL, db.String(50), nullable=True)
    institution_id = db.Column(INSTITUTION_ID_COL, db.Integer, ForeignKey(get_forgein_key_source(INSTITUTIONS_TBL, ID_COL)), nullable=False)
    hadar_plan_session = db.Column(HADAR_PLAN_SESSION_COL, db.Integer, nullable=False)
    base_address = db.Column(BASE_ADDRESS_COL, db.String(50), nullable=False)
    unit_name = db.Column(UNIT_NAME_COL, db.String(50), nullable=False)
    army_role = db.Column(ARMY_ROLE_COL, db.Integer, nullable=False)
    serve_type = db.Column(SERVE_TYPE_COL, db.Integer, nullable=False)
    recruitment_date = db.Column(RECRUITMENT_DATE_COL, db.DateTime, nullable=False)
    release_date = db.Column(RELEASE_DATE_COL, db.DateTime, nullable=False)
    paying = db.Column(PAYING_COL, db.Boolean, nullable=False)
    spirit_status = db.Column(SPIRIT_STATUS_COL, db.Integer, nullable=False)
    accompany_connect_status = db.Column(ACCOMPANY_CONNECT_STATUS_COL, db.Integer, nullable=False)

    def __init__(self, id, accompany_id, name, last_name, phone, email, birthday, marriage_status, marriage_date, wife_name, wife_phone, city_id, address, father_name, father_phone, father_email,
                 mother_name, mother_phone, mother_email, high_school_name, high_school_teacher, high_school_teacher_phone, pre_army_institution, teacher_grade_a, teacher_grade_a_phone, teacher_grade_b,
                 teacher_grade_b_phone, institution_id, hadar_plan_session, base_address, unit_name, army_role, serve_type, recruitment_date, release_date, paying, spirit_status, accompany_connect_status):
        self.id = id
        self.accompany_id = accompany_id
        self.name = name
        self.last_name = last_name
        self.phone = phone
        self.email = email
        self.birthday = birthday
        self.marriage_status = marriage_status
        self.marriage_date = marriage_date
        self.wife_name = wife_name
        self.wife_phone = wife_phone
        self.city_id = city_id
        self.address = address
        self.father_name = father_name
        self.father_phone = father_phone
        self.father_email = father_email
        self.mother_name = mother_name
        self.mother_phone = mother_phone
        self.mother_email = mother_email
        self.high_school_name = high_school_name
        self.high_school_teacher = high_school_teacher
        self.high_school_teacher_phone = high_school_teacher_phone
        self.pre_army_institution = pre_army_institution
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