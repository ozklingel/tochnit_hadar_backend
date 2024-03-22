import json
from datetime import datetime,date

from flask import Blueprint, request, jsonify, Response
from http import HTTPStatus

from sqlalchemy import func, or_

import config
from .user_Profile import toISO
from ..models.apprentice_model import Apprentice
from ..models.user_model import user1
from ..models.visit_model import Visit
from app import  db
import uuid
from ..models.notification_model import notifications

notification_form_blueprint = Blueprint('notification_form', __name__, url_prefix='/notification_form')

@notification_form_blueprint.route('/get_outbound', methods=['GET'])
def get_outbound():
    # get tasksAndEvents
    userId = request.args.get("userId")
    res = getAll_notification_form()
    todo_dict = []
    todo_ids = []
    try:
        for i in range(0, len(res[0].json)):
            ent = res[0].json[i]
            todo_ids.append(ent["id"])
            if ent["numOfLinesDisplay"] == 2:  # noti not created by user
                del ent["numOfLinesDisplay"]
                ent["status"] = "todo"
                ent["id"] = str(ent["id"])
                ent["apprenticeId"] = [ent["apprenticeId"]]
                if ent["event"] == config.groupMeet_report:
                    ent["apprenticeId"] = []
                if ent["daysfromnow"]==2 or ent["daysfromnow"]==5 or ent["daysfromnow"]==-2:
                    todo_dict.append(ent)

        too_old = datetime.date.today() - datetime.timedelta(20)
        print(too_old)
        ApprenticeList = db.session.query(Apprentice.id).filter(
            Apprentice.accompany_id == userId,Apprentice.association_date==too_old).all()
        print(ApprenticeList)
        all_ApprenticeList_Horim = [r[0] for r in ApprenticeList]
        visitHorim = db.session.query(Visit.ent_reported).filter(Visit.user_id == userId,
                                                                 Visit.title == config.HorimCall_report).all()
        for i in visitHorim:
            if i[0] in all_ApprenticeList_Horim:
                all_ApprenticeList_Horim.remove(i[0])
        for ent in all_ApprenticeList_Horim:
            # Apprentice1 = db.session.query(Apprentice.name,Apprentice.last_name).filter(Apprentice.id == ent).first()
            todo_dict.append({"frequency": "never", "description": "", 'status': 'todo', "allreadyread": False,
                              'apprenticeId': [str(ent)], 'date': '2023-01-01T00:00:00', 'daysfromnow': 373,
                              'event': 'מפגש_הורים', 'id': str(uuid.uuid4().int)[:5], 'title': 'מפגש הורים'})

        return Response(json.dumps(todo_dict), mimetype='application/json'), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': 'error while get' + str(e)}), HTTPStatus.BAD_REQUEST
@notification_form_blueprint.route('/getAll', methods=['GET'])
def getAll_notification_form():
    try:
        user = request.args.get('userId')
        print("user:",user)
        user_Role=db.session.query(user1.role_id).filter(user1.id == user).first()
        print("user role:",user_Role[0])
        if user_Role[0]=="0":#melave
            # update notification created by system=group meetings
            visitEvent = db.session.query(Visit).filter(Visit.user_id == user,
                                                        Visit.title == config.groupMeet_report).order_by(Visit.visit_date.desc()).first()
            # handle no row so insert need a meeting notification
            id1=0
            if visitEvent is None and date.today().weekday()==6:
                id1=add_visit_notification(user, None, config.groupMeet_report, '2023-01-01')
            gap = (date.today() - visitEvent.visit_date).days if visitEvent is not None else 0
            #if gap>60 add else remove if exist such
            print(date.today().weekday())
            if gap > 53 and date.today().weekday()==6:
                add_visit_notification(visitEvent.user_id, visitEvent.ent_reported, visitEvent.title, visitEvent.visit_date)

            #update notification table  birthday and events
            ApprenticeList = db.session.query(Apprentice.birthday,Apprentice.id,Apprentice.accompany_id).filter(Apprentice.accompany_id == user).all()
            for Apprentice1 in ApprenticeList:
                thisYearBirthday=date(date.today().year, Apprentice1.birthday.month, Apprentice1.birthday.day)
                gap = (date.today() - thisYearBirthday).days
                if gap <= 7 and date.today().weekday()==6:
                    update_event_notification(Apprentice1.accompany_id, Apprentice1.id, "יומהולדת", thisYearBirthday,None)
                # update notification created by system=apprentices call
                visitEvent = db.session.query(Visit).filter(Visit.user_id == user, Visit.ent_reported == Apprentice1.id,Visit.title==config.call_report).order_by(Visit.visit_date.desc()).first()
                #handle no row so insert need a call notification
                if visitEvent is None and date.today().weekday()==6:
                    id1=add_visit_notification(user, Apprentice1.id,config.call_report, '2023-01-01')

                gap = (date.today() - visitEvent.visit_date).days if visitEvent is not None else 0
                if gap > 14 and date.today().weekday()==6:
                    add_visit_notification(visitEvent.user_id, visitEvent.ent_reported,visitEvent.title, visitEvent.visit_date)

                # update notification created by system=apprentices meetings
                visitEvent = db.session.query(Visit).filter(Visit.user_id == user, Visit.ent_reported == Apprentice1.id,or_(Visit.title==config.groupMeet_report,Visit.title==config.personalMeet_report)).order_by(Visit.visit_date.desc()).first()
                #handle no row so insert need a meeting notification
                if visitEvent is None and date.today().weekday()==6:
                    id1=add_visit_notification(user, Apprentice1.id,config.personalMeet_report, '2023-01-01')
                gap = (date.today() - visitEvent.visit_date).days if visitEvent is not None else 0
                if gap > 83 and date.today().weekday()==6:
                    add_visit_notification(visitEvent.user_id, visitEvent.ent_reported,visitEvent.title, visitEvent.visit_date)

            #send  notifications.
            userEnt = db.session.query(user1.notifyStartWeek,user1.notifyDayBefore,user1.notifyMorning).filter_by(id=user).first()
            notiList = db.session.query(notifications).filter(notifications.userid == user).order_by(notifications.date.desc()).all()
            my_dict = []
            for noti in notiList:
                daysFromNow = (date.today() - noti.date).days if noti.date is not None else "None"
                if noti.event==config.groupMeet_report:
                    apprenticeids=""
                else:
                    apprenticeids=str(noti.apprenticeid)
                if noti.numoflinesdisplay==2:

                    noti.details = noti.event if noti.details is None else noti.details
                    my_dict.append(
                        {"id": str(noti.id),"apprenticeId":apprenticeids,
                         "date": toISO(noti.date),
                         "daysfromnow": daysFromNow, "event": noti.event.strip(), "allreadyread": noti.allreadyread,"description": noti.details,"frequency": noti.frequency if  noti.frequency is not None else "never",
                         "numOfLinesDisplay": noti.numoflinesdisplay})
                    continue

                if userEnt.notifyStartWeek==True and date(date.today().year, noti.date.month, noti.date.day).weekday()==6:
                    gap = (date.today() - date(date.today().year, noti.date.month, noti.date.day)).days
                    if gap<=7:
                        noti.details = noti.event.strip() if noti.details is None else noti.details.strip()
                        my_dict.append(
                            {"id": str(noti.id), "apprenticeId":str(noti.apprenticeid),
                             "date": toISO(noti.date),
                             "daysfromnow": daysFromNow, "event": noti.event.strip(),"description": noti.details, "allreadyread": noti.allreadyread,"frequency": noti.frequency if  noti.frequency is not None else "never",
                             "numOfLinesDisplay": noti.numoflinesdisplay, })
                        continue
                if userEnt.notifyDayBefore ==True :
                    is_shabat=date(date.today().year, noti.date.month, noti.date.day).weekday()==5
                    if (is_shabat  and daysFromNow==-2) or  daysFromNow==-1 :
                        noti.details = noti.event.strip() if noti.details is None else noti.details.strip()
                        my_dict.append(
                            {"id": str(noti.id),"apprenticeId":str(noti.apprenticeid),
                             "date": toISO(noti.date),
                             "daysfromnow": daysFromNow, "event": noti.event.strip(),"description": noti.details, "allreadyread": noti.allreadyread,"frequency": noti.frequency,
                             "numOfLinesDisplay": noti.numoflinesdisplay,})
                        continue
                if userEnt.notifyMorning ==True :
                    is_shabat=date(date.today().year, noti.date.month, noti.date.day).weekday()==5
                    if (is_shabat  and daysFromNow==-1) or  daysFromNow==0 :
                        noti.details = noti.event.strip() if noti.details is None else noti.details.strip()
                        my_dict.append(
                            {"id": str(noti.id),"apprenticeId":str(noti.apprenticeid),
                             "date": toISO(noti.date),
                             "daysfromnow": daysFromNow, "event": noti.event.strip(),"description": noti.details, "allreadyread": noti.allreadyread,"frequency": noti.frequency if  noti.frequency is not None else "never",
                             "numOfLinesDisplay": noti.numoflinesdisplay, })
                        continue
            if  my_dict is None or my_dict==[]  :
                # acount not found
                return jsonify([])
            else:
                # print(f' notifications: {my_dict}]')
                # TODO: get Noti form to DB
                return jsonify(my_dict), HTTPStatus.OK

        if user_Role[0]=="3":#ahrai tohhnit
            userEnt = db.session.query(user1.id,user1.notifyStartWeek,user1.notifyMorning,user1.notifyDayBefore,user1.notifyMorning_sevev,user1.notifyDayBefore_sevev,user1.notifyStartWeek_sevev,user1.notifyMorning_weekly_report).filter(user1.id == user).first()
            # too_old = datetime.datetime.today() - datetime.timedelta(days=60)
            # institotionList= db.session.query(Institution.id).all()
            # for ins in institotionList:
            #     visitEvent_sevev = db.session.query(Visit).filter(Visit.user_id == user,Visit.ent_reported==ins[0],
            #                                                 too_old<Visit.visit_date,Visit.title =="סבב_מוסד").first()
            #     if visitEvent_sevev==None:
            #         add_visit_notification(userEnt.id, ins[0],"סבב_מוסד", None)
            notiList = db.session.query(notifications).filter(notifications.userid == user).order_by(notifications.date.desc()).all()
            my_dict = []
            for noti in notiList:
                daysFromNow = (date.today() - noti.date).days if noti.date is not None else "None"
                if userEnt.notifyStartWeek == True and date(date.today().year, noti.date.month,
                                                            noti.date.day).weekday() == 6:
                    gap = (date.today() - date(date.today().year, noti.date.month, noti.date.day)).days
                    if gap <= 7:

                        noti.details = noti.event.strip() if noti.details is None else noti.details.strip()
                        my_dict.append(
                            {"id": noti.id, "apprenticeId": [str(noti.apprenticeid)],

                             "date": noti.date.strftime("%m.%d.%Y"),
                             "daysfromnow": daysFromNow, "event": noti.event.strip(), "description": noti.details,
                             "allreadyread": noti.allreadyread,
                             "frequency": noti.frequency if noti.frequency is not None else "never",
                             "numOfLinesDisplay": noti.numoflinesdisplay, })
                        continue
                if userEnt.notifyDayBefore == True :
                    is_shabat = date(date.today().year, noti.date.month, noti.date.day).weekday() == 5
                    if (is_shabat and daysFromNow == -2) or daysFromNow == -1:
                        noti.details = noti.event.strip() if noti.details is None else noti.details.strip()
                        my_dict.append(
                            {"id": noti.id, "apprenticeId": [str(noti.apprenticeid)],

                             "date": noti.date.strftime("%m.%d.%Y"),
                             "daysfromnow": daysFromNow, "event": noti.event.strip(), "description": noti.details,
                             "allreadyread": noti.allreadyread, "frequency": noti.frequency,
                             "numOfLinesDisplay": noti.numoflinesdisplay, })
                    continue
                if userEnt.notifyMorning == True :
                    is_shabat = date(date.today().year, noti.date.month, noti.date.day).weekday() == 5
                    if (is_shabat and daysFromNow == -1) or daysFromNow == 0:
                        noti.details = noti.event.strip() if noti.details is None else noti.details.strip()
                        my_dict.append(
                            {"id": noti.id, "apprenticeId": [str(noti.apprenticeid)],
                             "date": noti.date.strftime("%m.%d.%Y"),
                             "daysfromnow": daysFromNow, "event": noti.event.strip(), "description": noti.details,
                             "allreadyread": noti.allreadyread,
                             "frequency": noti.frequency if noti.frequency is not None else "never",
                             "numOfLinesDisplay": noti.numoflinesdisplay, })
                if userEnt.notifyMorning_weekly_report == True and daysFromNow==0 and noti.event=="דוח שבועי":
                    noti.details = noti.event.strip() if noti.details is None else noti.details.strip()
                    my_dict.append(
                        {"id": noti.id, "apprenticeId": [str(noti.apprenticeid)],
                         "date": noti.date.strftime("%m.%d.%Y"),
                         "daysfromnow": daysFromNow, "event": noti.event.strip(), "description": noti.details,
                         "allreadyread": noti.allreadyread,
                         "frequency": noti.frequency if noti.frequency is not None else "never",
                         "numOfLinesDisplay": noti.numoflinesdisplay, })

            if  my_dict is None or my_dict==[]  :
                # acount not found
                return jsonify([])
            else:
                # print(f' notifications: {my_dict}]')
                # TODO: get Noti form to DB
                return jsonify(my_dict), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST

@notification_form_blueprint.route('/add1', methods=['POST'])
def add_notification_form():
    try:
        json_object = request.json
        user = json_object["userId"]
        apprenticeid = json_object["apprenticeid"] if json_object["apprenticeid"] else ""
        event = json_object["event"]
        date = json_object["date"]
        details = json_object["details"]
        frequency = json_object["frequency"] if  json_object["frequency"] is not None else "never"
        notification1 = notifications(
                        userid=user,
                        apprenticeid = apprenticeid,
                        event=event,
                        date=date,
                        allreadyread=False,
                        numoflinesdisplay=3,
                        details=details,
                        frequency=frequency,

            id=int(str(uuid.uuid4().int)[:5]),

        )

        db.session.add(notification1)
        db.session.commit()
    except Exception as e:
        return jsonify({"result": str(e)}),HTTPStatus.BAD_REQUEST
    return jsonify({"result":"success"}), HTTPStatus.OK
        # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK

def update_event_notification(user,apprenticeid,event,date,details):
    allreadyread=db.session.query(notifications.allreadyread,notifications.id).filter(notifications.userid == user, notifications.apprenticeid == apprenticeid,notifications.event==event,notifications.details==details).first()
    res=db.session.query(notifications).filter(notifications.userid == user, notifications.apprenticeid == apprenticeid,notifications.event==event,notifications.details==details).delete()
    notification1=None
    if res==0:
        #total new row
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
        #existing row.save allready was read ststus
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
    res=db.session.query(notifications).filter(notifications.userid == user, notifications.apprenticeid == apprenticeid,notifications.event==event).first()
    notification1=None
    id1=int(str(uuid.uuid4().int)[:5]),
    if res is None:
        notification1 = notifications(
                    userid=user,
                    apprenticeid = apprenticeid,
                    event=event,
                    date=date,
                    allreadyread=False,
                    numoflinesdisplay=2,
                    id=id1

        )

        db.session.add(notification1)
        db.session.commit()
    return  id1

@notification_form_blueprint.route('/setWasRead', methods=['post'])
def setWasRead_notification_form():
    data = request.json
    notiId = data['noti_id']
    try:
        noti = notifications.query.get(notiId)
        noti.allreadyread = True
        db.session.commit()
        if notiId:
            # print(f'setWasRead form: subject: [{subject}, notiId: {notiId}]')
            # TODO: add contact form to DB
            return jsonify({'result': 'success'}), HTTPStatus.OK
    except:
        return jsonify({'result': 'wrong id'}), HTTPStatus.OK


@notification_form_blueprint.route('/setSetting', methods=['post'])
def setSetting_notification_form():
    data = request.json

    notifyMorningval = data['notifyMorning']
    notifyDayBeforeval = data['notifyDayBefore']
    notifyStartWeekval = data['notifyStartWeek']
    user = data['userId']
    print("user:",user)
    print("notifyMorningval:",notifyMorningval)
    print("notifyDayBeforeval:",notifyDayBeforeval)
    print("notifyStartWeekval:",notifyStartWeekval)
    user = user1.query.get(user)
    user.notifyStartWeek = notifyStartWeekval== 'true' or notifyStartWeekval== 'True'
    user.notifyDayBefore = notifyDayBeforeval== 'true' or notifyDayBeforeval== 'True'
    user.notifyMorning = notifyMorningval== 'true' or notifyMorningval== 'True'
    try:
        db.session.commit()
    except:
        return jsonify({'result': 'wrong id '}), HTTPStatus.OK

    if user:
        # print(f'setWasRead form: subject: [{subject}, notiId: {notiId}]')
        # TODO: add contact form to DB
        return jsonify({'result': 'success'}), HTTPStatus.OK


@notification_form_blueprint.route('/getAllSetting', methods=['GET'])
def getNotificationSetting_form():
    try:
        user = request.args.get('userId')
        notiSettingList = db.session.query(user1.notifyMorning,user1.notifyDayBefore,user1.notifyStartWeek).filter(user1.id == user).first()
        print("notiSettingList",notiSettingList)
        if not notiSettingList :
            # acount not found
            return jsonify(["Wrong id or emty list"])
        else:
            # print(f' notifications: {my_dict}]')
            # TODO: get Noti form to DB
            return jsonify({"notifyMorning":notiSettingList.notifyMorning,
                            "notifyDayBefore":notiSettingList.notifyDayBefore
                            ,"notifyStartWeek":notiSettingList.notifyStartWeek}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST

@notification_form_blueprint.route('/delete', methods=['POST'])
def delete():
    try:
        data = request.json
        NotificationId = data['NotificationId']
        res = db.session.query(notifications).filter(notifications.id == NotificationId).delete()
        db.session.commit()
    except Exception as e:
        return jsonify({"result": str(e)}),HTTPStatus.BAD_REQUEST
    return jsonify({"result":"success"}), HTTPStatus.OK
        # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK
@notification_form_blueprint.route("/update", methods=['put'])
def updateTask():
    try:
        # get tasksAndEvents
        NotificationId = request.args.get("NotificationId")
        data = request.json


        updatedEnt = notifications.query.get(NotificationId)
        for key in data:
            setattr(updatedEnt, key, data[key])
        db.session.commit()
        if updatedEnt:
            # print(f'setWasRead form: subject: [{subject}, notiId: {notiId}]')
            # TODO: add contact form to DB
            return jsonify({'result': 'success'}), HTTPStatus.OK
        return jsonify({'result': 'error'}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST
@notification_form_blueprint.route('/add_frequenced_notification', methods=['POST'])
def add_frequenced_notification():
    notiList = db.session.query(notifications).filter(notifications.frequency!="never").all()
    my_dict = []
    for noti in notiList:
        daysFromNow = (date.today() - noti.date).days if noti.date is not None else "None"
        print(daysFromNow)
        if noti.frequency == "daily" and daysFromNow == 1:
            notification1 = notifications(
                userid=noti.userid,
                apprenticeid=noti.apprenticeid,
                event=noti.event,
                date=toISO(noti.date + datetime.timedelta(days=1)),
                allreadyread=False,
                numoflinesdisplay=2,
                id=int(str(uuid.uuid4().int)[:5])

            )
        if noti.frequency == "weekly" and daysFromNow == 7:
            notification1 = notifications(
                userid=noti.userid,
                apprenticeid=noti.apprenticeid,
                event=noti.event,
                date=toISO(noti.date + datetime.timedelta(days=7)),
                allreadyread=False,
                numoflinesdisplay=2,
                id=int(str(uuid.uuid4().int)[:5])

            )
            if noti.frequency == "monthly" and daysFromNow == 30:
                notification1 = notifications(
                    userid=noti.userid,
                    apprenticeid=noti.apprenticeid,
                    event=noti.event,
                    date=toISO(noti.date + 30),
                    allreadyread=False,
                    numoflinesdisplay=2,
                    id=int(str(uuid.uuid4().int)[:5])

                )
                if noti.frequency == "yearly" and daysFromNow == 365:
                    notification1 = notifications(
                        userid=noti.userid,
                        apprenticeid=noti.apprenticeid,
                        event=noti.event,
                        date=toISO(noti.date + 365),
                        allreadyread=False,
                        numoflinesdisplay=2,
                        id=int(str(uuid.uuid4().int)[:5])

                    )
            db.session.add(notification1)
    try:
        db.session.commit()
        return jsonify({'result': 'success'}), HTTPStatus.OK
    except Exception:
        return jsonify({'result': str(Exception)}), HTTPStatus.BAD_REQUEST


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