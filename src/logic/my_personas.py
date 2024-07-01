from flask import jsonify
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict

import config
from src.models.models_utils import to_iso
from src.services import db
from src.models.apprentice_model import Apprentice
from src.models.base_model import Base
from src.models.city_model import City
from src.models.task_model import Task
from src.models.user_model import User
from src.models.report_model import Report
from src.logic.apprentices import visit_gap_color

# Constants for roles
ROLE_MELAVE = "0"
ROLE_RAKAZ_MOSAD = "1"
ROLE_RAKAZ_ESHKOL = "2"
ROLE_AHRAI_TOHEN = "3"


@dataclass
class Address:
    country: str
    city: str
    city_id: str
    street: str
    house_number: str
    apartment: str
    region: str
    entrance: str
    floor: str
    postal_code: str
    lat: float
    lng: float


@dataclass
class Contact:
    first_name: str
    last_name: str
    phone: str
    email: str
    relation: str


@dataclass
class Persona:
    role: List[int]
    horim_status: str
    personal_meet_status: str
    call_status: str
    high_school_teacher: str
    high_school_teacher_phone: str
    high_school_teacher_email: str
    teacher_grade_a: str
    teacher_grade_a_phone: str
    teacher_grade_a_email: str
    teacher_grade_b: str
    teacher_grade_b_phone: str
    teacher_grade_b_email: str
    address: Address
    contacts: List[Contact]
    activity_score: int
    reports: List[str]
    events: List[Dict[str, Any]]
    apprentice_id: str
    mentor_name: str
    mentor_id: str
    military_position_new: str
    avatar: str
    name: str
    last_name: str
    institution_id: str
    period: str
    serve_type: str
    marriage_status: str
    military_compound_id: str
    phone: str
    email: str
    teudat_zehut: str
    birthday: str
    marriage_date: str
    high_school_institution: str
    army_role: str
    unit_name: str
    spirit_status: str
    military_date_of_discharge: str
    military_date_of_enlistment: str
    military_updated_datetime: str
    military_position_old: str
    educational_institution: str
    education_faculty: str
    work_occupation: str
    work_type: str
    work_place: str
    work_status: str
    paying: str


class UserRepository:
    @staticmethod
    def fetch_user(user_id: str) -> Optional[User]:
        return db.session.query(User.role_ids, User.institution_id, User.cluster_id).filter(User.id == user_id).first()


class ApprenticeRepository:
    @staticmethod
    def fetch_apprentices_by_role(user: User, user_id: str) -> List[Apprentice]:
        apprentice_query = db.session.query(Apprentice)
        if ROLE_MELAVE in user.role_ids:
            return apprentice_query.filter(Apprentice.accompany_id == user_id).all()
        elif ROLE_RAKAZ_MOSAD in user.role_ids:
            return apprentice_query.filter(Apprentice.institution_id == user.institution_id).all()
        elif ROLE_RAKAZ_ESHKOL in user.role_ids:
            return apprentice_query.filter(Apprentice.cluster_id == user.cluster_id).all()
        elif ROLE_AHRAI_TOHEN in user.role_ids:
            return apprentice_query.all()
        return []


class RelatedDataRepository:
    @staticmethod
    def fetch_related_data(apprentices: List[Apprentice]) -> Dict[str, Any]:
        apprentice_ids = [apprentice.id for apprentice in apprentices]
        accompany_ids = [apprentice.accompany_id for apprentice in apprentices]
        city_ids = [apprentice.city_id for apprentice in apprentices]
        base_ids = [int(apprentice.base_address) for apprentice in apprentices]

        accompany_users = db.session.query(User.id, User.name, User.last_name).filter(
            User.id.in_(accompany_ids)).all()
        cities = db.session.query(City.id, City.name, City.region_id).filter(
            City.id.in_(city_ids)).all()
        bases = db.session.query(Base.id).filter(Base.id.in_(base_ids)).all()
        reports = db.session.query(Report.id, Report.ent_reported).filter(
            Report.ent_reported.in_(apprentice_ids)).all()
        tasks = db.session.query(Task.id, Task.event, Task.details, Task.date, Task.subject).filter(
            Task.subject.in_(map(str, apprentice_ids))).all()

        return {
            'accompany': {user.id: user for user in accompany_users},
            'city': {city.id: city for city in cities},
            'base': {base.id: base.id for base in bases},
            'report': RelatedDataRepository._organize_data_by_key(reports, 'ent_reported', 'id'),
            'task': RelatedDataRepository._organize_data_by_key(tasks, 'subject', lambda t: t)
        }

    @staticmethod
    def _organize_data_by_key(items: List[Any], key: str, value_mapper) -> Dict[str, List[Any]]:
        data_dict = {}
        for item in items:
            key_value = getattr(item, key)
            if key_value not in data_dict:
                data_dict[key_value] = []
            data_dict[key_value].append(value_mapper(item))
        return data_dict


class PersonaBuilder:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.apprentices = []
        self.users = []
        self.personas = []

    def build_personas(self) -> List[Persona]:
        user = UserRepository.fetch_user(self.user_id)
        if not user:
            raise ValueError(f"User with ID {self.user_id} not found")

        self.apprentices = ApprenticeRepository.fetch_apprentices_by_role(
            user, self.user_id)
        related_data = RelatedDataRepository.fetch_related_data(
            self.apprentices)
        self.personas = [self._build_persona(
            apprentice, related_data) for apprentice in self.apprentices]

        return self.personas

    def _build_persona(self, apprentice: Apprentice, related_data: Dict[str, Any]) -> Persona:
        accompany = related_data['accompany'].get(apprentice.accompany_id)
        city = related_data['city'].get(apprentice.city_id)
        report_list = related_data['report'].get(apprentice.id, [])
        event_list = related_data['task'].get(apprentice.id, [])
        base_id_value = related_data['base'].get(
            int(apprentice.base_address), 0)

        address = Address(
            country="IL",
            city=city.name if city else "",
            city_id=str(apprentice.city_id),
            street=apprentice.address,
            house_number="1",
            apartment="1",
            region=str(city.region_id) if city else "",
            entrance="a",
            floor="1",
            postal_code="12131",
            lat=32.04282620026557,
            lng=34.75186193813887
        )

        contacts = [
            Contact(apprentice.contact1_first_name, apprentice.contact1_last_name,
                    apprentice.contact1_phone, apprentice.contact1_email, apprentice.contact1_relation),
            Contact(apprentice.contact2_first_name, apprentice.contact2_last_name,
                    apprentice.contact2_phone, apprentice.contact2_email, apprentice.contact2_relation),
            Contact(apprentice.contact3_first_name, apprentice.contact3_last_name,
                    apprentice.contact3_phone, apprentice.contact3_email, apprentice.contact3_relation)
        ]

        return Persona(
            role=[],
            horim_status=visit_gap_color(
                config.HorimCall_report, apprentice, 365, 350),
            personal_meet_status=visit_gap_color(
                config.personalMeet_report, apprentice, 100, 80),
            call_status=visit_gap_color(
                config.call_report, apprentice, 30, 15),
            high_school_teacher=apprentice.high_school_teacher,
            high_school_teacher_phone=apprentice.high_school_teacher_phone,
            high_school_teacher_email=apprentice.high_school_teacher_email,
            teacher_grade_a=apprentice.teacher_grade_a,
            teacher_grade_a_phone=apprentice.teacher_grade_a_phone,
            teacher_grade_a_email=apprentice.teacher_grade_a_email,
            teacher_grade_b=apprentice.teacher_grade_b,
            teacher_grade_b_phone=apprentice.teacher_grade_b_phone,
            teacher_grade_b_email=apprentice.teacher_grade_b_email,
            address=address,
            contacts=contacts,
            activity_score=len(report_list),
            reports=[str(report) for report in report_list],
            events=[{
                "id": event.id, "subject": event.id, "date": to_iso(event.date),
                "created_at": to_iso(event.date), "event": event.event,
                "already_read": False, "description": event.details, "frequency": "never"
            } for event in event_list],
            apprentice_id=str(apprentice.id),
            mentor_name=f"{accompany.name} {
                accompany.last_name}" if accompany else "",
            mentor_id=str(apprentice.accompany_id),
            military_position_new=str(apprentice.militaryPositionNew),
            avatar=apprentice.photo_path if apprentice.photo_path else 'https://www.gravatar.com/avatar',
            name=apprentice.name,
            last_name=apprentice.last_name,
            institution_id=str(apprentice.institution_id),
            period=str(apprentice.hadar_plan_session),
            serve_type=apprentice.serve_type,
            marriage_status=str(apprentice.marriage_status),
            military_compound_id=str(base_id_value),
            phone=str(apprentice.id),
            email=apprentice.email,
            teudat_zehut=apprentice.teudatZehut,
            birthday=to_iso(
                apprentice.birthday) if apprentice.birthday else "",
            marriage_date=to_iso(apprentice.marriage_date),
            high_school_institution=apprentice.highSchoolInstitution,
            army_role=apprentice.army_role,
            unit_name=apprentice.unit_name,
            spirit_status=str(apprentice.spirit_status),
            military_date_of_discharge=to_iso(apprentice.release_date),
            military_date_of_enlistment=to_iso(apprentice.recruitment_date),
            military_updated_datetime=to_iso(
                apprentice.militaryupdateddatetime),
            military_position_old=apprentice.militaryPositionOld,
            educational_institution=apprentice.educationalinstitution,
            education_faculty=apprentice.educationfaculty,
            work_occupation=apprentice.workoccupation,
            work_type=apprentice.worktype,
            work_place=apprentice.workplace,
            work_status=apprentice.workstatus,
            paying=apprentice.paying
        )


def get_personas(created_by_id: str):
    """Endpoint to get personas."""
    try:
        builder = PersonaBuilder(created_by_id)
        personas = builder.build_personas()
        return jsonify([asdict(persona) for persona in personas])
    except Exception as e:
        raise e
