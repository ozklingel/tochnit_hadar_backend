from flask import jsonify, request
from typing import Optional, List, Dict, Any, Union
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

# Constants
ROLE_IDS = {
    "MELAVE": "0",
    "RAKAZ_MOSAD": "1",
    "RAKAZ_ESHKOL": "2",
    "AHRAI_TOHEN": "3"
}


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
    latitude: float
    longitude: float


@dataclass
class Contact:
    first_name: str
    last_name: str
    phone: str
    email: str
    relation: str


@dataclass
class Persona:
    roles: List[int]
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
    id: str
    th_mentor_name: str
    th_mentor_id: str
    military_position_new: str
    avatar: str
    name: str
    last_name: str
    institution_id: str
    th_period: str
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
    matsber: str
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
    def fetch_user_by_id(user_id: str) -> Optional[User]:
        return db.session.query(User).filter(User.id == user_id).first()

    @staticmethod
    def fetch_users_by_institution_id(institution_id: str) -> List[User]:
        return db.session.query(User).filter(User.institution_id == institution_id).all()

    @staticmethod
    def fetch_all_users() -> List[User]:
        return db.session.query(User).all()


class ApprenticeRepository:
    @staticmethod
    def fetch_apprentices_by_user_role(user: User, user_id: str) -> List[Apprentice]:
        query = db.session.query(Apprentice)
        if ROLE_IDS["MELAVE"] in user.role_ids:
            return query.filter(Apprentice.accompany_id == user_id).all()
        elif ROLE_IDS["RAKAZ_MOSAD"] in user.role_ids:
            return query.filter(Apprentice.institution_id == user.institution_id).all()
        elif ROLE_IDS["RAKAZ_ESHKOL"] in user.role_ids:
            return query.filter(Apprentice.cluster_id == user.cluster_id).all()
        elif ROLE_IDS["AHRAI_TOHEN"] in user.role_ids:
            return query.all()
        return []


class RelatedDataRepository:
    @staticmethod
    def fetch_related_data(apprentices: List[Apprentice], users: List[User]) -> Dict[str, Any]:
        apprentice_ids = []
        accompany_ids = []
        city_ids = set()
        base_ids = []

        for apprentice in apprentices:
            apprentice_ids.append(apprentice.id)
            accompany_ids.append(apprentice.accompany_id)
            if apprentice.city_id:
                city_ids.add(apprentice.city_id)
            if apprentice.base_address:
                base_ids.append(int(apprentice.base_address))

        for user in users:
            if user.city_id:
                city_ids.add(user.city_id)

        # entity = User / Persona
        all_entity_ids = apprentice_ids + [user.id for user in users]

        return {
            'accompany': RelatedDataRepository._fetch_users_by_ids(accompany_ids),
            'city': RelatedDataRepository._fetch_cities_by_ids(list(city_ids)),
            'base': RelatedDataRepository._fetch_bases_by_ids(base_ids),
            'report': RelatedDataRepository._fetch_reports_by_apprentice_ids(apprentice_ids),
            'task': RelatedDataRepository._fetch_tasks_by_entity_ids(all_entity_ids)
        }

    @staticmethod
    def _fetch_users_by_ids(user_ids: List[str]) -> Dict[str, User]:
        users = db.session.query(User.id, User.name, User.last_name).filter(
            User.id.in_(user_ids)).all()
        return {str(user.id): user for user in users}

    @staticmethod
    def _fetch_cities_by_ids(city_ids: List[str]) -> Dict[str, City]:
        cities = db.session.query(City).filter(City.id.in_(city_ids)).all()
        return {str(city.id): city for city in cities}

    @staticmethod
    def _fetch_bases_by_ids(base_ids: List[int]) -> Dict[int, Base]:
        bases = db.session.query(Base.id).filter(Base.id.in_(base_ids)).all()
        return {base.id: base for base in bases}

    @staticmethod
    def _fetch_reports_by_apprentice_ids(apprentice_ids: List[str]) -> Dict[str, List[Report]]:
        reports = db.session.query(Report).filter(
            Report.ent_reported.in_(apprentice_ids)).all()
        return RelatedDataRepository._organize_data_by_key(reports, 'ent_reported', lambda report: report.id)

    @staticmethod
    def _fetch_tasks_by_entity_ids(entity_ids: List[str]) -> Dict[str, List[Task]]:
        tasks = db.session.query(Task).filter(
            Task.subject.in_(map(str, entity_ids))).all()
        return RelatedDataRepository._organize_data_by_key(tasks, 'subject', lambda task: task)

    @staticmethod
    def _organize_data_by_key(items: List[Any], key: str, value_mapper) -> Dict[str, List[Any]]:
        organized_data = {}
        for item in items:
            key_value = str(getattr(item, key))
            if key_value not in organized_data:
                organized_data[key_value] = []
            organized_data[key_value].append(value_mapper(item))
        return organized_data


class PersonaBuilder:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.user = None
        self.apprentices = []
        self.users = []
        self.personas = []

    def build_personas(self) -> List[Persona]:
        self._fetch_user_and_related_data()
        related_data = RelatedDataRepository.fetch_related_data(
            self.apprentices, self.users)
        self.personas = self._build_personas_from_apprentices(
            related_data) + self._build_personas_from_users(related_data)
        return self.personas

    def _fetch_user_and_related_data(self):
        self.user = UserRepository.fetch_user_by_id(self.user_id)
        if not self.user:
            raise ValueError(f"User with ID {self.user_id} not found")

        self.apprentices = ApprenticeRepository.fetch_apprentices_by_user_role(
            self.user, self.user_id)

        if ROLE_IDS["RAKAZ_MOSAD"] in self.user.role_ids or ROLE_IDS["RAKAZ_ESHKOL"] in self.user.role_ids:
            self.users = UserRepository.fetch_users_by_institution_id(
                self.user.institution_id)
        elif ROLE_IDS["AHRAI_TOHEN"] in self.user.role_ids:
            self.users = UserRepository.fetch_all_users()

    def _build_personas_from_apprentices(self, related_data) -> List[Persona]:
        return [self._build_persona(apprentice, related_data, is_apprentice=True) for apprentice in self.apprentices]

    def _build_personas_from_users(self, related_data) -> List[Persona]:
        return [self._build_persona(user, related_data, is_apprentice=False) for user in self.users]

    def _build_persona(self, entity: Union[Apprentice, User], related_data: Dict[str, Any], is_apprentice: bool) -> Persona:
        city = related_data['city'].get(entity.city_id)
        report_list = related_data['report'].get(str(entity.id), [])
        event_list = related_data['task'].get(str(entity.id), [])

        address = self._create_address(entity, city)

        if is_apprentice:
            contacts = self._create_contacts(entity)
            return Persona(
                roles=[-1],
                horim_status=visit_gap_color(
                    config.HorimCall_report, entity, 365, 350),
                personal_meet_status=visit_gap_color(
                    config.personalMeet_report, entity, 100, 80),
                call_status=visit_gap_color(
                    config.call_report, entity, 30, 15),
                high_school_teacher=entity.high_school_teacher,
                high_school_teacher_phone=entity.high_school_teacher_phone,
                high_school_teacher_email=entity.high_school_teacher_email,
                teacher_grade_a=entity.teacher_grade_a,
                teacher_grade_a_phone=entity.teacher_grade_a_phone,
                teacher_grade_a_email=entity.teacher_grade_a_email,
                teacher_grade_b=entity.teacher_grade_b,
                teacher_grade_b_phone=entity.teacher_grade_b_phone,
                teacher_grade_b_email=entity.teacher_grade_b_email,
                address=address,
                contacts=contacts,
                activity_score=len(report_list),
                reports=[str(report) for report in report_list],
                events=[self._create_event(event) for event in event_list],
                id=str(entity.id),
                th_mentor_name=self._get_accompany_name(
                    related_data, entity.accompany_id),
                th_mentor_id=str(entity.accompany_id),
                military_position_new=str(entity.militaryPositionNew),
                avatar=self._get_avatar(entity),
                name=entity.name,
                last_name=entity.last_name,
                institution_id=str(entity.institution_id),
                th_period=str(entity.hadar_plan_session),
                serve_type=entity.serve_type,
                marriage_status=str(entity.marriage_status),
                military_compound_id=str(
                    related_data['base'].get(int(entity.base_address), 0)),
                phone=str(entity.id),
                email=entity.email,
                teudat_zehut=entity.teudatZehut,
                birthday=to_iso(entity.birthday) if entity.birthday else "",
                marriage_date=to_iso(entity.marriage_date),
                high_school_institution=entity.highSchoolInstitution,
                army_role=entity.army_role,
                unit_name=entity.unit_name,
                matsber=str(entity.spirit_status),
                military_date_of_discharge=to_iso(entity.release_date),
                military_date_of_enlistment=to_iso(entity.recruitment_date),
                military_updated_datetime=to_iso(
                    entity.militaryupdateddatetime),
                military_position_old=entity.militaryPositionOld,
                educational_institution=entity.educationalinstitution,
                education_faculty=entity.educationfaculty,
                work_occupation=entity.workoccupation,
                work_type=entity.worktype,
                work_place=entity.workplace,
                work_status=entity.workstatus,
                paying=entity.paying
            )
        else:
            return Persona(
                roles=[int(role) for role in entity.role_ids.split(",")],
                horim_status="",
                personal_meet_status="",
                call_status="",
                high_school_teacher="",
                high_school_teacher_phone="",
                high_school_teacher_email="",
                teacher_grade_a="",
                teacher_grade_a_phone="",
                teacher_grade_a_email="",
                teacher_grade_b="",
                teacher_grade_b_phone="",
                teacher_grade_b_email="",
                address=address,
                contacts=[],
                activity_score=len(report_list),
                reports=[],
                events=[],
                id=str(entity.id),
                th_mentor_name="",
                th_mentor_id="",
                military_position_new="",
                avatar=self._get_avatar(entity),
                name=entity.name,
                last_name=entity.last_name,
                institution_id=str(entity.institution_id),
                th_period="",
                serve_type="",
                marriage_status="",
                military_compound_id="",
                phone=str(entity.id),
                email=entity.email,
                teudat_zehut=entity.teudatZehut,
                birthday="",
                marriage_date="",
                high_school_institution="",
                army_role="",
                unit_name="",
                matsber="",
                military_date_of_discharge="",
                military_date_of_enlistment="",
                military_updated_datetime="",
                military_position_old="",
                educational_institution="",
                education_faculty="",
                work_occupation="",
                work_type="",
                work_place="",
                work_status="",
                paying=""
            )

    def _create_address(self, entity: Union[Apprentice, User], city: Optional[City]) -> Address:
        return Address(
            country="IL",
            city=city.name if city else "",
            city_id=str(entity.city_id),
            street=entity.address,
            house_number="1",
            apartment="1",
            region=str(city.region_id) if city else "",
            entrance="a",
            floor="1",
            postal_code="12131",
            latitude=32.04282620026557,
            longitude=34.75186193813887
        )

    def _create_contacts(self, entity: Apprentice) -> List[Contact]:
        return [
            Contact(entity.contact1_first_name, entity.contact1_last_name,
                    entity.contact1_phone, entity.contact1_email, entity.contact1_relation),
            Contact(entity.contact2_first_name, entity.contact2_last_name,
                    entity.contact2_phone, entity.contact2_email, entity.contact2_relation),
            Contact(entity.contact3_first_name, entity.contact3_last_name,
                    entity.contact3_phone, entity.contact3_email, entity.contact3_relation)
        ]

    def _create_event(self, event: Task) -> Dict[str, Any]:
        return {
            "id": event.id,
            "subject": event.id,
            "date": to_iso(event.date),
            "created_at": to_iso(event.date),
            "event": event.event,
            "already_read": False,
            "description": event.details,
            "frequency": "never"
        }

    def _get_accompany_name(self, related_data: Dict[str, Any], accompany_id: str) -> str:
        accompany = related_data['accompany'].get(accompany_id)
        return f"{accompany.name} {accompany.last_name}" if accompany else ""

    def _get_avatar(self, entity: Union[Apprentice, User]) -> str:
        return entity.photo_path if entity.photo_path else 'https://www.gravatar.com/avatar'


def get_personas(user_id: str):
    try:
        persona_builder = PersonaBuilder(user_id)
        personas = persona_builder.build_personas()
        return jsonify([asdict(persona) for persona in personas])
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except Exception as error:
        print(error)
        return jsonify({"error": "Internal Server Error"}), 500
