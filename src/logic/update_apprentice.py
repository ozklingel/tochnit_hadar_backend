import re
from datetime import datetime
from flask import Blueprint, request, jsonify
import boto3
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from src.services import db
from src.models.apprentice_model import Apprentice
from config import AWS_access_key_id, AWS_secret_access_key
from sqlalchemy import text
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

apprentice_profile_form_blueprint = Blueprint(
    'apprentice_profile_form', __name__)


def validate_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None


def validate_date(date_string):
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def parse_address(address_string):
    try:
        address_parts = address_string.split(', ')
        return {
            "address": address_parts[0] if len(address_parts) > 0 else "",
            "city_id": int(address_parts[1]) if len(address_parts) > 1 and address_parts[1].isdigit() else None,
        }
    except Exception as e:
        logger.error(f"Error parsing address: {str(e)}")
        raise ValueError(f"Invalid address format: {address_string}")


def handle_avatar(updated_ent, new_avatar):
    try:
        s3 = boto3.resource(
            "s3",
            aws_access_key_id=AWS_access_key_id,
            aws_secret_access_key=AWS_secret_access_key,
        )
        if updated_ent.photo_path != "https://www.gravatar.com/avatar":
            s3.Object("th01-s3", updated_ent.photo_path).delete()
        updated_ent.photo_path = new_avatar
    except Exception as e:
        logger.error(f"Error handling avatar: {str(e)}")
        raise RuntimeError(f"Failed to update avatar: {str(e)}")


def update(request):
    try:
        apprentice_id = request.args.get("apprenticetId")
        if not apprentice_id:
            return jsonify({"error": "Missing apprenticetId parameter"}), 400
        
        data = request.json
        if not data:
            return jsonify({"error": "No data provided for update"}), 400

        updated_ent = Apprentice.query.get(apprentice_id)
        if not updated_ent:
            return jsonify({"error": "Apprentice not found"}), 404

        update_warnings = []
        update_errors = []

        for key, value in data.items():
            try:
                db_key = front_end_dict.get(key, key)

                if key == "militaryCompoundId":
                    logger.info(f"Attempting to set militaryCompoundId to: {value}")
                    exists = db.session.execute(text("SELECT 1 FROM base WHERE id = :id"),
                        {"id": value}
                    ).scalar()
                    if exists:
                        if hasattr(updated_ent, 'base_address'):
                            setattr(updated_ent, 'base_address', value)
                        else:
                            update_warnings.append(f"base_address field not found in Apprentice model. militaryCompoundId: {value} not set.")
                    else:
                        if hasattr(updated_ent, 'base_address'):
                            setattr(updated_ent, 'base_address', None)
                            update_warnings.append(f"militaryCompoundId {value} does not exist in base table. Set to None.")
                        else:
                            update_warnings.append(f"base_address field not found in Apprentice model. militaryCompoundId: {value} not set.")
                elif key == "avatar":
                    handle_avatar(updated_ent, value)
                elif key == "email":
                    if validate_email(value):
                        setattr(updated_ent, db_key, value)
                    else:
                        update_errors.append(f"Invalid email format: {value}")
                elif key in ["birthday", "militaryDateOfEnlistment", "militaryDateOfDischarge", "marriage_date"]:
                    if validate_date(value[:10]):
                        setattr(updated_ent, db_key, value)
                    else:
                        update_errors.append(f"Invalid date format for {key}: {value}")
                elif key == "address":
                    address_data = parse_address(value)
                    for addr_key, addr_value in address_data.items():
                        if hasattr(updated_ent, addr_key):
                            setattr(updated_ent, addr_key, addr_value)
                elif key.startswith(("contact1_", "contact2_", "contact3_", "highSchoolRavMelamed_", "thRavMelamedYearA_", "thRavMelamedYearB_")):
                    setattr(updated_ent, key, value)
                else:
                    setattr(updated_ent, db_key, value)
            except Exception as e:
                update_errors.append(f"Error updating {key}: {str(e)}")

        if update_errors:
            return jsonify({"error": "Update failed", "details": update_errors}), 400

        try:
            logger.debug(f"base_address value before commit: {updated_ent.base_address}")
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Integrity error during commit: {str(e)}")
            return jsonify({"error": "Database integrity error", "details": str(e)}), 400

        response = {"result": "success"}
        if update_warnings:
            response["warnings"] = update_warnings

        return jsonify(response), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error: {str(e)}")
        return jsonify({"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Unexpected error", "details": str(e)}), 500


# The front_end_dict remains unchanged
# Ensure this is defined somewhere in your code
front_end_dict = {
    "address": "address",
    "cluster_id": "cluster_id",
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
