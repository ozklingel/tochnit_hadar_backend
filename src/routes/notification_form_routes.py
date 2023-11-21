from datetime import datetime,date

from flask import Blueprint, request, jsonify
from http import HTTPStatus
from os import sys, path

from ..models.user_model import user1

pth = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(pth)
from app import app, db
import uuid
from ..models.notification_model import notifications

notification_form_blueprint = Blueprint('notification_form', __name__, url_prefix='/notification_form')

@notification_form_blueprint.route('/add', methods=['POST'])
def add_notification_form():
    user = request.form.get('userId')
    apprenticeid = request.form.get('apprenticeid')
    event = request.form.get('event')
    date = request.form.get('date')

    print(user)

    newToner = notifications(

                    userid=user,
                    apprenticeid = apprenticeid,
                    event=event,
                    date=date,
                    timefromnow=None,
                    allreadyread=False,
                    id=int(str(uuid.uuid4().int)[:5]),

    )
    print(newToner)
    db.session.add(newToner)
    db.session.commit()
    if  newToner is None :
        # acount not found
        return jsonify(["Wrong id"])
    else:
        # print(f' notifications: {my_dict}]')
        # TODO: get Noti form to DB
        return jsonify({"result":"success"}), HTTPStatus.OK
        # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK


@notification_form_blueprint.route('/getAll', methods=['GET'])
def getAll_notification_form():
    user = request.args.get('userId')
    print(user)
    notiList = db.session.query(notifications).filter(notifications.userid == user).order_by(notifications.date.desc()).all()
    my_dict = []
    for noti in notiList:
        daysFromNow = str((date.today() - noti.date).days) if noti.date is not None else "None"
        print(daysFromNow)
        my_dict.append(
            {"id": noti.id, "apprenticeId": noti.apprenticeid, "date": noti.date.strftime("%m.%d.%Y"),
             "timeFromNow": daysFromNow, "event": noti.event.strip(), "allreadyread": noti.allreadyread,"numOfLinesDisplay":noti.numoflinesdisplay})

    if not notiList :
        # acount not found
        return jsonify(["Wrong id or emty list"])
    else:
        # print(f' notifications: {my_dict}]')
        # TODO: get Noti form to DB
        return jsonify(my_dict), HTTPStatus.OK
        # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK


@notification_form_blueprint.route('/setWasRead', methods=['post'])
def setWasRead_notification_form():
    notiId = request.form.get('noti_id')
    print(notiId)
    noti = notifications.query.get(notiId)
    noti.allreadyread = True
    db.session.commit()
    if notiId:
        # print(f'setWasRead form: subject: [{subject}, notiId: {notiId}]')
        # TODO: add contact form to DB
        return jsonify({'result': 'success', 'notiId form': request.form}), HTTPStatus.OK

@notification_form_blueprint.route('/setSetting', methods=['post'])
def setSetting_notification_form():
    notifyMorningval = request.form.get('notifyMorning')
    notifyDayBeforeval = request.form.get('notifyDayBefore')
    notifyStartWeekval = request.form.get('notifyStartWeek')
    user = request.form.get('userId')

    print(notifyMorningval)
    user = user1.query.get(user)
    user.notifyStartWeek = notifyMorningval
    user.notifyDayBefore = notifyDayBeforeval
    user.notifyMorning = notifyStartWeekval

    db.session.commit()
    if user:
        # print(f'setWasRead form: subject: [{subject}, notiId: {notiId}]')
        # TODO: add contact form to DB
        return jsonify({'result': 'success', 'notiId form': request.form}), HTTPStatus.OK


@notification_form_blueprint.route('/getAll', methods=['GET'])
def getNotificationSetting_notification_form():
    user = request.args.get('userId')


    print(user)
    notiSettingList = db.session.query(user1.notifyMorning,user1.notifyDayBefore,user1.notifyStartWeek).filter(notifications.userid == user).first()

    if not notiSettingList :
        # acount not found
        return jsonify(["Wrong id or emty list"])
    else:
        # print(f' notifications: {my_dict}]')
        # TODO: get Noti form to DB
        return jsonify(notiSettingList), HTTPStatus.OK
