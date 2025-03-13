import uuid
from http import HTTPStatus
from typing import Tuple, Dict, Any
from flask import Blueprint, request, jsonify, Response
from datetime import date

from sqlalchemy import or_
from ..models.apprentice_model import Apprentice
from ..models.user_model import User

from src.logic.tasks import (
    TaskFactory,
    TaskData,
    TaskFrequencyData,
    TaskNotFoundException,
    UserNotFoundException,
    InvalidTaskDataException,
)
from src.models import to_iso
from src.services import db
from src.models.task_model_v2 import (
    TaskStatusEnum,
    TaskSubjectTypeEnum,
    TaskFrequencyRepeatTypeEnum,
    TaskFrequencyWeekdayEnum,
    TaskTubTypeEnum,
)
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

tasks_form_blueprint = Blueprint("tasks", __name__, url_prefix="/tasks")


@tasks_form_blueprint.route("add", methods=["POST"])
def create_task() -> Tuple[Response, int]:
    task_service = get_task_service()
    try:
        task_data = _parse_task_data(request.json)
        new_task_dict = task_service.create_task(task_data)
        logger.debug(f"Created new task with id {new_task_dict['id']}")
        return jsonify(new_task_dict), HTTPStatus.CREATED
    except InvalidTaskDataException as e:
        logger.warning(f"Invalid task data: {str(e)}")
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST
    except UserNotFoundException as e:
        logger.warning(f"User not found: {str(e)}")
        return jsonify({"error": str(e)}), HTTPStatus.NOT_FOUND
    except Exception as e:
        logger.error(f"Error in create_task: {str(e)}", exc_info=True)
        return (
            jsonify({"error": "An unexpected error occurred"}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
@tasks_form_blueprint.route("add_all_users", methods=["POST"])
def add_all_users() -> Tuple[Response, int]:
    try:
        task_service = get_task_service()
        user_ent_list = db.session.query(User.id, User.fcmToken,User.name).filter(User.role_ids.contains("0")).all()
        not_committed=[]
        for user_ in user_ent_list:
            request.json["user_id"]=user_.id
            apprentice_ent_list = db.session.query(Apprentice.id).filter(Apprentice.accompany_id==user_.id,
                                                                         or_(Apprentice.hadar_plan_session=="ד",Apprentice.hadar_plan_session=="ה")).all()
            for appren_ in apprentice_ent_list:
                request.json["subject_id"]=appren_.id
                task_data = _parse_task_data(request.json)
                new_task_dict = task_service.create_task(task_data)
        return jsonify({"result":"success","not commited":not_committed}), HTTPStatus.OK
    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST

@tasks_form_blueprint.route("", methods=["GET"])
def get_tasks() -> Tuple[Response, int]:
    user_id = request.args.get("userId")
    is_contains_export = request.args.get("is_contains_export")

    if not user_id:
        logger.warning("Get tasks request missing user_id")
        return jsonify({"error": "User ID is required"}), HTTPStatus.BAD_REQUEST

    task_service = get_task_service()
    try:
        tasks = task_service.get_tasks_by_user_id(int(user_id),is_contains_export)
        logger.debug(f"Retrieved {len(tasks)} tasks for user {user_id}")
        return jsonify(tasks), HTTPStatus.OK
    except UserNotFoundException as e:
        logger.warning(f"User not found: {str(e)}")
        return jsonify({"error": str(e)}), HTTPStatus.NOT_FOUND
    except Exception as e:
        logger.error(f"Error in get_tasks: {str(e)}", exc_info=True)
        return (
            jsonify({"error": "An unexpected error occurred"}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


def get_task_service():
    return TaskFactory.create_task_service(db.session)


@tasks_form_blueprint.route("/subject/<int:subject_id>", methods=["GET"])
def get_events_by_subject_id(subject_id: int) -> Tuple[Response, int]:
    subject_type_str = request.args.get("subject_type")
    is_event = request.args.get("is_event")

    if not subject_type_str:
        logger.warning("Get events by subject ID request missing subject_type")
        return jsonify({"error": "Subject type is required"}), HTTPStatus.BAD_REQUEST

    try:
        subject_type = TaskSubjectTypeEnum[subject_type_str.upper()]
    except KeyError:
        logger.warning(f"Invalid subject type: {subject_type_str}")
        return jsonify({"error": "Invalid subject type"}), HTTPStatus.BAD_REQUEST

    task_service = get_task_service()
    try:
        tasks = task_service.get_events_by_subject_id(
            str(subject_id), subject_type, is_event
        )
        logger.debug(
            f"Retrieved {len(tasks)} tasks for subject {subject_id} of type {subject_type.name}"
        )
        return jsonify(tasks), HTTPStatus.OK
    except TaskNotFoundException as e:
        logger.warning(
            f"No tasks found for subject {subject_id} of type {subject_type.name}: {str(e)}"
        )
        return jsonify({"error": str(e)}), HTTPStatus.NOT_FOUND
    except Exception as e:
        logger.error(f"Error in get_events_by_subject_id: {str(e)}", exc_info=True)
        return (
            jsonify({"error": "An unexpected error occurred"}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


@tasks_form_blueprint.route("/<uuid:task_id>", methods=["GET"])
def get_task(task_id: uuid) -> Tuple[Response, int]:
    task_service = get_task_service()
    try:
        task = task_service.get_task_by_id(task_id)
        logger.debug(f"Retrieved task {task_id}")
        return jsonify(task), HTTPStatus.OK
    except TaskNotFoundException as e:
        logger.warning(f"Task not found: {str(e)}")
        return jsonify({"error": str(e)}), HTTPStatus.NOT_FOUND
    except Exception as e:
        logger.error(f"Error in get_task: {str(e)}", exc_info=True)
        return (
            jsonify({"error": "An unexpected error occurred"}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


@tasks_form_blueprint.route("/<uuid:task_id>", methods=["PUT"])
def update_task(task_id: uuid) -> Tuple[Response, int]:
    task_service = get_task_service()
    try:
        task_data = _parse_partial_task_data(request.json)
        updated_task_dict = task_service.update_task(task_id, task_data)
        logger.debug(f"Updated task {task_id}")
        return jsonify(updated_task_dict), HTTPStatus.OK
    except TaskNotFoundException as e:
        logger.warning(f"Task not found: {str(e)}")
        return jsonify({"error": str(e)}), HTTPStatus.NOT_FOUND
    except InvalidTaskDataException as e:
        logger.warning(f"Invalid task data: {str(e)}")
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST
    except Exception as e:
        logger.error(f"Error in update_task: {str(e)}", exc_info=True)
        return (
            jsonify({"error": "An unexpected error occurred"}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


@tasks_form_blueprint.route("/<uuid:task_id>", methods=["DELETE"])
def delete_task(task_id: uuid) -> Tuple[Response, int]:
    task_service = get_task_service()
    try:
        task_service.delete_task(task_id)
        logger.debug(f"Deleted task {task_id}")
        return jsonify({"result": "success"}), HTTPStatus.OK
    except TaskNotFoundException as e:
        logger.warning(f"Task not found: {str(e)}")
        return jsonify({"error": str(e)}), HTTPStatus.NOT_FOUND
    except Exception as e:
        logger.error(f"Error in delete_task: {str(e)}", exc_info=True)
        return (
            jsonify({"error": "An unexpected error occurred"}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


def _parse_task_data(data: Dict[str, Any]) -> TaskData:
    logger.debug(f"Parsing task data: {data}")
    if not data:
        logger.warning("No data provided for task creation/update")
        raise ValueError("No data provided")

    try:
        frequency_data = None
        if "frequency" in data:
            frequency_data = TaskFrequencyData(
                repeat_count=data["frequency"].get("repeat_count"),
                repeat_type=TaskFrequencyRepeatTypeEnum[
                    data["frequency"]["repeat_type"]
                ],
                weekdays=(
                    [
                        TaskFrequencyWeekdayEnum[day]
                        for day in data["frequency"].get("weekdays", [])
                    ]
                    if data["frequency"].get("weekdays")
                    else None
                ),
            )

        return TaskData(
            id=uuid.uuid4(),
            user_id=data["user_id"],
            subject_type=TaskSubjectTypeEnum[data["subject_type"]],
            subject_id=data["subject_id"],
            name=data["name"],
            description=data.get("description"),
            status=TaskStatusEnum[data.get("status", "TODO")],
            has_been_read=data.get("has_been_read", False),
            made_by_user=data.get("made_by_user", False),
            start_date=data["start_date"],
            end_date=(data["end_date"] if "end_date" in data else None),
            frequency=frequency_data,
            tub_type=TaskTubTypeEnum["PERSONAL"],
            created_at=to_iso(date.today()),
        )
    except KeyError as e:
        logger.error(f"Missing required field in task data: {str(e)}")
        raise InvalidTaskDataException(f"Missing required field: {str(e)}")
    except ValueError as e:
        logger.error(f"Invalid value in task data: {str(e)}")
        raise InvalidTaskDataException(f"Invalid value: {str(e)}")


def _parse_partial_task_data(data: Dict[str, Any]) -> dict:
    logger.debug(f"Parsing partial task data: {data}")
    if not data:
        logger.warning("No data provided for task update")
        raise ValueError("No data provided")

    parsed_data = {}

    if "user_id" in data:
        parsed_data["user_id"] = data["user_id"]
    if "subject_type" in data:
        parsed_data["subject_type"] = TaskSubjectTypeEnum[data["subject_type"]]
    if "subject_id" in data:
        parsed_data["subject_id"] = data["subject_id"]
    if "name" in data:
        parsed_data["name"] = data["name"]
    if "description" in data:
        parsed_data["description"] = data["description"]
    if "status" in data:
        parsed_data["status"] = TaskStatusEnum[data["status"].upper()]
    if "has_been_read" in data:
        parsed_data["has_been_read"] = data["has_been_read"]
    if "made_by_user" in data:
        parsed_data["made_by_user"] = data["made_by_user"]
    if "start_date" in data:
        parsed_data["start_date"] = datetime.fromisoformat(data["start_date"])
    if "end_date" in data:
        parsed_data["end_date"] = datetime.fromisoformat(data["end_date"]) if data["end_date"] else None

    if "frequency" in data:
        parsed_data["frequency"] = TaskFrequencyData(
            repeat_count=data["frequency"].get("repeat_count") if data["frequency"] and data["frequency"].get("repeat_count") else None ,
            repeat_type=TaskFrequencyRepeatTypeEnum[data["frequency"]["repeat_type"]],
            weekdays=(
                [
                    TaskFrequencyWeekdayEnum[day]
                    for day in data["frequency"].get("weekdays", [])
                ]
                if data["frequency"].get("weekdays")
                else None
            ),
        )
    if "is_delete_from_notification" in data:
        parsed_data["is_delete_from_notification"] = data["is_delete_from_notification"]


    return parsed_data
