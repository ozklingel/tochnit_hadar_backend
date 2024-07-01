from flask import jsonify
from http import HTTPStatus
from datetime import date
from typing import List, Dict, Any
import config

from src.services import db
from src.models.models_utils import to_iso
from src.models.apprentice_model import Apprentice
from src.models.city_model import City
from src.models.task_model import Task
from src.models.user_model import User
from src.models.report_model import Report


# Constants for role IDs
ROLE_MELAVE = "0"
ROLE_RAKAZ_MOSAD = "1"
ROLE_RAKAZ_ESHOL = "2"
ROLE_AHRAI_TOHNIT = "3"


class Address:
    def __init__(self, country: str, city: str, city_id: str, street: str, house_number: str,
                 apartment: str, region: str, entrance: str, floor: str, postal_code: str,
                 lat: float, lng: float):
        self.country = country
        self.city = city
        self.city_id = city_id
        self.street = street
        self.house_number = house_number
        self.apartment = apartment
        self.region = region
        self.entrance = entrance
        self.floor = floor
        self.postal_code = postal_code
        self.lat = lat
        self.lng = lng


class Event:
    def __init__(self, event_id: str, title: str, description: str, date: str):
        self.event_id = event_id
        self.title = title
        self.description = description
        self.date = date


class Contact:
    def __init__(self, first_name: str, last_name: str, phone: str, email: str, relation: str):
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.email = email
        self.relation = relation


class ApprenticeBuilder:
    def __init__(self, apprentice, city, mentor_name, base_id, report_list, event_list):
        self.apprentice = apprentice
        self.city = city
        self.mentor_name = mentor_name
        self.base_id = base_id
        self.report_list = report_list
        self.event_list = event_list

    def build_address(self) -> Address:
        return Address(
            country="IL",
            city=self.city.name if self.city else "",
            city_id=str(self.apprentice.city_id),
            street=self.apprentice.address,
            house_number="1",
            apartment="1",
            region=str(self.city.region_id) if self.city else "",
            entrance="a",
            floor="1",
            postal_code="12131",
            lat=32.04282620026557,
            lng=34.75186193813887
        )

    def build_contacts(self) -> List[Contact]:
        return [
            Contact(
                first_name=self.apprentice.contact1_first_name,
                last_name=self.apprentice.contact1_last_name,
                phone=self.apprentice.contact1_phone,
                email=self.apprentice.contact1_email,
                relation=self.apprentice.contact1_relation
            ),
            Contact(
                first_name=self.apprentice.contact2_first_name,
                last_name=self.apprentice.contact2_last_name,
                phone=self.apprentice.contact2_phone,
                email=self.apprentice.contact2_email,
                relation=self.apprentice.contact2_relation
            ),
            Contact(
                first_name=self.apprentice.contact3_first_name,
                last_name=self.apprentice.contact3_last_name,
                phone=self.apprentice.contact3_phone,
                email=self.apprentice.contact3_email,
                relation=self.apprentice.contact3_relation
            )
        ]

    def build_events(self) -> List[Event]:
        return [
            Event(
                event_id=str(row.id),
                title=row.event,
                description=row.details,
                date=to_iso(row.date)
            ) for row in self.event_list
        ]

    def build(self) -> Dict[str, Any]:
        return {
            "accompany_id": str(self.apprentice.accompany_id),
            "Horim_status": visit_gap_color(config.HorimCall_report, self.apprentice, 365, 350),
            "personalMeet_status": visit_gap_color(config.personalMeet_report, self.apprentice, 100, 80),
            "call_status": visit_gap_color(config.call_report, self.apprentice, 30, 15),
            "highSchoolRavMelamed_phone": self.apprentice.high_school_teacher_phone,
            "highSchoolRavMelamed_name": self.apprentice.high_school_teacher,
            "highSchoolRavMelamed_email": self.apprentice.high_school_teacher_email,
            "thRavMelamedYearA_name": self.apprentice.teacher_grade_a,
            "thRavMelamedYearA_phone": self.apprentice.teacher_grade_a_phone,
            "thRavMelamedYearA_email": self.apprentice.teacher_grade_a_email,
            "thRavMelamedYearB_name": self.apprentice.teacher_grade_b,
            "thRavMelamedYearB_phone": self.apprentice.teacher_grade_b_phone,
            "thRavMelamedYearB_email": self.apprentice.teacher_grade_b_email,
            "address": self.build_address().__dict__,
            "contacts": [contact.__dict__ for contact in self.build_contacts()],
            "activity_score": len(self.report_list),
            "reports": [str(i.id) for i in self.report_list],
            "events": [event.__dict__ for event in self.build_events()],
            "id": str(self.apprentice.id),
            "thMentor": str(self.apprentice.accompany_id),
            "thMentor_name": f"{self.mentor_name[0]} {self.mentor_name[1]}" if self.mentor_name else "",
            "militaryPositionNew": str(self.apprentice.militaryPositionNew),
            "avatar": self.apprentice.photo_path if self.apprentice.photo_path else "https://www.gravatar.com/avatar",
            "name": str(self.apprentice.name),
            "last_name": str(self.apprentice.last_name),
            "institution_id": str(self.apprentice.institution_id),
            "thPeriod": str(self.apprentice.hadar_plan_session),
            "serve_type": self.apprentice.serve_type,
            "marriage_status": str(self.apprentice.marriage_status),
            "militaryCompoundId": str(self.base_id),
            "phone": self.apprentice.phone,
            "email": self.apprentice.email,
            "teudatZehut": self.apprentice.teudatZehut,
            "birthday": to_iso(self.apprentice.birthday),
            "marriage_date": to_iso(self.apprentice.marriage_date),
            "highSchoolInstitution": self.apprentice.highSchoolInstitution,
            "army_role": self.apprentice.army_role,
            "unit_name": self.apprentice.unit_name,
            "matsber": str(self.apprentice.spirit_status),
            "militaryDateOfDischarge": to_iso(self.apprentice.release_date),
            "militaryDateOfEnlistment": to_iso(self.apprentice.recruitment_date),
            "militaryUpdatedDateTime": to_iso(self.apprentice.militaryupdateddatetime),
            "militaryPositionOld": self.apprentice.militaryPositionOld,
            "educationalInstitution": self.apprentice.educationalinstitution,
            "educationFaculty": self.apprentice.educationfaculty,
            "workOccupation": self.apprentice.workoccupation,
            "workType": self.apprentice.worktype,
            "workPlace": self.apprentice.workplace,
            "workStatus": self.apprentice.workstatus,
            "paying": self.apprentice.paying
        }


def get_user_details(user_id: str):
    return db.session.query(User.role_ids, User.institution_id, User.cluster_id).filter(User.id == user_id).first()


def get_apprentices_by_role(user_details):
    query = db.session.query(Apprentice)
    if ROLE_MELAVE in user_details.role_ids:
        query = query.filter(Apprentice.institution_id ==
                             user_details.institution_id)
    elif ROLE_RAKAZ_MOSAD in user_details.role_ids:
        query = query.filter(Apprentice.cluster_id == user_details.cluster_id)
    elif ROLE_RAKAZ_ESHOL in user_details.role_ids or ROLE_AHRAI_TOHNIT in user_details.role_ids:
        pass  # No filtering needed, fetch all
    else:
        return [], {}, {}, {}, {}

    apprentices = query.all()

    apprentice_ids = [str(apprentice.id) for apprentice in apprentices]
    city_ids = list(set(
        [apprentice.city_id for apprentice in apprentices if apprentice.city_id is not None]))
    accompany_ids = list(set(
        [apprentice.accompany_id for apprentice in apprentices if apprentice.accompany_id is not None]))

    cities = {city.id: city for city in db.session.query(
        City).filter(City.id.in_(city_ids)).all()}
    mentors = {user.id: user for user in db.session.query(
        User).filter(User.id.in_(accompany_ids)).all()}
    reports = db.session.query(Report).filter(
        Report.ent_reported.in_(apprentice_ids)).all()
    tasks = db.session.query(Task).filter(
        Task.subject.in_(apprentice_ids)).all()

    report_map = {}
    for report in reports:
        report_map.setdefault(report.ent_reported, []).append(report)

    task_map = {}
    for task in tasks:
        task_map.setdefault(task.subject, []).append(task)

    return apprentices, cities, mentors, report_map, task_map


def maps_apprentices(user_id):
    try:
        user_details = get_user_details(user_id)
        if not user_details:
            return jsonify({"result": "Wrong id"}), HTTPStatus.BAD_REQUEST

        apprentices, cities, mentors, report_map, task_map = get_apprentices_by_role(
            user_details)

        apprentices_data = [
            ApprenticeBuilder(
                apprentice=apprentice,
                city=cities.get(apprentice.city_id),
                mentor_name=(mentors.get(apprentice.accompany_id).name, mentors.get(
                    apprentice.accompany_id).last_name) if mentors.get(apprentice.accompany_id) else None,
                base_id=apprentice.base_address,
                report_list=report_map.get(apprentice.id, []),
                event_list=task_map.get(apprentice.id, [])
            ).build() for apprentice in apprentices
        ]

        return jsonify(apprentices_data), HTTPStatus.OK
    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR


def visit_gap_color(type, apprentice, redLine, greenLine):
    visitEvent = (
        db.session.query(Report)
        .filter(Report.ent_reported == apprentice.id, Report.title == type)
        .order_by(Report.visit_date.desc())
        .first()
    )
    if visitEvent is None:
        return "red"
    gap = (date.today() - visitEvent.visit_date).days
    if gap > redLine:
        return "red"
    if redLine >= gap > greenLine:
        return "orange"
    return "green"
