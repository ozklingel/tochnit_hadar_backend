import json

from http import HTTPStatus
from flask import Blueprint, request, jsonify, Response

from src.routes.user_profile import correct_auth
from src.services import db
from src.models.task_model import Task

tasks_form_blueprint = Blueprint("tasks_form", __name__, url_prefix="/tasks_form")


@tasks_form_blueprint.route("/getTasks", methods=["GET"])
def getTasks():
    if correct_auth() == False:
        return jsonify({"result": "wrong access token"}), HTTPStatus.OK
    userId = request.args.get("userId")

    tasks = db.session.query(Task).filter(Task.userid == userId).all()
    tasks_list = []

    for task in tasks:
        tasks_list.append(task.to_attributes())

    return Response(json.dumps(tasks_list), mimetype="application/json"), HTTPStatus.OK


@tasks_form_blueprint.route("/update", methods=["put"])
def updateTask():
    try:
        if correct_auth() == False:
            return jsonify({"result": "wrong access token"}), HTTPStatus.OK
        task_id = request.args.get("task_id")
        data = request.json
        if not data:
            raise Exception("no data")

        task = Task.query.get(task_id)
        for key in data:
            setattr(task, key, data[key])

        db.session.commit()
        return jsonify({"result": "error"}), HTTPStatus.OK
    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST


@tasks_form_blueprint.route("/add", methods=["POST"])
def add_task():
    try:
        if correct_auth() == False:
            return jsonify({"result": "wrong access token"}), HTTPStatus.OK
        data = request.json

        if not data:
            return jsonify({"result": "no data"}), HTTPStatus.BAD_REQUEST

        task = Task().from_attributes(data)
        db.session.add(task)
        db.session.commit()
    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST
    return jsonify({"result": "success"}), HTTPStatus.OK


@tasks_form_blueprint.route("/delete", methods=["POST"])
def delete():
    try:
        if correct_auth() == False:
            return jsonify({"result": "wrong access token"}), HTTPStatus.OK
        data = request.json
        taskId = data["task_id"]
        res = db.session.query(Task).filter(Task.id == taskId).delete()

        db.session.commit()
    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST
    return jsonify({"result": "success"}), HTTPStatus.OK


@tasks_form_blueprint.route("/setWasRead", methods=["post"])
def setWasRead_task_form():
    if correct_auth() == False:
        return jsonify({"result": "wrong access token"}), HTTPStatus.OK
    data = request.json
    task_id = data["task_id"]
    try:
        noti = Task.query.get(task_id)
        noti.allreadyread = True
        db.session.commit()
        return jsonify({"result": "success"}), HTTPStatus.OK
    except:
        return jsonify({"result": "wrong id"}), HTTPStatus.OK
