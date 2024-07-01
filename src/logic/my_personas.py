from flask import jsonify
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
from typing import Optional, List, Dict, Any

# Constants for roles
ROLE_MELAVE = "0"
ROLE_RAKAZ_MOSAD = "1"
ROLE_RAKAZ_ESHKOL = "2"
ROLE_AHRAI_TOHEN = "3"


class PersonaBuilder:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.apprentices = []
        self.users = []
        self.personas = []

    def fetch_user(self) -> Optional[User]:
        print(f"Fetching user with ID: {self.user_id}")
        user = db.session.query(User.role_ids, User.institution_id, User.cluster_id).filter(
            User.id == self.user_id).first()
        if not user:
            print(f"User with ID {self.user_id} not found")
            raise ValueError(f"User with ID {self.user_id} not found")
        return user

    def build_apprentice_list(self, user: User) -> None:
        print(f"Building apprentice list for user with ID: {self.user_id}")
        apprentice_query = db.session.query(Apprentice)
        if ROLE_MELAVE in user.role_ids:
            self.apprentices = apprentice_query.filter(Apprentice.accompany_id == self.user_id).all()
        elif ROLE_RAKAZ_MOSAD in user.role_ids:
            self.apprentices = apprentice_query.filter(Apprentice.institution_id == user.institution_id).all()
        elif ROLE_RAKAZ_ESHKOL in user.role_ids:
            self.apprentices = apprentice_query.filter(Apprentice.cluster_id == user.cluster_id).all()
        elif ROLE_AHRAI_TOHEN in user.role_ids:
            self.apprentices = apprentice_query.all()

    def build_user_list(self, user: User) -> None:
        print(f"Building user list for user with ID: {self.user_id}")
        user_query = db.session.query(User)
        if ROLE_RAKAZ_MOSAD in user.role_ids or ROLE_RAKAZ_ESHKOL in user.role_ids:
            self.users = user_query.filter(User.institution_id == user.institution_id).all()
        elif ROLE_AHRAI_TOHEN in user.role_ids:
            self.users = user_query.all()

    def fetch_related_data(self, apprentice_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        print(f"Fetching related data for apprentices")
        accompany_ids = [apprentice.accompany_id for apprentice in self.apprentices]
        city_ids = [apprentice.city_id for apprentice in self.apprentices]
        base_ids = [int(apprentice.base_address) for apprentice in self.apprentices]

        accompany_users = db.session.query(User.id, User.name, User.last_name).filter(User.id.in_(accompany_ids)).all()
        cities = db.session.query(City.id, City.name, City.region_id).filter(City.id.in_(city_ids)).all()
        bases = db.session.query(Base.id).filter(Base.id.in_(base_ids)).all()
        reports = db.session.query(Report.id, Report.ent_reported).filter(Report.ent_reported.in_(apprentice_ids)).all()
        tasks = db.session.query(Task.id, Task.event, Task.details, Task.date, Task.subject).filter(
            Task.subject.in_(map(str, apprentice_ids))
        ).all()

        accompany_dict = {user.id: user for user in accompany_users}
        city_dict = {city.id: city for city in cities}
        base_dict = {base.id: base.id for base in bases}
        report_dict = {}
        task_dict = {}

        for report in reports:
            if report.ent_reported not in report_dict:
                report_dict[report.ent_reported] = []
            report_dict[report.ent_reported].append(report.id)

        for task in tasks:
            if task.subject not in task_dict:
                task_dict[task.subject] = []
            task_dict[task.subject].append(task)

        return {
            'accompany': accompany_dict,
            'city': city_dict,
            'base': base_dict,
            'report': report_dict,
            'task': task_dict
        }

    def build_personas_from_apprentices(self, related_data: Dict[int, Dict[str, Any]]) -> None:
        print("Building personas from apprentices")
        try:
            for apprentice in self.apprentices:
                accompany = related_data['accompany'].get(apprentice.accompany_id)
                city = related_data['city'].get(apprentice.city_id)
                report_list = related_data['report'].get(apprentice.id, [])
                event_list = related_data['task'].get(apprentice.id, [])
                base_id_value = related_data['base'].get(int(apprentice.base_address), 0)

                self.personas.append(self.build_apprentice_dict(
                    apprentice, accompany, city, report_list, event_list, base_id_value))
        except Exception as e:
            print(f"Error building personas from apprentices: {str(e)}")
            raise ValueError(f"Error building personas from apprentices: {str(e)}")

    def build_apprentice_dict(self, apprentice: Apprentice, accompany: User, city: City, report_list: List[Report], event_list: List[Task], base_id_value: int) -> Dict[str, Any]:
        return {
            "role": [],
            "Horim_status": visit_gap_color(config.HorimCall_report, apprentice, 365, 350),
            "personalMeet_status": visit_gap_color(config.personalMeet_report, apprentice, 100, 80),
            "call_status": visit_gap_color(config.call_report, apprentice, 30, 15),
            "highSchoolRavMelamed_phone": apprentice.high_school_teacher_phone,
            "highSchoolRavMelamed_name": apprentice.high_school_teacher,
            "highSchoolRavMelamed_email": apprentice.high_school_teacher_email,
            "thRavMelamedYearA_name": apprentice.teacher_grade_a,
            "thRavMelamedYearA_phone": apprentice.teacher_grade_a_phone,
            "thRavMelamedYearA_email": apprentice.teacher_grade_a_email,
            "thRavMelamedYearB_name": apprentice.teacher_grade_b,
            "thRavMelamedYearB_phone": apprentice.teacher_grade_b_phone,
            "thRavMelamedYearB_email": apprentice.teacher_grade_b_email,
            "address": {
                "country": "IL",
                "city": city.name if city else "",
                "cityId": str(apprentice.city_id),
                "street": apprentice.address,
                "houseNumber": "1",
                "apartment": "1",
                "region": str(city.region_id) if city else "",
                "entrance": "a",
                "floor": "1",
                "postalCode": "12131",
                "lat": 32.04282620026557,
                "lng": 34.75186193813887
            },
            "contact1_first_name": apprentice.contact1_first_name,
            "contact1_last_name": apprentice.contact1_last_name,
            "contact1_phone": apprentice.contact1_phone,
            "contact1_email": apprentice.contact1_email,
            "contact1_relation": apprentice.contact1_relation,
            "contact2_first_name": apprentice.contact2_first_name,
            "contact2_last_name": apprentice.contact2_last_name,
            "contact2_phone": apprentice.contact2_phone,
            "contact2_email": apprentice.contact2_email,
            "contact2_relation": apprentice.contact2_relation,
            "contact3_first_name": apprentice.contact3_first_name,
            "contact3_last_name": apprentice.contact3_last_name,
            "contact3_phone": apprentice.contact3_phone,
            "contact3_email": apprentice.contact3_email,
            "contact3_relation": apprentice.contact3_relation,
            "activity_score": len(report_list),
            "reports": [str(report) for report in report_list],
            "events": [{"id": event.id, "subject": event.id, "date": to_iso(event.date), "created_at": to_iso(event.date), "event": event.event, "already_read": False, "description": event.details, "frequency": "never"} for event in event_list],
            "id": str(apprentice.id),
            "thMentor_name": f"{accompany.name} {accompany.last_name}",
            "thMentor_id": str(apprentice.accompany_id),
            "militaryPositionNew": str(apprentice.militaryPositionNew),
            "avatar": apprentice.photo_path if apprentice.photo_path else 'https://www.gravatar.com/avatar',
            "name": str(apprentice.name),
            "last_name": str(apprentice.last_name),
            "institution_id": str(apprentice.institution_id),
            "thPeriod": str(apprentice.hadar_plan_session),
            "serve_type": apprentice.serve_type,
            "marriage_status": str(apprentice.marriage_status),
            "militaryCompoundId": str(base_id_value),
            "phone": str(apprentice.id),
            "email": apprentice.email,
            "teudatZehut": apprentice.teudatZehut,
            "birthday": to_iso(apprentice.birthday) if apprentice.birthday else "",
            "marriage_date": to_iso(apprentice.marriage_date),
            "highSchoolInstitution": apprentice.highSchoolInstitution,
            "army_role": apprentice.army_role,
            "unit_name": apprentice.unit_name,
            "matsber": str(apprentice.spirit_status),
            "militaryDateOfDischarge": to_iso(apprentice.release_date),
            "militaryDateOfEnlistment": to_iso(apprentice.recruitment_date),
            "militaryUpdatedDateTime": to_iso(apprentice.militaryupdateddatetime),
            "militaryPositionOld": apprentice.militaryPositionOld,
            "educationalInstitution": apprentice.educationalinstitution,
            "educationFaculty": apprentice.educationfaculty,
            "workOccupation": apprentice.workoccupation,
            "workType": apprentice.worktype,
            "workPlace": apprentice.workplace,
            "workStatus": apprentice.workstatus,
            "paying": apprentice.paying
        }

    def build_personas_from_users(self) -> None:
        print("Building personas from users")
        try:
            for user in self.users:
                city = db.session.query(City).filter(City.id == user.city_id).first()
                report_list = db.session.query(Report.id).filter(Report.user_id == user.id).all()

                self.personas.append({
                    "role": [int(role) for role in user.role_ids.split(",")],
                    "Horim_status": "",
                    "personalMeet_status": "",
                    "call_status": "",
                    "highSchoolRavMelamed_phone": "",
                    "highSchoolRavMelamed_name": "",
                    "highSchoolRavMelamed_email": "",
                    "thRavMelamedYearA_name": "",
                    "thRavMelamedYearA_phone": "",
                    "thRavMelamedYearA_email": "",
                    "thRavMelamedYearB_name": "",
                    "thRavMelamedYearB_phone": "",
                    "thRavMelamedYearB_email": "",
                    "address": {
                        "country": "IL",
                        "city": city.name if city else "",
                        "cityId": str(user.city_id),
                        "street": user.address,
                        "houseNumber": "1",
                        "apartment": "1",
                        "region": str(city.region_id) if city else "",
                        "entrance": "a",
                        "floor": "1",
                        "postalCode": "12131",
                        "lat": 32.04282620026557,
                        "lng": 34.75186193813887
                    },
                    "contact1_first_name": "",
                    "contact1_last_name": "",
                    "contact1_phone": "",
                    "contact1_email": "",
                    "contact1_relation": "",
                    "contact2_first_name": "",
                    "contact2_last_name": "",
                    "contact2_phone": "",
                    "contact2_email": "",
                    "contact2_relation": "",
                    "contact3_first_name": "",
                    "contact3_last_name": "",
                    "contact3_phone": "",
                    "contact3_email": "",
                    "contact3_relation": "",
                    "activity_score": len(report_list),
                    "reports": [],
                    "events": [],
                    "id": str(user.id),
                    "thMentor": "",
                    "militaryPositionNew": "",
                    "avatar": user.photo_path if user.photo_path else 'https://www.gravatar.com/avatar',
                    "name": str(user.name),
                    "last_name": str(user.last_name),
                    "institution_id": str(user.institution_id),
                    "thPeriod": "",
                    "serve_type": "",
                    "marriage_status": "",
                    "militaryCompoundId": "",
                    "phone": str(user.id),
                    "email": user.email,
                    "teudatZehut": user.teudatZehut,
                    "birthday": "",
                    "marriage_date": "",
                    "highSchoolInstitution": "",
                    "army_role": "",
                    "unit_name": "",
                    "matsber": "",
                    "militaryDateOfDischarge": "",
                    "militaryDateOfEnlistment": "",
                    "militaryUpdatedDateTime": "",
                    "militaryPositionOld": "",
                    "educationalInstitution": "",
                    "educationFaculty": "",
                    "workOccupation": "",
                    "workType": "",
                    "workPlace": "",
                    "workStatus": "",
                    "paying": ""
                })
        except Exception as e:
            print(f"Error building personas from users: {str(e)}")
            raise ValueError(f"Error building personas from users: {str(e)}")

    def get_personas(self) -> List[Dict[str, Any]]:
        print(f"Getting personas for user ID: {self.user_id}")
        user = self.fetch_user()
        self.build_apprentice_list(user)
        self.build_user_list(user)
        apprentice_ids = [apprentice.id for apprentice in self.apprentices]
        related_data = self.fetch_related_data(apprentice_ids)
        self.build_personas_from_apprentices(related_data)
        self.build_personas_from_users()
        return self.personas


def get_personas(created_by_id):
    try:
        builder = PersonaBuilder(created_by_id)
        personas = builder.get_personas()
        return jsonify(personas)
    except Exception as e:
        raise e
