import json
from datetime import datetime as dt,date,timedelta

from flask import Blueprint, request, jsonify, Response
from http import HTTPStatus

from sqlalchemy import func, or_

import config
from .madadim import mosad__score, mosad_Coordinators_score, melave_score
from .user_Profile import toISO
from ..models.apprentice_model import Apprentice
from ..models.institution_model import Institution
from ..models.user_model import user1
from ..models.visit_model import Visit
from app import  db
import uuid
from ..models.notification_model import notifications

notification_form_blueprint = Blueprint('notification_form', __name__, url_prefix='/notification_form')


def add_notificaion_to_melave(user):
    # update notification created by system=group meetings
    visitEvent = db.session.query(Visit).filter(Visit.user_id == user.id,
                                                Visit.title == config.groupMeet_report).order_by(
                                                Visit.visit_date.desc()).first()

    if visitEvent is None or (date.today() - visitEvent.visit_date).days>53 :
        res = db.session.query(notifications).filter(notifications.userid == user.id,
                                                     notifications.event == config.groupMeet_report).first()
        if res is None and date.today().weekday() == 2:
            date1='2023-01-01' if visitEvent is None else visitEvent.visit_date
            notification1 = notifications(userid=user.id,subject = None,event=config.groupMeet_report,date=date1,
                                          allreadyread=False,numoflinesdisplay=2,id=int(str(uuid.uuid4().int)[:5]))
            db.session.add(notification1)
    # update notification table  birthday and events
    ApprenticeList = db.session.query(Apprentice.birthday, Apprentice.id, Apprentice.accompany_id).filter(
        Apprentice.accompany_id == user.id).all()
    for Apprentice1 in ApprenticeList:
        #call
        visitEvent = db.session.query(Visit).filter(Visit.user_id == user.id,
                                                    Visit.title == config.call_report).order_by(
                                                    Visit.visit_date.desc()).first()
        if visitEvent is None or (date.today() - visitEvent.visit_date).days > 14:
            res = db.session.query(notifications).filter(notifications.userid == user.id,notifications.subject==str(Apprentice1.id),
                                                         notifications.event == config.call_report).first()
            if res is None and date.today().weekday() == 2:
                date1 = '2023-01-01' if visitEvent is None else visitEvent.visit_date
                notification2 = notifications(userid=user.id, subject=str(Apprentice1.id), event=config.call_report,
                                              date=date1,
                                              allreadyread=False, numoflinesdisplay=2,
                                              id=int(str(uuid.uuid4().int)[:5]))
                db.session.add(notification2)
        # personal meet
        visitEvent = db.session.query(Visit).filter(Visit.user_id == user.id,Visit.ent_reported==str(Apprentice1.id),
                                                    Visit.title == config.personalMeet_report).order_by(Visit.visit_date.desc()).first()
        if visitEvent is None or (date.today() - visitEvent.visit_date).days > 83:
            res = db.session.query(notifications).filter(notifications.userid == user.id,notifications.subject==str(Apprentice1.id),
                                                         notifications.event == config.personalMeet_report).first()
            if res is None and date.today().weekday() == 2:
                date1 = '2023-01-01' if visitEvent is None else visitEvent.visit_date
                notification3 = notifications(userid=user.id, subject=str(Apprentice1.id), event=config.personalMeet_report,
                                              date=date1,
                                              allreadyread=False, numoflinesdisplay=2,
                                              id=int(str(uuid.uuid4().int)[:5]))
                db.session.add(notification3)
        #birthday
        thisYearBirthday = date(date.today().year, Apprentice1.birthday.month, Apprentice1.birthday.day)
        gap = (date.today() - thisYearBirthday).days
        if gap <= 7 and gap >= 7 and date.today().weekday() == 6:
            res = db.session.query(notifications).filter(notifications.userid == user.id,notifications.subject==str(Apprentice1.id) ,
                                                         notifications.event == "יומהולדת").first()
            if res is None and date.today().weekday() == 6:
                notification1 = notifications(userid=user.id, subject=str(Apprentice1.id), event="יומהולדת",
                                              date=thisYearBirthday,
                                              allreadyread=False, numoflinesdisplay=2,
                                              id=int(str(uuid.uuid4().int)[:5]))
                db.session.add(notification1)
    db.session.commit()


def add_notificaion_to_ahraiTohnit(user):
    institotionList = db.session.query(Institution.id, Institution.name, Institution.eshcol_id).all()
    eshcol_dict = dict()
    for institution_ in institotionList:
        mosad__score1, forgotenApprentice_Mosad1 = mosad__score(institution_[0])
        if mosad__score1 < 65:
            res = db.session.query(notifications).filter(notifications.userid == user,
                                                         notifications.event == "ציון מוסדות").first()
            if res is None and date.today().weekday() == 2:
                notification1 = notifications(userid=user.id, subject=str(institution_[0]), event="ציון מוסדות",
                                              date=date.today(),
                                              allreadyread=False, numoflinesdisplay=2,
                                              id=int(str(uuid.uuid4().int)[:5]))
                db.session.add(notification1)
        mosadCoord_ = db.session.query(user1.id, user1.name, user1.last_name).filter(user1.role_id == "1",
                                                                                     user1.institution_id == institution_.id).first()
        if mosadCoord_ is not None:
            mosad_Coordinators_score1 = mosad_Coordinators_score(mosadCoord_[0])
            if mosad_Coordinators_score1 < 65:
                res = db.session.query(notifications).filter(notifications.userid == user.id,
                                                             notifications.event == "ציון רכזים").first()
                if res is None and date.today().weekday() == 2:
                    notification1 = notifications(userid=user.id, subject=str(institution_[0]), event="ציון רכזים",
                                                  date=date.today(),
                                                  allreadyread=False, numoflinesdisplay=2,
                                                  id=int(str(uuid.uuid4().int)[:5]))
                    db.session.add(notification1)
        eshcol_dict[institution_[2]] = eshcol_dict.get(institution_[2], 0) + forgotenApprentice_Mosad1
    for k, v in eshcol_dict.items():
        res = db.session.query(notifications).filter(notifications.userid == user.id,
                                                     notifications.event == "חניכים נשכחים").first()
        if res is None and date.today().weekday() == 2:
            notification1 = notifications(userid=user.id, subject=str(k), event="חניכים נשכחים",details=v,
                                          date=date.today(),
                                          allreadyread=False, numoflinesdisplay=2,
                                          id=int(str(uuid.uuid4().int)[:5]))
            db.session.add(notification1)

    db.session.commit()


def add_notificaion_to_mosad(user):
    # doForBogrim
    visitEvent = db.session.query(Visit).filter(Visit.user_id == user.id,
                                                Visit.title == config.doForBogrim_report).order_by(
        Visit.visit_date.desc()).first()
    if visitEvent is None or (date.today() - visitEvent.visit_date).days > 83:
        res = db.session.query(notifications).filter(notifications.userid == user.id,
                                                     notifications.event == config.doForBogrim_report).first()
        if res is None and date.today().weekday() == 2:
            date1 = '2023-01-01' if visitEvent is None else visitEvent.visit_date
            notification1 = notifications(userid=user.id, subject="", event=config.doForBogrim_report,
                                          date=date1,
                                          allreadyread=False, numoflinesdisplay=2,
                                          id=int(str(uuid.uuid4().int)[:5]))
            db.session.add(notification1)
    # yeshiva
    visitEvent = db.session.query(Visit).filter(Visit.user_id == user.id,
                                                Visit.title == config.MelavimMeeting_report).order_by(
        Visit.visit_date.desc()).first()
    if visitEvent is None or (date.today() - visitEvent.visit_date).days > 23:
        res = db.session.query(notifications).filter(notifications.userid == user.id,
                                                     notifications.event == config.MelavimMeeting_report).first()
        if res is None and date.today().weekday() == 2:
            date1 = '2023-01-01' if visitEvent is None else visitEvent.visit_date
            notification1 = notifications(userid=user.id, subject="", event=config.MelavimMeeting_report,
                                          date=date1,
                                          allreadyread=False, numoflinesdisplay=2,
                                          id=int(str(uuid.uuid4().int)[:5]))
            db.session.add(notification1)

    melave_list = db.session.query(user1.id,user1.name,user1.last_name).filter(user1.institution_id==user.institution_id,user1.role_id=="0").all()
    under65_dict = dict()
    for melave_ in melave_list:
        # mathzbar
        visitEvent = db.session.query(Visit).filter(Visit.user_id == user.id,Visit.ent_reported==melave_.id,
                                                    Visit.title == config.matzbar_report).order_by(
            Visit.visit_date.desc()).first()
        if visitEvent is None or (date.today() - visitEvent.visit_date).days > 113:
            res = db.session.query(notifications).filter(notifications.userid == user.id,notifications.subject==str(melave_.id),
                                                         notifications.event == config.matzbar_report).first()
            if res is None and date.today().weekday() == 2:
                date1 = '2023-01-01' if visitEvent is None else visitEvent.visit_date
                notification1 = notifications(userid=user.id, subject=str(melave_.id), event=config.matzbar_report,
                                              date=date1,
                                              allreadyread=False, numoflinesdisplay=2,
                                              id=int(str(uuid.uuid4().int)[:5]))
                db.session.add(notification1)
        melave_score1,call_gap_avg,personal_meet_gap_avg=melave_score(melave_.id)
        if melave_score1<65:
            under65_dict[melave_.id]=melave_.name+" "+melave_.last_name
    res = db.session.query(notifications).filter(notifications.userid == user.id,
                                                 notifications.event == "ציון מלוים").first()

    if res is None and date.today().weekday() == 2:
        date1 = '2023-01-01' if visitEvent is None else visitEvent.visit_date
        notification1 = notifications(userid=user.id, subject="", event="ציון מלוים",
                                      date=date1,
                                      details=str(under65_dict),
                                      allreadyread=False, numoflinesdisplay=2,
                                      id=int(str(uuid.uuid4().int)[:5]))
        db.session.add(notification1)
    mosad__score1, forgotenApprentice_Mosad1 = mosad__score(user.institution_id)
    res = db.session.query(notifications).filter(notifications.userid == user.id,
                                                 notifications.event == "חניכים נשכחים").first()
    if res is None and date.today().weekday() == 2:
        date1 = '2023-01-01' if visitEvent is None else visitEvent.visit_date
        notification1 = notifications(userid=user.id, subject="", event="חניכים נשכחים",
                                      date=date1,
                                      details=forgotenApprentice_Mosad1,
                                      allreadyread=False, numoflinesdisplay=2,
                                      id=int(str(uuid.uuid4().int)[:5]))
        db.session.add(notification1)

def add_notificaion_to_eshcol(user):
    institotionList = db.session.query(Institution.id, Institution.name, Institution.eshcol_id).filter(Institution.eshcol_id==user.eshcol).all()
    eshcol_dict = dict()
    for institution_ in institotionList:
        mosad__score1, forgotenApprentice_Mosad1 = mosad__score(institution_[0])
        if mosad__score1 < 65:
            res = db.session.query(notifications).filter(notifications.userid == user.id,
                                                         notifications.event == "ציון מוסדות").first()
            if res is None and date.today().weekday() == 2:
                notification1 = notifications(userid=user.id, subject=str(institution_[0]), event="ציון מוסדות",
                                              date=date.today(),
                                              allreadyread=False, numoflinesdisplay=2,
                                              id=int(str(uuid.uuid4().int)[:5]))
                db.session.add(notification1)
        mosadCoord_ = db.session.query(user1.id, user1.name, user1.last_name).filter(user1.role_id == "1",
                                                                                     user1.institution_id == institution_.id).first()
        if mosadCoord_ is not None:
            # MOsadEshcolMeeting_report
            visitEvent = db.session.query(Visit).filter(Visit.user_id == user.id,Visit.ent_reported==mosadCoord_,
                                                        Visit.title == config.MOsadEshcolMeeting_report).order_by(
                Visit.visit_date.desc()).first()
            if visitEvent is None or (date.today() - visitEvent.visit_date).days > 23:
                res = db.session.query(notifications).filter(notifications.userid == user.id,
                                                             notifications.subject == str(mosadCoord_),
                                                             notifications.event == config.MOsadEshcolMeeting_report).first()
                if res is None and date.today().weekday() == 2:
                    date1 = '2023-01-01' if visitEvent is None else visitEvent.visit_date
                    notification1 = notifications(userid=user.id, subject=str(mosadCoord_), event=config.MOsadEshcolMeeting_report,
                                                  date=date1,
                                                  allreadyread=False, numoflinesdisplay=2,
                                                  id=int(str(uuid.uuid4().int)[:5]))
                    db.session.add(notification1)
            mosad_Coordinators_score1 = mosad_Coordinators_score(mosadCoord_[0])
            if mosad_Coordinators_score1 < 65:
                res = db.session.query(notifications).filter(notifications.userid == user.id,
                                                             notifications.event == "ציון רכזים").first()
                if res is None and date.today().weekday() == 2:
                    notification1 = notifications(userid=user.id, subject=str(institution_[0]), event="ציון רכזים",
                                                  date=date.today(),
                                                  allreadyread=False, numoflinesdisplay=2,
                                                  id=int(str(uuid.uuid4().int)[:5]))
                    db.session.add(notification1)
        eshcol_dict[institution_[2]] = eshcol_dict.get(institution_[2], 0) + forgotenApprentice_Mosad1
    for k, v in eshcol_dict.items():
        res = db.session.query(notifications).filter(notifications.userid == user.id,
                                                     notifications.event == "חניכים נשכחים").first()
        if res is None and date.today().weekday() == 2:
            notification1 = notifications(userid=user.id, subject=str(k), event="חניכים נשכחים", details=v,
                                          date=date.today(),
                                          allreadyread=False, numoflinesdisplay=2,
                                          id=int(str(uuid.uuid4().int)[:5]))
            db.session.add(notification1)

    db.session.commit()


@notification_form_blueprint.route('/getAll', methods=['GET'])
def getAll_notification_form():
        user = request.args.get('userId')
        print("user:",user)
        user_ent=db.session.query(user1.role_id,user1.institution_id,user1.eshcol,user1.id).filter(user1.id == user).first()
        print("user role:",user_ent[0])
        if user_ent[0]=="0":#melave
            add_notificaion_to_melave(user_ent)
        if user_ent[0] == "1":  # mosad
                add_notificaion_to_mosad(user_ent)
        if user_ent[0] == "2":  # eshcol
                add_notificaion_to_eshcol(user_ent)
        if user_ent[0] == "3":  # ahrah
            add_notificaion_to_ahraiTohnit(user_ent)
        #send  notifications.
        userEnt = db.session.query(user1.notifyStartWeek,user1.notifyDayBefore,user1.notifyMorning).filter_by(id=user).first()
        notiList = db.session.query(notifications).filter(notifications.userid == user).order_by(notifications.date.desc()).all()
        my_dict = []
        for noti in notiList:
            daysFromNow = (date.today() - noti.date).days if noti.date is not None else "None"
            if noti.event==config.groupMeet_report:
                apprenticeids=""
            else:
                apprenticeids=str(noti.subject)
            if noti.numoflinesdisplay==2:

                noti.details = noti.event if noti.details is None else noti.details
                my_dict.append(
                    {"id": str(noti.id),"subject":apprenticeids,
                     "date": toISO(noti.date),
                     "daysfromnow": daysFromNow, "event": noti.event.strip(), "allreadyread": noti.allreadyread,"description": noti.details,"frequency": noti.frequency if  noti.frequency is not None else "never",
                     "numOfLinesDisplay": noti.numoflinesdisplay})
                continue

            if userEnt.notifyStartWeek==True and date(date.today().year, noti.date.month, noti.date.day).weekday()==6:
                gap = (date.today() - date(date.today().year, noti.date.month, noti.date.day)).days
                if gap<=7:
                    noti.details = noti.event.strip() if noti.details is None else noti.details.strip()
                    my_dict.append(
                        {"id": str(noti.id), "subject":str(noti.subject),
                         "date": toISO(noti.date),
                         "daysfromnow": daysFromNow, "event": noti.event.strip(),"description": noti.details, "allreadyread": noti.allreadyread,"frequency": noti.frequency if  noti.frequency is not None else "never",
                         "numOfLinesDisplay": noti.numoflinesdisplay, })
                    continue
            if userEnt.notifyDayBefore ==True :
                is_shabat=date(date.today().year, noti.date.month, noti.date.day).weekday()==5
                if (is_shabat  and daysFromNow==-2) or  daysFromNow==-1 :
                    noti.details = noti.event.strip() if noti.details is None else noti.details.strip()
                    my_dict.append(
                        {"id": str(noti.id),"subject":str(noti.subject),
                         "date": toISO(noti.date),
                         "daysfromnow": daysFromNow, "event": noti.event.strip(),"description": noti.details, "allreadyread": noti.allreadyread,"frequency": noti.frequency,
                         "numOfLinesDisplay": noti.numoflinesdisplay,})
                    continue
            if userEnt.notifyMorning ==True :
                is_shabat=date(date.today().year, noti.date.month, noti.date.day).weekday()==5
                if (is_shabat  and daysFromNow==-1) or  daysFromNow==0 :
                    noti.details = noti.event.strip() if noti.details is None else noti.details.strip()
                    my_dict.append(
                        {"id": str(noti.id),"subject":str(noti.subject),
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
             institotionList= db.session.query(Institution.id,Institution.name,Institution.eshcol_id).all()
             eshcol_dict=dict()
             for institution_ in institotionList:
                 mosad__score1,forgotenApprentice_Mosad1=mosad__score(institution_[0])
                 if mosad__score1<65:
                     add_visit_notification(user, institution_[1], "ציון מוסדות", date.today())
                 print(institution_.id)
                 mosadCoord_ = db.session.query(user1.id,user1.name,user1.last_name).filter(user1.role_id == "1",
                                                                   user1.institution_id == institution_.id).first()
                 if mosadCoord_ is not None:
                     mosad_Coordinators_score1=mosad_Coordinators_score(mosadCoord_[0])
                     if mosad_Coordinators_score1<65:
                         add_visit_notification(user, None, mosadCoord_[1]+" "+mosadCoord_[2]+"ציון רכזים", date.today())
                 eshcol_dict[institution_[2]]=eshcol_dict.get(institution_[2], 0) + 1
             for k,v in eshcol_dict.items():
                 add_visit_notification(user, None,k +"חניכים נשכחים ", date.today())

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

             if  my_dict is None or my_dict==[]  :
            # acount not found
                return jsonify([])
             else:
                return jsonify(my_dict), HTTPStatus.OK


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