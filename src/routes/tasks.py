import datetime
import json
import uuid

from datetime import datetime as dt
from http import HTTPStatus
from flask import Blueprint, request, jsonify, Response

import config
from src.routes.user_profile import correct_auth
from src.services import db
from src.models.apprentice_model import Apprentice
from src.models.task_model import Task
from src.models.user_model import User

from src.models.report_model import Report
from src.routes.notification_form_routes import getAll_notification_form

tasks_form_blueprint = Blueprint('tasks_form', __name__, url_prefix='/tasks_form')


# frontend-if userid only melave-filter by title,else ,filter by status
@tasks_form_blueprint.route("/getTasks", methods=['GET'])
def getTasks():
    if correct_auth() == False:
        return jsonify({'result': "wrong access token"}), HTTPStatus.OK
    # get tasksAndEvents
    userId = request.args.get("userId")
    role = db.session.query(User.role_ids).filter(
        User.id == userId).first()
    myTask = []

    tasks = db.session.query(Task).filter(
        Task.userid == userId).all()

    for task in tasks:
        daysFromNow = (dt.today() - task.date).days if task.date is not None else 100
        date_format = '%Y-%m-%d'
        # time to new tsk
        if daysFromNow == 0 and dt.strptime(task.frequency_end[:-9],
                                            date_format) > dt.today():  # insert new row for next run todo
            if task.frequency_meta == "daily":
                next_date = datetime.datetime.today() - datetime.timedelta(days=(-1))
            if task.frequency_meta == "weekly":
                next_date = datetime.datetime.today() - datetime.timedelta(days=7 * (-1))
            if task.frequency_meta == "monthly":
                next_date = datetime.datetime.today() - datetime.timedelta(days=30 * (-1))
            if task.frequency_meta == "yearly":
                next_date = datetime.datetime.today() - datetime.timedelta(days=365 * (-1))
            daysFromNow = (dt.today() - next_date).days if task.date is not None else 100
            myTask.append(
                {"frequency": task.frequency_meta, "description": task.details, 'status': "private",
                 'subject': task.event,
                 'date': str(next_date) + str(task.date)[11:], 'daysfromnow': daysFromNow, 'event': task.event,
                 'id': str(uuid.uuid4().int)[:5],
                 'title': "own task"})
        # oldtsk
        myTask.append(
            {"frequency": task.frequency_meta, "description": task.details, 'status': task.status,
             'subject': task.event,
             'date': str(task.date), 'daysfromnow': 373, 'event': task.event, 'id': str(task.id),
             'title': "own task"})
    # handle not  ahrai tohnit
    res = getAll_notification_form(False)
    todo_dict = []
    todo_ids = []
    try:
        res[0]
    except Exception as e:
        return jsonify([]), HTTPStatus.OK

    try:
        for i in range(0, len(res[0].json)):
            ent = res[0].json[i]
            if "דוח" in ent["event"] or "עידכון" in ent["event"]:
                continue
            todo_ids.append(ent["id"])
            if ("," not in role.role_ids and ent["event"] in config.eshcol_reports) or (
                    "," not in role.role_ids and ent["event"] in config.mosad_reports):
                ent["status"] = "private"
            else:
                ent["status"] = "general"

            ent["id"] = str(ent["id"])
            ent["subject"] = [ent["subject"]]
            if ent["event"] == config.groupMeet_report or ent["event"] == config.basis_report:
                ent["subject"] = []
            ent["title"] = "מפגשים"
            if ent["event"] in config.report_as_meet:
                ent["title"] = "מפגשים"
            if ent["event"] in config.reports_as_call:
                ent["title"] = "שיחות"
            todo_dict.append(ent)

        ApprenticeList = db.session.query(Apprentice.id).filter(
            Apprentice.accompany_id == userId).all()
        all_ApprenticeList_Horim = [r[0] for r in ApprenticeList]

        visitHorim = db.session.query(Report.ent_reported).filter(Report.user_id == userId,
                                                                 Report.title == config.HorimCall_report).all()
        for i in visitHorim:
            if i[0] in all_ApprenticeList_Horim:
                all_ApprenticeList_Horim.remove(i[0])
        for ent in all_ApprenticeList_Horim:
            # Apprentice1 = db.session.query(Apprentice.name,Apprentice.last_name).filter(Apprentice.id == ent).first()
            todo_dict.append({"frequency": "never", "description": "", 'status': 'general', "allreadyread": False,
                              'subject': [str(ent)], 'date': '2023-01-01T00:00:00', 'daysfromnow': 373,
                              'event': 'מפגש_הורים', 'id': str(uuid.uuid4().int)[:5], 'title': 'הורים'})

        too_old = datetime.datetime.today() - datetime.timedelta(days=60)
        done_visits = db.session.query(Report.ent_reported, Report.title, Report.visit_date, Report.id,
                                       Report.description).filter(Report.user_id == userId,
                                                                 Report.id.not_in(todo_ids),
                                                                 Report.visit_date > too_old).distinct(Report.id).all()
        done_visits_dict = [{"frequency": "never", "allreadyread": False, "event": str(row[1]),
                             "description": str(row[4]), 'status': 'done', "subject": [str(row[0])],
                             "title": str(row[1])
                                , "daysfromnow": 373, "date": str(row[2]), "id": str(row[3])} for row in
                            [tuple(row) for row in done_visits]] if done_visits is not None else []

        tasks_list = todo_dict + done_visits_dict + myTask

        return Response(json.dumps(tasks_list), mimetype='application/json'), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': 'error while get' + str(e)}), HTTPStatus.BAD_REQUEST


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

        # frequency_weekday = json_object["frequency_weekday"]

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
            # frequency_weekday=frequency_weekday,#weekday
            frequency_meta=frequency_meta,  # daily
            frequency_end=str(future_date_finish)[:-7],  # finish date
            id=int(str(uuid.uuid4().int)[:5]),

        )

        db.session.add(task_userMade1)
        db.session.commit()
    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST
    return jsonify({"result": "success"}), HTTPStatus.OK
    # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK


@tasks_form_blueprint.route('/delete', methods=['POST'])
def delete():
    try:
        if correct_auth()==False:
            return jsonify({'result': "wrong access token"}), HTTPStatus.OK
        data = request.json
        taskId = data['taskId']
        res = db.session.query(Task).filter(Task.id == taskId).delete()

        # res = db.session.query(notifications).filter(notifications.id == taskId).delete()
        db.session.commit()
    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST
    return jsonify({"result": "success"}), HTTPStatus.OK
    # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK


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