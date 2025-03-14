import re
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass
from flask import jsonify
import boto3
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import text
import logging

from src.models.city_model import City
from src.models.task_model_v2 import Task, TaskStatusEnum
from src.services import db
from src.models.apprentice_model import Apprentice
from config import BUCKET, AWS_access_key_id, AWS_secret_access_key

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class UpdateResult:
    success: bool
    warnings: List[str]
    errors: List[str]


class ApprenticeUpdater:
    def __init__(self, db_session, front_end_dict: Dict[str, str]):
        self.db_session = db_session
        self.front_end_dict = front_end_dict
        self.s3 = boto3.resource(
            "s3",
            aws_access_key_id=AWS_access_key_id,
            aws_secret_access_key=AWS_secret_access_key,
        )

    def update(self, apprentice_id: str, data: Dict[str, Any]) -> UpdateResult:
        updated_ent = Apprentice.query.get(apprentice_id)
        if not updated_ent:
            return UpdateResult(False, [], ["Apprentice not found"])

        warnings = []
        errors = []

        for key, value in data.items():
            try:
                db_key = self.front_end_dict.get(key, key)
                if db_key is None:
                    errors.append(f"Error updating {key}: no such attribute")
                    continue
                self._update_field(updated_ent, key, db_key, value, warnings, errors)
            except Exception as e:
                errors.append(f"Error updating {key}: {str(e)}")

        if errors:
            return UpdateResult(False, warnings, errors)

        try:
            logger.debug(
                f"base_address value before commit: {updated_ent.base_address}"
            )
            self.db_session.commit()
        except IntegrityError as e:
            self.db_session.rollback()
            logger.error(f"Integrity error during commit: {str(e)}")
            return UpdateResult(
                False, warnings, [f"Database integrity error: {str(e)}"]
            )

        return UpdateResult(True, warnings, [])

    def _update_field(
        self,
        updated_ent: Apprentice,
        key: str,
        db_key: str,
        value: Any,
        warnings: List[str],
        errors: List[str],
    ) -> None:
        if key == "militaryCompoundId":
            self._update_military_compound_id(updated_ent, value, warnings)
        elif key == "avatar":
            self._update_avatar(updated_ent, value)
        elif key == "email":
            self._update_email(updated_ent, db_key, value, errors)
        elif key in [
            "birthday",
            "militaryDateOfEnlistment",
            "militaryDateOfDischarge",
            "marriage_date",
        ]:
            self._update_date(updated_ent, db_key, value, errors)
        elif key == "address":
            self._update_address(updated_ent, value)

        elif key == "thMentor_id" or key == "accompany_id":
            if value != "":
                tasks = (
                    db.session.query(Task)
                    .filter(
                        Task.user_id == updated_ent.accompany_id,
                        Task.subject_id == str(updated_ent.id),
                        Task.status == TaskStatusEnum.TODO,
                    )
                    .all()
                )
                for task_ in tasks:
                    task_.user_id = value
                    db.session.add(task_)
                setattr(updated_ent, db_key, value)
        else:
            setattr(updated_ent, db_key, value)

    def _update_military_compound_id(
        self, updated_ent: Apprentice, value: Any, warnings: List[str]
    ) -> None:
        logger.debug(f"Attempting to set militaryCompoundId to: {value}")
        exists = self.db_session.execute(
            text("SELECT 1 FROM base WHERE id = :id"), {"id": value}
        ).scalar()
        if exists:
            setattr(updated_ent, "base_address", value)
        else:
            setattr(updated_ent, "base_address", None)
            warnings.append(
                f"militaryCompoundId {value} does not exist in base table. Set to None."
            )

    def _update_avatar(self, updated_ent: Apprentice, new_avatar: str) -> None:
        if updated_ent.photo_path != "https://www.gravatar.com/avatar":
            self.s3.Object(BUCKET, updated_ent.photo_path).delete()
        updated_ent.photo_path = new_avatar

    def _update_email(
        self, updated_ent: Apprentice, db_key: str, value: str, errors: List[str]
    ) -> None:
        if self._validate_email(value):
            setattr(updated_ent, db_key, value)
        else:
            errors.append(f"Invalid email format: {value}")

    def _update_date(
        self, updated_ent: Apprentice, db_key: str, value: str, errors: List[str]
    ) -> None:
        if self._validate_date(value[:10]):
            setattr(updated_ent, db_key, value)
        else:
            errors.append(f"Invalid date format for {db_key}: {value}")

    def _update_address(self, updated_ent: Apprentice, value: str) -> None:
        address_data = value
        for addr_key, addr_value in address_data.items():
            if hasattr(updated_ent, addr_key):
                if addr_key == "city":
                    city_id = (
                        db.session.query(City.id).filter(City.name == value).first()
                    )
                    setattr(updated_ent, "city_id", city_id.id)
                    continue
                setattr(updated_ent, addr_key, addr_value)

    @staticmethod
    def _validate_email(email: str) -> bool:
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(email_regex, email) is not None

    @staticmethod
    def _validate_date(date_string: str) -> bool:
        try:
            datetime.strptime(date_string, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    @staticmethod
    def _parse_address(address_string: str) -> Dict[str, Any]:
        address_parts = address_string.split(", ")
        return {
            "address": address_parts[0] if len(address_parts) > 0 else "",
            "city_id": (
                int(address_parts[1])
                if len(address_parts) > 1 and address_parts[1].isdigit()
                else None
            ),
        }


def update(request):
    try:
        apprentice_id = request.args.get("apprenticeId")
        if not apprentice_id:
            return jsonify({"error": "Missing apprenticeId parameter"}), 400

        data = request.json
        if not data:
            return jsonify({"error": "No data provided for update"}), 400

        updater = ApprenticeUpdater(db.session, front_end_dict)
        result = updater.update(apprentice_id, data)

        if not result.success:
            return jsonify({"error": "Update failed", "details": result.errors}), 400

        response = {"result": "success"}
        if result.warnings:
            response["warnings"] = result.warnings

        return jsonify(response), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error: {str(e)}")
        return jsonify({"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Unexpected error", "details": str(e)}), 500


front_end_dict = {
    "avatar": "photo_path",
    "militaryCompoundId": "base_address",
    "army_role": "army_role",
    "militaryPositionNew": "militaryPositionNew",
    "militaryPositionOld": "militaryPositionOld",
    "militaryDateOfEnlistment": "recruitment_date",
    "militaryDateOfDischarge": "release_date",
    "unit_name": "unit_name",
    "teudatZehut": "teudatZehut",
    "email": "email",
    "address": "address",
    "city": "city",
    "house_number": "house_number",
    "marriage_status": "marriage_status",
    "phone": "phone",
    "birthday": "birthday",
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
    "contact3_email": "contact3_email",
    "contact3_relation": "contact3_relation",
    "highSchoolRavMelamed_phone": "high_school_teacher_phone",
    "highSchoolRavMelamed_name": "high_school_teacher",
    "highSchoolRavMelamed_email": "high_school_teacher_email",
    "cluster_id": "cluster_id",
    "thRavMelamedYearA_name": "teacher_grade_a",
    "thRavMelamedYearA_phone": "teacher_grade_a_phone",
    "thRavMelamedYearA_email": "teacher_grade_a_email",
    "thRavMelamedYearB_name": "teacher_grade_b",
    "thRavMelamedYearB_phone": "teacher_grade_b_phone",
    "thRavMelamedYearB_email": "teacher_grade_b_email",
    "th_mentor_id": "accompany_id",
    "thMentor_id": "accompany_id",#####33
    "educationalInstitution": "educationalinstitution",
    "thPeriod": "hadar_plan_session",
    "id": "id",
    "name": "name",
    "last_name": "last_name",
    "institution_id": "institution_id",
    "paying": "paying",
    "matsber": "spirit_status",
    "serve_type": "serve_type",
    "marriage_date": "marriage_date",
    "militaryUpdatedDateTime": "militaryupdateddatetime",
    "educationFaculty": "educationfaculty",
    "workOccupation": "workoccupation",
    "workPlace": "workplace",  
    "workType": "worktype",   
    "workStatus": "workstatus" 
}