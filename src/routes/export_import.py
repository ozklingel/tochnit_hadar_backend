import datetime
import uuid
import boto3
from flask import Blueprint, request, jsonify
from http import HTTPStatus
from datetime import datetime, date, timedelta
from sqlalchemy import func, or_

from src.logic.compute_score import mosad_score, melave_score
from src.logic.home_page import get_Eshcol_corrdintors_score
from src.logic.performence_metric import (
    compute_forgoten_apprectice,
    compute_apprentice_profile,
)
from src.models import system_report_model
from src.routes.utils.hebrw_date_cust import  start_of_current_rivon, start_of_year_greg_date
from src.services import db
from config import (
    AWS_access_key_id,
    AWS_secret_access_key,
    BUCKET,
    BUCKET_PATH,
)
from src.models.apprentice_model import Apprentice
from src.models.institution_model import Institution
from src.models.system_report_model import SystemReport
from src.models.user_model import User
from src.models.report_model import (
    Report,
    professional_report,
    groupMeet_report,
    personalMeet_report,
    HorimCall_report,
)
import src.routes.performance_metrics as md
from src.routes.homepage import (
    get_mosad_Coordinators_score,
    get_melave_score,
)

export_import_blueprint = Blueprint(
    "export_import", __name__, url_prefix="/export_import"
)


@export_import_blueprint.route("/monthly", methods=["GET"])
def monthly():
    try:

        # export_Eshcol_corrdintors_score
        export_Eshcol_corrdintors_score_csv = import_eshcol_corrdintors_score("local")
        system_report1 = SystemReport(
            related_id=0,
            type=system_report_model.eshcol_corrdintors_score_csv,
            value=export_Eshcol_corrdintors_score_csv,
            creation_date=date.today(),
        )
        db.session.add(system_report1)
        # export_forgoten_mosad
        export_forgoten_mosad_csv = import_forgoten_mosad("local")
        system_report1 = SystemReport(
            related_id=0,
            type=system_report_model.forgotenApprentice_mosad_csv,
            value=export_forgoten_mosad_csv,
            creation_date=date.today(),
        )
        db.session.add(system_report1)

        # export_forgoten_Tohnit
        export_forgoten_Tohnit_csv = import_forgoten_tohnit("local")
        system_report1 = SystemReport(
            related_id=0,
            type=system_report_model.forgotenApprentice_tochnit_scv,
            value=export_forgoten_Tohnit_csv,
            creation_date=date.today(),
        )
        db.session.add(system_report1)
        # export_melave_corrdintors_score
        export_melave_corrdintors_score_csv = import_melave_tochnit_score("local")
        system_report1 = SystemReport(
            related_id=0,
            type=system_report_model.melave_score_csv,
            value=export_melave_corrdintors_score_csv,
            creation_date=date.today(),
        )
        db.session.add(system_report1)

        # export_lowScoreApprentice_tohnit_csv
        export_mosad_melavim_cnt_csv = import_mosad_melavim_cnt("local")
        system_report1 = SystemReport(
            related_id=0,
            type=system_report_model.mosad_melavim_cnt_csv,
            value=export_mosad_melavim_cnt_csv,
            creation_date=date.today(),
        )
        db.session.add(system_report1)

        # export_mosad_corrdintors_score
        export_mosad_corrdintors_score_csv = import_mosad_corrdintors_score("local")
        system_report1 = SystemReport(
            related_id=0,
            type=system_report_model.mosad_corrdintors_score_csv,
            value=export_mosad_corrdintors_score_csv,
            creation_date=date.today(),
        )
        db.session.add(system_report1)

        all_melave = (
            db.session.query(User.id, User.name, User.institution_id)
            .filter(User.role_ids.contains("0"))
            .all()
        )
        for melave in all_melave:
            melaveId = melave[0]
            melave_score1, call_gap_avg, meet_gap_avg, group_meeting_gap_avg = (
                melave_score(melaveId)
            )
            system_report1 = SystemReport(
                related_id=melaveId,
                type=system_report_model.melave_Score,
                value=melave_score1,
                creation_date=date.today(),
            )
            db.session.add(system_report1)
            system_report1 = SystemReport(
                related_id=melaveId,
                type=system_report_model.visitcalls_melave_avg,
                value=call_gap_avg,
                creation_date=date.today(),
            )
            db.session.add(system_report1)
            system_report1 = SystemReport(
                related_id=melaveId,
                type=system_report_model.visitmeets_melave_avg,
                value=meet_gap_avg,
                creation_date=date.today(),
            )
            db.session.add(system_report1)

        # mosad Madadim:
        all_MosadCoordinator = (
            db.session.query(User.id, User.institution_id)
            .filter(User.role_ids.contains("1"))
            .all()
        )
        for mosadCoord in all_MosadCoordinator:
            # export_lowScoreApprentice_mosad
            export_lowScoreApprentice_mosad_csv = import_low_score_apprentice_mosad(
                "local", mosadCoord.institution_id
            )
            system_report1 = SystemReport(
                related_id=0,
                type=system_report_model.lowScoreApprentice_mosad_csv,
                value=export_lowScoreApprentice_mosad_csv,
                creation_date=date.today(),
            )
            db.session.add(system_report1)

            mosadCoord_id = mosadCoord[0]
            res = md.mosad_coordinator(mosadCoord_id)[0].json
            system_report1 = SystemReport(
                related_id=mosadCoord_id,
                type=system_report_model.apprentice_forgoten_cnt_mosad_monthly,
                value=res["Apprentice_forgoten_count"],
                creation_date=date.today(),
            )
            db.session.add(system_report1)
            res = md.mosad_coordinator(mosadCoord_id)[0].json
            system_report1 = SystemReport(
                related_id=mosadCoord_id,
                type=system_report_model.avg_groupMeeting_gap,
                value=res["avg_groupMeeting_gap"],
                creation_date=date.today(),
            )
            db.session.add(system_report1)
            system_report1 = SystemReport(
                related_id=mosadCoord_id,
                type=system_report_model.visitcalls_mosad_avg,
                value=res["avg_apprenticeCall_gap"],
                creation_date=date.today(),
            )
            db.session.add(system_report1)
            system_report1 = SystemReport(
                related_id=mosadCoord_id,
                type=system_report_model.visitmeets_mosad_avg,
                value=res["avg_apprenticeMeeting_gap"],
                creation_date=date.today(),
            )
            db.session.add(system_report1)
            all_Apprentices = (
                db.session.query(
                    Apprentice.paying,
                    Apprentice.militaryPositionNew,
                    Apprentice.spirit_status,
                    Apprentice.army_role,
                    Apprentice.institution_mahzor,
                )
                .filter(Apprentice.institution_id == mosadCoord.institution_id)
                .all()
            )
            paying_dict, Picud_dict, matzbar_dict, sugSherut_dict, mahzor_dict = (
                compute_apprentice_profile(all_Apprentices)
            )
            system_report1 = SystemReport(
                related_id=mosadCoord.institution_id,
                type=system_report_model.matzbar_apprentice_status_mosad,
                value=str(matzbar_dict),
                creation_date=date.today(),
            )
            db.session.add(system_report1)

        # eshcol Madadim:
        all_eshcol_coordinator = (
            db.session.query(User.id, User.institution_id)
            .filter(User.role_ids.contains("2"))
            .all()
        )
        for eshcol_Coord in all_eshcol_coordinator:

            res = md.eshcol_coordinator(eshcol_Coord.id)[0].json
            system_report1 = SystemReport(
                related_id=eshcol_Coord.id,
                type=system_report_model.mosad_eshcol_meeting,
                value=res["avg__mosad_racaz_meeting_monthly"],
                creation_date=date.today(),
            )
            db.session.add(system_report1)

        try:
            db.session.commit()
            return jsonify({"result": "success"}), HTTPStatus.OK

        except Exception as e:
            return jsonify({"result": "error" + str(e)}), HTTPStatus.BAD_REQUEST
    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST


@export_import_blueprint.route("/rivony", methods=["GET"])
def rivony():
    start_Of_Rivon = start_of_current_rivon()
    # melave Madadim:
    all_melave = (
        db.session.query(User.id, User.name, User.institution_id)
        .filter(User.role_ids.contains("0"))
        .all()
    )
    for melave in all_melave:
        melaveId = melave[0]
        all_melave_Apprentices = (
            db.session.query(
                Apprentice.id,
                Institution.name.label("Institution_name"),
                Apprentice.association_date,
            )
            .filter(
                Apprentice.accompany_id == melaveId,
                Institution.id == Apprentice.institution_id,
            )
            .all()
        )
        if len(all_melave_Apprentices) == 0:
            continue
        # מפגש מקצועי מלווה
        newvisit_professional = (
            db.session.query(Report.user_id)
            .filter(
                Report.ent_reported == melaveId,
                Report.title == professional_report,
                Report.visit_date > start_Of_Rivon,
            )
            .all()
        )
        system_report1 = SystemReport(
            related_id=melaveId,
            type=system_report_model.proffesionalMeet_presence_melave,
            value=len(newvisit_professional),
            creation_date=date.today(),
        )
        db.session.add(system_report1)

        forgoten_apprentice_per_insti, total_forgoten, ids_no_visit = (
            compute_forgoten_apprectice(all_melave_Apprentices)
        )

        system_report1 = SystemReport(
            related_id=melaveId,
            type=system_report_model.forgotenApprentice_cnt_melave,
            value=len(ids_no_visit),
            creation_date=date.today(),
        )
        db.session.add(system_report1)

    # mosad Madadim:
    all_MosadCoordinator = (
        db.session.query(User.id, User.institution_id)
        .filter(User.role_ids.contains("1"))
        .all()
    )
    for mosadCoord in all_MosadCoordinator:
        mosadCoord_id = mosadCoord[0]
        inst = db.session.query(User.institution_id).filter(User.id == mosadCoord_id)
        all_Apprentices = (
            db.session.query(
                Apprentice.id,
                Institution.name.label("Institution_name"),
                Apprentice.association_date,
            )
            .filter(
                Apprentice.institution_id == inst,
                Institution.id == Apprentice.institution_id,
            )
            .all()
        )

        forgoten_apprentice_per_insti, total_forgoten, ids_no_visit = (
            compute_forgoten_apprectice(all_Apprentices)
        )
        system_report1 = SystemReport(
            related_id=mosadCoord_id,
            type=system_report_model.forgotenApprentice_cnt_mosad_rivony,
            value=len(ids_no_visit),
            creation_date=date.today(),
        )
        db.session.add(system_report1)

    # eshcol Madadim:
    all_eshcol_coordinator = (
        db.session.query(User.id, User.institution_id)
        .filter(User.role_ids.contains("2"))
        .all()
    )
    for eshcol_Coord in all_eshcol_coordinator:
        res = md.eshcol_coordinator(eshcol_Coord.id)[0].json

        system_report1 = SystemReport(
            related_id=eshcol_Coord.id,
            type=system_report_model.forgotenApprentice_cnt_eshcol,
            value=res["Apprentice_forgoten_count"],
            creation_date=date.today(),
        )
        db.session.add(system_report1)

    try:
        db.session.commit()
        return jsonify({"result": "success"}), HTTPStatus.OK

    except Exception as e:
        return jsonify({"result": "error" + str(e)}), HTTPStatus.BAD_REQUEST


@export_import_blueprint.route("/yearly", methods=["GET"])
def yearly():
    start_Of_year = start_of_year_greg_date()
    all_Apprentices = db.session.query(Apprentice.spirit_status, Apprentice.id).all()
    for apprentice1 in all_Apprentices:
        system_report1 = SystemReport(
            related_id=apprentice1.id,
            type=system_report_model.spirit_status_tochnit,
            value=apprentice1.spirit_status,
            creation_date=date.today(),
        )
        db.session.add(system_report1)
    all_melave = (
        db.session.query(User.id, User.name, User.institution_id)
        .filter(User.role_ids.contains("0"))
        .all()
    )
    for melave in all_melave:
        melaveId = melave[0]
        all_melave_Apprentices = (
            db.session.query(Apprentice.id)
            .filter(Apprentice.accompany_id == melaveId)
            .all()
        )
        if len(all_melave_Apprentices) == 0:
            continue

        cenes_yearly = (
            db.session.query(
                Report.user_id, func.max(Report.visit_date).label("visit_date")
            )
            .group_by(Report.user_id)
            .filter(
                Report.title == "כנס_שנתי",
                Report.user_id == melaveId,
                Report.visit_date > start_Of_year,
            )
            .first()
        )
        if cenes_yearly:
            system_report1 = SystemReport(
                related_id=melaveId,
                type=system_report_model.cenes_presence_melave,
                value=1,
                creation_date=date.today(),
            )
            db.session.add(system_report1)
        Horim_meeting = (
            db.session.query(
                Report.ent_reported, func.max(Report.visit_date).label("visit_date")
            )
            .group_by(Report.ent_reported)
            .filter(
                Report.title == HorimCall_report,
                Report.user_id == melaveId,
                Report.visit_date > start_Of_year,
            )
            .all()
        )
        system_report1 = SystemReport(
            related_id=melaveId,
            type=system_report_model.horim_meeting_melave,
            value=len(Horim_meeting),
            creation_date=date.today(),
        )
        db.session.add(system_report1)
        too_old = datetime.today() - timedelta(days=365)
        base_meeting = (
            db.session.query(Report.visit_date)
            .distinct(Report.visit_date)
            .filter(
                or_(
                    Report.title == personalMeet_report,
                    Report.title == groupMeet_report,
                ),
                Report.visit_in_army == True,
                Report.visit_date > too_old,
                Report.user_id == melaveId,
            )
            .group_by(Report.visit_date)
            .count()
        )
        system_report1 = SystemReport(
            related_id=melaveId,
            type=system_report_model.basis_meeting_melave,
            value=base_meeting,
            creation_date=date.today(),
        )
        db.session.add(system_report1)
    try:
        db.session.commit()
        return jsonify({"result": "success"}), HTTPStatus.OK

    except Exception as e:
        return jsonify({"result": "error" + str(e)}), HTTPStatus.BAD_REQUEST


@export_import_blueprint.route("mosadot_score", methods=["post"])
def import_mosadot_score(type_="extenal"):
    try:

        export_date = request.args.get("export_date")
        new_filename = get_file_name_from_db(
            export_date, system_report_model.mosadot_score
        )
        if new_filename == "no export":
            return (
                jsonify({"result": "no such export was done"}),
                HTTPStatus.BAD_REQUEST,
            )
        if new_filename:
            return (
                jsonify(
                    {
                        "result": "success",
                        "image path": BUCKET_PATH + new_filename,
                    }
                ),
                HTTPStatus.OK,
            )
        all_inst = db.session.query(
            Institution.id, Institution.owner_id, Institution.name
        ).all()
        value = ""
        for inst_ in all_inst:
            mosad_score_, i = mosad_score(inst_.id)
            if inst_.owner_id:
                resJson = md.mosad_coordinator(inst_.owner_id)
                mosadCoordinatorJson = resJson[0].json
                if len(mosadCoordinatorJson)==1:
                    continue
                value = (
                    value
                    + inst_.name
                    + ","
                    + str(mosadCoordinatorJson["all_apprenties_mosad"])
                    + ","
                    + str(mosadCoordinatorJson["all_Melave_mosad_count"])
                    + ",+"
                    + str(mosad_score_)
                    + "\n"
                )
        fields = "מוסד,כמות מלווים,כמות חניכים,ציון מוסד" + "\n"
        data = fields + value
        if type_ == "local":
            return data
        new_filename = upload_to_s3(data)
        return (
            jsonify(
                {
                    "result": "success",
                    "image path": BUCKET_PATH + new_filename,
                }
            ),
            HTTPStatus.OK,
        )

    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST


@export_import_blueprint.route("low_score_apprentice_mosad", methods=["post"])
def import_low_score_apprentice_mosad(type_="extenal", inst_id="empty"):
    try:
        if inst_id == "empty":
            inst_id = request.args.get("institution_id")
        export_date = request.args.get("export_date")
        new_filename = get_file_name_from_db(
            export_date, system_report_model.lowScoreApprentice_mosad_csv
        )
        if new_filename == "no export":
            return (
                jsonify({"result": "no such export was done"}),
                HTTPStatus.BAD_REQUEST,
            )
        if new_filename:
            return (
                jsonify(
                    {
                        "result": "success",
                        "image path": BUCKET_PATH + new_filename,
                    }
                ),
                HTTPStatus.OK,
            )

        lowScoreApprentice_dict = md.apprentice_status()[0].json
        lowScoreApprentice_List = lowScoreApprentice_dict["lowScoreApprentice_List"]
        callApprentice_List = lowScoreApprentice_dict["missingCalleApprentice_count"]
        meetingApprentice_List = lowScoreApprentice_dict["missingmeetApprentice_count"]

        inst_name = (
            db.session.query(Institution.name).filter(Institution.id == inst_id).first()
        )
        score_ent = find_in_list(lowScoreApprentice_List, inst_name.name)
        call_ent = find_in_list(callApprentice_List, inst_name.name)
        meet_ent = find_in_list(meetingApprentice_List, inst_name.name)
        all_Apprentices_cnt = (
            db.session.query(func.count(Apprentice.id))
            .filter(
                Apprentice.institution_id == Institution.id,
                Institution.name == score_ent["name"],
            )
            .first()
        )
        fields = (
            "מוסד"
            + ","
            + "פערי מפגש"
            + ","
            + "פערי שיחה"
            + ","
            + "ציון נמוך"
            + ","
            + "כמות חניכים"
            + "\n"
        )
        values = (
            score_ent["name"]
            + ","
            + str(all_Apprentices_cnt[0])
            + ","
            + score_ent["value"]
            + ","
            + call_ent["value"]
            + ","
            + meet_ent["value"]
            + "\n"
        )
        data = fields + values
        if type_ == "local":
            return data
        new_filename = upload_to_s3(data)
        return (
            jsonify(
                {
                    "result": "success",
                    "image path": BUCKET_PATH + new_filename,
                }
            ),
            HTTPStatus.OK,
        )
    except Exception as e:
        print(str(e))
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST


@export_import_blueprint.route("low_score_apprentice_tohnit", methods=["post"])
def import_low_score_apprentice_tohnit(type_="extenal"):
    try:
        export_date = request.args.get("export_date")
        new_filename = get_file_name_from_db(
            export_date, system_report_model.lowScoreApprentice_tochnit_csv
        )
        if new_filename == "no export":
            return (
                jsonify({"result": "no such export was done"}),
                HTTPStatus.BAD_REQUEST,
            )
        if new_filename:
            return (
                jsonify(
                    {
                        "result": "success",
                        "image path": BUCKET_PATH + new_filename,
                    }
                ),
                HTTPStatus.OK,
            )

        lowScoreApprentice_dict = md.apprentice_status()[0].json
        lowScoreApprentice_List = lowScoreApprentice_dict["lowScoreApprentice_List"]
        callApprentice_List = lowScoreApprentice_dict["missingCalleApprentice_count"]
        meetingApprentice_List = lowScoreApprentice_dict["missingmeetApprentice_count"]

        all_inst = db.session.query(Institution.name).all()
        values = ""
        for inst in all_inst:
            score_ent = find_in_list(lowScoreApprentice_List, inst.name)
            call_ent = find_in_list(callApprentice_List, inst.name)
            meet_ent = find_in_list(meetingApprentice_List, inst.name)
            all_Apprentices_cnt = (
                db.session.query(func.count(Apprentice.id))
                .filter(
                    Apprentice.institution_id == Institution.id,
                    Institution.name == score_ent["name"],
                )
                .first()
            )
            values = (
                values
                + score_ent["name"]
                + ","
                + str(all_Apprentices_cnt[0])
                + ","
                + score_ent["value"]
                + ","
                + call_ent["value"]
                + ","
                + meet_ent["value"]
                + "\n"
            )

        fields = (
            "מוסד"
            + ","
            + "פערי מפגש"
            + ","
            + "פערי שיחה"
            + ","
            + "ציון נמוך"
            + ","
            + "כמות חניכים"
            + "\n"
        )

        data = fields + values
        if type_ == "local":
            return data
        new_filename = upload_to_s3(data)
        return (
            jsonify(
                {
                    "result": "success",
                    "image path": BUCKET_PATH + new_filename,
                }
            ),
            HTTPStatus.OK,
        )

    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST


@export_import_blueprint.route("/melave_tochnit_score", methods=["post"])
def import_melave_tochnit_score(type_="extenal"):
    try:
        export_date = request.args.get("export_date")
        new_filename = get_file_name_from_db(
            export_date, system_report_model.melave_score_csv
        )
        if new_filename == "no export":
            return (
                jsonify({"result": "no such export was done"}),
                HTTPStatus.BAD_REQUEST,
            )
        if new_filename:
            return (
                jsonify(
                    {
                        "result": "success",
                        "image path": BUCKET_PATH + new_filename,
                    }
                ),
                HTTPStatus.OK,
            )
        score_dict, score_melaveProfile = get_melave_score()
        rows = score_melaveProfile
        values = ""
        for dict_ in rows:
            user_mosad = (
                db.session.query(
                    User.name,
                    Institution.name,
                    User.last_name,
                )
                .filter(
                    User.id == dict_["melaveId"], Institution.id == User.institution_id
                )
                .first()
            )
            if user_mosad is None:
                continue

            values = (
                values
                + user_mosad[0]
                + " "
                + user_mosad[2]
                + ","
                + user_mosad[1]
                + ","
                + str(dict_["melave_score1"])
                + ","
                + str(dict_["melaveId"])
                + "\n"
            )
        fields = "שם מלא,מוסד,פלאפון,ציון" + "\n"
        data = fields + values
        if type_ == "local":
            return data
        new_filename = upload_to_s3(data)
        return (
            jsonify(
                {
                    "result": "success",
                    "image path": BUCKET_PATH + new_filename,
                }
            ),
            HTTPStatus.OK,
        )

    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST


@export_import_blueprint.route("/mosad_melavim_cnt", methods=["post"])
def import_mosad_melavim_cnt(type_="extenal"):
    try:
        export_date = request.args.get("export_date")
        new_filename = get_file_name_from_db(
            export_date, system_report_model.mosad_melavim_cnt_csv
        )
        if new_filename == "no export":
            return (
                jsonify({"result": "no such export was done"}),
                HTTPStatus.BAD_REQUEST,
            )
        if new_filename:
            return (
                jsonify(
                    {
                        "result": "success",
                        "image path": BUCKET_PATH + new_filename,
                    }
                ),
                HTTPStatus.OK,
            )

        mosad_melavim_cnt = (
            db.session.query(Institution.name, func.count(User.name))
            .filter(User.institution_id == Institution.id, User.role_ids.contains("0"))
            .group_by(Institution.id)
            .all()
        )
        values = ""
        for k in mosad_melavim_cnt:
            values = values + str(k[0]) + "," + str(k[1]) + "\n"
        fields = "מוסד,כמות" + "\n"
        data = fields + values
        if type_ == "local":
            return data
        new_filename = upload_to_s3(data)
        return (
            jsonify(
                {
                    "result": "success",
                    "image path": BUCKET_PATH + new_filename,
                }
            ),
            HTTPStatus.OK,
        )

    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST


@export_import_blueprint.route("/mosad_corrdintors_score", methods=["post"])
def import_mosad_corrdintors_score(type_="extenal"):
    try:
        export_date = request.args.get("export_date")
        new_filename = get_file_name_from_db(
            export_date, system_report_model.mosad_corrdintors_score_csv
        )
        if new_filename == "no export":
            return (
                jsonify({"result": "no such export was done"}),
                HTTPStatus.BAD_REQUEST,
            )
        if new_filename:
            return (
                jsonify(
                    {
                        "result": "success",
                        "image path": BUCKET_PATH + new_filename,
                    }
                ),
                HTTPStatus.OK,
            )
        score_dict = get_mosad_Coordinators_score()
        rows = score_dict[1]
        values = ""
        for dict_ in rows:
            user_name = (
                db.session.query(
                    User.name,
                    User.last_name,
                )
                .filter(User.id == dict_["id"])
                .first()
            )
            values = (
                values
                + user_name[0]
                + " "
                + user_name[1]
                + ","
                + str(dict_["id"])
                + ","
                + str(dict_["score"])
                + "\n"
            )
        fields = "שם,ציון,פלאפון\n"  # quick hack
        data = fields + values
        if type_ == "local":
            return data
        new_filename = upload_to_s3(data)
        return (
            jsonify(
                {
                    "result": "success",
                    "image path": BUCKET_PATH + new_filename,
                }
            ),
            HTTPStatus.OK,
        )

    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST


@export_import_blueprint.route("/eshcol_corrdintors_score", methods=["post"])
def import_eshcol_corrdintors_score(type_="extenal"):
    try:
        export_date = request.args.get("export_date")
        new_filename = get_file_name_from_db(
            export_date, system_report_model.eshcol_corrdintors_score_csv
        )
        if new_filename == "no export":
            return (
                jsonify({"result": "no such export was done"}),
                HTTPStatus.BAD_REQUEST,
            )
        if new_filename:
            return (
                jsonify(
                    {
                        "result": "success",
                        "image path": BUCKET_PATH + new_filename,
                    }
                ),
                HTTPStatus.OK,
            )

        score_dict = get_Eshcol_corrdintors_score()
        rows = score_dict[1]
        values = ""
        for dict_ in rows:
            user_name = (
                db.session.query(
                    User.name,
                    User.last_name,
                )
                .filter(User.id == dict_["id"])
                .first()
            )
            dict_["name"] = user_name[0]
            values = (
                values
                + user_name[0]
                + " "
                + user_name[1]
                + ","
                + str(dict_["score"])
                + ","
                + str(dict_["id"])
                + "\n"
            )
        fields = "שם,פלאפון,ציון\n"  # quick hack
        data = fields + values
        if type_ == "local":
            return data
        new_filename = upload_to_s3(data)
        return (
            jsonify(
                {
                    "result": "success",
                    "image path": BUCKET_PATH + new_filename,
                }
            ),
            HTTPStatus.OK,
        )

    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST


@export_import_blueprint.route("/forgoten_Tohnit", methods=["post"])
def import_forgoten_tohnit(type_="extenal"):
    try:
        export_date = request.args.get("export_date")
        new_filename = get_file_name_from_db(
            export_date, system_report_model.forgotenApprentice_tochnit_scv
        )
        if new_filename == "no export":
            return (
                jsonify({"result": "no such export was done"}),
                HTTPStatus.BAD_REQUEST,
            )
        if new_filename:
            return (
                jsonify(
                    {
                        "result": "success",
                        "image path": BUCKET_PATH + new_filename,
                    }
                ),
                HTTPStatus.OK,
            )

        all_Apprentices = (
            db.session.query(
                Apprentice.id,
                Institution.name.label("Institution_name"),
                Apprentice.association_date,
            )
            .filter(Apprentice.institution_id == Institution.id)
            .all()
        )
        # update apprentices meet

        forgoten_apprentice_per_insti, total_forgoten, ids_no_visit = (
            compute_forgoten_apprectice(all_Apprentices)
        )
        fields = "שם,כמות" + "\n"
        rows = forgoten_apprentice_per_insti.items()
        values = ""

        for i in rows:
            values = values + i[0] + "," + str(i[1]) + "\n"
        data = fields + values
        if type_ == "local":
            return data
        new_filename = upload_to_s3(data)
        return (
            jsonify(
                {
                    "result": "success",
                    "image path": BUCKET_PATH + new_filename,
                }
            ),
            HTTPStatus.OK,
        )

    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST


@export_import_blueprint.route("/forgoten_mosad", methods=["post"])
def import_forgoten_mosad(type_="extenal"):
    try:
        export_date = request.args.get("export_date")
        new_filename = get_file_name_from_db(
            export_date, system_report_model.forgotenApprentice_mosad_csv
        )
        if new_filename == "no export":
            return (
                jsonify({"result": "no such export was done"}),
                HTTPStatus.BAD_REQUEST,
            )
        if new_filename:
            return (
                jsonify(
                    {
                        "result": "success",
                        "image path": BUCKET_PATH + new_filename,
                    }
                ),
                HTTPStatus.OK,
            )

        all_Apprentices = (
            db.session.query(
                Apprentice.id,
                Apprentice.name.label("name"),
                Institution.name.label("Institution_name"),
                Apprentice.last_name.label("last_name"),
                Apprentice.association_date,
            )
            .filter(Apprentice.institution_id == Institution.id)
            .all()
        )
        forgoten_apprentice_per_insti, total_forgoten, ids_no_visit = (
            compute_forgoten_apprectice(all_Apprentices)
        )
        all_Apprentices = (
            db.session.query(
                Apprentice.id,
                Apprentice.name.label("name"),
                Institution.name.label("Institution_name"),
                Apprentice.last_name.label("last_name"),
            )
            .filter(
                Apprentice.institution_id == Institution.id,
                Apprentice.id.in_(ids_no_visit),
            )
            .all()
        )
        values = ""
        for ent in all_Apprentices:
            values = (
                values
                + str(ent.name)
                + " "
                + str(ent.last_name)
                + ","
                + str(ent.Institution_name)
                + "\n"
            )
        fields = "שם,שם מוסד" + "\n"
        data = fields + values
        if type_ == "local":
            return data
        new_filename = upload_to_s3(data)
        return (
            jsonify(
                {
                    "result": "success",
                    "image path": BUCKET_PATH + new_filename,
                }
            ),
            HTTPStatus.OK,
        )

    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST


def upload_to_s3(data):

    # Set up S3 client
    session = boto3.Session()
    s3_client = session.client(
        "s3",
        aws_access_key_id=AWS_access_key_id,
        aws_secret_access_key=AWS_secret_access_key,
    )
    # Upload to S3
    new_filename = "export_" + uuid.uuid4().hex + ".csv"
    s3_client.put_object(
        Bucket=BUCKET,
        Key=new_filename,
        Body=data,
        ContentType="text/csv; charset=utf-8",  # Ensure the correct content type and encoding
    )

    return new_filename


def upload_str_to_s3(data):
    s3 = boto3.resource(
        "s3",
        aws_access_key_id=AWS_access_key_id,
        aws_secret_access_key=AWS_secret_access_key,
    )
    new_filename = "export_" + uuid.uuid4().hex + ".csv"
    object_ = s3.Object(bucket_name=BUCKET, key=new_filename)
    object_.put(Body=data.value)
    return new_filename


@export_import_blueprint.route("/remove_old_files_s3", methods=["post"])
def remove_old_files_s3():
    try:
        s3 = boto3.resource(
            "s3",
            aws_access_key_id=AWS_access_key_id,
            aws_secret_access_key=AWS_secret_access_key,
        )
        bucket = s3.Bucket(BUCKET)

        files = [os.key for os in bucket.objects.filter(Prefix="export_")]
        for f in files:
            s3.Object(BUCKET, f).delete()
        return jsonify({"result": "success"}), HTTPStatus.OK
    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST


@export_import_blueprint.route("/upload_file", methods=["post"])
def uploadfile():
    try:

        images_list = []
        for imagefile in request.files.getlist("file"):
            new_filename = (
                uuid.uuid4().hex + "." + imagefile.filename.rsplit(".", 1)[1].lower()
            )
            session = boto3.Session()
            s3_client = session.client(
                "s3",
                aws_access_key_id=AWS_access_key_id,
                aws_secret_access_key=AWS_secret_access_key,
            )
            try:
                s3_client.upload_fileobj(imagefile, BUCKET, new_filename)
            except Exception as e:
                return (
                    jsonify({"result": str(e), "image path": new_filename}),
                    HTTPStatus.OK,
                )
            images_list.append(BUCKET_PATH + new_filename)
        # if updatedEnt:
        #    updatedEnt.attachments=images_list
        #    db.session.commit()
        return jsonify({"result": "success", "image path": images_list}), HTTPStatus.OK
    except Exception:
        return jsonify({"result": str(Exception)}), HTTPStatus.BAD_REQUEST


def find_in_list(list_to_check, inst_name):
    for i in list_to_check:
        if i["name"] == inst_name:
            return {"name": str(i["name"]), "value": str(i["value"])}
    return {"name": inst_name, "value": "0"}


def get_file_name_from_db(export_date, export_type):
    if export_date != str(date.today()) and export_date is not None:
        data = (
            db.session.query(SystemReport.value)
            .filter(
                SystemReport.type == export_type,  # is it in use?
                SystemReport.creation_date == export_date,
            )
            .first()
        )
        if data is None:
            return "no export"

        new_filename = upload_str_to_s3(data)
        return new_filename
    return None
