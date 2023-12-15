import json

from datetime import datetime,date

from flask import Blueprint, request, jsonify
from http import HTTPStatus
from os import sys, path

from sqlalchemy import func, or_

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
    details = json_object["details"]


    print(user)

    notification1 = notifications(
                    userid=user[4:],
                    apprenticeid = apprenticeid[4:],
                    event=event,
                    date=date,
                    allreadyread=False,
                    numoflinesdisplay=3,
                    details=details,
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

def update_event_notification(user,apprenticeid,event,date,details):
    allreadyread=db.session.query(notifications.allreadyread).filter(notifications.userid == user, notifications.apprenticeid == apprenticeid,notifications.event==event,notifications.details==details).first()
    res=db.session.query(notifications).filter(notifications.userid == user, notifications.apprenticeid == apprenticeid,notifications.event==event,notifications.details==details).delete()
    notification1=None
    print("deleted 1",res)
    if res==0:
        notification1 = notifications(
                        userid=user,
                        apprenticeid = apprenticeid,
                        event=event,
                        date=date,
                        allreadyread=False,
                        numoflinesdisplay=3,
                        id=int(str(uuid.uuid4().int)[:5]),

        )
    else:
        notification1 = notifications(
            userid=user,
            apprenticeid=apprenticeid,
            event=event,
            date=date,
            allreadyread=allreadyread.allreadyread,
            numoflinesdisplay=3,
            id=int(str(uuid.uuid4().int)[:5]),

        )
    db.session.add(notification1)
    db.session.commit()

def add_visit_notification(user,apprenticeid,event,date):
    allreadyread=db.session.query(notifications.allreadyread).filter(notifications.userid == user, notifications.apprenticeid == apprenticeid,notifications.event==event).first()
    res=db.session.query(notifications).filter(notifications.userid == user, notifications.apprenticeid == apprenticeid,notifications.event==event).delete()
    notification1=None
    print("deleted 2",res)

    if res==0:
        notification1 = notifications(
                    userid=user,
                    apprenticeid = apprenticeid,
                    event=event,
                    date=date,
                    allreadyread=False,
                    numoflinesdisplay=2,
                    id=int(str(uuid.uuid4().int)[:5]),

        )
    else:
        notification1 = notifications(
                    userid=user,
                    apprenticeid = apprenticeid,
                    event=event,
                    date=date,
                    allreadyread=allreadyread.allreadyread,
                    numoflinesdisplay=2,
                    id=int(str(uuid.uuid4().int)[:5]),

        )
    db.session.add(notification1)
    db.session.commit()
@notification_form_blueprint.route('/getAll', methods=['GET'])
def getAll_notification_form():
    user = request.args.get('userId')[4:]
    print("user:",user)
    #update notification table  birthday and events
    ApprenticeList = db.session.query(Apprentice).filter(Apprentice.accompany_id == user).order_by(
        Apprentice.birthday.desc()).all()
    for Apprentice1 in ApprenticeList:
        BD = Apprentice1.birthday.strip().split("-")
        gap = (date.today() - date(date.today().year, int(BD[1]), int(BD[2]))).days
        print("birthday gap:", gap)
        if gap >= -7 and gap <= 7:
            update_event_notification(Apprentice1.accompany_id, Apprentice1.id, "יומהולדת", date(date.today().year, int(BD[1]), int(BD[2])),None)
        else:
            db.session.query(notifications).filter(notifications.userid == user,
                                                     notifications.apprenticeid == Apprentice1.id,
                                                     notifications.event == "יומהולדת",
                                                    ).delete()

        # update notification created by system=apprentices call
        visitEvent = db.session.query(Visit).filter(Visit.user_id == user, Visit.apprentice_id == Apprentice1.id,Visit.title=="שיחה").first()
        gap = (date.today() - visitEvent.visit_date).days if visitEvent is not None else 0
        print("call gap:", gap)
        if gap > 30:
            add_visit_notification(visitEvent.user_id, visitEvent.apprentice_id,visitEvent.title, visitEvent.visit_date)
        # update notification created by system=apprentices meetings
        visitEvent = db.session.query(Visit).filter(Visit.user_id == user, Visit.apprentice_id == Apprentice1.id,Visit.title=="מפגש").first()
        gap = (date.today() - visitEvent.visit_date).days if visitEvent is not None else 0
        print("meeting gap:", gap)
        if gap > 30:
            add_visit_notification(visitEvent.user_id, visitEvent.apprentice_id,visitEvent.title, visitEvent.visit_date)
    #send  notifications.
    userEnt = db.session.query(user1.notifyStartWeek,user1.notifyDayBefore,user1.notifyMorning).filter_by(id=user).first()
    notiList = db.session.query(notifications).filter(notifications.userid == user).order_by(notifications.date.desc()).all()
    my_dict = []
    for noti in notiList:
        if noti.numoflinesdisplay==2:
            ApprenticeNames = db.session.query(Apprentice.name, Apprentice.last_name).filter(
                Apprentice.id == noti.apprenticeid).first()
            noti.details = noti.event.strip() if noti.details is None else noti.details.strip()
            my_dict.append(
                {"id": noti.id, "apprenticeId": ApprenticeNames.last_name.strip() + " " + ApprenticeNames.name.strip(),
                 "date": noti.date.strftime("%m.%d.%Y"),
                 "daysfromnow": daysFromNow, "event": noti.event.strip(), "allreadyread": noti.allreadyread,
                 "numOfLinesDisplay": noti.numoflinesdisplay, "title": noti.details})
            continue
        #print("date:",date(date.today().year, noti.date.month, noti.date.day))
        #print("day of week:",date(date.today().year, noti.date.month, noti.date.day).weekday())
        #print(userEnt.notifyStartWeek)
        if userEnt.notifyStartWeek==True and date(date.today().year, noti.date.month, noti.date.day).weekday()==6:
            ApprenticeNames = db.session.query(Apprentice.name, Apprentice.last_name).filter(
                Apprentice.id == noti.apprenticeid).first()
            noti.details = noti.event.strip() if noti.details is None else noti.details.strip()
            daysFromNow = str((date.today() - noti.date).days) if noti.date is not None else "None"
            my_dict.append(
                {"id": noti.id, "apprenticeId": ApprenticeNames.last_name.strip() + " " + ApprenticeNames.name.strip(),
                 "date": noti.date.strftime("%m.%d.%Y"),
                 "daysfromnow": daysFromNow, "event": noti.event.strip(), "allreadyread": noti.allreadyread,
                 "numOfLinesDisplay": noti.numoflinesdisplay, "title": noti.details})
            continue
        daysFromNow = str((date.today() - noti.date).days) if noti.date is not None else "None"
        print(noti.event.strip())
        print(userEnt.notifyMorning)
        if userEnt.notifyDayBefore ==True and daysFromNow==-1:
            ApprenticeNames = db.session.query(Apprentice.name, Apprentice.last_name).filter(
                Apprentice.id == noti.apprenticeid).first()
            noti.details = noti.event.strip() if noti.details is None else noti.details.strip()
            my_dict.append(
                {"id": noti.id, "apprenticeId": ApprenticeNames.last_name.strip() + " " + ApprenticeNames.name.strip(),
                 "date": noti.date.strftime("%m.%d.%Y"),
                 "daysfromnow": daysFromNow, "event": noti.event.strip(), "allreadyread": noti.allreadyread,
                 "numOfLinesDisplay": noti.numoflinesdisplay, "title": noti.details})
            continue
        if userEnt.notifyMorning ==True and daysFromNow==0:
            ApprenticeNames = db.session.query(Apprentice.name, Apprentice.last_name).filter(
                Apprentice.id == noti.apprenticeid).first()
            noti.details = noti.event.strip() if noti.details is None else noti.details.strip()
            my_dict.append(
                {"id": noti.id, "apprenticeId": ApprenticeNames.last_name.strip() + " " + ApprenticeNames.name.strip(),
                 "date": noti.date.strftime("%m.%d.%Y"),
                 "daysfromnow": daysFromNow, "event": noti.event.strip(), "allreadyread": noti.allreadyread,
                 "numOfLinesDisplay": noti.numoflinesdisplay, "title": noti.details})
            continue
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