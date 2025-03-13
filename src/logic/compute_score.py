import csv
from io import StringIO

from flask import Blueprint, request, jsonify
from http import HTTPStatus
from datetime import datetime, date, timedelta

from pyluach import dates
from sqlalchemy import func, or_

from src.logic.performence_metric import (
    compute_visit_score,
    compute_group_visit_score,
    compute_simple_visit_score,
    forgotenApprentice_Mosad,
)
from src.models import report_model
from src.models.madadim_setting_model import MadadimSetting
from src.routes.utils.hebrw_date_cust import start_of_year_greg_date, num_of_rivon_passed, num_of_shlish_passed

from src.services import db
from src.models.apprentice_model import Apprentice

from src.models.user_model import User
from src.models.report_model import Report


def mosad_score(institution_id):
    melaveScore_wight = 72
    mosad_Coordinators_score_wight = 7
    forgtenAppren_wight = 16.6
    bogrim_wight = 3

    mosad_score = 0
    try:
        mosadCoord_id = (
            db.session.query(User.id)
            .filter(User.role_ids.contains("1"), User.institution_id == institution_id)
            .first()
        )
        all_Mosad_Melave = (
            db.session.query(User.id)
            .filter(User.role_ids.contains("0"), User.institution_id == institution_id)
            .all()
        )
        all_Mosad_apprentices = (
            db.session.query(Apprentice.id)
            .filter(Apprentice.institution_id == institution_id)
            .all()
        )

        if len(all_Mosad_Melave) == 0:
            return 100, []
        all_Mosad_Melaves_list = [r[0] for r in all_Mosad_Melave]
        total_melave_score = 0
        # melave score
        for melaveId in all_Mosad_Melaves_list:
            total_melave_score += melave_score(melaveId)[0]

        total_melave_score = total_melave_score / len(all_Mosad_Melaves_list)
        mosad_score += melaveScore_wight * total_melave_score / 100
        # mosad coordinator score
        (
            mosad_Coordinators_score1,
            visitprofessionalMeet_melave_avg,
            avg_matzbarMeeting_gap,
            total_avg_call,
            total_avg_meet,
            groupNeeting_gap_avg,
        ) = mosad_Coordinators_score(mosadCoord_id[0])
        mosad_score += mosad_Coordinators_score_wight * mosad_Coordinators_score1 / 100

        # forgoten apppre
        forgoten_Apprentice_count = forgotenApprentice_Mosad(institution_id, False)[
            0
        ].json
        mosad_score += (
            forgtenAppren_wight
            * (len(all_Mosad_apprentices) - len(forgoten_Apprentice_count))
            / len(all_Mosad_apprentices)
            if len(all_Mosad_apprentices) != 0
            else 16.6
        )

        # עשייה_לבוגרים=5
        too_old = datetime.today() - timedelta(days=365)
        visit_did_for_apprentice = (
            db.session.query(
                Report.user_id,
            )
            .filter(
                Report.title.in_(report_model.report_as_DoForBogrim),
                Report.user_id == mosadCoord_id[0],
                Report.visit_date > too_old,
            )
            .distinct(Report.id)
            .all()
        )

        mosad_score += (
            len(visit_did_for_apprentice)
            if len(visit_did_for_apprentice) <= bogrim_wight
            else bogrim_wight
        )
        return mosad_score, forgoten_Apprentice_count
    except Exception as e:
        print(str(e))
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST


def melave_score(melaveId):
    try:
        call_wight = 20
        presonalMeet_wight = 20
        groupMeet_wight = 20
        cenes_wight = 5
        proffesional_wight = 5
        horim_wight = 10
        monthlyYeshiva_wight = 10
        basis_wight = 10
        madadim_setting1 = db.session.query(MadadimSetting).first()
        association_date = (
            db.session.query(User.association_date).filter(User.id == melaveId).first()
        )
        association_date_gap = (date.today() - association_date.association_date).days if association_date.association_date else 0
        # compute score diagram
        all_melave_Apprentices = (
            db.session.query(Apprentice.id)
            .filter(Apprentice.accompany_id == melaveId)
            .all()
        )
        if len(all_melave_Apprentices) == 0:
            return 100, 0, 0, 0
        # call_score
        visitcalls = (
            db.session.query(Report.ent_reported, Report.visit_date)
            .filter(
                Report.title.in_(report_model.reports_as_call),
                Report.user_id == melaveId,
                Report.visit_date > madadim_setting1.call_madad_date,
            )
            .order_by(Report.visit_date)
            .all()
        )
        call_score, call_gap_avg = compute_visit_score(
            all_melave_Apprentices, visitcalls, call_wight, 21, melaveId
        )
        # personal_meet_score
        visitmeetings = (
            db.session.query(Report.ent_reported, Report.visit_date)
            .filter(
                Report.title.in_(report_model.report_as_meet),
                Report.user_id == melaveId,
                Report.visit_date > madadim_setting1.meet_madad_date,
            )
            .order_by(Report.visit_date)
            .all()
        )
        personal_meet_score, personal_meet_gap_avg = compute_visit_score(
            all_melave_Apprentices, visitmeetings, presonalMeet_wight, 90, melaveId
        )

        # group_meeting
        group_meeting = (
            db.session.query(
                Report.ent_reported, func.max(Report.visit_date).label("visit_date")
            )
            .group_by(Report.ent_reported)
            .filter(
                Report.title == report_model.groupMeet_report,
                Report.user_id == melaveId,
                Report.visit_date > madadim_setting1.groupMeet_madad_date,
            )
            .all()
        )
        group_meeting_score, group_meeting_gap_avg = compute_group_visit_score(
            group_meeting, groupMeet_wight, 90, melaveId
        )
        # professional_2monthly
        professional_2monthly = (
            db.session.query(
                Report.user_id, func.max(Report.visit_date).label("visit_date")
            )
            .group_by(Report.user_id)
            .filter(
                Report.title == report_model.professional_report,
                Report.ent_reported == melaveId,
            )
            .first()
        )
        professional_2monthly_score = compute_simple_visit_score(
            professional_2monthly, proffesional_wight, 60, melaveId, None
        )
        # _yearly_cenes

        start_Of_year = start_of_year_greg_date()
        newvisit_cenes = (
            db.session.query(Report.user_id)
            .filter(
                Report.user_id == melaveId,
                Report.title == report_model.cenes_report,
                Report.visit_date > start_Of_year,
            )
            .all()
        )

        # yeshiva_monthly
        yeshiva_monthly = (
            db.session.query(
                Report.user_id, func.max(Report.visit_date).label("visit_date")
            )
            .group_by(Report.user_id)
            .filter(
                Report.title == report_model.MelavimMeeting_report,
                Report.ent_reported == melaveId,
            )
            .first()
        )
        yeshiva_monthly_score = cenes_yearly_score = compute_simple_visit_score(
            yeshiva_monthly,
            monthlyYeshiva_wight,
            31,
            melaveId,
            report_model.MelavimMeeting_report,
        )

        # Horim_meetingr.
        all_melave_Apprentices_ids=[r.id for r in all_melave_Apprentices]
        start_of_year_greg_date_=start_of_year_greg_date()
        Horim_meeting_score = 0
        Horim_meeting = (
            db.session.query(Report.ent_reported)
            .filter(
                Report.title == report_model.HorimCall_report,
                Report.user_id == melaveId,
                Report.visit_date>=start_of_year_greg_date_,
                Report.ent_reported.in_(all_melave_Apprentices_ids)
            )
            .distinct(Report.ent_reported)
            .all()
        )
        if Horim_meeting:
            Horim_meeting_score = (
                len(Horim_meeting) / len(all_melave_Apprentices)
            ) * horim_wight

        # base_meeting
        base_meeting = (
            db.session.query(Report.visit_date)
            .distinct(Report.visit_date)
            .filter(
                Report.title == report_model.basis_report,
                Report.visit_in_army == True,
                Report.visit_date > start_Of_year,
                Report.user_id == melaveId,
            )
            .group_by(Report.visit_date)
            .count()
        )
        base_meeting_score = 0
        if (
            base_meeting and base_meeting >= num_of_rivon_passed()
        ) or association_date_gap < 120:
            base_meeting_score += basis_wight

        melave_score = (
            base_meeting_score
            + Horim_meeting_score
            + professional_2monthly_score
            + yeshiva_monthly_score
            + cenes_yearly_score
            + group_meeting_score
            + personal_meet_score
            + call_score
        )
        return melave_score, call_gap_avg, personal_meet_gap_avg, group_meeting_gap_avg
    except Exception as e:
        print(str(e))


def mosad_Coordinators_score(mosadCoord_id):
    melaveScore_wight = 30
    matzbar_wight = 30
    proffesional_wight = 10
    monthlyYeshiva_wight = 10
    hazana_wight = 10
    ahraiYeshva_wight = 5
    bogrim_wight = 5

    madadim_setting1 = db.session.query(MadadimSetting).first()

    try:
        user_prof = (
            db.session.query(User.institution_id, User.association_date)
            .filter(User.id == mosadCoord_id)
            .first()
        )
        all_Mosad_Melave = (
            db.session.query(User.id)
            .filter(User.role_ids.contains("0"), User.institution_id == user_prof[0])
            .all()
        )

        if len(all_Mosad_Melave) == 0:
            return 100, 0, 0, 0, 0, 0
        all_Mosad_Melaves_ids = [r[0] for r in all_Mosad_Melave]

        total_melave_score = 0
        Mosad_coord_score = 0
        personal_meet_gap_avg_total = 0
        call_gap_avg_total = 0
        group_meeting_gap_avg_total = 0
        # avg call,meet from all melaves
        for melaveId in all_Mosad_Melaves_ids:
            (
                melave_score1,
                call_gap_avg,
                personal_meet_gap_avg,
                group_meeting_gap_avg,
            ) = melave_score(melaveId)
            total_melave_score += melave_score1
            personal_meet_gap_avg_total += personal_meet_gap_avg
            call_gap_avg_total += call_gap_avg
            group_meeting_gap_avg_total += group_meeting_gap_avg

        total_melave_score = total_melave_score / len(all_Mosad_Melaves_ids)
        personal_meet_gap_avg_total = personal_meet_gap_avg_total / len(
            all_Mosad_Melaves_ids
        )
        call_gap_avg_total = call_gap_avg_total / len(all_Mosad_Melaves_ids)
        group_meeting_gap_avg_total = group_meeting_gap_avg_total / len(
            all_Mosad_Melaves_ids
        )

        # interaction=30
        Mosad_coord_score += melaveScore_wight * total_melave_score / 100
        # מצבר==20
        visit_matzbar_meetings = (
            db.session.query(Report.ent_reported, Report.visit_date)
            .filter(
                Report.visit_date > madadim_setting1.matzbarmeet_madad_date,
                Report.title == report_model.matzbar_report,
            )
            .filter(Report.ent_reported.in_(list(all_Mosad_Melaves_ids)))
            .order_by(Report.visit_date)
            .all()
        )
        visit_matzbar_meetings_score, visitMatzbar_melave_avg = compute_visit_score(
            all_Mosad_Melave,
            visit_matzbar_meetings,
            matzbar_wight,
            90,
            mosadCoord_id,
        )
        Mosad_coord_score += visit_matzbar_meetings_score
        # מפגש_מקצועי=10
        visit_mosad_professional_meetings = (
            db.session.query(Report.ent_reported, Report.visit_date)
            .filter(
                Report.visit_date > madadim_setting1.professionalMeet_madad_date,
                Report.title == report_model.professional_report,
            )
            .filter(Report.ent_reported.in_(list(all_Mosad_Melaves_ids)))
            .order_by(Report.visit_date)
            .all()
        )
        visit_mosad_professional_meetings_score, visitprofessionalMeet_melave_avg = (
            compute_visit_score(
                all_Mosad_Melave,
                visit_mosad_professional_meetings,
                proffesional_wight,
                90,
                mosadCoord_id,
            )
        )
        Mosad_coord_score += visit_mosad_professional_meetings_score

        # ישיבת_מלוים=10
        todays_Month = dates.HebrewDate.today().month
        if todays_Month == 2 or todays_Month == 6 or todays_Month == 8:
            Mosad_coord_score += 10  # nisan ,Av and Tishrey dont compute
            Mosad_coord_score += 5  # precence of melavim
        else:
            visit_mosad_yeshiva = (
                db.session.query(Report.ent_reported, Report.visit_date)
                .filter(
                    Report.visit_date > madadim_setting1.eshcolMosadMeet_madad_date,
                    Report.title == report_model.MelavimMeeting_report,
                )
                .filter(Report.ent_reported.in_(list(all_Mosad_Melaves_ids)))
                .order_by(Report.visit_date)
                .all()
            )
            visit_mosad_yeshiva_score, visitprofessionalMeet_melave_avg = (
                compute_visit_score(
                    all_Mosad_Melave,
                    visit_mosad_yeshiva,
                    monthlyYeshiva_wight,
                    30,
                    mosadCoord_id,
                )
            )
            Mosad_coord_score += visit_mosad_professional_meetings_score

        # עשייה_לבוגרים=5
        d = user_prof.association_date
        association_date_converted = datetime(d.year, d.month, d.day)
        gap_since_created = (datetime.today() - association_date_converted).days
        too_old = start_of_year_greg_date()
        visit_did_for_apprentice = (
            db.session.query(
                Report.user_id,
            )
            .filter(
                Report.title.in_(report_model.report_as_DoForBogrim),
                Report.user_id == mosadCoord_id,
                Report.visit_date > too_old,
            )
            .all()
        )
        if (
            len(visit_did_for_apprentice) >= num_of_shlish_passed()
            or gap_since_created < 120
        ):
            Mosad_coord_score += bogrim_wight

        # ישיבה אחראי תוכנית=5
        too_old = datetime.today() - timedelta(days=31)
        is_tochnitMeeting_exist = (
            db.session.query(
                Report.user_id,
            )
            .filter(
                Report.title == report_model.tochnitMeeting_report,
                Report.visit_date > too_old,
            )
            .first()
        )
        tochnitMeeting_report1 = (
            db.session.query(
                Report.user_id,
            )
            .filter(
                Report.title == report_model.tochnitMeeting_report,
                Report.ent_reported == mosadCoord_id,
                Report.visit_date > too_old,
            )
            .first()
        )
        if not is_tochnitMeeting_exist or tochnitMeeting_report1:
            Mosad_coord_score += ahraiYeshva_wight

        # הזנת_מחזור_חדש=10
        too_old = datetime.today() - timedelta(days=365)
        visit_Hazana_new_THsession = (
            db.session.query(
                Report.user_id, func.max(Report.visit_date).label("visit_date")
            )
            .group_by(Report.user_id)
            .filter(
                Report.title == report_model.hazanatMachzor_report,
                Report.user_id == mosadCoord_id,
                Report.visit_date > too_old,
            )
            .all()
        )
        start_Of_year = start_of_year_greg_date()
        d = user_prof.association_date
        if (
            datetime(d.year, d.month, d.day) > start_Of_year
            or len(visit_Hazana_new_THsession) >= 1
        ):
            Mosad_coord_score += hazana_wight
        return (
            Mosad_coord_score,
            int(visitprofessionalMeet_melave_avg),
            int(visitMatzbar_melave_avg),
            int(call_gap_avg_total),
            int(personal_meet_gap_avg_total),
            int(group_meeting_gap_avg_total),
        )
    except Exception as e:
        print(str(e))
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST


def eshcol_Coordinators_score(eshcolCoord_id):
    eshcol = (
        db.session.query(User.cluster_id).filter(User.id == eshcolCoord_id).first()[0]
    )
    all_eshcol_mosadCoord = (
        db.session.query(User.id)
        .filter(User.role_ids.contains("1"), User.cluster_id == eshcol)
        .all()
    )
    all_eshcol_apprentices = (
        db.session.query(Apprentice.id).filter(Apprentice.cluster_id == eshcol).all()
    )
    if len(all_eshcol_mosadCoord) == 0:
        return 100, 0
    madadim_setting1 = db.session.query(MadadimSetting).first()

    all_eshcol_mosadCoord_list = [r[0] for r in all_eshcol_mosadCoord]
    visit_MOsadEshcolMeeting_report = (
        db.session.query(Report.ent_reported, Report.visit_date)
        .filter(
            Report.user_id == eshcolCoord_id,
            Report.title == report_model.MOsadEshcolMeeting_report,
            Report.visit_date > madadim_setting1.eshcolMosadMeet_madad_date,
        )
        .all()
    )
    MOsadEshcolMeeting_score, MOsadEshcolMeeting_avg = compute_visit_score(
        all_eshcol_mosadCoord, visit_MOsadEshcolMeeting_report, 60, 30, eshcolCoord_id
    )
    # tochnitMeeting_report
    too_old = datetime.today() - timedelta(days=31)
    is_tochnitMeeting_exist = (
        db.session.query(
            Report.user_id,
        )
        .filter(
            Report.title == report_model.tochnitMeeting_report,
            Report.visit_date > too_old,
        )
        .first()
    )
    tohnit_yeshiva = (
        db.session.query(
            Report.ent_reported, func.max(Report.visit_date).label("visit_date")
        )
        .group_by(Report.ent_reported)
        .filter(
            Report.title == report_model.tochnitMeeting_report,
            Report.ent_reported == eshcolCoord_id,
        )
        .first()
    )
    gap = (
        (date.today() - tohnit_yeshiva.visit_date).days
        if tohnit_yeshiva is not None
        else 100
    )
    tohnit_yeshiva_score = 0
    if not is_tochnitMeeting_exist or gap < 30:
        tohnit_yeshiva_score += 40
    # forgoten apprentice
    Apprentice_ids_forgoten = [r[0] for r in all_eshcol_apprentices]
    too_old = datetime.today() - timedelta(days=100)
    Oldvisitcalls = (
        db.session.query(Report.ent_reported)
        .filter(
            Apprentice.id == Report.ent_reported,
            eshcol == Apprentice.cluster_id,
            or_(
                Report.title == report_model.call_report,
                Report.title == report_model.groupMeet_report,
                Report.title == report_model.personalMeet_report,
            ),
            Report.visit_date > too_old,
        )
        .all()
    )
    for i in Oldvisitcalls:
        if i[0] in Apprentice_ids_forgoten:
            Apprentice_ids_forgoten.remove(i[0])
    eshcolCoord_score = tohnit_yeshiva_score + MOsadEshcolMeeting_score

    return eshcolCoord_score, MOsadEshcolMeeting_avg
