import json

from datetime import datetime,date

from flask import Blueprint, request, jsonify
from http import HTTPStatus
from os import sys, path

from sqlalchemy import func

from ..models.apprentice_model import Apprentice
from ..models.user_model import user1
from ..models.visit_model import Visit

pth = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(pth)
from app import app, db
import uuid
from ..models.notification_model import notifications

notification_form_blueprint = Blueprint('notification_form', __name__, url_prefix='/notification_form')

@notification_form_blueprint.route('/add1', methods=['POST'])
def add_notification_form():
    data=request.data.decode()
    json_object = json.loads(data)
    print(json_object)
    user = json_object["userId"]
    apprenticeid = json_object["apprenticeid"]
    event = json_object["event"]
    date = json_object["date"]

    print(user)

    notification1 = notifications(
                    userid=user[4:],
                    apprenticeid = apprenticeid[4:],
                    event=event,
                    date=date,
                    allreadyread=False,
                    id=int(str(uuid.uuid4().int)[:5]),

    )
    print(notification1.date)
    db.session.add(notification1)
    db.session.commit()
    if  notification1 is None :
        # acount not found
        return jsonify(["Wrong id"])
    else:
        # print(f' notifications: {my_dict}]')
        # TODO: get Noti form to DB
        return jsonify({"result":"success"}), HTTPStatus.OK
        # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK


@notification_form_blueprint.route('/getAll', methods=['GET'])
def getAll_notification_form():
    user = request.args.get('userId')[4:]
    print(user)
    #get notification created by user.
    notiList = db.session.query(notifications).filter(notifications.userid == user).order_by(notifications.date.desc()).all()
    my_dict = []
    for noti in notiList:
        daysFromNow = str((date.today() - noti.date).days) if noti.date is not None else "None"
        my_dict.append(
            {"id": noti.id, "apprenticeId": noti.apprenticeid, "date": noti.date.strftime("%m.%d.%Y"),
             "timeFromNow": daysFromNow, "event": noti.event.strip(), "allreadyread": noti.allreadyread,"numOfLinesDisplay":noti.numoflinesdisplay})
    #get notification created by system=apprentices birthday
    ApprenticeList = db.session.query(Apprentice).filter(Apprentice.accompany_id == user).order_by(Apprentice.birthday.desc()).all()
    for noti in ApprenticeList:
        BD=noti.birthday.strip().split("-")
        gap = (date.today() - date(date.today().year, int(BD[1]), int(BD[2]))).days
        print("birthday gap:",gap)
        if gap<=0 and gap>=-3:
            my_dict.append(
                {"id": noti.id, "apprenticeId": "ל"+noti.last_name.strip()+" "+noti.name.strip(), "date": BD[2]+"."+BD[1]+"."+str(date.today().year),
                 "timeFromNow": gap, "event": "יומהולדת", "allreadyread": False,
                 "numOfLinesDisplay": "3"})
        # get notification created by system=apprentices visit
        visitEvent = db.session.query(Visit).filter(Visit.user_id == user,Visit.apprentice_id == noti.id).first()
        gap = (date.today() - visitEvent.visit_date).days
        print("visit gap:",gap)
        if  gap>30:
            my_dict.append(
                {"id": noti.id, "apprenticeId": noti.last_name.strip()+" "+noti.name.strip(), "date": str(date.today().day)+"."+str(date.today().month)+"."+str(date.today().year),
                 "timeFromNow": gap, "event": visitEvent.title.strip(), "allreadyread": False,
                 "numOfLinesDisplay": "2"})
    if not user  :
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
    print(request.form.to_dict())
    data = request.form.to_dict()
    notifyMorningval = data['notifyMorning']
    notifyDayBeforeval = data['notifyDayBefore']
    notifyStartWeekval = data['notifyStartWeek']
    user = data['userId'][4:]
    print("user:",user)
    print("notifyMorningval:",bool(notifyMorningval))
    print("notifyMorningval:",notifyMorningval)

    user = user1.query.get(user)
    user.notifyStartWeek = notifyMorningval== 'true'
    user.notifyDayBefore = notifyDayBeforeval== 'true'
    user.notifyMorning = notifyStartWeekval== 'true'

    db.session.commit()
    if user:
        # print(f'setWasRead form: subject: [{subject}, notiId: {notiId}]')
        # TODO: add contact form to DB
        return jsonify({'result': 'success', 'notiId form': request.form}), HTTPStatus.OK


@notification_form_blueprint.route('/getAllSetting', methods=['GET'])
def getNotificationSetting_form():
    user = request.args.get('userId')[4:]
    notiSettingList = db.session.query(user1.notifyMorning,user1.notifyDayBefore,user1.notifyStartWeek).filter(user1.id == user).first()
    if not notiSettingList :
        # acount not found
        return jsonify(["Wrong id or emty list"])
    else:
        # print(f' notifications: {my_dict}]')
        # TODO: get Noti form to DB
        return jsonify({"notifyMorning":notiSettingList.notifyMorning,
                        "notifyDayBefore":notiSettingList.notifyDayBefore
                        ,"notifyStartWeek":notiSettingList.notifyStartWeek}), HTTPStatus.OK
import datetime
import sqlalchemy as sa

def age_years_at(sa_col, next_days: int = 0):
    """
    Generates a postgresql specific statement to return 'age' (in years)'
    from an provided field either today (next_days == 0) or with the `next_days` offset.
    """
    stmt = func.age(
        (sa_col - sa.func.cast(datetime.timedelta(next_days), sa.Interval))
        if next_days != 0
        else sa_col
    )
    stmt = func.date_part("year", stmt)
    return stmt

def has_birthday_next_days(sa_col, next_days: int = 0):
    """
    sqlalchemy expression to indicate that an sa_col (such as`User.birthday`)
    has anniversary within next `next_days` days.

    It is implemented by simply checking if the 'age' of the person (in years)
    has changed between today and the `next_days` date.
    """
    return age_years_at(sa_col, next_days) > age_years_at(sa_col)