from collections import defaultdict
from datetime import datetime, date, timedelta
from http import HTTPStatus

from flask import request, jsonify
from sqlalchemy import or_, func

from src.models import report_model
from src.models.system_report_model import SystemReport
from src.models.user_model import User
from src.routes.utils.hebrw_date_cust import start_of_year_greg_date, num_of_rivon_passed, \
    get_hebrew_date_from_greg_date

from src.services import db
from src.models.apprentice_model import Apprentice

from src.models.institution_model import Institution

from src.models.report_model import Report


def report_status_apprentice_priod_mosad(all_Apprentices):
    low_score_list = []

    for Apprentice1 in all_Apprentices:
        visitEvent_call = (
            db.session.query(Report)
            .filter(
                Report.ent_reported == Apprentice1.id,
                Report.title.in_(report_model.reports_as_call),
            )
            .order_by(Report.visit_date.desc())
            .first()
        )
        visitEvent_meet = (
            db.session.query(Report)
            .filter(
                Report.ent_reported == Apprentice1.id,
                Report.title.in_(report_model.report_as_meet),
            )
            .order_by(Report.visit_date.desc())
            .first()
        )
        daysFromNow = (
            (date.today() - Apprentice1.association_date).days
            if Apprentice1.association_date is not None
            else 100
        )
        call_gap_window = (
            (date.today() - visitEvent_call.visit_date).days
            if visitEvent_call
            else daysFromNow
        )
        meet_gap_window = (
            (date.today() - visitEvent_meet.visit_date).days
            if visitEvent_meet
            else daysFromNow
        )

        if 65 < call_gap_window < 100 and 65 < meet_gap_window < 100:
            low_score_list.append(str(Apprentice1.id))
    return low_score_list


def report_status_apprentice_priod(all_Apprentices):
    low_score_list = report_status_apprentice_priod_mosad(all_Apprentices)
    inst_no_call_dict = dict()
    # handle no record
    for ent in all_Apprentices:
        if str(ent.id) in low_score_list:
            inst_no_call_dict[ent.Institution_name] = (
                inst_no_call_dict.get(ent.Institution_name, 0) + 1
            )
    return inst_no_call_dict, len(low_score_list)


def report_status_apprentice(all_Apprentices, too_old_, report_type):
    no_visit_meet = report_status_apprentice_mosad(
        all_Apprentices, too_old_, report_type
    )
    no_visit_meet_ids = [str(k) for k, v in no_visit_meet.items()]
    # handle no record
    inst_no_call_dict = dict()
    for ent in all_Apprentices:
        if str(ent.id) in no_visit_meet_ids:
            association_date_gap = (
                (date.today() - ent.association_date).days
                if ent.association_date is not None
                else 100
            )
            if association_date_gap > too_old_:
                inst_no_call_dict[ent.Institution_name] = (
                    inst_no_call_dict.get(ent.Institution_name, 0) + 1
                )
    return inst_no_call_dict, len(no_visit_meet_ids)


def report_status_apprentice_mosad(ApprenticeList, days_count, report_type):
    no_visit_dict = dict()
    for Apprentice1 in ApprenticeList:
        visitEvent = (
            db.session.query(Report)
            .filter(
                Report.ent_reported == Apprentice1.id,
                Report.title.in_(report_type),
            )
            .order_by(Report.visit_date.desc())
            .first()
        )
        daysFromNow = (
            (date.today() - Apprentice1.association_date).days
            if Apprentice1.association_date is not None
            else 100
        )
        if visitEvent is None:
            if daysFromNow > days_count:
                no_visit_dict[str(Apprentice1.id)] = daysFromNow
        else:
            if (
                (date.today() - visitEvent.visit_date).days > days_count
                and Report.ent_reported not in no_visit_dict
                and daysFromNow > days_count
            ):
                daysFromNow = (
                    (date.today() - visitEvent.visit_date).days
                    if visitEvent.visit_date is not None
                    else 100
                )
                no_visit_dict[str(Apprentice1.id)] = daysFromNow
    return no_visit_dict


def compute_forgoten_apprectice(all_Apprentices):
    all_Apprentices_ids = [i.id for i in all_Apprentices]
    too_old = datetime.today() - timedelta(days=100)
    call_reports = (
        db.session.query(
            Report.ent_reported,
            func.max(Report.visit_date).label("visit_date"),
        )
        .filter(
            Report.ent_reported.in_(all_Apprentices_ids),
            or_(
                Report.title.in_(report_model.reports_as_call),
                Report.title.in_(report_model.report_as_meet),
            ),
            Report.visit_date > too_old,
        )
        .group_by(Report.ent_reported)
        .all()
    )
    ids_have_visit = [r[0] for r in call_reports]
    ids_no_visit = []
    # handle no record
    for ent in all_Apprentices:
        if ent.id not in ids_have_visit:
            init_gap = (date.today() - ent.association_date).days
            if init_gap > 100:
                ids_no_visit.append(ent)
    inst_no_call_dict = dict()
    missingCallApprentice_total = 0
    for i in ids_no_visit:
        missingCallApprentice_total += 1
        inst_no_call_dict[i.Institution_name] = (
            inst_no_call_dict.get(i.Institution_name, 0) + 1
        )
    return inst_no_call_dict, missingCallApprentice_total, [i[0] for i in ids_no_visit]


def forgotenApprentice_Mosad(institution_id="empty", external=True):
    try:

        if institution_id == "empty":
            institution_id = request.args.get("institutionId")
        all_Apprentices = (
            db.session.query(
                Apprentice.id,
                Apprentice.name,
                Apprentice.last_name,
                Institution.name.label("Institution_name"),
                Apprentice.association_date,
            )
            .filter(
                Apprentice.institution_id == institution_id,
                Institution.id == Apprentice.institution_id,
            )
            .all()
        )
        # update apprentices meet
        forgoten_apprentice_per_insti, total_forgoten, ids_no_visit = (
            compute_forgoten_apprectice(all_Apprentices)
        )

        return jsonify([str(r) for r in ids_no_visit]), HTTPStatus.OK
    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST


def fetch_Diagram_monthly(related_id, type="melave_Score"):
    too_old = datetime.today() - timedelta(days=30 * 12)
    data = (
        db.session.query(SystemReport.creation_date, SystemReport.value)
        .filter(
            SystemReport.type == type,
            SystemReport.related_id == related_id,
            SystemReport.creation_date > too_old,
        )
        .all()
    )
    x_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    y_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for row in data:
        month = row[0].month
        value = row[1]
        i = x_list.index(month)
        y_list[i] = int(float(value))
    return (
        x_list,
        y_list,
    )


def fetch_Diagram_rivonly(related_id, type="melave_Score"):
    too_old = datetime.today() - timedelta(days=30 * 12)
    data = (
        db.session.query(SystemReport.creation_date, SystemReport.value)
        .filter(SystemReport.type == type, SystemReport.creation_date > too_old)
        .all()
    )
    x_list = [1, 2, 3, 4]
    y_list = [0, 0, 0, 0]
    for row in data:
        rivon = int(row[0].month / 3)
        value = row[1]
        i = x_list.index(rivon + 1)
        y_list[i] = int(value)
    return x_list, y_list


def fetch_Diagram_yearly(related_id, type="melave_Score"):
    too_old = datetime.today() - timedelta(days=30 * 12)
    data = (
        db.session.query(SystemReport.creation_date, SystemReport.value)
        .filter(SystemReport.type == type, SystemReport.creation_date > too_old)
        .all()
    )
    this_year = datetime.today().year
    x_list = [this_year - 3, this_year - 2, this_year - 1, this_year]
    y_list = [0, 0, 0, 0]
    for row in data:
        year = row[0].year
        value = row[1]
        i = x_list.index(year)
        y_list[i] = int(value)
    this_year_hebrew=get_hebrew_date_from_greg_date(datetime.today())[0]
    x_list = [this_year_hebrew - 3, this_year_hebrew - 2, this_year_hebrew - 1, this_year_hebrew]

    return (
        x_list,
        y_list,
    )


def compute_visit_score(all_children, visits, maxScore, expected_gap, user_id):
    all_children_ids = [r[0] for r in all_children]
    # no child
    if len(all_children_ids) == 0:
        return maxScore, 0
    association_date = (
        db.session.query(User.association_date).filter(User.id == user_id).first()
    )
    init_gap = (
        (date.today() - association_date.association_date).days
        if association_date is not None
        else 0
    )
    # no report
    if len(visits) == 0:
        return 0, init_gap

    visitcalls_melave_list = defaultdict(list)
    # key is apprenticeId and value is list of   visits date
    for index in range(0, len(visits)):
        visitcalls_melave_list[visits[index][0]].append(visits[index][1])
    # key is apprenticeId and value is avg gap for this apprentice
    gap_melave_list = defaultdict(list)
    for k, v in visitcalls_melave_list.items():
        init_gap = (v[0] - association_date.association_date).days
        gap_melave_list[k] = init_gap
        for index in range(1, len(v)):
            gap = (v[index] - v[index - 1]).days if v[index] is not None else 0
            gap_melave_list[k] += gap
        gap_melave_list[k] = gap_melave_list[k] / len(v)
    # at least one apprentice with no calls
    if len(all_children_ids) != len(gap_melave_list):
        visitcalls_melave_avg = init_gap
    else:
        visitcalls_melave_avg = (
            sum(gap_melave_list.values()) / len(gap_melave_list)
            if len(gap_melave_list) != 0
            else 1000
        )
    # avg lower than expacted
    if expected_gap <= visitcalls_melave_avg:
        call_score = maxScore
    else:
        # avg higher than expacted
        call_score = maxScore - (expected_gap - visitcalls_melave_avg) / 2
    if call_score < 0:
        # prevent negative score
        call_score = 0
    return call_score, visitcalls_melave_avg


def compute_group_visit_score(visits, maxScore, expected_gap, user_id):
    association_date = (
        db.session.query(User.association_date).filter(User.id == user_id).first()
    )
    init_gap = (
        (date.today() - association_date.association_date).days
        if association_date is not None
        else 0
    )
    # no report
    if not visits or len(visits) == 0:
        return 0, init_gap
    gap = (visits[0].visit_date - association_date.association_date).days
    for index in range(1, len(visits)):
        gap += (
            (visits[index][1] - visits[index - 1][1]).days
            if visits[index] is not None
            else 0
        )

    avg_gap = gap / len(visits)
    # avg lower than expacted
    if expected_gap <= avg_gap:
        call_score = maxScore
    else:
        # avg higher than expacted
        call_score = maxScore - (expected_gap - avg_gap) / 2
    if call_score < 0:
        # prevent negative score
        call_score = 0
    return call_score, avg_gap


def compute_simple_visit_score(visit, maxScore, expected_gap, user_id, type):
    if type:
        start_Of_year = start_of_year_greg_date()
        _yearly_cenes = (
            db.session.query(SystemReport.creation_date)
            .filter(
                SystemReport.type == type,
                SystemReport.creation_date > start_Of_year,
            )
            .first()
        )
        if not _yearly_cenes:
            return maxScore
    if visit is None:
        return 0
    association_date = (
        db.session.query(User.association_date).filter(User.id == user_id).first()
    )
    gap = (date.today() - visit.visit_date).days
    if (
        gap <= expected_gap
        or (date.today() - association_date.association_date).days < 60
    ):
        return maxScore
    return 0


def apprentice_old_intercation(Apprentice_melaveId, is_mosad_level, report_type):
    Apprentice_old_call = [r[0] for r in Apprentice_melaveId]
    if is_mosad_level:
        melaveIds = [
            Apprentice_melaveId_.accompany_id
            for Apprentice_melaveId_ in Apprentice_melaveId
        ]
    else:
        melaveIds = [Apprentice_melaveId[0].accompany_id]
    too_old = datetime.today() - timedelta(days=21)
    call_reports = (
        db.session.query(Report.ent_reported)
        .filter(
            Report.user_id.in_(melaveIds),
            Report.title.in_(report_type),
            Report.visit_date > too_old,
        )
        .all()
    )
    for i in call_reports:
        if i[0] in Apprentice_old_call:
            Apprentice_old_call.remove(i[0])
    return Apprentice_old_call


def melave_professional_meet_(melaveId):
    start_Of_year = start_of_year_greg_date()
    numOfQuarter_passed = num_of_rivon_passed()
    Proffesional_meet_report = (
        db.session.query(Report.user_id)
        .filter(
            Report.user_id == melaveId,
            Report.title == report_model.professional_report,
            Report.visit_date > start_Of_year,
        )
        .all()
    )
    if numOfQuarter_passed == 0:
        Proffesional_meet_score = 100
    else:
        Proffesional_meet_score = (
            100 * len(Proffesional_meet_report) / numOfQuarter_passed
        )
    return Proffesional_meet_score, Proffesional_meet_report


def get_cenes_score(melaveId):
    start_Of_year = start_of_year_greg_date()
    cenes_since_start_Of_year = (
        db.session.query(SystemReport)
        .filter(
            SystemReport.type == report_model.cenes_report,
            SystemReport.creation_date > start_Of_year,
        )
        .all()
    )
    cenes_reports = []
    if len(cenes_since_start_Of_year) > 0:
        cenes_reports = (
            db.session.query(Report.user_id)
            .filter(
                Report.user_id == melaveId,
                Report.title == report_model.cenes_report,
                Report.visit_date > start_Of_year,
            )
            .all()
        )
        cenes_score = 100 * len(cenes_reports) / len(cenes_since_start_Of_year)
    else:
        cenes_score = 100
    return cenes_score, cenes_since_start_Of_year, cenes_reports


def apprentice_old_horim(Apprentice_old_Horim, melaveId):
    start_Of_year = start_of_year_greg_date()

    horim_reports = (
        db.session.query(Report.ent_reported)
        .filter(
            Report.user_id == melaveId,
            Report.title == report_model.HorimCall_report,
            Report.visit_date > start_Of_year,
        )
        .all()
    )
    for i in horim_reports:
        if i[0] in Apprentice_old_Horim:
            Apprentice_old_Horim.remove(i[0])
    return Apprentice_old_Horim


def forgoten_apprentice_full_details(ids_no_visit):
    forgotenApprentice_full_details = (
        db.session.query(
            Institution.name,
            Apprentice.name,
            Apprentice.last_name,
            Apprentice.base_address,
            Apprentice.army_role,
            Apprentice.unit_name,
            Apprentice.marriage_status,
            Apprentice.serve_type,
            Apprentice.hadar_plan_session,
            Apprentice.id,
        )
        .filter(
            Apprentice.id.in_(list(ids_no_visit)),
            Apprentice.institution_id == Institution.id,
        )
        .all()
    )

    forgotenApprentice_full_details = (
        [
            {
                "Institution_name": row[0],
                "name": row[1],
                "last_name": row[2],
                "base_address": row[3],
                "army_role": row[4],
                "unit_name": row[5],
                "marriage_status": row[6],
                "serve_type": row[7],
                "hadar_plan_session": row[8],
                "id": str(row[9]),
            }
            for row in [tuple(row) for row in forgotenApprentice_full_details]
        ]
        if forgotenApprentice_full_details is not None
        else []
    )
    return forgotenApprentice_full_details


def no_melave_interaction(all_Melave, institutionId, report_type, max_gap):
    all_Melave_ids = [r[0] for r in all_Melave]
    too_old = datetime.today() - timedelta(days=max_gap)
    newvisit_professional = (
        db.session.query(Report.ent_reported)
        .filter(
            Report.user_id == User.id,
            User.institution_id == institutionId,
            Report.title == report_type,
            Report.visit_date > too_old,
        )
        .all()
    )
    for i in newvisit_professional:
        if i[0] in all_Melave_ids:
            all_Melave_ids.remove(i[0])
    return all_Melave_ids


def no_apprentice_interaction(all_Melave, institutionId, report_type, max_gap):
    all_Melave_ids = [r[0] for r in all_Melave]
    too_old = datetime.today() - timedelta(days=max_gap)
    newvisit_professional = (
        db.session.query(Report.user_id)
        .filter(
            Report.user_id == User.id,
            User.institution_id == institutionId,
            Report.title == report_type,
            Report.visit_date > too_old,
        )
        .all()
    )
    for i in newvisit_professional:
        if i[0] in all_Melave_ids:
            all_Melave_ids.remove(i[0])
    return all_Melave_ids


def no_mosad_coordinator_interaction(
    all_MosadCoordinator, cluster, report_type, expected_gap
):
    MosadCoordinator_old_MosadEshcolMeeting = [r[0] for r in all_MosadCoordinator]
    too_old = datetime.today() - timedelta(days=expected_gap)
    new_visit_MosadEshcolMeeting = (
        db.session.query(Report.user_id)
        .filter(
            Report.ent_reported == User.id,
            User.cluster_id == cluster,
            Report.title == report_type,
            Report.visit_date > too_old,
        )
        .all()
    )
    for i in new_visit_MosadEshcolMeeting:
        if i[0] in MosadCoordinator_old_MosadEshcolMeeting:
            MosadCoordinator_old_MosadEshcolMeeting.remove(i[0])
    return MosadCoordinator_old_MosadEshcolMeeting


def interaction_count(all_melaves_ids, madadim_setting1):
    visitcallsCount = (
        db.session.query(Report.ent_reported, Report.visit_date)
        .filter(
            Report.title.in_(report_model.reports_as_call),
            Report.user_id.in_(all_melaves_ids),
            Report.visit_date > madadim_setting1.call_madad_date,
        )
        .order_by(Report.visit_date)
        .count()
    )
    visitMeetCount = (
        db.session.query(Report.ent_reported, Report.visit_date)
        .filter(
            Report.title.in_(report_model.report_as_meet),
            Report.user_id.in_(all_melaves_ids),
            Report.visit_date > madadim_setting1.meet_madad_date,
        )
        .order_by(Report.visit_date)
        .count()
    )
    return visitcallsCount, visitMeetCount


def compute_apprentice_profile(all_Apprentices):
    paying_dict = dict()
    Picud_dict = dict()
    matzbar_dict = dict()
    sugSherut_dict = dict()
    mahzor_dict = dict()
    for apprentice1 in all_Apprentices:
        paying_dict[str(apprentice1.paying).upper()] = (
            paying_dict.get(str(apprentice1.paying).upper(), 0) + 1
        )
        Picud_dict[apprentice1.militaryPositionNew] = (
            Picud_dict.get(apprentice1.militaryPositionNew, 0) + 1
        )
        matzbar_dict[apprentice1.spirit_status] = (
            matzbar_dict.get(apprentice1.spirit_status, 0) + 1
        )
        sugSherut_dict[apprentice1.army_role] = (
            sugSherut_dict.get(apprentice1.army_role, 0) + 1
        )
        mahzor_dict[apprentice1.institution_mahzor] = (
            mahzor_dict.get(apprentice1.institution_mahzor, 0) + 1
        )
    return paying_dict, Picud_dict, matzbar_dict, sugSherut_dict, mahzor_dict
