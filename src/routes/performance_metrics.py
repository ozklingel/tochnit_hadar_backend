import csv
from io import StringIO

from flask import Blueprint, request, jsonify
from http import HTTPStatus
from datetime import datetime, date, timedelta

from sqlalchemy import func, or_

from src.logic.compute_score import (
    melave_score,
    mosad_Coordinators_score,
    eshcol_Coordinators_score,
    mosad_score,
)
from src.logic.home_page import (
    red_green_orange_status,
    get_Eshcol_corrdintors_score,
    get_mosad_Coordinators_score,
    get_melave_score,
)
from src.logic.performence_metric import (
    report_status_apprentice,
    report_status_apprentice_mosad,
    compute_forgoten_apprectice,
    fetch_Diagram_monthly,
    fetch_Diagram_rivonly,
    fetch_Diagram_yearly,
    melave_professional_meet_,
    get_cenes_score,
    apprentice_old_horim,
    forgoten_apprentice_full_details,
    no_melave_interaction,
    no_apprentice_interaction,
    no_mosad_coordinator_interaction,
    apprentice_old_intercation,
    report_status_apprentice_priod,
    report_status_apprentice_priod_mosad,
)
from src.models import report_model, system_report_model
from src.models.madadim_setting_model import MadadimSetting
from src.models.models_utils import to_iso
from src.routes.institutions import get_institution_list
from src.routes.utils.hebrw_date_cust import start_of_year_greg_date, num_of_rivon_passed
from src.services import db
from src.models.apprentice_model import Apprentice

from src.models.institution_model import Institution
from src.models.system_report_model import SystemReport
from src.models.user_model import User
from src.models.report_model import Report

madadim_form_blueprint = Blueprint(
    "performance_metrics", __name__, url_prefix="/performance_metrics"
)


@madadim_form_blueprint.route("/melave", methods=["GET"])
def melave():
    try:

        melaveId = request.args.get("melaveId")
        user_ent = (
            db.session.query(
                User.association_date,
            )
            .filter(User.id == melaveId)
            .first()
        )
        Apprentice_melaveId = (
            db.session.query(Apprentice.id, Apprentice.accompany_id)
            .filter(Apprentice.accompany_id == melaveId)
            .all()
        )
        start_Of_year = start_of_year_greg_date()
        numOfQuarter_passed = num_of_rivon_passed()
        ######call#######
        apprentice_old_call_ = apprentice_old_intercation(
            Apprentice_melaveId, True, report_model.reports_as_call
        )
        ########meet personal#########
        apprentice_old_meet_ = apprentice_old_intercation(
            Apprentice_melaveId, True, report_model.report_as_meet
        )
        # professional_report
        Proffesional_meet_score, Proffesional_meet_report = melave_professional_meet_(
            melaveId
        )
        ###### cenes_report#####3
        cenes_score, cenes_since_start_Of_year, cenes_reports = get_cenes_score(
            melaveId
        )
        ####### HorimCall_report##########3
        Apprentice_old_Horim = [r[0] for r in Apprentice_melaveId]
        Apprentice_old_Horim = apprentice_old_horim(Apprentice_old_Horim, melaveId)
        program_start_date = date.today() - user_ent.association_date
        ######meetInArmy#######
        base_visit_report = (
            db.session.query(Report.ent_reported, Report.visit_date)
            .distinct(Report.visit_date)
            .filter(
                Report.user_id == melaveId,
                Report.title.in_(report_model.report_as_meet),
                Report.visit_in_army == True,
                Report.visit_date > start_Of_year,
            )
            .all()
        )
        ###forgeoten-no reports_as_call###
        too_old = datetime.today() - timedelta(days=100)
        apprentice_melave_forgoten = (
            db.session.query(
                Apprentice.id,
                Institution.name.label("Institution_name"),
                Apprentice.association_date,
            )
            .filter(
                Apprentice.institution_id == Institution.id,
                Apprentice.accompany_id == melaveId,
                Apprentice.association_date < too_old,
            )
            .all()
        )

        forgoten_apprentice_per_insti, total_forgoten, ids_no_visit = (
            compute_forgoten_apprectice(apprentice_melave_forgoten)
        )

        forgotenApprentice_full_details = forgoten_apprentice_full_details(ids_no_visit)
        melave_score1, call_gap_avg, meet_gap_avg, group_meeting_gap_avg = melave_score(
            melaveId
        )
        ######group_meeting####
        madadim_setting1 = db.session.query(MadadimSetting).first()

        group_meeting = (
            db.session.query(Report.ent_reported, Report.visit_date)
            .filter(
                Report.title == report_model.groupMeet_report,
                Report.user_id == melaveId,
                Report.visit_date > madadim_setting1.groupMeet_madad_date,
            )
            .all()
        )
        last_group_meeting = user_ent.association_date
        for meeting in group_meeting:
            if meeting.visit_date > last_group_meeting:
                last_group_meeting = meeting.visit_date
        last_group_meeting_gap = date.today() - last_group_meeting
        return (
            jsonify(
                {
                    "call_gap_avg_expected": 21,
                    "meet_gap_avg_expected": 90,
                    "last_group_meeting": last_group_meeting_gap.days,
                    "group_meeting_done": len(group_meeting) if group_meeting else 0,
                    "group_meeting_todo": int(program_start_date.days / 60),
                    "visit_meeting_army_todo": 3 - len(base_visit_report),
                    "program_start_date_passed": program_start_date.days,
                    "melave_score": melave_score1,
                    "numOfApprentice": len(Apprentice_melaveId),
                    "visitcalls": len(Apprentice_melaveId) - len(apprentice_old_call_),
                    "visitmeetings": len(Apprentice_melaveId)
                    - len(apprentice_old_meet_),
                    "numOfQuarter_passed": numOfQuarter_passed,
                    "sadna_todo": numOfQuarter_passed,
                    "sadna_done": len(Proffesional_meet_report),
                    "sadna_percent": Proffesional_meet_score,
                    "cenes_2year": len(cenes_since_start_Of_year),
                    "newvisit_cenes": len(cenes_reports),
                    "cenes_percent": cenes_score,
                    "visitHorim": len(Apprentice_melaveId) - len(Apprentice_old_Horim),
                    "forgotenApprenticeCount": len(ids_no_visit),
                    "new_visitmeeting_Army": len(base_visit_report),
                    "call_gap_avg": call_gap_avg,
                    "meet_gap_avg": meet_gap_avg,
                    "forgotenApprentice_full_details": forgotenApprentice_full_details,
                    "visitCall_monthlyGap_avg": fetch_Diagram_monthly(
                        melaveId, system_report_model.visitcalls_melave_avg
                    ),
                    "visitMeeting_monthlyGap_avg": fetch_Diagram_monthly(
                        melaveId, system_report_model.visitmeets_melave_avg
                    ),
                    "forgotenApprentice_rivonly": fetch_Diagram_rivonly(
                        melaveId, system_report_model.forgotenApprentice_cnt_melave
                    ),
                    "visitsadna_presence": fetch_Diagram_rivonly(
                        melaveId, system_report_model.proffesionalMeet_presence_melave
                    ),
                    "visitCenes_4_yearly_presence": fetch_Diagram_yearly(
                        melaveId, system_report_model.cenes_presence_melave
                    ),
                    "visitHorim_4_yearly": fetch_Diagram_yearly(
                        melaveId, system_report_model.horim_meeting_melave
                    ),
                }
            ),
            HTTPStatus.OK,
        )
    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST


@madadim_form_blueprint.route("/mosad_coordinator", methods=["GET"])
def mosad_coordinator(mosadCoordinator="empty"):
    try:
        if mosadCoordinator == "empty":
            mosadCoordinator = request.args.get("mosadCoordinator")
        current_month = datetime.today().month
        numOfQuarter_passed = int(current_month / 3)
        institutionId = (
            db.session.query(User.institution_id)
            .filter(User.id == mosadCoordinator)
            .first()
        )
        if institutionId:
            institutionId=institutionId.institution_id
        else:
            return jsonify({"result": str("no such mosad coordinator")}), HTTPStatus.BAD_REQUEST

        all_Melave = (
            db.session.query(User.id)
            .filter(User.role_ids.contains("0"), User.institution_id == institutionId)
            .all()
        )
        # professional_report
        Melaves_old_professional = no_melave_interaction(
            all_Melave, institutionId, report_model.professional_report, 90
        )
        # matzbar_report
        old_Melave_ids_matzbar = no_melave_interaction(
            all_Melave, institutionId, report_model.matzbar_report, 60
        )
        # groupMeet
        melave_old_groupMeet = no_apprentice_interaction(
            all_Melave, institutionId, report_model.groupMeet_report, 60
        )
        # call
        all_apprenties_mosad = (
            db.session.query(
                Apprentice.id,
                Apprentice.accompany_id,
                Institution.name.label("Institution_name"),
                Apprentice.association_date,
            )
            .filter(
                Apprentice.institution_id == institutionId,
                Institution.id == Apprentice.institution_id,
            )
            .all()
        )
        old_apprenties_mosad_old_call = apprentice_old_intercation(
            all_apprenties_mosad, True, report_model.reports_as_call
        )
        # meet personal
        old_apprenties_mosad_old_meet = apprentice_old_intercation(
            all_apprenties_mosad, True, report_model.report_as_meet
        )
        # hazanatMachzor_report
        too_old = datetime.today() - timedelta(days=365)
        isVisitenterMahzor = False
        visitenterMahzor = (
            db.session.query(Report.visit_date)
            .filter(
                Report.user_id == mosadCoordinator,
                Report.title == report_model.hazanatMachzor_report,
                Report.visit_date > too_old,
            )
            .all()
        )
        if visitenterMahzor:
            isVisitenterMahzor = True
        # DoForBogrim
        too_old = datetime.today() - timedelta(days=365)
        visitDoForBogrim = (
            db.session.query(Report.visit_date, Report.title, Report.description)
            .filter(
                Report.user_id == mosadCoordinator,
                Report.title.in_(report_model.report_as_DoForBogrim),
                Report.visit_date > too_old,
            )
            .distinct(Report.id)
            .all()
        )
        # MelavimMeeting
        old_Melave_ids_MelavimMeeting = no_melave_interaction(
            all_Melave, institutionId, report_model.MelavimMeeting_report, 120
        )
        # forgoten apprentice

        forgoten_apprentice_per_insti, total_forgoten, ids_no_visit = (
            compute_forgoten_apprectice(all_apprenties_mosad)
        )
        forgotenApprentice_full_details = forgoten_apprentice_full_details(ids_no_visit)

        (
            mosad_Coordinators_score1,
            visitprofessionalMeet_melave_avg,
            avg_matzbarMeeting_gap,
            total_avg_call,
            total_avg_meet,
            total_avg_groupmeet,
        ) = mosad_Coordinators_score(mosadCoordinator)
        mosad__score1, forgotenApprentice_Mosad1 = mosad_score(institutionId)
        return (
            jsonify(
                {
                    "mosad_score": mosad__score1,
                    "mosadCoordinator_score": mosad_Coordinators_score1,
                    "all_apprenties_mosad": len(all_apprenties_mosad),
                    "numOfQuarter_passed": numOfQuarter_passed,
                    "all_Melave_mosad_count": len(all_Melave),
                    "good_apprenties_mosad_call": len(all_apprenties_mosad)
                    - len(old_apprenties_mosad_old_call),
                    "good_apprenties_mosad_meet": len(all_apprenties_mosad)
                    - len(old_apprenties_mosad_old_meet),
                    "good_apprentice_mosad_groupMeet": len(all_Melave)
                    - len(melave_old_groupMeet),
                    "good_Melave_ids_sadna": len(all_Melave)
                    - len(Melaves_old_professional),
                    "good_Melave_ids_matzbar": len(all_Melave)
                    - len(old_Melave_ids_matzbar),
                    "visitprofessionalMeet_melave_avg": visitprofessionalMeet_melave_avg,
                    "avg_matzbarMeeting_gap": avg_matzbarMeeting_gap,
                    "avg_apprenticeCall_gap": total_avg_call,
                    "avg_apprenticeMeeting_gap": total_avg_meet,
                    "avg_groupMeeting_gap": total_avg_groupmeet,
                    "isVisitenterMahzor": isVisitenterMahzor,
                    "visitDoForBogrim": len(visitDoForBogrim),
                    "new_MelavimMeeting": len(all_Melave)
                    - len(old_Melave_ids_MelavimMeeting),
                    "MelavimMeeting_todo": numOfQuarter_passed * 3,
                    "Apprentice_forgoten_count": total_forgoten,
                    "forgotenApprentice_full_details": forgotenApprentice_full_details,
                    "visitDoForBogrim_list": [
                        {
                            "visit_date": to_iso(row[0]),
                            "title": row[1],
                            "description": row[2],
                            "daysFromNow": (date.today() - row[0]).days,
                        }
                        for row in visitDoForBogrim
                    ],
                    "avg_presence_professionalMeeting_monthly": fetch_Diagram_monthly(
                        mosadCoordinator,
                        system_report_model.proffesionalMeet_presence_mosad,
                    ),
                    "avg_matzbarMeeting_gap_monthly": fetch_Diagram_monthly(
                        mosadCoordinator, system_report_model.matzbarMeeting_gap_mosad
                    ),
                    "avg_apprenticeCall_gap_monthly": fetch_Diagram_monthly(
                        mosadCoordinator, system_report_model.apprenticeCall_gap_mosad
                    ),
                    "avg_apprenticeMeeting_gap_monthly": fetch_Diagram_monthly(
                        mosadCoordinator,
                        system_report_model.apprenticeMeeting_gap_mosad,
                    ),
                    "forgotenApprentice_rivonly": fetch_Diagram_rivonly(
                        mosadCoordinator,
                        system_report_model.forgotenApprentice_cnt_mosad_rivony,
                    ),
                }
            ),
            HTTPStatus.OK,
        )
    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST


@madadim_form_blueprint.route("/eshcol_coordinator", methods=["GET"])
def eshcol_coordinator(eshcolCoordinatorId="empty"):
    try:

        if eshcolCoordinatorId == "empty":
            eshcolCoordinatorId = request.args.get("eshcolCoordinator")
        # get  Eshcol id
        user_ent = (
            db.session.query(User.cluster_id)
            .filter(User.id == eshcolCoordinatorId, User.role_ids.contains("2"))
            .first()
        )
        if user_ent is None:
            return (
                jsonify(
                    {
                        "result": "not  eshcolCoordinator",
                    }
                ),
                HTTPStatus.OK,
            )
        all_MosadCoordinator = (
            db.session.query(User.id)
            .filter(User.cluster_id == user_ent.cluster_id, User.role_ids.contains("1"))
            .all()
        )
        all_EshcolApprentices = (
            db.session.query(Apprentice.id)
            .filter(Apprentice.cluster_id == user_ent.cluster_id)
            .all()
        )
        # MosadEshcolMeeting
        MosadCoordinator_old_MosadEshcolMeeting = no_mosad_coordinator_interaction(
            all_MosadCoordinator,
            user_ent.cluster_id,
            report_model.MOsadEshcolMeeting_report,
            30,
        )
        # tochnitMeeting_report
        current_month = datetime.today().month
        start_Of_year = datetime.today() - timedelta(days=30 * current_month)
        newvisit_yeshiva_Tohnit = (
            db.session.query(Report.visit_date)
            .filter(
                Report.user_id == eshcolCoordinatorId,
                Report.title == report_model.tochnitMeeting_report,
                Report.visit_date > start_Of_year,
            )
            .all()
        )

        # forgoten-no reports_as_call
        all_Apprentices = (
            db.session.query(
                Apprentice.id,
                Institution.name.label("Institution_name"),
                Apprentice.association_date,
            )
            .filter(
                Apprentice.cluster_id == user_ent.cluster_id,
                Apprentice.institution_id == Institution.id,
            )
            .all()
        )
        forgoten_apprentice_per_insti, total_forgoten, ids_no_visit = (
            compute_forgoten_apprectice(all_Apprentices)
        )

        forgotenApprentice_full_details = forgoten_apprentice_full_details(ids_no_visit)
        eshcolCoordinator_score1, avg__mosad_racaz_meeting_monthly = (
            eshcol_Coordinators_score(eshcolCoordinatorId)
        )
        return (
            jsonify(
                {
                    "eshcolCoordinator_score": eshcolCoordinator_score1,
                    "all_MosadCoordinator_count": len(all_MosadCoordinator),
                    "good__mosad_racaz_meeting": len(all_MosadCoordinator)
                    - len(MosadCoordinator_old_MosadEshcolMeeting),
                    "newvisit_yeshiva_Tohnit_precent": 100
                    * len(newvisit_yeshiva_Tohnit)
                    / current_month,
                    "yeshiva_Tohnit_todo": current_month,
                    "newvisit_yeshiva_Tohnit": len(newvisit_yeshiva_Tohnit),
                    "Apprentice_forgoten_count": len(ids_no_visit),
                    "all_EshcolApprentices_count": len(all_EshcolApprentices),
                    "avg__mosad_racaz_meeting_monthly": avg__mosad_racaz_meeting_monthly,
                    "avg__mosad_racaz_meeting_monthly_Diagram": fetch_Diagram_monthly(
                        eshcolCoordinatorId, system_report_model.mosad_eshcol_meeting
                    ),
                    "forgotenApprentice_4_rivonly": fetch_Diagram_rivonly(
                        eshcolCoordinatorId,
                        system_report_model.forgotenApprentice_cnt_eshcol,
                    ),
                    "forgotenApprentice_full_details": forgotenApprentice_full_details,
                }
            ),
            HTTPStatus.OK,
        )
    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST


@madadim_form_blueprint.route("/mosad", methods=["GET"])
def mosad():
    try:
        institution_id = request.args.get("institution_id")
        mosadCoordinator1 = (
            db.session.query(User.id)
            .filter(User.role_ids.contains("1"), User.institution_id == institution_id)
            .first()
        )
        all_Apprentices = (
            db.session.query(
                Apprentice.id,
                Apprentice.association_date,
            )
            .filter(Apprentice.institution_id == institution_id)
            .all()
        )
        mosadCoordinatorJson = mosad_coordinator(mosadCoordinator1.id)[0].json
        mosad_coord_score_diagram = fetch_Diagram_monthly(
            mosadCoordinator1.id, system_report_model.mosad_corrdintors_score_csv
        )
        counts_melave_score, score_melaveProfile_list = get_melave_score(
            cluster_id="0", mosad=institution_id
        )
        (
            greenvisitmeetings,
            orangevisitmeetings,
            redvisitmeetings,
            greenvisitcalls,
            orangevisitcalls,
            redvisitcalls,
            forgotenApprenticCount,
        ) = red_green_orange_status(all_Apprentices)
        return (
            jsonify(
                {
                    "mosad_coord_score_diagram": mosad_coord_score_diagram,
                    "melave_score_diagram": counts_melave_score,
                    "mosad_score": mosadCoordinatorJson["mosad_score"],
                    "orangevisitmeetings": orangevisitmeetings,
                    "redvisitmeetings": redvisitmeetings,
                    "greenvisitmeetings": greenvisitmeetings,
                    "greenvisitcalls": greenvisitcalls,
                    "orangevisitcalls": orangevisitcalls,
                    "redvisitcalls": redvisitcalls,
                }
            ),
            HTTPStatus.OK,
        )
    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST


@madadim_form_blueprint.route("/mosadot_scores", methods=["GET"])
def mosadot_scores():
    institotionList = db.session.query(
        Institution.id, Institution.name, Institution.cluster_id
    ).all()
    mosadlist_score = []
    for institution_ in institotionList:
        mosad__score1, forgotenApprentice_Mosad1 = mosad_score(institution_[0])
        mosadlist_score.append(
            {"institution": institution_[0], "mosad_score": mosad__score1}
        )
    return jsonify(mosadlist_score), HTTPStatus.OK


@madadim_form_blueprint.route("/personas_scores", methods=["GET"])
def personas_scores():
    counts_melave_score, score_melaveProfile_list = get_melave_score()
    mosad_Cooordinator_score, score_MosadCoordProfile_list = (
        get_mosad_Coordinators_score()
    )
    eshcol_Cooordinator_score, score_EshcolCoordProfile_list = (
        get_Eshcol_corrdintors_score()
    )
    return jsonify(
        {
            "score_melaveProfile_list": score_melaveProfile_list,
            "score_MosadCoordProfile_list": score_MosadCoordProfile_list,
            "score_EshcolCoordProfile_list": score_EshcolCoordProfile_list,
        }
    )


@madadim_form_blueprint.route("/set_setting", methods=["post"])
def set_setting_madadim():

    data = request.json
    madadim_setting1 = db.session.query(MadadimSetting).first()
    if madadim_setting1 is None:
        rep = MadadimSetting(
            call_madad_date="1995-09-09",
            cenes_madad_date="1995-09-09",
            tochnitMeet_madad_date="1995-09-09",
            eshcolMosadMeet_madad_date="1995-09-09",
            mosadYeshiva_madad_date="1995-09-09",
            hazana_madad_date="1995-09-09",
            professionalMeet_madad_date="1995-09-09",
            doForBogrim_madad_date="1995-09-09",
            basis_madad_date="1995-09-09",
            callHorim_madad_date="1995-09-09",
            groupMeet_madad_date="1995-09-09",
            matzbarmeet_madad_date="1995-09-09",
            meet_madad_date="1995-09-09",
        )
        db.session.add(rep)
        db.session.commit()
        return jsonify({"result": "success"}), HTTPStatus.OK
    madadim_setting1.meet_madad_date = data["meet_madad_date"]
    madadim_setting1.matzbarmeet_madad_date = data["matzbarmeet_madad_date"]
    madadim_setting1.groupMeet_madad_date = data["groupMeet_madad_date"]
    madadim_setting1.callHorim_madad_date = data["callHorim_madad_date"]
    madadim_setting1.basis_madad_date = data["basis_madad_date"]
    madadim_setting1.call_madad_date = data["call_madad_date"]
    madadim_setting1.cenes_madad_date = data["cenes_madad_date"]
    madadim_setting1.tochnitMeet_madad_date = data["tochnitMeet_madad_date"]
    madadim_setting1.eshcolMosadMeet_madad_date = data["eshcolMosadMeet_madad_date"]
    madadim_setting1.mosadYeshiva_madad_date = data["mosadYeshiva_madad_date"]
    madadim_setting1.hazana_madad_date = data["hazana_madad_date"]
    madadim_setting1.professionalMeet_madad_date = data["professionalMeet_madad_date"]
    madadim_setting1.doForBogrim_madad_date = data["doForBogrim_madad_date"]

    db.session.commit()
    return jsonify({"result": "success"}), HTTPStatus.OK


@madadim_form_blueprint.route("/get_all_setting", methods=["GET"])
def get_notification_setting_form():
    try:
        madadim_setting1 = db.session.query(MadadimSetting).first()
        return (
            jsonify(
                {
                    "call_madad_date": str(madadim_setting1.call_madad_date),
                    "meet_madad_date": str(madadim_setting1.meet_madad_date),
                    "groupMeet_madad_date": str(madadim_setting1.groupMeet_madad_date),
                    "callHorim_madad_date": str(madadim_setting1.callHorim_madad_date),
                    "basis_madad_date": str(madadim_setting1.basis_madad_date),
                    "doForBogrim_madad_date": str(
                        madadim_setting1.doForBogrim_madad_date
                    ),
                    "matzbarmeet_madad_date": str(
                        madadim_setting1.matzbarmeet_madad_date
                    ),
                    "professionalMeet_madad_date": str(
                        madadim_setting1.professionalMeet_madad_date
                    ),
                    "hazana_madad_date": str(madadim_setting1.hazana_madad_date),
                    "mosadYeshiva_madad_date": str(
                        madadim_setting1.mosadYeshiva_madad_date
                    ),
                    "eshcolMosadMeet_madad_date": str(
                        madadim_setting1.eshcolMosadMeet_madad_date
                    ),
                    "tochnitMeet_madad_date": str(
                        madadim_setting1.tochnitMeet_madad_date
                    ),
                    "cenes_madad_date": str(madadim_setting1.cenes_madad_date),
                }
            ),
            HTTPStatus.OK,
        )
    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST


@madadim_form_blueprint.route("/apprentice_status", methods=["GET"])
def apprentice_status():
    try:
        user_id = request.args.get("userId")
        inst_List = get_institution_list(user_id)
        inst_List_ids = [r.id for r in inst_List]
        all_Apprentices = (
            db.session.query(
                Apprentice.id,
                Institution.name.label("Institution_name"),
                Apprentice.association_date,
            )
            .filter(
                Apprentice.institution_id == Institution.id,
                Apprentice.institution_id.in_(inst_List_ids),
            )
            .all()
        )
        #########call##########
        inst_no_call_dict, missingCallApprentice_total = report_status_apprentice(
            all_Apprentices, 45, report_model.reports_as_call
        )
        ###########meet#############
        inst_no_meet_dict, missingMeetApprentice_total = report_status_apprentice(
            all_Apprentices, 60, report_model.report_as_meet
        )
        ########fail score########
        inst_low_dict, missingCallApprentice_total2 = report_status_apprentice_priod(
            all_Apprentices
        )

        for inst in inst_List:
            if inst.name not in inst_no_meet_dict:
                inst_no_meet_dict[inst.name] = 0
            if inst.name not in inst_no_call_dict:
                inst_no_call_dict[inst.name] = 0
            if inst.name not in inst_low_dict:
                inst_low_dict[inst.name] = 0
        return (
            jsonify(
                {
                    "lowScoreApprentice_Count": missingCallApprentice_total2,
                    "lowScoreApprentice_List": [
                        {"name": key, "value": value}
                        for key, value in inst_low_dict.items()
                    ],
                    "missingCallApprentice_total": missingCallApprentice_total,
                    "missingCalleApprentice_count": [
                        {"name": key, "value": value}
                        for key, value in inst_no_call_dict.items()
                    ],
                    "missingmeetApprentice_total": missingMeetApprentice_total,
                    "missingmeetApprentice_count": [
                        {"name": key, "value": value}
                        for key, value in inst_no_meet_dict.items()
                    ],
                }
            ),
            HTTPStatus.OK,
        )
    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST


@madadim_form_blueprint.route("/apprentice_status_mosad", methods=["GET"])
def apprentice_status_mosad():
    try:

        institution = request.args.get("institutionId")
        ApprenticeList = (
            db.session.query(
                Apprentice.birthday_ivry,
                Apprentice.id,
                Apprentice.accompany_id,
                Apprentice.association_date,
                Apprentice.name,
                Apprentice.last_name,
                Apprentice.birthday,
            )
            .filter(Apprentice.institution_id == institution)
            .all()
        )

        #####call###
        no_visit_call = report_status_apprentice_mosad(
            ApprenticeList, 45, report_model.reports_as_call
        )
        #####meet###
        no_visit_meet = report_status_apprentice_mosad(
            ApprenticeList, 60, report_model.report_as_meet
        )
        #######fail report############
        low_score_merged = report_status_apprentice_priod_mosad(ApprenticeList)
        ####compuite precentage of deacrese/increase ######
        too_old = datetime.today() - timedelta(days=31)
        too_new = datetime.today() - timedelta(days=61)

        mosad_corrdintors_score_csv = (
            db.session.query(SystemReport)
            .filter(
                SystemReport.type == system_report_model.lowScoreApprentice_mosad_csv,
                SystemReport.creation_date < too_old,
                SystemReport.creation_date > too_new,
            )
            .first()
        )
        inst_name = (
            db.session.query(
                Institution.name,
            )
            .filter(Institution.id == institution)
            .first()
        )
        missing_calls_direction = 0
        missing_meet_direction = 0
        low_score_direction = 0
        if mosad_corrdintors_score_csv is not None:
            f = StringIO(mosad_corrdintors_score_csv.value)
            reader = csv.reader(f, delimiter=",")
            for row in reader:
                if inst_name.name in row:
                    missing_calls_direction = len(no_visit_call) - int(row[2])
                    missing_meet_direction = len(no_visit_meet) - int(row[1])
                    low_score_direction = len(low_score_merged) - int(row[3])

        return (
            jsonify(
                {
                    "call": [
                        {"apprentice": str(k), "gap": v}
                        for k, v in no_visit_call.items()
                    ],
                    "meet": [
                        {"apprentice": str(k), "gap": v}
                        for k, v in no_visit_meet.items()
                    ],
                    "low_score": low_score_merged,
                    "missing_calls_direction": missing_calls_direction,
                    "missing_meet_direction": missing_meet_direction,
                    "low_score_direction": low_score_direction,
                }
            ),
            HTTPStatus.OK,
        )
    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST


@madadim_form_blueprint.route("/forgoten_apprentices", methods=["GET"])
def forgoten_apprentice():
    try:
        user_id = request.args.get("userId")
        inst_List = get_institution_list(user_id)
        inst_List_ids = [r.id for r in inst_List]
        all_Apprentices = (
            db.session.query(
                Apprentice.id,
                Institution.name.label("Institution_name"),
                Apprentice.association_date,
            )
            .filter(
                Apprentice.institution_id == Institution.id,
                Apprentice.institution_id.in_(inst_List_ids),
            )
            .all()
        )

        forgoten_apprentice_per_insti, total_forgoten, ids_no_visit = (
            compute_forgoten_apprectice(all_Apprentices)
        )
        return (
            jsonify(
                {
                    "forgotenApprentice_total": total_forgoten,
                    "forgotenApprentice_count": [
                        {"id": str(key), "value": value}
                        for key, value in forgoten_apprentice_per_insti.items()
                    ],
                }
            ),
            HTTPStatus.OK,
        )
    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST


@madadim_form_blueprint.route("/forgoten_apprentice_mosad", methods=["GET"])
def forgoten_apprentices_mosad_outbound():
    try:
        institution_id = request.args.get("institutionId")

        all_Apprentices = (
            db.session.query(
                Apprentice.id,
                Institution.name.label("Institution_name"),
                Apprentice.association_date,
            )
            .filter(
                Apprentice.institution_id == Institution.id,
                Apprentice.institution_id == institution_id,
            )
            .all()
        )
        forgoten_apprentice_per_insti, total_forgoten, ids_no_visit = (
            compute_forgoten_apprectice(all_Apprentices)
        )
        forgoten_apprentice_gap = {}

        for appren in ids_no_visit:
            # reports_as_call
            call_report = (
                db.session.query(
                    Report.ent_reported,
                    func.max(Report.visit_date).label("visit_date"),
                )
                .filter(
                    Report.ent_reported == appren,
                    or_(
                        Report.title.in_(report_model.reports_as_call),
                        Report.title.in_(report_model.report_as_meet),
                    ),
                )
                .group_by(Report.ent_reported)
                .first()
            )
            if call_report:
                gap = (date.today() - call_report.visit_date).days
            else:
                appren_ent = (
                    db.session.query(Apprentice.id, Apprentice.association_date)
                    .filter(Apprentice.id == appren)
                    .first()
                )
                gap = (date.today() - appren_ent.association_date).days
            forgoten_apprentice_gap[str(appren)] = gap

        #####compuite precentage of deacrese/increase ####
        too_old = datetime.today() - timedelta(days=31)
        forgoten_Tohnit_report = (
            db.session.query(SystemReport)
            .filter(
                SystemReport.type == system_report_model.forgotenApprentice_tochnit_scv,
                SystemReport.creation_date > too_old,
            )
            .first()
        )
        inst_name = (
            db.session.query(
                Institution.name,
            )
            .filter(Institution.id == institution_id)
            .first()
        )
        prev_month_forgoten_precentage = 0
        if forgoten_Tohnit_report is not None:
            f = StringIO(forgoten_Tohnit_report.value)
            reader = csv.reader(f, delimiter=",")
            for row in reader:
                if inst_name.name in row:
                    prev_month_forgoten_precentage = (
                        len(forgoten_apprentice_gap) - int(row[1])
                    ) / len(all_Apprentices)
        return (
            jsonify(
                {
                    "apprentice_list": [
                        {"id": k, "gap": v} for k, v in forgoten_apprentice_gap.items()
                    ],
                    "percentage": prev_month_forgoten_precentage * 100,
                }
            ),
            HTTPStatus.OK,
        )
    except Exception as e:
        return (
            jsonify({"result": "no such instituiton .addidtional details:" + str(e)}),
            HTTPStatus.BAD_REQUEST,
        )


@madadim_form_blueprint.route("/melave_score_tochnit", methods=["GET"])
# only returns count of melave per mosad
def melave_score_tochnit():
    Institution_all = db.session.query(Institution.id).all()
    inst_melave_dict = dict()
    for inst in Institution_all:
        counts_melave_score, score_melaveProfile_list = get_melave_score(mosad=inst.id)
        inst_melave_dict[str(inst.id)] = len(score_melaveProfile_list)
    return (
        jsonify([{"name": k, "value": v} for k, v in inst_melave_dict.items()]),
        HTTPStatus.OK,
    )


@madadim_form_blueprint.route("/melave_score_mosad", methods=["GET"])
def melave_score_mosad():

    institution = request.args.get("institutionId")

    counts_melave_score, score_melaveProfile_list = get_melave_score(mosad=institution)
    return jsonify(score_melaveProfile_list), HTTPStatus.OK
