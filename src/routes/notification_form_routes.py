from datetime import datetime as dt, date, timedelta

import arrow as arrow
from flask import Blueprint, request, jsonify
from http import HTTPStatus

from hebrew import Hebrew
from pyluach import dates

import config

from .utils.notification_details import GROUP_MEET_DETAILS, PERSONAL_MEET_DETAILS, BASIS_VISIT_DETAILS, EVENT_DETAILS, \
    PERSONAL_CALL_DETAILS, BIRTHDAY_DETAILS, MELAVIM_LOW_SCORE_DETAILS, MATZBAR_DETAILS, DO_FOR_BOGRIM_DETAILS, \
    YESHIVAT_MELAVIM_DETAILS, FORGOTTEN_APPRENTICE_DETAILS, LOW_SCORE_MOSDOT_DETAILS, MOSAD_ESCHOL_MEETING_DETAILS
from .madadim import melave_score, mosad_score
from .user_profile import correct_auth
from src.models.models_utils import to_iso
from ..models.apprentice_model import Apprentice
from ..models.institution_model import Institution
from ..models.user_model import User
from ..models.report_model import Report
from src.services import db
import uuid
from ..models.task_model import Task

notification_form_blueprint = Blueprint('notification_form', __name__, url_prefix='/notification_form')
init_weekDay = date.today().weekday()


def convert_hebrewDate_to_Lozai(hebrew_date):
    today = dates.HebrewDate.today()
    birthday_ivry1 = hebrew_date.split(" ")
    try:
        thisYearBirthday = dates.HebrewDate(today.year, int(config.Ivry_month[birthday_ivry1[1]]),
                                            Hebrew(birthday_ivry1[0]).gematria()).to_greg()
        thisYearBirthday = date(thisYearBirthday.year, thisYearBirthday.month, thisYearBirthday.day)
    except:
        thisYearBirthday = dates.HebrewDate(today.year, int(config.Ivry_month[birthday_ivry1[1]]),
                                            Hebrew(birthday_ivry1[0]).gematria() - 2).to_greg()
        thisYearBirthday = date(thisYearBirthday.year, thisYearBirthday.month, thisYearBirthday.day)
    return thisYearBirthday


def add_notificaion_to_melave(user):
    ApprenticeList = db.session.query(Apprentice.birthday_ivry, Apprentice.id, Apprentice.accompany_id, Apprentice.name,
                                      Apprentice.last_name, Apprentice.birthday).filter(
        Apprentice.accompany_id == user.id).all()
    # basis meetings
    visitEvent = db.session.query(Report).filter(Report.user_id == user.id,
                                                Report.title == config.basis_report).order_by(
        Report.visit_date.desc()).first()

    if visitEvent is None or (date.today() - visitEvent.visit_date).days > 113:
        too_old = dt.today() - timedelta(days=83)
        res = db.session.query(Task).filter(Task.userid == user.id,
                                                     Task.created_at > too_old,
                                                     Task.event == config.basis_report).first()
        if res is None and date.today().weekday() == init_weekDay:
            date1 = user.association_date if visitEvent is None else visitEvent.visit_date
            add_task(
                user.id,
                "",
                config.basis_report,
                BASIS_VISIT_DETAILS.format(user.name),
                date1
            )
    # group meetings
    visitEvent = db.session.query(Report).filter(Report.user_id == user.id,
                                                Report.title == config.groupMeet_report).order_by(
        Report.visit_date.desc()).first()

    if visitEvent is None or (date.today() - visitEvent.visit_date).days > 53:
        too_old = dt.today() - timedelta(days=53)
        res = db.session.query(Task).filter(Task.userid == user.id,
                                                     Task.created_at > too_old,

                                                     Task.event == config.groupMeet_report).first()
        if res is None and date.today().weekday() == init_weekDay:
            date1 = user.association_date if visitEvent is None else visitEvent.visit_date
            add_task(
                user.id,
                "",
                config.groupMeet_report,
                GROUP_MEET_DETAILS.format(user.name),
                date1
            )

    for Apprentice1 in ApprenticeList:
        # call
        visitEvent = db.session.query(Report).filter(Report.user_id == user.id, Report.ent_reported == Apprentice1.id,
                                                    Report.title.in_(config.reports_as_call)).order_by(
            Report.visit_date.desc()).first()
        if visitEvent is None or (date.today() - visitEvent.visit_date).days > 14:
            too_old = dt.today() - timedelta(days=14)
            res = db.session.query(Task).filter(Task.userid == user.id,
                                                         Task.subject == str(Apprentice1.id),
                                                         Task.created_at > too_old,
                                                         Task.event == config.call_report).first()
            if res is None and date.today().weekday() == init_weekDay:
                date1 = user.association_date if visitEvent is None else visitEvent.visit_date
                add_task(
                    user.id,
                    str(Apprentice1.id),
                    config.call_report,
                    PERSONAL_CALL_DETAILS.format(user.name, Apprentice1.name + " " + Apprentice1.last_name),
                    date1
                )
        # personal meet
        visitEvent = db.session.query(Report).filter(Report.user_id == user.id, Report.ent_reported == str(Apprentice1.id),
                                                    Report.title.in_(config.report_as_meet)).order_by(
            Report.visit_date.desc()).first()
        if visitEvent is None or (date.today() - visitEvent.visit_date).days > 83:
            too_old = dt.today() - timedelta(days=83)
            res = db.session.query(Task).filter(Task.userid == user.id,
                                                         Task.subject == str(Apprentice1.id),
                                                         Task.created_at > too_old,
                                                         Task.event == config.personalMeet_report).first()
            if res is None and date.today().weekday() == init_weekDay:
                date1 = user.association_date if visitEvent is None else visitEvent.visit_date
                add_task(
                    user.id,
                    str(Apprentice1.id),
                    config.personalMeet_report,
                    PERSONAL_MEET_DETAILS.format(user.name, Apprentice1.name + " " + Apprentice1.last_name),
                    date1
                )
        # birthday
        gap_loazi = 1000
        gap = 1000
        thisYearBirthday = None
        if Apprentice1.birthday_ivry:
            thisYearBirthday = convert_hebrewDate_to_Lozai(Apprentice1.birthday_ivry)
            gap = (date.today() - thisYearBirthday).days
        if Apprentice1.birthday:
            gap_loazi = (dt.today() - dt(date.today().year, Apprentice1.birthday.month, Apprentice1.birthday.day)).days

        if ((gap <= 0 and gap >= -7) or (
                gap_loazi <= 0 and gap_loazi >= -7)) and date.today().weekday() == init_weekDay:
            if thisYearBirthday is None:
                thisYearBirthday = Apprentice1.birthday
            too_old = dt.today() - timedelta(days=8)
            res = db.session.query(Task).filter(Task.userid == user.id,
                                                         Task.subject == str(Apprentice1.id),
                                                         Task.created_at > too_old,
                                                         Task.event == "יום הולדת").first()
            if res is None and date.today().weekday() == init_weekDay:
                add_task(
                    user.id,
                    str(Apprentice1.id),
                    "יום הולדת",
                    BIRTHDAY_DETAILS.format(user.name, thisYearBirthday, Apprentice1.name + " " + Apprentice1.last_name),
                    thisYearBirthday
                )
    db.session.commit()


def add_notificaion_to_mosad(user):
    # doForBogrim
    visitEvent = db.session.query(Report).filter(Report.user_id == user.id,
                                                Report.title.in_(config.report_as_DoForBogrim)).order_by(
        Report.visit_date.desc()).first()
    if visitEvent is None or (date.today() - visitEvent.visit_date).days > 23:
        too_old = dt.today() - timedelta(days=23)

        res = db.session.query(Task).filter(Task.userid == user.id,
                                                     Task.created_at > too_old,
                                                     Task.event == config.doForBogrim_report).first()
        if res is None and date.today().weekday() == init_weekDay:
            date1 = user.association_date if visitEvent is None else visitEvent.visit_date
            add_task(
                user.id,
                "",
                config.doForBogrim_report,
                DO_FOR_BOGRIM_DETAILS.format(user.name),
                date1
            )
    # ישיבה מוסדית
    visitEvent = db.session.query(Report).filter(Report.user_id == user.id,
                                                Report.title == config.MelavimMeeting_report).order_by(
        Report.visit_date.desc()).first()
    if visitEvent is None or (date.today() - visitEvent.visit_date).days > 23:
        too_old = dt.today() - timedelta(days=23)
        res = db.session.query(Task).filter(Task.userid == user.id,
                                                     Task.created_at > too_old,
                                                     Task.event == config.MelavimMeeting_report).first()
        if res is None and date.today().weekday() == init_weekDay:
            date1 = user.association_date if visitEvent is None else visitEvent.visit_date
            add_task(
                user.id,
                "",
                config.MelavimMeeting_report,
                YESHIVAT_MELAVIM_DETAILS.format(user.name),
                date1
            )

    melave_list = db.session.query(User.id, User.name, User.last_name).filter(
        User.institution_id == user.institution_id, User.role_ids.contains("0")).all()
    under65_dict = dict()
    no_matzbar_list = []
    for melave_ in melave_list:
        # mathzbar
        visitEvent = db.session.query(Report).filter(Report.user_id == user.id, Report.ent_reported == melave_.id,
                                                    Report.title == config.matzbar_report).order_by(
            Report.visit_date.desc()).first()
        if visitEvent is None or (date.today() - visitEvent.visit_date).days > 113:
            no_matzbar_list.append(melave_.name + melave_.last_name)
        melave_score1, call_gap_avg, personal_meet_gap_avg, group_meeting_gap_avg = melave_score(melave_.id)

        if melave_score1 < 65:
            under65_dict[melave_.id] = melave_.name + " " + melave_.last_name
    # Matzbar noti create
    too_old = dt.today() - timedelta(days=83)
    res = db.session.query(Task).filter(Task.userid == user.id,
                                                 Task.event == config.matzbar_report).first()

    if res:
        d = res.created_at
        date_noti = dt(d.year, d.month, d.day)
    if (res is None or date_noti < too_old) and date.today().weekday() == init_weekDay:
        date1 = user.association_date if visitEvent is None else visitEvent.visit_date
        melavim = ""
        for k in no_matzbar_list:
            melavim += k + "\n"
        add_task(
            user.id,
            str(melave_.id),
            config.matzbar_report,
            MATZBAR_DETAILS.format(user.name) + melavim,
            date1
        )
    # melave_Score_
    too_old = dt.today() - timedelta(days=23)
    res = db.session.query(Task).filter(Task.userid == user.id,
                                                 Task.created_at > too_old,
                                                 Task.event == config.melave_Score_list).first()
    too_old = dt.today() - timedelta(days=23)

    if res:
        d = res.created_at
        date_noti = dt(d.year, d.month, d.day)
    if (res is None or date_noti < too_old) and date.today().weekday() == init_weekDay:
        date1 = user.association_date if visitEvent is None else visitEvent.visit_date
        melavim = ""
        for k, v in under65_dict.items():
            melavim += v + "\n"
        add_task(
            user.id,
            "",
            config.melave_Score_list,
            MELAVIM_LOW_SCORE_DETAILS.format(user.name) + melavim,
            date1
        )
    res = db.session.query(Task).filter(Task.userid == user.id,
                                                 Task.event == config.forgotenApprentice_list).first()
    too_old = dt.today() - timedelta(days=8)
    if res:
        d = res.created_at
        date_noti = dt(d.year, d.month, d.day)
    if (res is None or date_noti < too_old) and date.today().weekday() == init_weekDay:
        date1 = user.association_date if visitEvent is None else visitEvent.visit_date
        apprenticeList = db.session.query(Apprentice.name, Apprentice.last_name).filter(
            Apprentice.id.in_(forgotenApprentice_Mosad1)).all()

        apprenFOrgoten = ""
        for r in apprenticeList:
            apprenFOrgoten += r.name + " " + r.last_name + "\n"
        add_task(
            user.id,
            "",
            config.forgotenApprentice_list,
            FORGOTTEN_APPRENTICE_DETAILS.format(user.name) + apprenFOrgoten,
            date.today()
        )
    db.session.commit()


def add_notificaion_to_eshcol(user):
    institotionList = db.session.query(Institution.id, Institution.name, Institution.eshcol_id).filter(
        Institution.eshcol_id == user.eshcol).all()
    eshcol_dict = dict()
    lowScore_mosdot = []
    no_MOsadEshcolMeeting = []
    for institution_ in institotionList:
        mosad__score1, forgotenApprentice_Mosad1 = mosad_score(institution_[0])
        if mosad__score1 < 65:
            lowScore_mosdot.append(institution_[1])
        mosadCoord_ = db.session.query(User.id, User.name, User.last_name).filter(User.role_ids.contains("1"),
                                                                                     User.institution_id == institution_.id).first()
        if mosadCoord_ is not None:
            # MOsadEshcolMeeting_report
            visitEvent = db.session.query(Report).filter(Report.user_id == user.id, Report.ent_reported == mosadCoord_.id,
                                                        Report.title == config.MOsadEshcolMeeting_report).order_by(
                Report.visit_date.desc()).first()
            if visitEvent is None or (date.today() - visitEvent.visit_date).days > 23:
                no_MOsadEshcolMeeting.append(mosadCoord_.name)
            # ציון מלווים
            melave_list = db.session.query(User.id, User.name, User.last_name).filter(
                User.institution_id == institution_[0], User.role_ids.contains("0")).all()
            under65_dict = dict()
            for melave_ in melave_list:
                melave_score1, call_gap_avg, personal_meet_gap_avg, group_meeting_gap_avg = melave_score(melave_.id)
                if melave_score1 < 65:
                    under65_dict[institution_[1]] = under65_dict.get(institution_[1], []) + [melave_.name]
        eshcol_dict[institution_[1]] = eshcol_dict.get(institution_[1], []) + forgotenApprentice_Mosad1
    # ישיבת אשכול רכז מוסד
    res = db.session.query(Task).filter(Task.userid == user.id,
                                                 Task.event == config.MOsadEshcolMeeting_report).first()
    too_old = dt.today() - timedelta(days=23)
    if res:
        d = res.created_at
        date_noti = dt(d.year, d.month, d.day)
    if (res is None or date_noti < too_old) and date.today().weekday() == init_weekDay:
        no_MOsadEshcolMeeting_str = ""
        for r in no_MOsadEshcolMeeting:
            no_MOsadEshcolMeeting_str += r + "\n"
        add_task(
            user.id,
            "",
            config.MOsadEshcolMeeting_report,
            MOSAD_ESCHOL_MEETING_DETAILS.format(user.name) + no_MOsadEshcolMeeting_str,
            date.today()
        )
    # ישיבת  רכזים מלוים
    res = db.session.query(Task).filter(Task.userid == user.id,
                                                 Task.event == config.tochnitMeeting_report).first()
    too_old = dt.today() - timedelta(days=53)
    if res:
        d = res.created_at
        date_noti = dt(d.year, d.month, d.day)
    if (res is None or date_noti < too_old) and date.today().weekday() == init_weekDay:
        no_MOsadEshcolMeeting_str = ""
        for r in no_MOsadEshcolMeeting:
            no_MOsadEshcolMeeting_str += r + "\n"
        add_task(
            user.id,
            "",
            config.tochnitMeeting_report,
            MOSAD_ESCHOL_MEETING_DETAILS.format(user.name) + no_MOsadEshcolMeeting_str,
            date.today()
        )
    # ציון מוסדות נמוך-הכנסה
    res = db.session.query(Task).filter(Task.userid == user.id,
                                                 Task.event == "עידכון חודשי-ציון מוסדות").first()
    too_old = dt.today() - timedelta(days=23)
    if res:
        d = res.created_at
        date_noti = dt(d.year, d.month, d.day)
    lowScore_mosdot_str = ""
    for r in lowScore_mosdot:
        lowScore_mosdot_str += r + "\n"
    if (res is None or date_noti < too_old) and date.today().weekday() == init_weekDay:
        add_task(
            user.id,
            "",
            "עידכון חודשי-ציון מוסדות",
            LOW_SCORE_MOSDOT_DETAILS.format(user.name) + lowScore_mosdot_str,
            date.today()
        )
    inst_forgoten_dict = dict()
    res = db.session.query(Task).filter(Task.userid == user.id,
                                                 Task.event == config.forgotenApprentice_list).first()
    if res:
        d = res.created_at
        date_noti = dt(d.year, d.month, d.day)
    too_old = dt.today() - timedelta(days=8)
    if (res is None or date_noti < too_old) and date.today().weekday() == init_weekDay:
        for inst, appren in eshcol_dict.items():
            melave_appren_forgoten = dict()
            for appren1 in appren:
                Apprentice1 = db.session.query(Apprentice.accompany_id, Apprentice.name).filter(
                    Apprentice.id == appren1).first()
                user_name = db.session.query(User.name).filter(User.id == Apprentice1.accompany_id).first()
                melave_appren_forgoten[user_name.name] = melave_appren_forgoten.get(user_name.name,
                                                                                    "") + Apprentice1.name + ","
            inst_forgoten_dict[inst] = melave_appren_forgoten
        inst_str = ""
        for inst, dict2 in inst_forgoten_dict.items():
            inst_str += str(inst)
            inst_str += ":"
            for melave, appren in dict2.items():
                inst_str += melave
                for a in appren:
                    inst_str += a + "\n"
                inst_str + "\n"
            inst_str + "\n"

        add_task(
            user.id,
            "",
            config.forgotenApprentice_list,
            FORGOTTEN_APPRENTICE_DETAILS.format(user.name) + str(inst_str),
            date.today()
        )
    db.session.commit()


def add_notificaion_to_ahraiTohnit(user):
    lowScore_mosdot = dict()
    no_MOsadEshcolMeeting = []
    all_eshcols_forgoten = dict()
    eshcol_list = db.session.query(Institution.eshcol_id).distinct(Institution.eshcol_id).all()
    for eshcol in eshcol_list:
        eshcol_forgoten = dict()
        institotionList = db.session.query(Institution.id, Institution.name, Institution.eshcol_id).filter(
            Institution.eshcol_id == eshcol.eshcol_id).all()
        for institution_ in institotionList:
            mosad__score1, forgotenApprentice_Mosad1 = mosad_score(institution_[0])
            if mosad__score1 < 65:
                lowScore_mosdot[institution_.eshcol_id] = lowScore_mosdot.get(institution_.eshcol_id, []) + [
                    institution_.name]
            mosadCoord_ = db.session.query(User.id, User.name, User.last_name).filter(User.role_ids.contains("1"),
                                                                                         User.institution_id == institution_.id).first()
            if mosadCoord_ is not None:
                # ישיבת רכזי תוכנית
                visitEvent = db.session.query(Report).filter(Report.user_id == user.id,
                                                            Report.ent_reported == mosadCoord_.id,
                                                            Report.title == config.tochnitMeeting_report).order_by(
                    Report.visit_date.desc()).first()
                if visitEvent is None or (date.today() - visitEvent.visit_date).days > 23:
                    no_MOsadEshcolMeeting.append(mosadCoord_.name)
                # ציון מלווים
                melave_list = db.session.query(User.id, User.name, User.last_name).filter(
                    User.institution_id == institution_[0], User.role_ids.contains("0")).all()
                under65_dict = dict()
                for melave_ in melave_list:
                    melave_score1, call_gap_avg, personal_meet_gap_avg, group_meeting_gap_avg = melave_score(melave_.id)
                    if melave_score1 < 65:
                        under65_dict[institution_[1]] = under65_dict.get(institution_[1], []) + [melave_.name]
            eshcol_forgoten[institution_[1]] = eshcol_forgoten.get(institution_[1], []) + forgotenApprentice_Mosad1
        all_eshcols_forgoten[eshcol] = eshcol_forgoten

    # ציון מוסדות נמוך-הכנסה
    res = db.session.query(Task).filter(Task.userid == user.id,
                                                 Task.event == "עידכון חודשי-ציון מוסדות").first()
    too_old = dt.today() - timedelta(days=23)
    if res:
        d = res.created_at
        date_noti = dt(d.year, d.month, d.day)
    lowScore_mosdot_str = ""
    for eshcol, insts in lowScore_mosdot.items():
        lowScore_mosdot_str += eshcol + ":"
        for r in insts:
            lowScore_mosdot_str += r + "\n"
        lowScore_mosdot_str += "\n"
    if (res is None or date_noti < too_old) and date.today().weekday() == init_weekDay:
        add_task(
            user.id,
            str(institution_[0]),
            "עידכון חודשי-ציון מוסדות",
            LOW_SCORE_MOSDOT_DETAILS.format(user.name) + lowScore_mosdot_str,
            date.today()
        )
    # נשכחים
    res = db.session.query(Task).filter(Task.userid == user.id,
                                                 Task.event == config.forgotenApprentice_list).first()
    too_old = dt.today() - timedelta(days=8)
    if res:
        d = res.created_at
        date_noti = dt(d.year, d.month, d.day)
    if (res is None or date_noti < too_old) and date.today().weekday() == init_weekDay:
        eshcol_forgoten_dict = dict()
        for eshcol, list1 in all_eshcols_forgoten.items():
            inst_forgoten_dict = dict()
            for inst, appren in list1.items():
                melave_appren_forgoten = dict()
                for appren1 in appren:
                    Apprentice1 = db.session.query(Apprentice.accompany_id, Apprentice.name).filter(
                        Apprentice.id == appren1).first()
                    user_name = db.session.query(User.name).filter(User.id == Apprentice1.accompany_id).first()
                    melave_appren_forgoten[user_name.name] = melave_appren_forgoten.get(user_name.name,
                                                                                        "") + Apprentice1.name + ","
                inst_forgoten_dict[inst] = melave_appren_forgoten
            eshcol_forgoten_dict[eshcol[0]] = inst_forgoten_dict
        forgoten_str = ""
        for eshcol, dict2 in eshcol_forgoten_dict.items():
            forgoten_str += str(eshcol) + ":"
            for inst, dict3 in dict2.items():
                forgoten_str += inst + ":"
                for melave, appren in dict3.items():
                    forgoten_str += melave + ":" + appren + "\n"
                forgoten_str += "\n"
            forgoten_str += "\n"

        add_task(user.id,
                 str(inst),
                 config.forgotenApprentice_list,
                 FORGOTTEN_APPRENTICE_DETAILS.format(user.name) + str(forgoten_str),
                 date.today()
        )
        db.session.commit()


def add_task(user_id: str, subject: str,  event: str, details: str, task_date):
    task = Task(
        id=int(str(uuid.uuid4().int)[:5]),
        userid=user_id,
        subject=subject,
        event=event,
        details=details,
        date= task_date if task_date is not None else date.today(),
        created_at=arrow.now().format('YYYY-MM-DDThh:mm:ss'),
        allreadyread=False,
    )
    db.session.add(task)

@notification_form_blueprint.route('/getAll', methods=['GET'])
def getAll_notification_form(isExternal=True):
    if correct_auth(isExternal) == False:
        return jsonify({'result': "wrong access token"}), HTTPStatus.OK
    user = request.args.get('userId')
    user_ent = db.session.query(User.role_ids, User.institution_id, User.eshcol, User.id, User.name,
                                User.association_date).filter(User.id == user).first()
    if "0" in user_ent[0]:  # melave
        add_notificaion_to_melave(user_ent)
    if "1" in user_ent[0]:  # mosad
        add_notificaion_to_mosad(user_ent)
    if "2" in user_ent[0]:  # eshcol
        add_notificaion_to_eshcol(user_ent)
    if "3" in user_ent[0]:  # ahrah
        add_notificaion_to_ahraiTohnit(user_ent)
    # send  notifications.
    userEnt = db.session.query(User.notifyStartWeek, User.notifyDayBefore, User.notifyMorning).filter(
        User.id == user).first()
    notiList = db.session.query(Task).filter(Task.userid == user).order_by(
        Task.date.desc()).all()
    my_dict = []
    for noti in notiList:
        daysFromNow = (dt.today() - noti.date).days if noti.date is not None else ""
        if noti.event == config.groupMeet_report:
            apprenticeids = ""
        else:
            apprenticeids = str(noti.subject)
        # if noti.numoflinesdisplay == 2:
        if True:
            my_dict.append(
                {"id": str(noti.id), "subject": apprenticeids,
                 "date": to_iso(noti.date), "created_at": str(noti.created_at),
                 "daysfromnow": daysFromNow, "event": noti.event.strip(), "allreadyread": noti.allreadyread,
                 "description": noti.details, "frequency": noti.frequency_meta if noti.frequency_meta is not None else "never"})
            continue
        # Dead code, will be addressed once we delete the notifications route
        if userEnt.notifyStartWeek == True and date(date.today().year, noti.date.month, noti.date.day).weekday() == 6:
            gap = (date.today() - date(date.today().year, noti.date.month, noti.date.day)).days
            if gap <= 7:
                my_dict.append(
                    {"id": str(noti.id), "subject": str(noti.subject),
                     "date": to_iso(noti.date), "created_at": str(noti.created_at),
                     "daysfromnow": daysFromNow, "event": noti.event.strip(), "description": noti.details,
                     "allreadyread": noti.allreadyread,
                     "frequency": noti.frequency if noti.frequency is not None else "never" })
                continue
        if userEnt.notifyDayBefore == True:
            is_shabat = date(date.today().year, noti.date.month, noti.date.day).weekday() == 5
            if (is_shabat and daysFromNow == -2) or daysFromNow == -1:
                my_dict.append(
                    {"id": str(noti.id), "subject": str(noti.subject),
                     "date": to_iso(noti.date), "created_at": str(noti.created_at),
                     "daysfromnow": daysFromNow, "event": noti.event.strip(), "description": noti.details,
                     "allreadyread": noti.allreadyread, "frequency": noti.frequency })
                continue
        if userEnt.notifyMorning == True:
            is_shabat = date(date.today().year, noti.date.month, noti.date.day).weekday() == 5
            if (is_shabat and daysFromNow == -1) or daysFromNow == 0:
                noti.details = noti.event.strip() if noti.details is None else noti.details.strip()
                my_dict.append(
                    {"id": str(noti.id), "subject": str(noti.subject),
                     "date": to_iso(noti.date), "created_at": str(noti.created_at),
                     "daysfromnow": daysFromNow, "event": noti.event.strip(), "description": noti.details,
                     "allreadyread": noti.allreadyread,
                     "frequency": noti.frequency if noti.frequency is not None else "never"})
                continue
    if my_dict is None or my_dict == []:
        # acount not found
        return jsonify([])
    else:
        # TODO: get Noti form to DB
        return jsonify(my_dict), HTTPStatus.OK


@notification_form_blueprint.route('/add1', methods=['POST'])
def add_notification_form():
    try:
        if correct_auth()==False:
            return jsonify({'result': "wrong access token"}), HTTPStatus.OK
        json_object = request.json
        user = json_object["userId"]
        subject = json_object["subject"] if json_object["subject"] else ""
        event = json_object["event"]
        date = json_object["date"]
        user_ent = db.session.query(User.role_ids, User.institution_id, User.eshcol, User.id, User.name).filter(
            User.id == user).first()
        subject_ent = db.session.query(Apprentice.name).filter(Apprentice.id == subject).first()
        if subject_ent is None:
            subject_ent = "מי שקבעת"
        else:
            subject_ent = subject_ent.name
        details = EVENT_DETAILS.format(user_ent.name, date, event, subject_ent) + json_object["details"]
        frequency = json_object["frequency"] if json_object["frequency"] is not None else "never"
        notification1 = Task(
            userid=user,
            subject=str(subject),
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
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST
    return jsonify({"result": "success"}), HTTPStatus.OK
    # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK


@notification_form_blueprint.route('/setWasRead', methods=['post'])
def setWasRead_notification_form():
    if correct_auth() == False:
        return jsonify({'result': "wrong access token"}), HTTPStatus.OK
    data = request.json
    notiId = data['noti_id']
    try:
        noti = Task.query.get(notiId)
        noti.allreadyread = True
        db.session.commit()
        if notiId:
            # TODO: add contact form to DB
            return jsonify({'result': 'success'}), HTTPStatus.OK
    except:
        return jsonify({'result': 'wrong id'}), HTTPStatus.OK


@notification_form_blueprint.route('/setSetting', methods=['post'])
def setSetting_notification_form():
    if correct_auth() == False:
        return jsonify({'result': "wrong access token"}), HTTPStatus.OK
    data = request.json

    notifyMorningval = data['notifyMorning']
    notifyDayBeforeval = data['notifyDayBefore']
    notifyStartWeekval = data['notifyStartWeek']
    notifyMorning_weekly_report = data['notifyMorning_weekly_report']
    notifyMorning_sevev = data['notifyMorning_sevev']
    notifyDayBefore_sevev = data['notifyDayBefore_sevev']
    notifyStartWeek_sevev = data['notifyStartWeek_sevev']

    user = data['userId']
    user = User.query.get(user)
    user.notifyStartWeek = notifyStartWeekval == 'true' or notifyStartWeekval == 'True'
    user.notifyDayBefore = notifyDayBeforeval == 'true' or notifyDayBeforeval == 'True'
    user.notifyMorning = notifyMorningval == 'true' or notifyMorningval == 'True'
    user.notifyMorning_weekly_report = notifyMorning_weekly_report == 'true' or notifyMorning_weekly_report == 'True'
    user.notifyMorning_sevev = notifyMorning_sevev == 'true' or notifyMorning_sevev == 'True'
    user.notifyDayBefore_sevev = notifyDayBefore_sevev == 'true' or notifyDayBefore_sevev == 'True'
    user.notifyStartWeek_sevev = notifyStartWeek_sevev == 'true' or notifyStartWeek_sevev == 'True'

    try:
        db.session.commit()
    except:
        return jsonify({'result': 'wrong id '}), HTTPStatus.OK

    if user:
        # TODO: add contact form to DB
        return jsonify({'result': 'success'}), HTTPStatus.OK


@notification_form_blueprint.route('/getAllSetting', methods=['GET'])
def getNotificationSetting_form():
    try:
        if correct_auth()==False:
            return jsonify({'result': "wrong access token"}), HTTPStatus.OK
        user = request.args.get('userId')
        notiSettingList = db.session.query(User.notifyMorning, User.notifyDayBefore, User.notifyStartWeek,
                                           User.notifyMorning_weekly_report, User.notifyMorning_sevev, User.notifyDayBefore_sevev,
                                           User.notifyStartWeek_sevev,).filter(
            User.id == user).first()
        if not notiSettingList:
            # acount not found
            return jsonify(["Wrong id or emty list"])
        else:
            # TODO: get Noti form to DB
            return jsonify({"notifyMorning": notiSettingList.notifyMorning,
                            "notifyDayBefore": notiSettingList.notifyDayBefore
                               , "notifyStartWeek": notiSettingList.notifyStartWeek,
                            "notifyStartWeek_sevev": notiSettingList.notifyStartWeek_sevev,
                            "notifyDayBefore_sevev":notiSettingList.notifyDayBefore_sevev,
                            "notifyMorning_sevev": notiSettingList.notifyMorning_sevev
                               , "notifyMorning_weekly_report": notiSettingList.notifyMorning_weekly_report
                            }), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST


@notification_form_blueprint.route('/delete', methods=['POST'])
def delete():
    try:
        if correct_auth()==False:
            return jsonify({'result': "wrong access token"}), HTTPStatus.OK
        data = request.json
        NotificationId = data['NotificationId']
        res = db.session.query(Task).filter(Task.id == NotificationId).delete()
        db.session.commit()
    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST
    return jsonify({"result": "success"}), HTTPStatus.OK
    # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK


@notification_form_blueprint.route("/update", methods=['put'])
def updateTask():
    try:
        if correct_auth()==False:
            return jsonify({'result': "wrong access token"}), HTTPStatus.OK
        # get tasksAndEvents
        NotificationId = request.args.get("NotificationId")
        data = request.json

        updatedEnt = Task.query.get(NotificationId)
        for key in data:
            setattr(updatedEnt, key, data[key])
        db.session.commit()
        if updatedEnt:
            # TODO: add contact form to DB
            return jsonify({'result': 'success'}), HTTPStatus.OK
        return jsonify({'result': 'error'}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST

