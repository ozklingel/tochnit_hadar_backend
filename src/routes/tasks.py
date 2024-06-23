import datetime
import json
import uuid

from http import HTTPStatus
from flask import Blueprint, request, jsonify, Response

from src.routes.user_profile import correct_auth
from src.services import db
from src.models.task_model import Task

tasks_form_blueprint = Blueprint('tasks_form', __name__, url_prefix='/tasks_form')


@tasks_form_blueprint.route("/getTasks", methods=['GET'])
def getTasks():
    if correct_auth() == False:
        return jsonify({'result': "wrong access token"}), HTTPStatus.OK
    userId = request.args.get("userId")

    tasks = db.session.query(Task).filter(Task.userid == userId).all()
    tasks_list = []

    for task in tasks:
        tasks_list.append(task.to_attributes())

    return Response(json.dumps(tasks_list), mimetype='application/json'), HTTPStatus.OK


@tasks_form_blueprint.route("/update", methods=['put'])
def updateTask():
    # get tasksAndEvents
    try:
        if correct_auth()==False:
            return jsonify({'result': "wrong access token"}), HTTPStatus.OK
        taskId = request.args.get("taskId")
        data = request.json
        updatedEnt = Task.query.get(taskId)
        for key in data:
            setattr(updatedEnt, key, data[key])
        db.session.commit()
        if updatedEnt:
            # TODO: add contact form to DB
            return jsonify({'result': 'success'}), HTTPStatus.OK
        return jsonify({'result': 'error'}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST


@tasks_form_blueprint.route('/add', methods=['POST'])
def add_task():
    try:
        if correct_auth()==False:
            return jsonify({'result': "wrong access token"}), HTTPStatus.OK
        json_object = request.json
        user = json_object["userId"]
        event = json_object["event"]
        date = json_object["date"]
        details = json_object["details"]
        frequency_end = json_object["frequency_end"]  # 1,2,3,4 or once or never
        frequency_meta = json_object["frequency_meta"]

        if frequency_end.isnumeric():
            if frequency_meta == "daily":
                future_date_finish = datetime.datetime.today() - datetime.timedelta(days=(-frequency_end))
            if frequency_meta == "weekly":
                future_date_finish = datetime.datetime.today() - datetime.timedelta(days=7 * (-frequency_end))
            if frequency_meta == "monthly":
                future_date_finish = datetime.datetime.today() - datetime.timedelta(days=30 * (-frequency_end))
            if frequency_meta == "yearly":
                future_date_finish = datetime.datetime.today() - datetime.timedelta(days=365 * (-frequency_end))
        elif frequency_meta == "once":
            future_date_finish = date
        else:
            future_date_finish = datetime.datetime.today() - datetime.timedelta(days=1000 * (-1))
        task_userMade1 = Task(
            userid=user,
            event=event,
            details=details,
            status="private",
            date=date,
            frequency_meta=frequency_meta,
            frequency_end=str(future_date_finish)[:-7],
            id=int(str(uuid.uuid4().int)[:5]),
        )
        db.session.add(task_userMade1)
        db.session.commit()
    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST
    return jsonify({"result": "success"}), HTTPStatus.OK


@tasks_form_blueprint.route('/delete', methods=['POST'])
def delete():
    try:
        if correct_auth()==False:
            return jsonify({'result': "wrong access token"}), HTTPStatus.OK
        data = request.json
        taskId = data['taskId']
        res = db.session.query(Task).filter(Task.id == taskId).delete()

        db.session.commit()
    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST
    return jsonify({"result": "success"}), HTTPStatus.OK


@tasks_form_blueprint.route('/setWasRead', methods=['post'])
def setWasRead_task_form():
    if correct_auth() == False:
        return jsonify({'result': "wrong access token"}), HTTPStatus.OK
    data = request.json
    task_id = data['task_id']
    try:
        noti = Task.query.get(task_id)
        noti.allreadyread = True
        db.session.commit()
        if task_id:
            # TODO: add contact form to DB
            return jsonify({'result': 'success'}), HTTPStatus.OK
    except:
        return jsonify({'result': 'wrong id'}), HTTPStatus.OK