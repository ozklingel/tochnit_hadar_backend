from flask import Blueprint, request, jsonify
from http import HTTPStatus
from datetime import datetime, date, timedelta

from pyluach import dates
from sqlalchemy import func, or_

import config
from src.models.madadim_setting import madadim_setting
from src.services import db, red
from src.models.apprentice_model import Apprentice

from src.models.institution_model import Institution
from src.models.system_report import system_report
from src.models.user_model import user1
from src.models.visit_model import Visit
from src.routes.user_Profile import toISO, correct_auth

madadim_form_blueprint = Blueprint('madadim', __name__, url_prefix='/madadim')


@madadim_form_blueprint.route("/lowScoreApprentice", methods=['GET'])
def lowScoreApprentice(external=True):
    try:
        if correct_auth(external)==False:
            return jsonify({'result': f"wrong access token "}), HTTPStatus.OK
        Oldvisitcalls = db.session.query(Visit.ent_reported, Institution.name).filter(
            Visit.ent_reported == Apprentice.id, Institution.id ==
            Apprentice.institution_id, Visit.title == config.failCall_report).all()
        forgotenApprenticCount = 0
        forgotenApprenticeList = {}

        for ent in Oldvisitcalls:
            forgotenApprenticCount += 1
            if ent[1] not in forgotenApprenticeList:
                forgotenApprenticeList[ent[1]] = 0
            forgotenApprenticeList[ent[1]] += 1

        return jsonify({
            'lowScoreApprentice_Count': forgotenApprenticCount,
            'lowScoreApprentice_List': [{"name": key, "value": value} for key, value in forgotenApprenticeList.items()],
        }), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST


@madadim_form_blueprint.route("/missingCalleApprentice", methods=['GET'])
def missingCalleApprentice(external=True):
    try:
        if correct_auth(external)==False:
            return jsonify({'result': f"wrong access token "}), HTTPStatus.OK
        all_Apprentices = db.session.query(Apprentice.id, Institution.name).filter(
            Apprentice.institution_id == Institution.id).all()
        # update apprentices meet

        visitcalls = db.session.query(Visit.ent_reported, func.max(Visit.visit_date).label("visit_date"),
                                      Institution.name).filter(Apprentice.id == Visit.ent_reported,
                                                               Institution.id == Apprentice.institution_id,
                                                               Visit.title.in_(config.reports_as_call)).group_by(
            Visit.ent_reported,
            Institution.name).all()
        ids_have_visit = [r[0] for r in visitcalls]
        ids_no_visit = []
        # handle no record
        for ent in all_Apprentices:
            if ent.id not in ids_have_visit:
                ids_no_visit.append([ent[0], ent[1]])
        counts = dict()
        missingCallApprentice_total = 0
        for i in visitcalls:
            vIsDate = i.visit_date
            now = date.today()
            gap = (now - vIsDate).days if vIsDate is not None else 0
            if gap > 21:
                missingCallApprentice_total += 1
                counts[i[2]] = counts.get(i[2], 0) + 1
        for i in ids_no_visit:
            missingCallApprentice_total += 1
            counts[i[1]] = counts.get(i[1], 0) + 1
        return jsonify({
            'missingCallApprentice_total': missingCallApprentice_total,

            'missingCalleApprentice_count': [{"name": key, "value": value} for key, value in counts.items()],

        }), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST


@madadim_form_blueprint.route("/missingMeetingApprentice", methods=['GET'])
def missingMeetingApprentice(external=True):
    try:
        if correct_auth(external)==False:
            return jsonify({'result': f"wrong access token "}), HTTPStatus.OK
        all_Apprentices = db.session.query(Apprentice.id, Institution.name).filter(
            Apprentice.institution_id == Institution.id).all()
        # update apprentices meet

        visitcalls = db.session.query(Visit.ent_reported, func.max(Visit.visit_date).label("visit_date"),
                                      Institution.name).filter(Apprentice.id == Visit.ent_reported,
                                                               Institution.id == Apprentice.institution_id,
                                                               Visit.title.in_(config.report_as_meet)).group_by(
            Visit.ent_reported,
            Institution.name).all()
        ids_have_visit = [r[0] for r in visitcalls]
        ids_no_visit = []
        # handle no record
        for ent in all_Apprentices:
            if ent.id not in ids_have_visit:
                ids_no_visit.append([ent[0], ent[1]])
        counts = dict()
        missingmeetApprentice_total = 0
        for i in visitcalls:
            vIsDate = i.visit_date
            now = date.today()
            gap = (now - vIsDate).days if vIsDate is not None else 0
            if gap > 21:
                missingmeetApprentice_total += 1
                counts[i[2]] = counts.get(i[2], 0) + 1
        for i in ids_no_visit:
            missingmeetApprentice_total += 1
            counts[i[1]] = counts.get(i[1], 0) + 1
        return jsonify({
            'missingmeetApprentice_total': missingmeetApprentice_total,
            'missingmeetApprentice_count': [{"name": key, "value": value} for key, value in counts.items()],

        }), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST


@madadim_form_blueprint.route("/forgotenApprentices", methods=['GET'])
def forgotenApprentice():
    try:
        if correct_auth()==False:
            return jsonify({'result': f"wrong access token "}), HTTPStatus.OK
        all_Apprentices = db.session.query(Apprentice.id, Institution.id).filter(
            Apprentice.institution_id == Institution.id).all()
        # update apprentices meet
        visitcalls = db.session.query(Visit.ent_reported, func.max(Visit.visit_date).label("visit_date"),
                                      Institution.id).filter(Apprentice.id == Visit.ent_reported,
                                                             Institution.id == Apprentice.institution_id,
                                                             Visit.title.in_(config.reports_as_call)).group_by(
            Visit.ent_reported,
            Institution.id).all()
        ids_have_visit = [r[0] for r in visitcalls]
        ids_no_visit = []
        # handle no record
        for ent in all_Apprentices:
            if ent.id not in ids_have_visit:
                ids_no_visit.append([ent[0], ent[1]])
        counts = dict()
        forgotenApprentice_total = 0
        for i in visitcalls:
            vIsDate = i.visit_date
            now = date.today()
            gap = (now - vIsDate).days if vIsDate is not None else 0
            if gap > 100:
                forgotenApprentice_total += 1
                counts[i[2]] = counts.get(i[2], 0) + 1
        for i in ids_no_visit:
            forgotenApprentice_total += 1
            counts[i[1]] = counts.get(i[1], 0) + 1
        return jsonify({
            'forgotenApprentice_total': forgotenApprentice_total,

            'forgotenApprentice_count': [{"id": str(key), "value": value} for key, value in counts.items()],

        }), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST


@madadim_form_blueprint.route("/forgotenApprentice_Mosad", methods=['GET'])
def forgotenApprentices_mosad_outbound():
    try:
        if correct_auth()==False:
            return jsonify({'result': f"wrong access token "}), HTTPStatus.OK
        institution_id = request.args.get("institutionId")
        all_Apprentices = db.session.query(Apprentice.id, ).filter(
            Apprentice.institution_id == institution_id).all()
        # update apprentices meet
        visitcalls = db.session.query(Visit.ent_reported, func.max(Visit.visit_date).label("visit_date"),
                                      Institution.name).filter(Apprentice.id == Visit.ent_reported,
                                                               Institution.id == Apprentice.institution_id,
                                                               Visit.title.in_(config.reports_as_call)).group_by(
            Visit.ent_reported,
            Institution.name).all()
        ids_have_visit = [r[0] for r in visitcalls]
        ids_no_visit = []
        # handle no record
        for ent in all_Apprentices:
            if ent.id not in ids_have_visit:
                ids_no_visit.append([ent[0], 100])
        for i in visitcalls:
            vIsDate = i.visit_date
            now = date.today()
            gap = (now - vIsDate).days if vIsDate is not None else 0
            ids_no_visit.append(i, gap)

        return jsonify(
            [{"id": r[0], "gap": r[1]} for r in ids_no_visit],

        ), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST


@madadim_form_blueprint.route("/forgotenApprentice_inbound", methods=['GET'])
def forgotenApprentice_Mosad(institution_id='empty',external=True):
    try:
        if correct_auth(external)==False:
            return jsonify({'result': f"wrong access token "}), HTTPStatus.OK
        if institution_id == 'empty':
            institution_id = request.args.get("institutionId")
        all_Apprentices = db.session.query(Apprentice.id, Apprentice.name, Apprentice.last_name).filter(
            Apprentice.institution_id == institution_id).all()
        # update apprentices meet
        Apprentice_ids_forgoten = [r[0] for r in all_Apprentices]
        too_old = datetime.today() - timedelta(days=100)
        Oldvisitcalls = db.session.query(Visit.ent_reported).filter(Apprentice.id == Visit.ent_reported,
                                                                    Institution.id == Apprentice.institution_id,
                                                                    Institution.id == institution_id,
                                                                    Visit.title.in_(config.reports_as_call),
                                                                    Visit.visit_date > too_old).all()
        for i in Oldvisitcalls:
            if i[0] in Apprentice_ids_forgoten:
                Apprentice_ids_forgoten.remove(i[0])
        return jsonify([str(r) for r in Apprentice_ids_forgoten]), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST


@madadim_form_blueprint.route("/missingCallsApprentice_Mosad", methods=['GET'])
def missingCallsApprentice_Mosad():
    try:
        if correct_auth()==False:
            return jsonify({'result': f"wrong access token "}), HTTPStatus.OK
        institution = request.args.get("institutionId")
        ApprenticeList = db.session.query(Apprentice.birthday_ivry, Apprentice.id, Apprentice.accompany_id,
                                          Apprentice.association_date,
                                          Apprentice.name, Apprentice.last_name, Apprentice.birthday).filter(
            Apprentice.institution_id == institution).all()
        no_visit_dict = dict()
        for Apprentice1 in ApprenticeList:
            # call
            visitEvent = db.session.query(Visit).filter(Visit.ent_reported == Apprentice1.id,
                                                        Visit.title.in_(config.reports_as_call)).order_by(
                Visit.visit_date.desc()).first()
            print("visitEvent", visitEvent)
            if visitEvent is None:

                daysFromNow = (
                        date.today() - Apprentice1.association_date).days if Apprentice1.association_date is not None else 100
                print(daysFromNow)
                no_visit_dict[Apprentice1.id] = daysFromNow

            elif (date.today() - visitEvent.visit_date).days > 21 and Visit.ent_reported not in no_visit_dict:
                daysFromNow = (date.today() - Visit.visit_date).days if Visit.visit_date is not None else 100
                no_visit_dict[Apprentice1.id] = daysFromNow

        print(no_visit_dict)
        return jsonify([{"apprentice": str(k), "gap": v} for k, v in no_visit_dict.items()],
                       ), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST


@madadim_form_blueprint.route("/missingMeetingsApprentice_Mosad", methods=['GET'])
def missingMeetingsApprentice_Mosad():
    try:
        if correct_auth()==False:
            return jsonify({'result': f"wrong access token "}), HTTPStatus.OK
        institution = request.args.get("institutionId")
        ApprenticeList = db.session.query(Apprentice.birthday_ivry, Apprentice.id, Apprentice.accompany_id,
                                          Apprentice.association_date,
                                          Apprentice.name, Apprentice.last_name, Apprentice.birthday).filter(
            Apprentice.institution_id == institution).all()
        no_visit_dict = dict()
        for Apprentice1 in ApprenticeList:

            # personal meet
            visitEvent = db.session.query(Visit).filter(
                Visit.ent_reported == str(Apprentice1.id),
                Visit.title.in_(config.report_as_meet)).order_by(
                Visit.visit_date.desc()).first()
            if visitEvent is None:
                daysFromNow = (
                            date.today() - Apprentice1.association_date).days if Apprentice1.association_date is not None else 100
                no_visit_dict[Apprentice1.id] = daysFromNow
            elif (date.today() - visitEvent.visit_date).days > 90 and Visit.ent_reported not in no_visit_dict:
                daysFromNow = (date.today() - Visit.visit_date).days if Visit.visit_date is not None else 100
                no_visit_dict[Apprentice1.id] = daysFromNow
        print(no_visit_dict)
        return jsonify([{"apprentice": str(k), "gap": v} for k, v in no_visit_dict.items()],
                       ), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST


@madadim_form_blueprint.route("/lowScoreApprentice_mosad", methods=['GET'])
def lowScoreApprentice_mosad():
    try:
        if correct_auth()==False:
            return jsonify({'result': f"wrong access token "}), HTTPStatus.OK
        institution = request.args.get("institutionId")

        Oldvisitcalls = db.session.query(Visit.ent_reported, Institution.name).filter(
            Visit.ent_reported == Apprentice.id, Institution.id ==
            Apprentice.institution_id, Institution.id == institution, Visit.title == config.failCall_report).all()
        forgotenApprenticCount = 0
        forgotenApprenticeList = {}

        for ent in Oldvisitcalls:
            if ent[1] not in forgotenApprenticeList:
                forgotenApprenticeList[ent[0]] = 0

        print(forgotenApprenticeList)
        return jsonify({
            'lowScoreApprentice_Count': forgotenApprenticCount,
            'lowScoreApprentice_List': [str(key) for key, value in forgotenApprenticeList.items()],
        }), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST


@madadim_form_blueprint.route("/melave_score_tochnit", methods=['GET'])
def melave_score_tochnit():
    if correct_auth() == False:
        return jsonify({'result': f"wrong access token "}), HTTPStatus.OK
    Institution_all = db.session.query(Institution.id).all()
    inst_melave_dict = dict()
    for inst in Institution_all:
        from src.routes.homepage import get_melave_score
        counts_melave_score, score_melaveProfile_list = get_melave_score(mosad=inst.id)
        inst_melave_dict[str(inst.id)] = len(score_melaveProfile_list)
    return jsonify([{"name": k, "value": v} for k, v in inst_melave_dict.items()]), HTTPStatus.OK


@madadim_form_blueprint.route("/melave_score_mosad", methods=['GET'])
def melave_score_mosad():
    if correct_auth() == False:
        return jsonify({'result': f"wrong access token "}), HTTPStatus.OK
    institution = request.args.get("institutionId")
    print(institution)
    from src.routes.homepage import get_melave_score
    counts_melave_score, score_melaveProfile_list = get_melave_score(mosad=institution)
    return jsonify(score_melaveProfile_list), HTTPStatus.OK


def fetch_Diagram_monthly(related_id, type="melave_Score"):
    too_old = datetime.today() - timedelta(days=30 * 12)
    data = db.session.query(system_report.creation_date, system_report.value).filter(system_report.type == type,
                                                                                     system_report.related_id == related_id,
                                                                                     system_report.creation_date > too_old).all()
    x_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    y_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for row in data:
        month = row[0].month
        value = row[1]
        i = x_list.index(month)
        y_list[i] = value
    return x_list, y_list,


def fetch_Diagram_rivonly(related_id, type="melave_Score"):
    too_old = datetime.today() - timedelta(days=30 * 12)
    data = db.session.query(system_report.creation_date, system_report.value).filter(system_report.type == type,
                                                                                     system_report.creation_date > too_old).all()
    x_list = [1, 2, 3, 4]
    y_list = [0, 0, 0, 0]
    for row in data:
        rivon = row[0].month % 3
        value = row[1]
        i = x_list.index(rivon+1)
        y_list[i] = value
    return x_list, y_list


def fetch_Diagram_yearly(related_id, type="melave_Score"):
    too_old = datetime.today() - timedelta(days=30 * 12)
    data = db.session.query(system_report.creation_date, system_report.value).filter(system_report.type == type,
                                                                                     system_report.creation_date > too_old).all()
    this_year = datetime.today().year
    x_list = [this_year - 3, this_year - 2, this_year - 1, this_year]
    y_list = [0, 0, 0, 0]
    for row in data:
        year = row[0].year
        value = row[1]
        i = x_list.index(year)
        y_list[i] = value
    return x_list, y_list,


@madadim_form_blueprint.route("/melave", methods=['GET'])
def Melave():
    try:
        if correct_auth()==False:
            return jsonify({'result': f"wrong access token "}), HTTPStatus.OK
        melaveId = request.args.get("melaveId")
        Apprentice_melaveId = db.session.query(Apprentice.id).filter(Apprentice.accompany_id == melaveId).all()
        # call
        Apprentice_old_call = [r[0] for r in Apprentice_melaveId]
        too_old = datetime.today() - timedelta(days=21)
        newvisitcalls = db.session.query(Visit.ent_reported).filter(Visit.user_id == melaveId,
                                                                    Visit.title.in_(config.reports_as_call),
                                                                    Visit.visit_date > too_old).all()
        for i in newvisitcalls:
            if i[0] in Apprentice_old_call:
                Apprentice_old_call.remove(i[0])
        # meet personal
        Apprentice_old_meet = [r[0] for r in Apprentice_melaveId]
        too_old = datetime.today() - timedelta(days=90)
        newvisitmeet = db.session.query(Visit.ent_reported).filter(Visit.user_id == melaveId,
                                                                   Visit.title.in_(config.report_as_meet),
                                                                   Visit.visit_date >= too_old).all()
        for i in newvisitmeet:
            if i[0] in Apprentice_old_meet:
                Apprentice_old_meet.remove(i[0])
        # professional_report
        current_month = datetime.today().month
        start_Of_year = datetime.today() - timedelta(days=30 * current_month)
        numOfQuarter_passed = int(current_month / 3)
        newvisitProffesionalMeet_year = db.session.query(Visit.user_id).filter(Visit.user_id == melaveId,
                                                                               Visit.title == config.professional_report,
                                                                               Visit.visit_date > start_Of_year).all()
        if numOfQuarter_passed == 0:
            sadna_score = 100
        else:
            sadna_score = 100 * len(newvisitProffesionalMeet_year) / numOfQuarter_passed
        # cenes_report
        start_Of_prev_year = datetime.today() - timedelta(days=30 * current_month + 30 * 12)
        _yearly_cenes = db.session.query(system_report).filter(system_report.type == config.cenes_report,
                                                               system_report.creation_date > start_Of_prev_year).all()
        newvisit_cenes = []
        if len(_yearly_cenes) > 0:
            newvisit_cenes = db.session.query(Visit.user_id).filter(Visit.user_id == melaveId,
                                                                    Visit.title == config.cenes_report,
                                                                    Visit.visit_date > start_Of_year).all()
            cenes_score = 100 * len(newvisit_cenes) / len(_yearly_cenes)
        else:
            cenes_score = 100
        Apprentice_old_Horim = [r[0] for r in Apprentice_melaveId]
        # HorimCall_report
        newvisitHorim = db.session.query(Visit.ent_reported).filter(Visit.user_id == melaveId,
                                                                    Visit.title == config.HorimCall_report,
                                                                    Visit.visit_date > start_Of_year).all()
        for i in newvisitHorim:
            if i[0] in Apprentice_old_Horim:
                Apprentice_old_Horim.remove(i[0])
        # meetInArmy
        Apprentice_old_meetInArmy = [r[0] for r in Apprentice_melaveId]
        newvisitmeetInArmy = db.session.query(Visit.ent_reported, Visit.visit_date).distinct(Visit.visit_date).filter(
            Visit.user_id == melaveId, Visit.title.in_(config.report_as_meet), Visit.visit_in_army == True,
            Visit.visit_date > start_Of_year).all()
        for i in newvisitmeetInArmy:
            if i[0] in Apprentice_old_meetInArmy:
                Apprentice_old_meetInArmy.remove(i[0])

        # forgeoten-no reports_as_call
        too_old = datetime.today() - timedelta(days=100)
        Apprentice_melaveId_forgoten = db.session.query(Apprentice.id).filter(Apprentice.accompany_id == melaveId,
                                                                              Apprentice.association_date < too_old).all()
        print(Apprentice_melaveId_forgoten)
        Apprentice_melaveId_forgoten = [r[0] for r in Apprentice_melaveId_forgoten]
        newvisitcalls = db.session.query(Visit.ent_reported).filter(Visit.user_id == melaveId,
                                                                    Apprentice.id == Visit.ent_reported,
                                                                    Institution.id == Apprentice.institution_id,
                                                                    or_(Visit.title.in_(config.reports_as_call),
                                                                        Visit.title.in_(config.report_as_meet)),
                                                                    Visit.visit_date > too_old).all()
        for i in newvisitcalls:
            if i[0] in Apprentice_melaveId_forgoten:
                Apprentice_melaveId_forgoten.remove(i[0])
        forgotenApprentice_full_details = db.session.query(Institution.name, Apprentice.name, Apprentice.last_name,
                                                           Apprentice.base_address, Apprentice.army_role,
                                                           Apprentice.unit_name,
                                                           Apprentice.marriage_status, Apprentice.serve_type,
                                                           Apprentice.hadar_plan_session).filter(
            Apprentice.id.in_(list(Apprentice_melaveId_forgoten)), Apprentice.institution_id == Institution.id).all()
        forgotenApprentice_full_details = [
            {"Institution_name": row[0], "name": row[1], "last_name": row[2], "base_address": row[3],
             "army_role": row[4], "unit_name": row[5], "marriage_status": row[6],
             "serve_type": row[7], "hadar_plan_session": row[8]} for row in
            [tuple(row) for row in
             forgotenApprentice_full_details]] if forgotenApprentice_full_details is not None else []
        melave_score1, call_gap_avg, meet_gap_avg, group_meeting_gap_avg = melave_score(melaveId)

        return jsonify({
            'melave_score': melave_score1,
            "numOfApprentice": len(Apprentice_melaveId),
            'visitcalls': len(Apprentice_melaveId) - len(Apprentice_old_call),
            'visitmeetings': len(Apprentice_melaveId) - len(Apprentice_old_meet),
            'numOfQuarter_passed': numOfQuarter_passed,
            'sadna_todo': numOfQuarter_passed,
            'sadna_done': len(newvisitProffesionalMeet_year),
            'sadna_percent': sadna_score,
            'cenes_2year': len(_yearly_cenes),
            'newvisit_cenes': len(newvisit_cenes),
            'cenes_percent': cenes_score,
            'visitHorim': len(Apprentice_melaveId) - len(Apprentice_old_Horim),
            'forgotenApprenticeCount': len(Apprentice_melaveId_forgoten),
            'new_visitmeeting_Army': len(Apprentice_melaveId) - len(Apprentice_old_meetInArmy),
            'call_gap_avg': call_gap_avg,
            'meet_gap_avg': meet_gap_avg,
            'visitCall_monthlyGap_avg': fetch_Diagram_monthly(melaveId, config.visitcalls_melave_avg),
            'visitMeeting_monthlyGap_avg': fetch_Diagram_monthly(melaveId, config.visitmeets_melave_avg),
            'forgotenApprentice_full_details': forgotenApprentice_full_details,
            'forgotenApprentice_rivonly': fetch_Diagram_rivonly(melaveId, config.forgotenApprentice_cnt),

            'visitsadna_presence': fetch_Diagram_rivonly(melaveId, config.proffesionalMeet_presence),
            'visitCenes_4_yearly_presence': fetch_Diagram_yearly(melaveId, config.cenes_presence),
            'visitHorim_4_yearly': fetch_Diagram_yearly(melaveId, config.horim_meeting),
        }), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST


@madadim_form_blueprint.route("/mosadCoordinator", methods=['GET'])
def mosadCoordinator(mosadCoordinator="empty",external=True):
    try:
        if correct_auth(external)==False:
            return jsonify({'result': f"wrong access token "}), HTTPStatus.OK
        if mosadCoordinator == "empty":
            mosadCoordinator = request.args.get("mosadCoordinator")
        current_month = datetime.today().month
        start_Of_year = datetime.today() - timedelta(days=30 * current_month)
        numOfQuarter_passed = int(current_month / 3)
        institutionId = db.session.query(user1.institution_id).filter(user1.id == mosadCoordinator).first()[0]
        all_Melave = db.session.query(user1.id).filter(user1.role_ids.contains("0"),
                                                       user1.institution_id == institutionId).all()

        # professional_report
        Melaves_old_professional = [r[0] for r in all_Melave]
        too_old = datetime.today() - timedelta(days=90)
        newvisit_professional = db.session.query(Visit.user_id).filter(Visit.user_id == user1.id,
                                                                       user1.institution_id == institutionId,
                                                                       Visit.title == config.professional_report,
                                                                       Visit.visit_date > too_old).all()
        for i in newvisit_professional:
            if i[0] in Melaves_old_professional:
                Melaves_old_professional.remove(i[0])
        # matzbar_report
        old_Melave_ids_matzbar = [r[0] for r in all_Melave]
        too_old = datetime.today() - timedelta(days=60)
        Oldvisit_matzbar = db.session.query(Visit.user_id).filter(Visit.user_id == user1.id,
                                                                  user1.institution_id == institutionId,
                                                                  Visit.title == config.matzbar_report,
                                                                  Visit.visit_date > too_old).all()
        for i in Oldvisit_matzbar:
            if i[0] in old_Melave_ids_matzbar:
                old_Melave_ids_matzbar.remove(i[0])
        # call
        all_apprenties_mosad = db.session.query(Apprentice.id).filter(Apprentice.institution_id == institutionId).all()
        old_apprenties_mosad_old_call = [r[0] for r in all_apprenties_mosad]
        too_old = datetime.today() - timedelta(days=60)
        newvisit_call = db.session.query(Visit.ent_reported).filter(Visit.ent_reported == Apprentice.id,
                                                                    Apprentice.institution_id == institutionId,
                                                                    Visit.title.in_(config.reports_as_call),
                                                                    Visit.visit_date > too_old).all()
        for i in newvisit_call:
            if i[0] in old_apprenties_mosad_old_call:
                old_apprenties_mosad_old_call.remove(i[0])
        # meet personal
        old_apprenties_mosad_old_meet = [r[0] for r in all_apprenties_mosad]
        too_old = datetime.today() - timedelta(days=60)
        newvisit_meet = db.session.query(Visit.ent_reported).filter(Visit.ent_reported == Apprentice.id,
                                                                    Apprentice.institution_id == institutionId,
                                                                    Visit.title.in_(config.report_as_meet),
                                                                    Visit.visit_date > too_old).all()
        for i in newvisit_meet:
            if i[0] in old_apprenties_mosad_old_meet:
                old_apprenties_mosad_old_meet.remove(i[0])
        # groupMeet
        melave_old_groupMeet = [r[0] for r in all_Melave]
        too_old = datetime.today() - timedelta(days=60)
        new_visit_groupMeet = db.session.query(Visit.user_id).filter(Visit.user_id.in_(melave_old_groupMeet),
                                                                     user1.institution_id == institutionId,
                                                                     Visit.title == config.groupMeet_report,
                                                                     Visit.visit_date > too_old).all()
        for i in new_visit_groupMeet:
            if i[0] in melave_old_groupMeet:
                melave_old_groupMeet.remove(i[0])
        # hazanatMachzor_report
        too_old = datetime.today() - timedelta(days=365)
        isVisitenterMahzor = False
        visitenterMahzor = db.session.query(Visit.visit_date).filter(Visit.user_id == mosadCoordinator,
                                                                     Visit.title == config.hazanatMachzor_report,
                                                                     Visit.visit_date > too_old).all()
        if visitenterMahzor:
            isVisitenterMahzor = True
        # DoForBogrim
        too_old = datetime.today() - timedelta(days=365)
        visitDoForBogrim = db.session.query(Visit.visit_date, Visit.title, Visit.description).filter(
            Visit.user_id == mosadCoordinator, Visit.title.in_(config.report_as_DoForBogrim),
            Visit.visit_date > too_old).all()
        # MelavimMeeting
        old_Melave_ids_MelavimMeeting = [r[0] for r in all_Melave]
        too_old = datetime.today() - timedelta(days=120)
        new_MelavimMeeting = db.session.query(Visit.visit_date).distinct(Visit.visit_date).filter(
            Visit.user_id == user1.id,
            user1.institution_id == institutionId,
            Visit.title == config.MelavimMeeting_report,
            Visit.visit_date > too_old).all()
        for i in new_MelavimMeeting:
            if i[0] in old_Melave_ids_MelavimMeeting:
                old_Melave_ids_MelavimMeeting.remove(i[0])

        # forgoten apprentice
        too_old = datetime.today() - timedelta(days=100)
        all_apprenties_mosad_forgoten = db.session.query(Apprentice.id).filter(
            Apprentice.institution_id == institutionId, Apprentice.association_date < too_old).all()
        all_apprenties_mosad_forgoten = [r[0] for r in all_apprenties_mosad_forgoten]
        newvisitcalls = db.session.query(Visit.ent_reported).filter(Apprentice.id == Visit.ent_reported,
                                                                    Institution.id == Apprentice.institution_id,
                                                                    Institution.id == institutionId,
                                                                    or_(Visit.title.in_(config.reports_as_call),
                                                                        Visit.title.in_(config.report_as_meet)),
                                                                    Visit.visit_date > too_old).all()
        for i in newvisitcalls:
            if i[0] in all_apprenties_mosad_forgoten:
                all_apprenties_mosad_forgoten.remove(i[0])
        forgotenApprentice_full_details = db.session.query(Institution.name, Apprentice.name, Apprentice.last_name,
                                                           Apprentice.base_address, Apprentice.army_role,
                                                           Apprentice.unit_name,
                                                           Apprentice.marriage_status, Apprentice.serve_type,
                                                           Apprentice.hadar_plan_session).filter(
            Apprentice.id.in_(list(all_apprenties_mosad_forgoten)), Apprentice.institution_id == Institution.id).all()

        forgotenApprentice_full_details = [
            {"Institution_name": row[0], "name": row[1], "last_name": row[2], "base_address": row[3],
             "army_role": row[4], "unit_name": row[5], "marriage_status": row[6],
             "serve_type": row[7], "hadar_plan_session": row[8]} for row in
            [tuple(row) for row in
             forgotenApprentice_full_details]] if forgotenApprentice_full_details is not None else []
        mosad_Coordinators_score1, visitprofessionalMeet_melave_avg, avg_matzbarMeeting_gap, total_avg_call, total_avg_meet, total_avg_groupmeet = mosad_Coordinators_score(
            mosadCoordinator)
        return jsonify({

            'mosadCoordinator_score': mosad_Coordinators_score1,
            'good_Melave_ids_sadna': len(all_Melave) - len(Melaves_old_professional),
            'all_Melave_mosad_count': len(all_Melave),
            'good_Melave_ids_matzbar': len(all_Melave) - len(old_Melave_ids_matzbar),
            'all_apprenties_mosad': len(all_apprenties_mosad),
            'good_apprenties_mosad_call': len(all_apprenties_mosad) - len(old_apprenties_mosad_old_call),
            'good_apprenties_mosad_meet': len(all_apprenties_mosad) - len(old_apprenties_mosad_old_meet),
            'good_apprentice_mosad_groupMeet': len(all_Melave) - len(melave_old_groupMeet),
            'isVisitenterMahzor': isVisitenterMahzor,
            'visitDoForBogrim': len(visitDoForBogrim),
            'new_MelavimMeeting': len(new_MelavimMeeting),
            'avg_presence_MelavimMeeting': (len(all_Melave) - len(old_Melave_ids_MelavimMeeting)) / len(
                all_Melave) if len(all_Melave) != 0 else 0,
            'Apprentice_forgoten_count': len(all_apprenties_mosad_forgoten),
            'numOfQuarter_passed': numOfQuarter_passed,

            'visitprofessionalMeet_melave_avg': visitprofessionalMeet_melave_avg,
            'avg_matzbarMeeting_gap': avg_matzbarMeeting_gap,
            'avg_apprenticeCall_gap': total_avg_call,
            'avg_apprenticeMeeting_gap': total_avg_meet,
            'avg_groupMeeting_gap': total_avg_groupmeet,
            "visitDoForBogrim_list": [{"visit_date": toISO(row[0]), "title": row[1], "description": row[2],
                                       "daysFromNow": (date.today() - row[0]).days} for row in visitDoForBogrim],
            'forgotenApprentice_full_details': forgotenApprentice_full_details,
            'MelavimMeeting_todo': numOfQuarter_passed * 3,
            'avg_presence_professionalMeeting_monthly': fetch_Diagram_monthly(mosadCoordinator,
                                                                              config.proffesionalMeet_presence),
            'avg_matzbarMeeting_gap_monthly': fetch_Diagram_monthly(mosadCoordinator, config.matzbarMeeting_gap),
            'avg_apprenticeCall_gap_monthly': fetch_Diagram_monthly(mosadCoordinator, config.apprenticeCall_gap),
            'avg_apprenticeMeeting_gap_monthly': fetch_Diagram_monthly(mosadCoordinator, config.apprenticeMeeting_gap),
            'forgotenApprentice_rivonly': fetch_Diagram_rivonly(mosadCoordinator, config.forgotenApprentice_cnt),
        }), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST


@madadim_form_blueprint.route("/eshcolCoordinator", methods=['GET'])
def EshcolCoordinator():
    try:
        if correct_auth()==False:
            return jsonify({'result': f"wrong access token "}), HTTPStatus.OK
        eshcolCoordinatorId = request.args.get("eshcolCoordinator")
        # get  Eshcol id
        eshcol = db.session.query(user1.eshcol).filter(user1.id == eshcolCoordinatorId,
                                                       user1.role_ids.contains("2")).first()
        if eshcol is None:
            return jsonify({'result': "not  eshcolCoordinator", }), HTTPStatus.OK
        all_MosadCoordinator = db.session.query(user1.id).filter(user1.eshcol == eshcol[0],
                                                                 user1.role_ids.contains("1")).all()
        all_EshcolApprentices = db.session.query(Apprentice.id).filter(Apprentice.institution_id == Institution.id,
                                                                       Institution.eshcol_id == str(eshcol[0])).all()
        # MosadEshcolMeeting
        MosadCoordinator_old_MosadEshcolMeeting = [r[0] for r in all_MosadCoordinator]
        too_old = datetime.today() - timedelta(days=30)
        new_visit_MosadEshcolMeeting = db.session.query(Visit.user_id).filter(Visit.ent_reported == user1.id,
                                                                              user1.eshcol == eshcol[0],
                                                                              Visit.title == config.MOsadEshcolMeeting_report,
                                                                              Visit.visit_date > too_old).all()
        for i in new_visit_MosadEshcolMeeting:
            if i[0] in MosadCoordinator_old_MosadEshcolMeeting:
                MosadCoordinator_old_MosadEshcolMeeting.remove(i[0])
        current_month = datetime.today().month
        start_Of_year = datetime.today() - timedelta(days=30 * current_month)
        # tochnitMeeting_report
        newvisit_yeshiva_Tohnit = db.session.query(Visit.visit_date).filter(Visit.user_id == eshcolCoordinatorId,
                                                                            Visit.title == config.tochnitMeeting_report,
                                                                            Visit.visit_date > start_Of_year).all()

        # forgoten-no reports_as_call
        too_old = datetime.today() - timedelta(days=100)
        Apprentice_eshcol_forgoten = db.session.query(Apprentice.id).filter(Apprentice.eshcol == eshcol[0],
                                                                            Apprentice.association_date < too_old).all()
        Apprentice_eshcol_forgoten = [r[0] for r in Apprentice_eshcol_forgoten]
        newvisitcalls = db.session.query(Visit.ent_reported).filter(Apprentice.id == Visit.ent_reported,
                                                                    Institution.id == Apprentice.institution_id,
                                                                    or_(Visit.title.in_(config.reports_as_call),
                                                                        Visit.title.in_(config.report_as_meet)),
                                                                    Visit.visit_date > too_old).all()
        for i in newvisitcalls:
            if i[0] in Apprentice_eshcol_forgoten:
                Apprentice_eshcol_forgoten.remove(i[0])
        forgotenApprentice_full_details = db.session.query(Institution.name, Apprentice.name, Apprentice.last_name,
                                                           Apprentice.base_address, Apprentice.army_role,
                                                           Apprentice.unit_name,
                                                           Apprentice.marriage_status, Apprentice.serve_type,
                                                           Apprentice.hadar_plan_session).filter(
            Apprentice.id.in_(list(Apprentice_eshcol_forgoten)), Apprentice.institution_id == Institution.id).all()

        forgotenApprentice_full_details = [
            {"Institution_name": row[0], "name": row[1], "last_name": row[2], "base_address": row[3],
             "army_role": row[4], "unit_name": row[5], "marriage_status": row[6],
             "serve_type": row[7], "hadar_plan_session": row[8]} for row in
            [tuple(row) for row in
             forgotenApprentice_full_details]] if forgotenApprentice_full_details is not None else []
        eshcolCoordinator_score1, avg__mosad_racaz_meeting_monthly = eshcol_Coordinators_score(eshcolCoordinatorId)
        return jsonify({
            'eshcolCoordinator_score': eshcolCoordinator_score1,
            'all_MosadCoordinator_count': len(all_MosadCoordinator),
            'good__mosad_racaz_meeting': len(all_MosadCoordinator) - len(MosadCoordinator_old_MosadEshcolMeeting),
            'newvisit_yeshiva_Tohnit_precent': 100 * len(newvisit_yeshiva_Tohnit) / current_month,
            'yeshiva_Tohnit_todo': current_month,
            'newvisit_yeshiva_Tohnit': len(newvisit_yeshiva_Tohnit),
            'Apprentice_forgoten_count': len(Apprentice_eshcol_forgoten),
            'all_EshcolApprentices_count': len(all_EshcolApprentices),
            'avg__mosad_racaz_meeting_monthly': avg__mosad_racaz_meeting_monthly,
            'avg__mosad_racaz_meeting_monthly_Diagram': fetch_Diagram_monthly(eshcolCoordinatorId,
                                                                              config.mosad_racaz_meeting),

            'forgotenApprentice_full_details': forgotenApprentice_full_details,
            'forgotenApprentice_4_rivonly': fetch_Diagram_rivonly(eshcolCoordinatorId, config.forgotenApprentice_cnt),

        }), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST


def melave_score(melaveId):
    try:
        call_wight = 20
        presonalMeet_wight = 20
        groupMeet_wight = 20
        cenes_wight = 5
        horim_wight = 10
        proffesional_wight = 5
        monthlyYeshiva_wight = 10
        basis_wight = 10
        madadim_setting1 = db.session.query(madadim_setting).first()

        # compute score diagram
        all_melave_Apprentices = db.session.query(Apprentice.id).filter(
            Apprentice.accompany_id == melaveId).all()
        if len(all_melave_Apprentices) == 0:
            print(melaveId)
            return 100, 0, 0, 0
        # call_score
        visitcalls = db.session.query(Visit.ent_reported, Visit.visit_date).filter(
            Visit.title.in_(config.reports_as_call), Visit.user_id == melaveId,
                                                     Visit.visit_date > madadim_setting1.call_madad_date).order_by(
            Visit.visit_date).all()
        call_score, call_gap_avg = compute_visit_score(all_melave_Apprentices, visitcalls, call_wight, 21, melaveId)
        # personal_meet_score
        visitmeetings = db.session.query(Visit.ent_reported, Visit.visit_date).filter(
            Visit.title.in_(config.report_as_meet), Visit.user_id == melaveId,
                                                    Visit.visit_date > madadim_setting1.meet_madad_date).order_by(
            Visit.visit_date).all()
        personal_meet_score, personal_meet_gap_avg = compute_visit_score(all_melave_Apprentices, visitmeetings,
                                                                         presonalMeet_wight, 90, melaveId)
        # group_meeting
        group_meeting = db.session.query(Visit.ent_reported, func.max(Visit.visit_date).label("visit_date")).group_by(
            Visit.ent_reported).filter(Visit.title == config.groupMeet_report, Visit.user_id == melaveId,
                                       Visit.visit_date > madadim_setting1.groupMeet_madad_date).all()
        association_date = db.session.query(user1.association_date).filter(
            user1.id == melaveId).first()
        group_meeting_score = 0
        group_meeting_gap_avg = (date.today() - association_date.association_date).days
        if group_meeting_score:
            init_gap = (group_meeting[0][
                            1] - association_date.association_date).days if association_date is not None else 0
            group_meeting_gap = init_gap
            for index in range(1, len(group_meeting)):
                group_meeting_gap += (group_meeting[index][1] - group_meeting[index - 1][1]).days if group_meeting[
                                                                                                         index] is not None else 21
            group_meeting_gap_avg = group_meeting_gap / len(group_meeting + 1)
            group_meeting_panish = group_meeting_gap_avg - 60
            if group_meeting_panish > 0:
                group_meeting_score = groupMeet_wight - group_meeting_panish / 2
            else:
                group_meeting_score = groupMeet_wight
            if group_meeting_score < 0:
                group_meeting_score = 0
        # professional_2monthly
        professional_2monthly = db.session.query(Visit.user_id,
                                                 func.max(Visit.visit_date).label("visit_date")).group_by(
            Visit.user_id).filter(Visit.title == config.professional_report, Visit.ent_reported == melaveId).first()
        gap = (date.today() - professional_2monthly.visit_date).days if professional_2monthly is not None else 100
        professional_2monthly_score = 0
        if gap < 90:
            professional_2monthly_score += proffesional_wight
        current_month = datetime.today().month
        start_Of_prev_year = datetime.today() - timedelta(days=30 * current_month + 30 * 12)
        # _yearly_cenes
        _yearly_cenes = db.session.query(system_report).filter(system_report.type == config.cenes_report,
                                                               system_report.creation_date > start_Of_prev_year).all()
        cenes_yearly_score = 0
        if len(_yearly_cenes) > 0:
            start_Of_year = datetime.today() - timedelta(days=30 * current_month)

            newvisit_cenes = db.session.query(Visit.user_id).filter(Visit.user_id == melaveId,
                                                                    Visit.title == config.cenes_report,
                                                                    Visit.visit_date > start_Of_year).all()
            if len(newvisit_cenes) > 0:
                cenes_yearly_score += cenes_wight
        else:
            cenes_yearly_score += cenes_wight
        # yeshiva_monthly
        yeshiva_monthly = db.session.query(Visit.user_id, func.max(Visit.visit_date).label("visit_date")).group_by(
            Visit.user_id).filter(Visit.title == config.MelavimMeeting_report, Visit.ent_reported == melaveId).first()
        gap = (date.today() - yeshiva_monthly.visit_date).days if yeshiva_monthly is not None else 100
        yeshiva_monthly_score = 0
        if gap < 31:
            yeshiva_monthly_score += monthlyYeshiva_wight
        # Horim_meeting
        Horim_meeting = db.session.query(Visit.ent_reported).filter(Visit.title == config.HorimCall_report,
                                                                    Visit.user_id == melaveId).all()
        Horim_meeting_score = (len(Horim_meeting) / len(all_melave_Apprentices)) * horim_wight

        too_old = datetime.today() - timedelta(days=365)
        # base_meeting
        base_meeting = db.session.query(Visit.visit_date).distinct(Visit.visit_date).filter(
            Visit.title == config.basis_report, Visit.visit_in_army == True,
            Visit.visit_date > too_old, Visit.user_id == melaveId).group_by(Visit.visit_date).count()
        base_meeting_score = 0
        if base_meeting > 3:
            base_meeting_score += basis_wight
        melave_score = base_meeting_score + Horim_meeting_score + professional_2monthly_score + yeshiva_monthly_score + \
                       cenes_yearly_score + \
                       group_meeting_score + personal_meet_score + call_score
        return melave_score, call_gap_avg, personal_meet_gap_avg, group_meeting_gap_avg
    except Exception as e:
        print(str(e))


def mosad_Coordinators_score(mosadCoord_id):
    melaveScore_wight = 30
    bogrim_wight = 5
    proffesional_wight = 10
    monthlyYeshiva_wight = 10
    hazana_wight = 10
    ahraiYeshva_wight = 5
    matzbar_wight = 30
    madadim_setting1 = db.session.query(madadim_setting).first()

    try:
        user_prof = db.session.query(user1.institution_id, user1.association_date).filter(
            user1.id == mosadCoord_id).first()
        all_Mosad_Melave = db.session.query(user1.id).filter(user1.role_ids.contains("0"),
                                                             user1.institution_id == user_prof[0]).all()

        if len(all_Mosad_Melave) == 0:
            return 100, 0, 0, 0, 0, 0
        all_Mosad_Melaves_list = [r[0] for r in all_Mosad_Melave]

        total_melave_score = 0
        Mosad_coord_score = 0
        personal_meet_gap_avg = 0
        call_gap_avg = 0
        group_meeting_gap_avg = 0
        # avg call,meet from all melaves
        for melaveId in all_Mosad_Melaves_list:
            melave_score1, call_gap_avg, personal_meet_gap_avg, group_meeting_gap_avg = melave_score(melaveId)
            total_melave_score += melave_score1
            personal_meet_gap_avg += personal_meet_gap_avg
            call_gap_avg += call_gap_avg
            group_meeting_gap_avg += group_meeting_gap_avg
        total_melave_score = total_melave_score / len(all_Mosad_Melaves_list)
        personal_meet_gap_avg = personal_meet_gap_avg / len(all_Mosad_Melaves_list)
        call_gap_avg = call_gap_avg / len(all_Mosad_Melaves_list)
        group_meeting_gap_avg = group_meeting_gap_avg / len(all_Mosad_Melaves_list)

        # interaction=30
        Mosad_coord_score += melaveScore_wight * total_melave_score / 100
        # מצבר==20
        visit_matzbar_meetings = db.session.query(Visit.ent_reported, Visit.visit_date).filter(
            Visit.visit_date > madadim_setting1.matzbarmeet_madad_date, Visit.title == config.matzbar_report).filter(
            Visit.ent_reported.in_(list(all_Mosad_Melaves_list))).order_by(Visit.visit_date).all()
        visit_matzbar_meetings_score, visitMatzbar_melave_avg = compute_visit_score_users(all_Mosad_Melave,
                                                                                          visit_matzbar_meetings,
                                                                                          matzbar_wight, 90,
                                                                                          mosadCoord_id)
        Mosad_coord_score += visit_matzbar_meetings_score
        # מפגש_מקצועי=10
        visit_mosad_professional_meetings = db.session.query(Visit.ent_reported, Visit.visit_date).filter(
            Visit.visit_date > madadim_setting1.professionalMeet_madad_date,
            Visit.title == config.professional_report).filter(
            Visit.ent_reported.in_(list(all_Mosad_Melaves_list))).order_by(Visit.visit_date).all()
        visit_mosad_professional_meetings_score, visitprofessionalMeet_melave_avg = compute_visit_score_users(
            all_Mosad_Melave, visit_mosad_professional_meetings, proffesional_wight, 90, mosadCoord_id)
        Mosad_coord_score += visit_mosad_professional_meetings_score

        # ישיבת_מלוים=10
        todays_Month = dates.HebrewDate.today().month
        if todays_Month == 2 or todays_Month == 6 or todays_Month == 8:
            Mosad_coord_score += 10  # nisan ,Av and Tishrey dont compute
            Mosad_coord_score += 5  # precence of melavim
        else:
            visit_mosad_yeshiva = db.session.query(Visit.ent_reported, Visit.visit_date).filter(
                Visit.visit_date > madadim_setting1.eshcolMosadMeet_madad_date,
                Visit.title == config.MelavimMeeting_report).filter(
                Visit.ent_reported.in_(list(all_Mosad_Melaves_list))).order_by(Visit.visit_date).all()
            visit_mosad_yeshiva_score, visitprofessionalMeet_melave_avg = compute_visit_score_users(all_Mosad_Melave,
                                                                                                    visit_mosad_yeshiva,
                                                                                                    monthlyYeshiva_wight,
                                                                                                    30, mosadCoord_id)
            Mosad_coord_score += visit_mosad_professional_meetings_score
        # עשייה_לבוגרים=5
        d = user_prof.association_date
        association_date_converted = datetime(d.year, d.month, d.day)
        gap_since_created = (datetime.today() - association_date_converted).days
        current_month = datetime.today().month
        too_old = datetime.today() - timedelta(days=30 * current_month)
        visit_did_for_apprentice = db.session.query(Visit.user_id,
                                                    ).filter(Visit.title.in_(config.report_as_DoForBogrim),
                                                             Visit.user_id == mosadCoord_id,
                                                             Visit.visit_date > too_old).all()
        if len(visit_did_for_apprentice) >= current_month / 3 or gap_since_created < 120:
            Mosad_coord_score += bogrim_wight

        # ישיבה אחראי תוכנית=5
        too_old = datetime.today() - timedelta(days=31)
        is_tochnitMeeting_exist = db.session.query(Visit.user_id,
                                                   ).filter(Visit.title == config.tochnitMeeting_report,
                                                            Visit.visit_date > too_old).first()
        tochnitMeeting_report1 = db.session.query(Visit.user_id,
                                                  ).filter(Visit.title == config.tochnitMeeting_report,
                                                           Visit.ent_reported == mosadCoord_id,
                                                           Visit.visit_date > too_old).first()
        if not is_tochnitMeeting_exist or tochnitMeeting_report1:
            Mosad_coord_score += ahraiYeshva_wight

        # הזנת_מחזור_חדש=10
        too_old = datetime.today() - timedelta(days=365)
        visit_Hazana_new_THsession = db.session.query(Visit.user_id,
                                                      func.max(Visit.visit_date).label("visit_date")).group_by(
            Visit.user_id).filter(Visit.title == config.hazanatMachzor_report, Visit.user_id == mosadCoord_id,
                                  Visit.visit_date > too_old).all()
        start_Of_year = datetime.today() - timedelta(days=30 * current_month)
        d = user_prof.association_date
        if datetime(d.year, d.month, d.day) > start_Of_year or len(visit_Hazana_new_THsession) >= 1:
            Mosad_coord_score += hazana_wight

        return Mosad_coord_score, visitprofessionalMeet_melave_avg, visitMatzbar_melave_avg, call_gap_avg, personal_meet_gap_avg, group_meeting_gap_avg
    except Exception as e:
        print(str(e))
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST


def eshcol_Coordinators_score(eshcolCoord_id):
    eshcol = db.session.query(user1.eshcol).filter(user1.id == eshcolCoord_id).first()[0]
    all_eshcol_mosadCoord = db.session.query(user1.id).filter(user1.role_ids.contains("1"),
                                                              user1.eshcol == eshcol).all()
    all_eshcol_apprentices = db.session.query(Apprentice.id).filter(
        Apprentice.eshcol == eshcol).all()
    if len(all_eshcol_mosadCoord) == 0:
        return 100, 0
    madadim_setting1 = db.session.query(madadim_setting).first()

    all_eshcol_mosadCoord_list = [r[0] for r in all_eshcol_mosadCoord]
    visit_MOsadEshcolMeeting_report = db.session.query(Visit).filter(Visit.user_id == eshcolCoord_id,
                                                                     Visit.title == config.MOsadEshcolMeeting_report,
                                                                     Visit.visit_date > madadim_setting1.eshcolMosadMeet_madad_date).all()
    MOsadEshcolMeeting_score, MOsadEshcolMeeting_avg = compute_visit_score_users(all_eshcol_mosadCoord,
                                                                                 visit_MOsadEshcolMeeting_report, 60,
                                                                                 30, eshcolCoord_id)
    # tochnitMeeting_report
    too_old = datetime.today() - timedelta(days=31)
    is_tochnitMeeting_exist = db.session.query(Visit.user_id,
                                               ).filter(Visit.title == config.tochnitMeeting_report,
                                                        Visit.visit_date > too_old).first()
    tohnit_yeshiva = db.session.query(Visit.ent_reported,
                                      func.max(Visit.visit_date).label("visit_date")).group_by(
        Visit.ent_reported).filter(Visit.title == config.tochnitMeeting_report,
                                   Visit.ent_reported == eshcolCoord_id).first()
    gap = (date.today() - tohnit_yeshiva.visit_date).days if tohnit_yeshiva is not None else 100
    tohnit_yeshiva_score = 0
    if not is_tochnitMeeting_exist or gap < 30:
        tohnit_yeshiva_score += 40
    # forgoten apprentice
    Apprentice_ids_forgoten = [r[0] for r in all_eshcol_apprentices]
    too_old = datetime.today() - timedelta(days=100)
    Oldvisitcalls = db.session.query(Visit.ent_reported).filter(
        Apprentice.id == Visit.ent_reported,
        eshcol == Apprentice.eshcol,
        or_(Visit.title == config.call_report, Visit.title == config.groupMeet_report,
            Visit.title == config.personalMeet_report),
        Visit.visit_date > too_old).all()
    for i in Oldvisitcalls:
        if i[0] in Apprentice_ids_forgoten:
            Apprentice_ids_forgoten.remove(i[0])
    eshcolCoord_score = tohnit_yeshiva_score + MOsadEshcolMeeting_score

    return eshcolCoord_score, MOsadEshcolMeeting_avg


@madadim_form_blueprint.route("/mosadot_scores", methods=['GET'])
def mosadot_scores():
    institotionList = db.session.query(Institution.id, Institution.name, Institution.eshcol_id).all()
    mosadlist_score = []
    for institution_ in institotionList:
        mosad__score1, forgotenApprentice_Mosad1 = mosad_score(institution_[0])
        mosadlist_score.append({"institution": institution_[0], "mosad__score": mosad__score1})
    return jsonify(mosadlist_score), HTTPStatus.OK


def mosad_score(institution_id):
    melaveScore_wight = 72
    mosad_Coordinators_score_wight = 7
    forgtenAppren_wight = 16.6
    bogrim_wight = 3

    mosad_score = 0
    try:
        mosadCoord_id = db.session.query(user1.id).filter(user1.role_ids.contains("1"),
                                                          user1.institution_id == institution_id).first()
        all_Mosad_Melave = db.session.query(user1.id).filter(user1.role_ids.contains("0"),
                                                             user1.institution_id == institution_id).all()
        all_Mosad_apprentices = db.session.query(Apprentice.id).filter(
            Apprentice.institution_id == institution_id).all()

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
        mosad_Coordinators_score1, visitprofessionalMeet_melave_avg, avg_matzbarMeeting_gap, total_avg_call, total_avg_meet, groupNeeting_gap_avg = mosad_Coordinators_score(
            mosadCoord_id[0])
        mosad_score += mosad_Coordinators_score_wight * mosad_Coordinators_score1 / 100

        # forgoten apppre
        forgoten_Apprentice_count = forgotenApprentice_Mosad(institution_id,False)[0].json
        mosad_score += forgtenAppren_wight * (len(all_Mosad_apprentices) - len(forgoten_Apprentice_count)) / len(
            all_Mosad_apprentices) if len(all_Mosad_apprentices) != 0 else 16.6

        # עשייה_לבוגרים=5
        too_old = datetime.today() - timedelta(days=365)
        visit_did_for_apprentice = db.session.query(Visit.user_id,
                                                    ).filter(Visit.title.in_(config.report_as_DoForBogrim),
                                                             Visit.user_id == mosadCoord_id[0],
                                                             Visit.visit_date > too_old).all()
        mosad_score += bogrim_wight * len(visit_did_for_apprentice)
        return mosad_score, forgoten_Apprentice_count
    except Exception as e:
        print(str(e))
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST


def compute_visit_score(all_children, visits, maxScore, expected_gap, user_id):
    all_children_ids = [r[0] for r in all_children]

    from collections import defaultdict
    visitcalls_melave_list = defaultdict(list)
    # key is apprenticeId and value is list of  gaps visits date
    for index in range(0, len(visits)):
        visitcalls_melave_list[visits[index][0]].append(visits[index][1])
    # print(visitcalls_melave_list)
    visitcalls_melave_avg = 0
    gap_melave_list = defaultdict(list)

    for k, v in visitcalls_melave_list.items():
        association_date = db.session.query(Apprentice.association_date).filter(
            Apprentice.id == k).first()
        init_gap = (v[0] - association_date.association_date).days if association_date is not None else 0
        gap_melave_list[k] = init_gap
        for index in range(1, len(v)):
            gap = (v[index] - v[index - 1]).days if v[index] is not None else 0
            gap_melave_list[k] += gap
            # all_children_ids.remove(k)
        gap_melave_list[k] = gap_melave_list[k] / len(v)
    # at least one apprentice with no calls
    if len(all_children_ids) != len(gap_melave_list):
        association_date = db.session.query(user1.association_date).filter(
            user1.id == user_id).first()
        init_gap = (date.today() - association_date.association_date).days if association_date is not None else 0
        visitcalls_melave_avg = init_gap
    else:
        visitcalls_melave_avg = sum(gap_melave_list.values()) / len(gap_melave_list) if len(
            gap_melave_list) != 0 else 1000
    call_panish = visitcalls_melave_avg - expected_gap
    if call_panish > 0:
        call_score = maxScore - call_panish / 2
    else:
        call_score = maxScore
    if call_score < 0:
        call_score = 0
    return call_score, visitcalls_melave_avg


def compute_visit_score_users(all_children, visits, maxScore, expected_gap, user_id):
    all_children_ids = [r[0] for r in all_children]

    from collections import defaultdict
    visitcalls_melave_list = defaultdict(list)
    # key is apprenticeId and value is list of  gaps visits date
    for index in range(0, len(visits)):
        visitcalls_melave_list[visits[index][0]].append(visits[index][1])
    # print(visitcalls_melave_list)
    visitcalls_melave_avg = 0
    gap_melave_list = defaultdict(list)

    for k, v in visitcalls_melave_list.items():
        association_date = db.session.query(user1.association_date).filter(
            user1.id == k).first()
        init_gap = (v[0] - association_date.association_date).days if association_date is not None else 0
        gap_melave_list[k] = init_gap
        for index in range(1, len(v)):
            gap = (v[index] - v[index - 1]).days if v[index] is not None else 0
            gap_melave_list[k] += gap
            # all_children_ids.remove(k)
        gap_melave_list[k] = gap_melave_list[k] / len(v)
    # at least one apprentice with no calls
    if len(all_children_ids) != len(gap_melave_list):
        association_date = db.session.query(user1.association_date).filter(
            user1.id == user_id).first()
        init_gap = (date.today() - association_date.association_date).days if association_date is not None else 0
        visitcalls_melave_avg = init_gap
    else:
        visitcalls_melave_avg = sum(gap_melave_list.values()) / len(gap_melave_list) if len(
            gap_melave_list) != 0 else 1000
    call_panish = visitcalls_melave_avg - expected_gap
    if call_panish > 0:
        call_score = maxScore - call_panish / 2
    else:
        call_score = maxScore
    if call_score < 0:
        call_score = 0
    return call_score, visitcalls_melave_avg
