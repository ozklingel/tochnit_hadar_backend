from datetime import datetime as dt, date, timedelta, datetime
from http import HTTPStatus

import arrow as arrow
from flask import jsonify

from src.models.models_utils import to_iso
from .compute_score import (
    mosad_score,
    melave_score,
    mosad_Coordinators_score,
    eshcol_Coordinators_score,
)
from ..logic.tasks import logger
from ..models import report_model, models_utils
from ..models.apprentice_model import Apprentice
from ..models.cluster_model import Cluster
from ..models.institution_model import Institution
from ..models.system_report_model import forgotenApprentice_list, melave_Score_list,low_score_65_list,mosdot_score_list
from ..models.user_model import User
from ..models.report_model import Report
from src.services import db
import uuid
from ..models.task_model_v2 import Task, TaskFrequencyWeekdayEnum, TaskTubTypeEnum, TaskStatusEnum
from src.routes.utils.notification_details import (
    GROUP_MEET_DETAILS,
    PERSONAL_MEET_DETAILS,
    BASIS_VISIT_DETAILS,
    PERSONAL_CALL_DETAILS,
    BIRTHDAY_DETAILS,
    MELAVIM_LOW_SCORE_DETAILS,
    MATZBAR_DETAILS,
    DO_FOR_BOGRIM_DETAILS,
    YESHIVAT_MELAVIM_DETAILS,
    FORGOTTEN_APPRENTICE_DETAILS,
    LOW_SCORE_MOSDOT_DETAILS,
    MOSAD_ESCHOL_MEETING_DETAILS,
    HAZANAT_MAHZOR_DETAILS,
    HORIML_MEET_DETAILS,
    TOCHNIT_MEETING_DETAILS,
    CLUSTER_COORD_LOW_SCORE_DETAILS,
)
from ..routes.tasks import get_task_service
from ..routes.utils.hebrw_date_cust import start_of_year_greg_date, start_of_current_rivon, \
     hebrew_date_to_greg_date, get_start_of_year_greg_date


def add_notificaion_to_melave(user):
    ApprenticeList = (
        db.session.query(
            Apprentice.birthday_ivry,
            Apprentice.id,
            Apprentice.accompany_id,
            Apprentice.name,
            Apprentice.last_name,
            Apprentice.birthday,
            Apprentice.association_date,
        )
        .filter(Apprentice.accompany_id == user.id)
        .all()
    )
    # basis meetings -once a rivon
    visitEvent = (
        db.session.query(Report)
        .filter(Report.user_id == user.id, Report.title == report_model.basis_report)
        .order_by(Report.visit_date.desc())
        .first()
    )
    res = (
        db.session.query(Task)
        .filter(
            Task.user_id == user.id,
            Task.name == report_model.basis_report,
        )
        .order_by(Task.created_at.desc())
        .first()
    )
    if res is None :
        date1 = (
            user.association_date
            if res is None
            else dt.today() - timedelta(days=7 * (-1))
        )
        add_task(
            user.id,
            None,
            report_model.basis_report,
            BASIS_VISIT_DETAILS.format(user.name),
            date1,
            "APPRENTICE",
            (
                TaskTubTypeEnum["MEET"]
                if "," not in user.role_ids
                else TaskTubTypeEnum.GENERAL
            ),
            visitEvent.visit_date if visitEvent else user.association_date
        )
    # group meetings
    visitEvent = (
        db.session.query(Report)
        .filter(
            Report.user_id == user.id, Report.title == report_model.groupMeet_report
        )
        .order_by(Report.visit_date.desc())
        .first()
    )

    if visitEvent is None or (date.today() - visitEvent.visit_date).days > 53:
        too_old = dt.today() - timedelta(days=53)
        res = (
            db.session.query(Task)
            .filter(
                Task.user_id == user.id,
                Task.created_at > too_old,
                Task.name == report_model.groupMeet_report,
            )
            .first()
        )
        if res is None:
            date1 = (
                user.association_date
                if visitEvent is None
                else dt.today() - timedelta(days=7 * (-1))
            )

            add_task(
                user.id,
                "",
                report_model.groupMeet_report,
                GROUP_MEET_DETAILS.format(user.name),
                date1,
                "APPRENTICE",
                (
                    TaskTubTypeEnum["MEET"]
                    if "," not in user.role_ids
                    else TaskTubTypeEnum.GENERAL
                ),
                visitEvent.visit_date if visitEvent else user.association_date
            )

    for Apprentice1 in ApprenticeList:
        start_Of_year = get_start_of_year_greg_date()
        half_Of_year = start_Of_year + timedelta(days=30 * 6)
        # Horim call
        visitEvent = (
            db.session.query(Report)
            .filter(
                Report.user_id == user.id,
                Report.ent_reported == Apprentice1.id,
                Report.title == report_model.HorimCall_report,
                Report.visit_date > start_Of_year,
            )
            .order_by(Report.visit_date.desc())
            .first()
        )
        if visitEvent is None or  visitEvent.visit_date <start_Of_year  :
            res = (
                db.session.query(Task)
                .filter(
                    Task.user_id == user.id,
                    Task.subject_id == str(Apprentice1.id),
                    Task.name == report_model.HorimCall_report,
                    Task.created_at > start_Of_year,
                )
                .first()
            )
            if res is None or date.today()==half_Of_year :
                date1 = (
                    Apprentice1.association_date
                    if visitEvent is None
                    else dt.today() - timedelta(days=7 * (-1))
                )
                add_task(
                    user.id,
                    str(Apprentice1.id),
                    report_model.HorimCall_report,
                    HORIML_MEET_DETAILS.format(
                        user.name, Apprentice1.name + " " + Apprentice1.last_name
                    ),
                    date1,
                    "APPRENTICE",
                    (
                        TaskTubTypeEnum["PARENTS"]
                        if "," not in user.role_ids
                        else TaskTubTypeEnum.GENERAL
                    ),
                visitEvent.visit_date if visitEvent else user.association_date

                )
        # call
        visitEvent = (
            db.session.query(Report)
            .filter(
                Report.user_id == user.id,
                Report.ent_reported == Apprentice1.id,
                Report.title.in_(report_model.reports_as_call),
            )
            .order_by(Report.visit_date.desc())
            .first()
        )
        if visitEvent is None or (date.today() - visitEvent.visit_date).days > 14:
            too_old = dt.today() - timedelta(days=14)
            res = (
                db.session.query(Task)
                .filter(
                    Task.user_id == user.id,
                    Task.subject_id == str(Apprentice1.id),
                    Task.created_at > too_old,
                    Task.name == report_model.call_report,
                )
                .first()
            )
            if res is None:
                date1 = (
                    Apprentice1.association_date
                    if visitEvent is None
                    else dt.today() - timedelta(days=7 * (-1))
                )
                add_task(
                    user.id,
                    str(Apprentice1.id),
                    report_model.call_report,
                    PERSONAL_CALL_DETAILS.format(
                        user.name, Apprentice1.name + " " + Apprentice1.last_name
                    ),
                    date1,
                    "APPRENTICE",
                    (
                        TaskTubTypeEnum["CALL"]
                        if "," not in user.role_ids
                        else TaskTubTypeEnum.GENERAL
                    ),
                visitEvent.visit_date if visitEvent else user.association_date

                )
        # personal meet
        visitEvent = (
            db.session.query(Report)
            .filter(
                Report.user_id == user.id,
                Report.ent_reported == str(Apprentice1.id),
                Report.title.in_(report_model.report_as_meet),
            )
            .order_by(Report.visit_date.desc())
            .first()
        )
        if visitEvent is None or (date.today() - visitEvent.visit_date).days > 83:
            too_old = dt.today() - timedelta(days=83)
            res = (
                db.session.query(Task)
                .filter(
                    Task.user_id == user.id,
                    Task.subject_id == str(Apprentice1.id),
                    Task.created_at > too_old,
                    Task.name == report_model.personalMeet_report,
                )
                .first()
            )
            if res is None:
                date1 = (
                    Apprentice1.association_date
                    if visitEvent is None
                    else dt.today() - timedelta(days=7 * (-1))
                )
                add_task(
                    user.id,
                    str(Apprentice1.id),
                    report_model.personalMeet_report,
                    PERSONAL_MEET_DETAILS.format(
                        user.name, Apprentice1.name + " " + Apprentice1.last_name
                    ),
                    date1,
                    "APPRENTICE",
                    (
                        TaskTubTypeEnum["MEET"]
                        if "," not in user.role_ids
                        else TaskTubTypeEnum.GENERAL
                    ),
                visitEvent.visit_date if visitEvent else user.association_date

                )
        # birthday
        gap = 1000
        thisYearBirthday = None

        if Apprentice1.birthday_ivry:
            thisYearBirthday = hebrew_date_to_greg_date(Apprentice1.birthday_ivry)
            if thisYearBirthday:
                gap = (datetime.today() - thisYearBirthday).days
        if Apprentice1.birthday:
            try:
                thisYearBirthday = dt(
                    date.today().year,
                    Apprentice1.birthday.month,
                    Apprentice1.birthday.day,
                )
                gap = (dt.today() - thisYearBirthday).days
            except Exception as e:
                print(Apprentice1.id,Apprentice1.birthday,e)
        if thisYearBirthday and gap <= 0 and gap >= -7:
            too_old = dt.today() - timedelta(days=8)
            res = (
                db.session.query(Task)
                .filter(
                    Task.user_id == user.id,
                    Task.subject_id == str(Apprentice1.id),
                    Task.created_at > too_old,
                    Task.name == "יום הולדת",
                )
                .first()
            )
            if res is None:
                add_task(
                    user.id,
                    str(Apprentice1.id),
                    "יום הולדת",
                    BIRTHDAY_DETAILS.format(
                        user.name,
                        thisYearBirthday,
                        Apprentice1.name + " " + Apprentice1.last_name,
                    ),
                    thisYearBirthday,
                    "APPRENTICE",
                    (
                        TaskTubTypeEnum["NOTIFICATION_ONLY"]
                        if "," not in user.role_ids
                        else TaskTubTypeEnum.GENERAL
                    ),
                    dt.today()- timedelta(days=365)
                )
    db.session.commit()


def add_notificaion_to_mosad(user):
    # hazanatMachzor
    start_Of_year = start_of_year_greg_date()

    visitEvent = (
        db.session.query(Report)
        .filter(
            Report.user_id == user.id,
            Report.title == report_model.hazanatMachzor_report,
            Report.visit_date > start_Of_year,
        )
        .first()
    )
    if visitEvent is None:
        res = (
            db.session.query(Task)
            .filter(
                Task.user_id == user.id,
                Task.created_at > start_Of_year,
                Task.name == report_model.hazanatMachzor_report,
            )
            .first()
        )
        if res is None:
            date1 = (
                user.association_date
                if visitEvent is None
                else dt.today() - timedelta(days=7 * (-1))
            )
            add_task(
                user.id,
                "",
                report_model.hazanatMachzor_report,
                HAZANAT_MAHZOR_DETAILS.format(user.name),
                date1,
                "APPRENTICE",
                (
                    TaskTubTypeEnum["PERSONAL"]
                    if get_max_role(user.role_ids) == 1
                    else TaskTubTypeEnum["GENERAL"]
                ),
                visitEvent.visit_date if visitEvent else user.association_date

            )
    # doForBogrim
    visitEvent = (
        db.session.query(Report)
        .filter(
            Report.user_id == user.id,
            Report.title.in_(report_model.report_as_DoForBogrim),
        )
        .order_by(Report.visit_date.desc())
        .first()
    )
    if visitEvent is None or (date.today() - visitEvent.visit_date).days > 23:
        too_old = dt.today() - timedelta(days=23)

        res = (
            db.session.query(Task)
            .filter(
                Task.user_id == user.id,
                Task.created_at > too_old,
                Task.name == report_model.doForBogrim_report,
            )
            .first()
        )
        too_old = dt.today() - timedelta(days=23)
        d = res.created_at if res else None
        if res is None or dt(d.year, d.month, d.day) < too_old:
            date1 = (
                user.association_date
                if visitEvent is None
                else dt.today() - timedelta(days=7 * (-1))
            )
            add_task(
                user.id,
                "",
                report_model.doForBogrim_report,
                DO_FOR_BOGRIM_DETAILS.format(user.name),
                date1,
                "APPRENTICE",
                (
                    TaskTubTypeEnum["PERSONAL"]
                    if get_max_role(user.role_ids) == 1
                    else TaskTubTypeEnum["GENERAL"]
                ),
                visitEvent.visit_date if visitEvent else user.association_date

            )
    # ישיבה מוסדית
    visitEvent = (
        db.session.query(Report)
        .filter(
            Report.user_id == user.id,
            Report.title == report_model.MelavimMeeting_report,
        )
        .order_by(Report.visit_date.desc())
        .first()
    )
    if visitEvent is None or (date.today() - visitEvent.visit_date).days > 23:
        too_old = dt.today() - timedelta(days=23)
        res = (
            db.session.query(Task)
            .filter(
                Task.user_id == user.id,
                Task.created_at > too_old,
                Task.name == report_model.MelavimMeeting_report,
            )
            .first()
        )
        too_old = dt.today() - timedelta(days=23)
        d = res.created_at if res else None
        if res is None or dt(d.year, d.month, d.day) < too_old:
            date1 = (
                user.association_date
                if visitEvent is None
                else dt.today() - timedelta(days=7 * (-1))
            )
            add_task(
                user.id,
                "",
                report_model.MelavimMeeting_report,
                YESHIVAT_MELAVIM_DETAILS.format(user.name),
                date1,
                "INSTITUTION",
                (
                    TaskTubTypeEnum["PERSONAL"]
                    if get_max_role(user.role_ids) == 1
                    else TaskTubTypeEnum["GENERAL"]
                ),
                visitEvent.visit_date if visitEvent else user.association_date

            )

    melave_list = (
        db.session.query(User.id, User.name, User.last_name)
        .filter(User.institution_id == user.institution_id, User.role_ids.contains("0"))
        .all()
    )
    under65_dict = dict()
    no_matzbar_list = []
    for melave_ in melave_list:
        # mathzbar
        visitEvent = (
            db.session.query(Report)
            .filter(
                Report.user_id == user.id,
                Report.ent_reported == melave_.id,
                Report.title == report_model.matzbar_report,
            )
            .order_by(Report.visit_date.desc())
            .first()
        )
        if visitEvent is None or (date.today() - visitEvent.visit_date).days > 83:
            # Matzbar noti create
            too_old = dt.today() - timedelta(days=83)
            res = (
                db.session.query(Task)
                .filter(
                    Task.user_id == user.id,
                    Task.subject_id == str(melave_.id),
                    Task.name == report_model.matzbar_report,
                )
                .first()
            )

            d = res.created_at if res else None
            if res is None or dt(d.year, d.month, d.day) < too_old:
                date1 = (
                    user.association_date
                    if visitEvent is None
                    else dt.today() - timedelta(days=7 * (-1))
                )
                add_task(
                    user.id,
                    melave_.id,
                    report_model.matzbar_report,
                    MATZBAR_DETAILS.format(
                        user.name, melave_.name + " " + melave_.last_name
                    ),
                    date1,
                    "USER",
                    (
                        TaskTubTypeEnum["PERSONAL"]
                        if get_max_role(user.role_ids) == 1
                        else TaskTubTypeEnum["GENERAL"]
                    ),
                visitEvent.visit_date if visitEvent else user.association_date

                )
        # collect melave_Score_
        melave_score1, call_gap_avg, personal_meet_gap_avg, group_meeting_gap_avg = (
            melave_score(melave_.id)
        )

        if melave_score1 < 65:
            under65_dict[melave_.id] = melave_.name + " " + melave_.last_name

    # melave_Score_
    too_old = dt.today() - timedelta(days=23)
    res = (
        db.session.query(Task)
        .filter(
            Task.user_id == user.id,
            Task.created_at > too_old,
            Task.name == melave_Score_list,
        )
        .first()
    )
    too_old = dt.today() - timedelta(days=23)
    d = res.created_at if res else None
    if res is None or dt(d.year, d.month, d.day) < too_old:
        date1 = (
            user.association_date
            if visitEvent is None
            else dt.today() - timedelta(days=7 * (-1))
        )
        melavim = ""
        for k, v in under65_dict.items():
            melavim += v + "\n"
        add_task(
            user.id,
            "",
            melave_Score_list,
            MELAVIM_LOW_SCORE_DETAILS.format(user.name) + melavim,
            date1,
            "INSTITUTION",
            (
                TaskTubTypeEnum["PERSONAL"]
                if get_max_role(user.role_ids) == 1
                else TaskTubTypeEnum["GENERAL"]
            ),
            date1
        )
    # forgotenApprentice_list
    res = (
        db.session.query(Task)
        .filter(Task.user_id == user.id, Task.name == forgotenApprentice_list)
        .first()
    )
    too_old = dt.today() - timedelta(days=7)
    d = res.created_at if res else None
    if res is None or dt(d.year, d.month, d.day) < too_old:
        (
            user.association_date
            if visitEvent is None
            else dt.today() - timedelta(days=7 * (-1))
        )
        mosad__score1, forgotenApprentice_Mosad1 = mosad_score(user.institution_id)
        apprenticeList = (
            db.session.query(Apprentice.name, Apprentice.last_name)
            .filter(Apprentice.id.in_(forgotenApprentice_Mosad1))
            .all()
        )
        apprenFOrgoten = ""
        for r in apprenticeList:
            apprenFOrgoten += r.name + " " + r.last_name + "\n"
        if apprenticeList==[] or apprenticeList is None:
            apprenFOrgoten+="אין חניכים נשכחים"
        add_task(
            user.id,
            "",
            forgotenApprentice_list,
            FORGOTTEN_APPRENTICE_DETAILS.format(user.name) + apprenFOrgoten,
            date.today(),
            "INSTITUTION",
            (
                TaskTubTypeEnum["PERSONAL"]
                if get_max_role(user.role_ids) == 1
                else TaskTubTypeEnum["GENERAL"]
            ),
            date.today(),

        )
    db.session.commit()


def add_notificaion_to_eshcol(user):
    institotionList = (
        db.session.query(Institution.id, Institution.name, Institution.cluster_id)
        .filter(Institution.cluster_id == user.cluster_id)
        .all()
    )
    eshcol_dict = dict()
    lowScore_mosdot = []
    no_MOsadEshcolMeeting = []
    for institution_ in institotionList:
        mosad__score1, forgotenApprentice_Mosad1 = mosad_score(institution_[0])
        if mosad__score1 < 65:
            lowScore_mosdot.append(institution_[1] +" - " +str(mosad__score1))
        mosadCoord_ = (
            db.session.query(User.id, User.name, User.last_name)
            .filter(User.role_ids.contains("1"), User.institution_id == institution_.id)
            .first()
        )
        if mosadCoord_ is not None:

            # MOsadEshcolMeeting_report
            visitEvent = (
                db.session.query(Report)
                .filter(
                    Report.user_id == user.id,
                    Report.ent_reported == mosadCoord_.id,
                    Report.title == report_model.MOsadEshcolMeeting_report,
                )
                .order_by(Report.visit_date.desc())
                .first()
            )
            if visitEvent is None or (date.today() - visitEvent.visit_date).days > 23:
                too_old = dt.today() - timedelta(days=23)
                res = (
                    db.session.query(Task)
                    .filter(
                        Task.user_id == user.id,
                        Task.created_at > too_old,
                        Task.name == report_model.MOsadEshcolMeeting_report,
                    )
                    .first()
                )

                if res is None:
                    date1 = (
                        user.association_date
                        if visitEvent is None
                        else dt.today() - timedelta(days=7 * (-1))
                    )

                    add_task(
                        user.id,
                        str(mosadCoord_.id),
                        report_model.MOsadEshcolMeeting_report,
                        MOSAD_ESCHOL_MEETING_DETAILS.format(
                            user.name, mosadCoord_.name + " " + mosadCoord_.last_name
                        ),
                        date1,
                        "INSTITUTION",
                        (
                            TaskTubTypeEnum["PERSONAL"]
                            if get_max_role(user.role_ids) == 2
                            else TaskTubTypeEnum["GENERAL"]
                        ),
                        visitEvent.visit_date if visitEvent else user.association_date

                    )
            # ציון מלווים
            melave_list = (
                db.session.query(User.id, User.name, User.last_name)
                .filter(
                    User.institution_id == institution_[0], User.role_ids.contains("0")
                )
                .all()
            )
            under65_dict = dict()
            for melave_ in melave_list:
                (
                    melave_score1,
                    call_gap_avg,
                    personal_meet_gap_avg,
                    group_meeting_gap_avg,
                ) = melave_score(melave_.id)
                if melave_score1 < 65:
                    under65_dict[institution_[1]] = under65_dict.get(
                        institution_[1], []
                    ) + [melave_.name]
        eshcol_dict[institution_[1]] = (
            eshcol_dict.get(institution_[1], []) + forgotenApprentice_Mosad1
        )

    # ישיבת  רכזים מלוים
    res = (
        db.session.query(Task)
        .filter(
            Task.user_id == user.id, Task.name == report_model.tochnitMeeting_report
        )
        .first()
    )
    too_old = dt.today() - timedelta(days=53)
    d = res.created_at if res else None
    if res is None or dt(d.year, d.month, d.day) < too_old:
        no_MOsadEshcolMeeting_str = ""
        for r in no_MOsadEshcolMeeting:
            no_MOsadEshcolMeeting_str += r.name + "\n"
        add_task(
            user.id,
            "",
            report_model.tochnitMeeting_report,
            TOCHNIT_MEETING_DETAILS.format(
                user.name,
            ),
            date.today(),
            "INSTITUTION",
            (
                TaskTubTypeEnum["PERSONAL"]
                if get_max_role(user.role_ids) == 2
                else TaskTubTypeEnum["GENERAL"]
            ),
            date.today()- timedelta(days=60),

        )

    # ציון מוסדות נמוך-הכנסה
    res = (
        db.session.query(Task)
        .filter(Task.user_id == user.id, Task.name == mosdot_score_list)
        .first()
    )
    too_old = dt.today() - timedelta(days=23)

    d = res.created_at if res else None
    if res is None or dt(d.year, d.month, d.day) < too_old:
        lowScore_mosdot_str = ""
        for r in lowScore_mosdot:
            lowScore_mosdot_str += r + "\n\n"
        add_task(
            user.id,
            "",
            mosdot_score_list,
            LOW_SCORE_MOSDOT_DETAILS.format(user.name) + lowScore_mosdot_str,
            date.today(),
            "INSTITUTION",
            (
                TaskTubTypeEnum["PERSONAL"]
                if get_max_role(user.role_ids) == 2
                else TaskTubTypeEnum["GENERAL"]
            ),
            date.today(),

        )
    inst_forgoten_dict = dict()
    res = (
        db.session.query(Task)
        .filter(Task.user_id == user.id, Task.name == forgotenApprentice_list)
        .first()
    )
    too_old = dt.today() - timedelta(days=8)
    d = res.created_at if res else None
    if res is None or dt(d.year, d.month, d.day) < too_old:
        for inst, appren in eshcol_dict.items():
            melave_appren_forgoten = dict()
            for appren1 in appren:
                Apprentice1 = (
                    db.session.query(Apprentice.accompany_id, Apprentice.name, Apprentice.last_name)
                    .filter(Apprentice.id == appren1)
                    .first()
                )

                user_name = (
                    db.session.query(User.name)
                    .filter(User.id == Apprentice1.accompany_id)
                    .first()
                )
                user_name_str = "לא ידוע"
                if user_name:
                    user_name_str = user_name.name
                melave_appren_forgoten[user_name_str] = (
                    melave_appren_forgoten.get(user_name_str, "")
                    + Apprentice1.name+" "+ Apprentice1.last_name
                    + ","
                )
            inst_forgoten_dict[inst] = melave_appren_forgoten
        inst_str = ""
        for inst, dict2 in inst_forgoten_dict.items():

            inst_str += str(inst)
            inst_str += ":\n"
            if dict2 == {}:
                inst_str = inst_str + "אין חניכים נשכחים\n\n"
                continue
            for melave, appren in dict2.items():
                inst_str += melave + ":\n"
                for a in appren.split(","):
                    inst_str += a + "\n"
                inst_str + "\n"
            inst_str + "\n\n"
        add_task(
            user.id,
            "",
            forgotenApprentice_list,
            FORGOTTEN_APPRENTICE_DETAILS.format(user.name) + str(inst_str),
            date.today(),
            "INSTITUTION",
            (
                TaskTubTypeEnum["PERSONAL"]
                if get_max_role(user.role_ids) == 2
                else TaskTubTypeEnum["GENERAL"]
            ),
            date.today(),

        )
    db.session.commit()


def add_notificaion_to_ahraiTohnit(user):
    lowScore_mosdot = dict()
    no_MOsadEshcolMeeting = []
    all_eshcols_forgoten = dict()
    eshcol_list = (
        db.session.query(Institution.cluster_id).distinct(Institution.cluster_id).all()
    )
    low_Score_eshcol_coord_str = ""
    for eshcol in eshcol_list:
        eshcolCoordinatorId = (
            db.session.query(User.id, User.name, User.last_name)
            .filter(User.role_ids.contains("2"), User.cluster_id == eshcol[0])
            .first()
        )
        eshcolCoordinator_score1 = 100
        if eshcolCoordinatorId:
            eshcolCoordinator_score1, avg__mosad_racaz_meeting_monthly = (
                eshcol_Coordinators_score(eshcolCoordinatorId.id)
            )
        if eshcolCoordinator_score1 < 65:
            low_Score_eshcol_coord_str += (
                eshcolCoordinatorId.name + " " + eshcolCoordinatorId.last_name + "\n"
            )
        if eshcolCoordinatorId is None:
            Cluster_ = (
                db.session.query(Cluster.name)
                .filter(
                    Cluster.id == eshcol[0],
                )
                .first()
            )
            low_Score_eshcol_coord_str += Cluster_.name + " " + "ללא רכז" + "\n"
        eshcol_forgoten = dict()
        institotionList = (
            db.session.query(Institution.id, Institution.name, Institution.cluster_id)
            .filter(Institution.cluster_id == eshcol.cluster_id)
            .all()
        )
        for institution_ in institotionList:
            mosad__score1, forgotenApprentice_Mosad1 = mosad_score(institution_[0])
            if mosad__score1 < 65:
                lowScore_mosdot[institution_.cluster_id] = lowScore_mosdot.get(
                    institution_.cluster_id, []
                ) + [institution_.name]
            mosadCoord_ = (
                db.session.query(User.id, User.name, User.last_name)
                .filter(
                    User.role_ids.contains("1"), User.institution_id == institution_.id
                )
                .first()
            )
            if mosadCoord_ is not None:
                visitEvent = (
                    db.session.query(Report)
                    .filter(
                        Report.user_id == user.id,
                        Report.ent_reported == mosadCoord_.id,
                        Report.title == report_model.tochnitMeeting_report,
                    )
                    .order_by(Report.visit_date.desc())
                    .first()
                )
                if (
                    visitEvent is None
                    or (date.today() - visitEvent.visit_date).days > 23
                ):
                    no_MOsadEshcolMeeting.append(mosadCoord_.name)
                # ציון מלווים
                melave_list = (
                    db.session.query(User.id, User.name, User.last_name)
                    .filter(
                        User.institution_id == institution_[0],
                        User.role_ids.contains("0"),
                    )
                    .all()
                )
                under65_dict = dict()
                for melave_ in melave_list:
                    (
                        melave_score1,
                        call_gap_avg,
                        personal_meet_gap_avg,
                        group_meeting_gap_avg,
                    ) = melave_score(melave_.id)
                    if melave_score1 < 65:
                        under65_dict[institution_[1]] = under65_dict.get(
                            institution_[1], []
                        ) + [melave_.name]
            eshcol_forgoten[institution_[1]] = (
                eshcol_forgoten.get(institution_[1], []) + forgotenApprentice_Mosad1
            )
        all_eshcols_forgoten[eshcol] = eshcol_forgoten

    # CLUSTER_COORD_LOW_SCORE_DETAILS
    res = (
        db.session.query(Task)
        .filter(Task.user_id == user.id, Task.name == low_score_65_list)
        .first()
    )
    too_old = dt.today() - timedelta(days=23)
    d = res.created_at if res else None
    if res is None or dt(d.year, d.month, d.day) < too_old:
        add_task(
            user.id,
            "",
            low_score_65_list,
            CLUSTER_COORD_LOW_SCORE_DETAILS.format(user.name)
            + low_Score_eshcol_coord_str,
            date.today(),
            "INSTITUTION",
            (
                TaskTubTypeEnum["PERSONAL"]
                if get_max_role(user.role_ids) == 3
                else TaskTubTypeEnum["GENERAL"]
            ),
            date.today(),

        )
    # LOW_SCORE_MOSDOT_DETAILS
    res = (
        db.session.query(Task)
        .filter(Task.user_id == user.id, Task.name == mosdot_score_list)
        .first()
    )
    # get clusters and institiotion as str
    lowScore_mosdot_str = ""
    for Cluster_id, insts in lowScore_mosdot.items():
        Cluster_ = (
            db.session.query(Cluster.name)
            .filter(
                Cluster.id == Cluster_id,
            )
            .first()
        )
        lowScore_mosdot_str += Cluster_.name + ":\n"
        for r in insts:
            lowScore_mosdot_str += r + "\n"
        lowScore_mosdot_str += "\n"
    too_old = dt.today() - timedelta(days=23)

    d = res.created_at if res else None
    if res is None or dt(d.year, d.month, d.day) < too_old:
        add_task(
            user.id,
            "",
            mosdot_score_list,
            LOW_SCORE_MOSDOT_DETAILS.format(user.name) + lowScore_mosdot_str,
            date.today(),
            "INSTITUTION",
            (
                TaskTubTypeEnum["PERSONAL"]
                if get_max_role(user.role_ids) == 3
                else TaskTubTypeEnum["GENERAL"]
            ),
            date.today(),

        )
    # FORGOTTEN_APPRENTICE_DETAILS
    res = (
        db.session.query(Task)
        .filter(Task.user_id == user.id, Task.name == forgotenApprentice_list)
        .first()
    )
    too_old = dt.today() - timedelta(days=8)

    d = res.created_at if res else None
    if res is None or dt(d.year, d.month, d.day) < too_old:
        eshcol_forgoten_dict = dict()
        for eshcol, list1 in all_eshcols_forgoten.items():
            inst_forgoten_dict = dict()
            for inst, appren in list1.items():
                melave_appren_forgoten = dict()
                for appren1 in appren:
                    Apprentice1 = (
                        db.session.query(Apprentice.accompany_id, Apprentice.name)
                        .filter(Apprentice.id == appren1)
                        .first()
                    )
                    user_name = (
                        db.session.query(User.name)
                        .filter(User.id == Apprentice1.accompany_id)
                        .first()
                    )
                    user_name_str = "לא ידוע"
                    if user_name:
                        user_name_str = user_name.name
                    melave_appren_forgoten[user_name_str] = (
                        melave_appren_forgoten.get(user_name_str, "")
                        + Apprentice1.name
                        + ","
                    )
                inst_forgoten_dict[inst] = melave_appren_forgoten
            eshcol_forgoten_dict[eshcol[0]] = inst_forgoten_dict
        forgoten_str = ""
        for eshcol, dict2 in eshcol_forgoten_dict.items():
            Cluster_ = (
                db.session.query(Cluster.name)
                .filter(
                    Cluster.id == eshcol,
                )
                .first()
            )
            forgoten_str += Cluster_.name + ":\n"
            for inst, dict3 in dict2.items():
                forgoten_str += inst + ":"
                forgoten_str +="\n"
                for melave, appren in dict3.items():
                    forgoten_str += melave + ":" + appren + "\n"
                forgoten_str += "\n"
            forgoten_str += "\n"
        add_task(
            user.id,
            "",
            forgotenApprentice_list,
            FORGOTTEN_APPRENTICE_DETAILS.format(user.name) + str(forgoten_str),
            date.today(),
            "INSTITUTION",
            (
                TaskTubTypeEnum["PERSONAL"]
                if get_max_role(user.role_ids) == 3
                else TaskTubTypeEnum["GENERAL"]
            ),
            date.today(),

        )
        db.session.commit()


def add_task(
    user_id: str,
    subject: str,
    event: str,
    details: str,
    task_date,
    subject_type,
    task_tub_type,
last_time_done_
):
    if user_id==subject:
        Visit1 = Report(
                    created_at=arrow.now().format("YYYY-MM-DDThh:mm:ss"),
                    user_id=user_id,
                    ent_reported=str(subject),
                    visit_in_army=(
                        True
                        if event == report_model.basis_report
                        else False
                    ),
                    visit_date=datetime.fromisoformat(str(task_date)),
                    allreadyread=False,
                    id=uuid.uuid4(),
                    title=event,
                    attachments=None,
                    ent_group=None,
                    description=None,
                )
        db.session.add(Visit1)
    else:
        #insure no 2 same 2 tasks
        db.session.query(Task).filter(Task.user_id == user_id,Task.subject_id==str(subject),Task.name==event).delete()
        task = Task(
            id=uuid.uuid4(),
            subject_type=subject_type,
            user_id=user_id,
            subject_id=subject,
            name=event,
            description=details,
            start_date=to_iso(
                task_date
            ),  # because we always push to table 7 days before start of task
            created_at=arrow.now().format("YYYY-MM-DDThh:mm:ss"),
            has_been_read=False,
            tub_type=task_tub_type.name,
            last_time_done=last_time_done_,
            status=TaskStatusEnum.TODO
        )
        db.session.add(task)
        #if user is the subject make  it as  done


def add_next_task_to_table(noti):
    next_date = None
    if noti.end_date > dt.today():  # insure end date is not today
        if noti.frequency.repeat_type.name == "DAILY":  # schedule next run
            next_date = dt.today() - timedelta(days=(-1))
        if (
            noti.frequency.repeat_type.name == "WEEKLY"
            and noti.frequency.repeat_count > 0
        ):
            next_date = dt.today() - timedelta(days=7 * (-1))
            for (
                weekday_
            ) in noti.frequency.weekdays.name:  # comupute closet day from list
                weekday_number = TaskFrequencyWeekdayEnum[weekday_].value
                candidant_date = dt.today() + timedelta(
                    (weekday_number - dt.today().weekday()) % 7
                )
                if next_date > candidant_date:
                    next_date = candidant_date
        if noti.frequency.repeat_type.name == "MONTHLY":
            next_date = dt.today() - timedelta(days=30 * (-1))
        if noti.frequency.repeat_type.name == "YEARLY":
            next_date = dt.today() - timedelta(days=365 * (-1))
        if next_date:
            task_service = get_task_service()
            task_data = task_service._task_to_data(noti)
            task_data.frequency.repeat_count = task_data.frequency.repeat_count - 1
            task_data.id = uuid.uuid4()
            # task_service._update_frequency(noti, task_data.frequency)
            new_task_dict = task_service.create_task(task_data)
            logger.debug(f"Created new task with id {new_task_dict['id']}")


def add_tasks_to_table(user):
    user_ent = (
        db.session.query(
            User.role_ids,
            User.institution_id,
            User.cluster_id,
            User.id,
            User.name,
            User.association_date,
        )
        .filter(User.id == user)
        .first()
    )
    if "0" in user_ent[0]:  # melave
        add_notificaion_to_melave(user_ent)
    if "1" in user_ent[0]:  # mosad
        add_notificaion_to_mosad(user_ent)
    if "2" in user_ent[0]:  # eshcol
        add_notificaion_to_eshcol(user_ent)
    if "3" in user_ent[0]:  # ahrah
        add_notificaion_to_ahraiTohnit(user_ent)



def get_max_role(roles_str):
    roles_list = roles_str.split(",")
    roles_list_int = [int(r) for r in roles_list]
    return max(roles_list_int)


