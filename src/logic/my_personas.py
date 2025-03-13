import logging
from flask import jsonify, request
from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass, asdict

import config
from src.models import report_model
from src.models.models_utils import to_iso
from src.services import db
from src.models.apprentice_model import Apprentice
from src.models.base_model import Base
from src.models.city_model import City
from src.models.task_model_v2 import Task
from src.models.user_model import User
from src.models.report_model import Report
from src.logic.apprentices import visit_gap_color

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Constants
ROLE_IDS = {"MELAVE": "0", "RAKAZ_MOSAD": "1", "RAKAZ_ESHKOL": "2", "AHRAI_TOHEN": "3"}


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
    event_ids: List[int]
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
    militaryCompoundId: str
    phone: str
    email: str
    teudatZehut: str
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
    cluster_id: int
    institution_mahzor: str
    birthday_ivry:str

class UserRepository:
    @staticmethod
    def fetch_user_by_id(user_id: str) -> Optional[User]:
        logger.debug(f"Fetching user with ID: {user_id}")
        return db.session.query(User).filter(User.id == user_id).first()

    @staticmethod
    def fetch_users_by_institution_id(institution_id: str) -> List[User]:
        logger.debug(f"Fetching users with institution ID: {institution_id}")
        return (
            db.session.query(User).filter(User.institution_id == institution_id).all()
        )

    @staticmethod
    def fetch_all_users(user_id) -> List[User]:
        logger.debug("Fetching all users")
        return db.session.query(User).filter(User.id != user_id).all()

    @staticmethod
    def fetch_users_by_cluster_id_and_roles(
        cluster_id: int, role_ids: List[str], user_id
    ) -> List[User]:
        logger.debug(
            f"Fetching users with cluster ID: {cluster_id} and role IDs: {role_ids}"
        )
        return (
            db.session.query(User)
            .filter(
                User.cluster_id == cluster_id,
                User.id != user_id,
                db.or_(
                    User.role_ids.like(f"%{role_ids[0]}%"),
                    User.role_ids.like(f"%{role_ids[1]}%"),
                ),
            )
            .all()
        )

    @staticmethod
    def fetch_users_by_institution_id_and_role(
        institution_id: str, role_id: str, user_id
    ) -> List[User]:
        logger.debug(
            f"Fetching users with institution ID: {institution_id} and role ID: {role_id}"
        )
        return (
            db.session.query(User)
            .filter(
                User.institution_id == institution_id,
                User.id != user_id,
                User.role_ids.like(f"%{role_id}%"),
            )
            .all()
        )


class ApprenticeRepository:
    @staticmethod
    def fetch_apprentices_by_user_roles(user: User, user_id: str) -> List[Apprentice]:
        logger.debug(
            f"Fetching apprentices for user ID: {user_id} with roles: {user.role_ids}"
        )
        query = db.session.query(Apprentice)
        roles = user.role_ids.split(",")
        apprentices = set()

        if ROLE_IDS["MELAVE"] in roles:
            logger.debug(
                f"User has role MELAVE. Fetching apprentices with accompany ID: {user_id}"
            )
            apprentices.update(query.filter(Apprentice.accompany_id == user_id).all())
        if ROLE_IDS["RAKAZ_MOSAD"] in roles:
            logger.debug(
                f"User has role RAKAZ_MOSAD. Fetching apprentices with institution ID: {user.institution_id}"
            )
            apprentices.update(
                query.filter(Apprentice.institution_id == user.institution_id).all()
            )
        if ROLE_IDS["RAKAZ_ESHKOL"] in roles:
            logger.debug(
                f"User has role RAKAZ_ESHKOL. Fetching apprentices with cluster ID: {user.cluster_id}"
            )
            apprentices.update(
                query.filter(Apprentice.cluster_id == user.cluster_id).all()
            )
        if ROLE_IDS["AHRAI_TOHEN"] in roles:
            logger.debug(f"User has role AHRAI_TOHEN. Fetching all apprentices")
            apprentices.update(query.all())

        logger.debug(
            f"Fetched apprentices: {[apprentice.id for apprentice in apprentices]}"
        )
        return list(apprentices)


class RelatedDataRepository:
    @staticmethod
    def fetch_related_data(
        apprentices: List[Apprentice], users: List[User]
    ) -> Dict[str, Any]:
        logger.debug("Fetching related data for apprentices and users")
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

        all_entity_ids = apprentice_ids + [user.id for user in users]

        related_data = {
            "accompany": RelatedDataRepository._fetch_users_by_ids(accompany_ids),
            "city": RelatedDataRepository._fetch_cities_by_ids(list(city_ids)),
            "base": RelatedDataRepository._fetch_bases_by_ids(base_ids),
            "report": RelatedDataRepository._fetch_reports_by_apprentice_ids(
                apprentice_ids
            ),
            "task": RelatedDataRepository._fetch_tasks_by_entity_ids(all_entity_ids),
        }

        logger.debug(f"Related data fetched: {related_data}")
        return related_data

    @staticmethod
    def _fetch_users_by_ids(user_ids: List[str]) -> Dict[str, User]:
        logger.debug(f"Fetching users by IDs: {user_ids}")
        users = (
            db.session.query(User.id, User.name, User.last_name)
            .filter(User.id.in_(user_ids))
            .all()
        )
        return {str(user.id): user for user in users}

    @staticmethod
    def _fetch_cities_by_ids(city_ids: List[str]) -> Dict[str, City]:
        logger.debug(f"Fetching cities by IDs: {city_ids}")
        cities = db.session.query(City).filter(City.id.in_(city_ids)).all()
        return {str(city.id): city for city in cities}

    @staticmethod
    def _fetch_bases_by_ids(base_ids: List[int]) -> Dict[int, Base]:
        logger.debug(f"Fetching bases by IDs: {base_ids}")
        bases = db.session.query(Base.id).filter(Base.id.in_(base_ids)).all()
        return {base.id: base for base in bases}

    @staticmethod
    def _fetch_reports_by_apprentice_ids(
        apprentice_ids: List[str],
    ) -> Dict[str, List[Report]]:
        logger.debug(f"Fetching reports by apprentice IDs: {apprentice_ids}")
        reports = (
            db.session.query(Report)
            .filter(Report.ent_reported.in_(apprentice_ids))
            .all()
        )
        return RelatedDataRepository._organize_data_by_key(
            reports, "ent_reported", lambda report: report.id
        )

    @staticmethod
    def _fetch_tasks_by_entity_ids(entity_ids: List[str]) -> Dict[str, List[Task]]:
        list_string = map(str, entity_ids)
        logger.debug(f"Fetching tasks by entity IDs: {entity_ids}")
        tasks = db.session.query(Task).filter(Task.subject_id.in_(list_string)).all()
        return RelatedDataRepository._organize_data_by_key(
            tasks, "subject_id", lambda task: task
        )

    @staticmethod
    def _organize_data_by_key(
        items: List[Any], key: str, value_mapper
    ) -> Dict[str, List[Any]]:
        logger.debug(f"Organizing data by key: {key}")
        organized_data = {}
        for item in items:
            key_value = str(getattr(item, key))
            if key_value not in organized_data:
                organized_data[key_value] = []
            organized_data[key_value].append(value_mapper(item))
        logger.debug(f"Organized data: {organized_data}")
        return organized_data


class PersonaBuilder:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.user = None
        self.apprentices = []
        self.users = []
        self.personas = []

    def build_personas(self) -> List[Persona]:
        logger.debug(f"Building personas for user ID: {self.user_id}")
        self._fetch_user_and_related_data()
        related_data = RelatedDataRepository.fetch_related_data(
            self.apprentices, self.users
        )
        self.personas = self._build_personas_from_apprentices(
            related_data
        ) + self._build_personas_from_users(related_data)
        logger.debug(f"Built personas: {self.personas}")
        return self.personas

    def _fetch_user_and_related_data(self):
        logger.debug(f"Fetching user and related data for user ID: {self.user_id}")
        self.user = UserRepository.fetch_user_by_id(self.user_id)
        if not self.user:
            logger.error(f"User with ID {self.user_id} not found")
            raise ValueError(f"User with ID {self.user_id} not found")

        self.apprentices = ApprenticeRepository.fetch_apprentices_by_user_roles(
            self.user, self.user_id
        )

        roles = self.user.role_ids.split(",")
        logger.debug(f"User roles: {roles}")
        if ROLE_IDS["AHRAI_TOHEN"] in roles:
            self.users = UserRepository.fetch_all_users(self.user_id)
        elif ROLE_IDS["RAKAZ_ESHKOL"] in roles:
            logger.debug(
                f"User has role RAKAZ_ESHKOL. Cluster ID: {self.user.cluster_id}"
            )
            self.users = UserRepository.fetch_users_by_cluster_id_and_roles(
                self.user.cluster_id,
                [ROLE_IDS["RAKAZ_MOSAD"], ROLE_IDS["MELAVE"]],
                self.user_id,
            )
        elif ROLE_IDS["RAKAZ_MOSAD"] in roles:
            self.users = UserRepository.fetch_users_by_institution_id_and_role(
                self.user.institution_id, ROLE_IDS["MELAVE"], self.user_id
            )

    def _build_personas_from_apprentices(self, related_data) -> List[Persona]:
        logger.debug("Building personas from apprentices")
        return [
            self._build_persona(apprentice, related_data, is_apprentice=True)
            for apprentice in self.apprentices
        ]

    def _build_personas_from_users(self, related_data) -> List[Persona]:
        logger.debug("Building personas from users")
        return [
            self._build_persona(user, related_data, is_apprentice=False)
            for user in self.users
        ]


    def _build_persona(
        self,
        entity: Union[Apprentice, User],
        related_data: Dict[str, Any],
        is_apprentice: bool,
    ) -> Persona:
        logger.debug(
            f"Building persona for entity ID: {entity.id}, is_apprentice: {is_apprentice}"
        )
        city = related_data["city"][str(entity.city_id)] if entity.city_id else ""
        report_list = related_data["report"].get(str(entity.id), [])
        event_ids = [task.id for task in related_data["task"].get(str(entity.id), [])]

        address = self._create_address(entity, city)
        if is_apprentice:
            contacts = self._create_contacts(entity)
            persona = Persona(
                roles=[-1],
                horim_status=visit_gap_color(
                    report_model.HorimCall_report, entity, 365, 350
                )
                or "",
                personal_meet_status=visit_gap_color(
                    report_model.personalMeet_report, entity, 100, 80
                )
                or "",
                call_status=visit_gap_color(report_model.call_report, entity, 30, 15)
                or "red",
                high_school_teacher=entity.high_school_teacher or "",
                high_school_teacher_phone=entity.high_school_teacher_phone or "",
                high_school_teacher_email=entity.high_school_teacher_email or "",
                teacher_grade_a=entity.teacher_grade_a or "",
                teacher_grade_a_phone=entity.teacher_grade_a_phone or "",
                teacher_grade_a_email=entity.teacher_grade_a_email or "",
                teacher_grade_b=entity.teacher_grade_b or "",
                teacher_grade_b_phone=entity.teacher_grade_b_phone or "",
                teacher_grade_b_email=entity.teacher_grade_b_email or "",
                address=address or "",
                contacts=contacts or [],
                activity_score=get_color_from_int(len(report_list)) or "red",
                reports=[str(report) for report in report_list] or [],
                event_ids=event_ids,
                id=str(entity.id),
                th_mentor_name=self._get_accompany_name(
                    related_data, entity.accompany_id
                )
                or "",
                th_mentor_id=str(entity.accompany_id) or "",
                military_position_new=str(entity.militaryPositionNew) or "",
                avatar=self._get_avatar(entity) or "",
                name=entity.name or "",
                last_name=entity.last_name or "",
                institution_id=str(entity.institution_id) or "",
                th_period=str(entity.hadar_plan_session) or "",
                serve_type=entity.serve_type or "",
                marriage_status=str(entity.marriage_status) or "",
                militaryCompoundId=str(
                    related_data["base"].get(entity.base_address, [0])[0]
                ),
                phone=str(entity.id) or "",
                email=entity.email or "",
                teudatZehut=entity.teudatZehut or "",
                birthday=to_iso(entity.birthday)[:10] if entity.birthday else "",
                marriage_date=to_iso(entity.marriage_date) or "",
                high_school_institution=entity.high_school_name or "",
                army_role=entity.army_role or "",
                unit_name=entity.unit_name or "",
                matsber=str(entity.spirit_status) or "אדוק",
                military_date_of_discharge=to_iso(entity.release_date) or "",
                military_date_of_enlistment=to_iso(entity.recruitment_date) or "",
                military_updated_datetime=to_iso(entity.militaryupdateddatetime) or "",
                military_position_old=entity.militaryPositionOld or "",
                educational_institution=entity.educationalinstitution or "",
                education_faculty=entity.educationfaculty or "",
                work_occupation=entity.workoccupation or "",
                work_type=entity.worktype or "",
                work_place=entity.workplace or "",
                work_status=entity.workstatus or "",
                paying=entity.paying or "",
                cluster_id=entity.cluster_id,
                institution_mahzor=entity.institution_mahzor or "",
                birthday_ivry=entity.birthday_ivry or ""

            )
            logger.debug(f"Built apprentice persona: {persona}")
            return persona
        else:
            persona = Persona(
                roles=[int(role) for role in entity.role_ids.split(",")],
                horim_status="",
                personal_meet_status="",
                call_status="red",
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
                activity_score=get_color_from_int(len(report_list)) or "red",
                reports=[],
                event_ids=event_ids,
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
                militaryCompoundId="",
                phone=str(entity.id),
                email=entity.email or "",
                teudatZehut=entity.teudatZehut or "",
                birthday=to_iso(entity.birthday)[:10] if entity.birthday else "",
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
                paying="",
                cluster_id=entity.cluster_id,
                institution_mahzor="",
                birthday_ivry=""
            )
            logger.debug(f"Built user persona: {persona}")
            return persona

    def _create_address(
        self, entity: Union[Apprentice, User], city: Optional[City]
    ) -> Address:
        logger.debug(f"Creating address for entity ID: {entity.id}")
        address = Address(
            country="IL",
            city=city.name if city else "",
            city_id=str(entity.city_id) if entity.city_id else "",
            street=entity.address or "",
            house_number=entity.house_number or 0,
            apartment="1",
            region=str(city.region_id) if city else "",
            entrance="a",
            floor="1",
            postal_code="12131",
            latitude=32.04282620026557,
            longitude=34.75186193813887,
        )
        logger.debug(f"Created address: {address}")
        return address

    def _create_contacts(self, entity: Apprentice) -> List[Contact]:
        logger.debug(f"Creating contacts for apprentice ID: {entity.id}")
        contacts = [
            Contact(
                entity.contact1_first_name,
                entity.contact1_last_name,
                entity.contact1_phone,
                entity.contact1_email,
                entity.contact1_relation,
            ),
            Contact(
                entity.contact2_first_name,
                entity.contact2_last_name,
                entity.contact2_phone,
                entity.contact2_email,
                entity.contact2_relation,
            ),
            Contact(
                entity.contact3_first_name,
                entity.contact3_last_name,
                entity.contact3_phone,
                entity.contact3_email,
                entity.contact3_relation,
            ),
        ]
        logger.debug(f"Created contacts: {contacts}")
        return contacts

    def _get_accompany_name(
        self, related_data: Dict[str, Any], accompany_id: str
    ) -> str:
        logger.debug(f"Getting accompany name for accompany ID: {accompany_id}")
        accompany = related_data["accompany"].get(accompany_id)
        accompany_name = f"{accompany.name} {accompany.last_name}" if accompany else ""
        logger.debug(f"Accompany name: {accompany_name}")
        return accompany_name

    def _get_avatar(self, entity: Union[Apprentice, User]) -> str:
        logger.debug(f"Getting avatar for entity ID: {entity.id}")
        avatar = (
            entity.photo_path
            if entity.photo_path
            else "https://www.gravatar.com/avatar"
        )
        logger.debug(f"Avatar: {avatar}")
        return avatar


#
def get_personas(user_id: str):
    try:
        logger.debug(f"Getting personas for user ID: {user_id}")
        persona_builder = PersonaBuilder(user_id)
        personas = persona_builder.build_personas()
        response = jsonify([asdict(persona) for persona in personas])
        logger.debug(f"Personas response: {response}")
        return response
    except ValueError as error:
        logger.error(f"Error getting personas: {error}")
        return jsonify({"error": str(error)}), 400
    except Exception as error:
        logger.error(f"Internal Server Error: {error}")
        return jsonify({"error": "Internal Server Error"}), 500


def get_program_managers():
    try:
        logger.debug("Getting program managers")
        program_managers = (
            db.session.query(User)
            .filter(User.role_ids.like(f"%{ROLE_IDS['AHRAI_TOHEN']}%"))
            .all()
        )

        persona_builder = PersonaBuilder("dummy_id")

        personas = []
        for manager in program_managers:
            city_ = db.session.query(City).filter(City.id == manager.city_id).first()
            persona = persona_builder._build_persona(
                manager,
                {
                    "city": {str(manager.city_id): city_},
                    "report": {},
                    "task": {},
                    "accompany": {},
                    "base": {},
                },
                is_apprentice=False,
            )
            personas.append(persona)

        response = jsonify([asdict(persona) for persona in personas])
        logger.debug(f"Program managers response: {response}")
        return response
    except Exception as error:
        logger.error(f"Internal Server Error: {error}")
        return jsonify({"error": "Internal Server Error"}), 500
    
def get_color_from_int(value):
    if 0 <= value <= 26:
        return "red"
    elif 27 <= value <= 42:
        return "orange"
    elif 43 <= value:
        return "green"
 
    else:
        return "Value out of range"
