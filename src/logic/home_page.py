import csv
from io import StringIO

from src.logic.compute_score import (
    eshcol_Coordinators_score,
    mosad_Coordinators_score,
    melave_score,
)
from src.logic.performence_metric import report_status_apprentice_mosad
from src.models import report_model, system_report_model
from src.models.system_report_model import SystemReport
from src.models.user_model import User
from src.routes.utils.hebrw_date_cust import get_hebrew_date_from_greg_date
from src.services import db

from datetime import datetime, date, timedelta


def get_Eshcol_corrdintors_score():
    all_Eshcol_coord = (
        db.session.query(User.id, User.region_id, User.name, User.institution_id)
        .filter(User.role_ids.contains("2"))
        .all()
    )
    eshcol_Cooordinator_score = dict()
    score_EshcolCoordProfile = []
    for Eshcol_coord in all_Eshcol_coord:
        Eshcol_coord_id = Eshcol_coord[0]
        eshcolCoordinator_score1, avg__mosad_racaz_meeting_monthly = (
            eshcol_Coordinators_score(Eshcol_coord_id)
        )
        eshcol_Cooordinator_score[eshcolCoordinator_score1] = (
            eshcol_Cooordinator_score.get(eshcolCoordinator_score1, 0) + 1
        )
        score_EshcolCoordProfile.append(
            {"score": eshcolCoordinator_score1, "id": Eshcol_coord_id}
        )
    ####compuite precentage of deacrese/increase ######
    too_old = datetime.today() - timedelta(days=365)
    Eshcol_corrdintors_score_csv = (
        db.session.query(SystemReport)
        .filter(
            SystemReport.type == system_report_model.eshcol_corrdintors_score_csv,
            SystemReport.creation_date > too_old,
        )
        .all()
    )
    month, score_avg = score_avg_monthly_diagram(
        Eshcol_corrdintors_score_csv, all_Eshcol_coord, 1, 2
    )
    return (month, score_avg), score_EshcolCoordProfile

def get_score_until_current_month(eshcol_Cooordinator_score):
    hebrew_date_=get_hebrew_date_from_greg_date(datetime.today())
    current_month = hebrew_date_[1]
    for month_ in eshcol_Cooordinator_score[0]:#iterate over month
        if month_ > current_month: #if month is  later than today -make it 0
            eshcol_Cooordinator_score[1][month_ - 1]=0
    return eshcol_Cooordinator_score

def red_green_orange_status(all_Apprentices):
    redvisitcalls = 0
    orangevisitcalls = 0
    greenvisitcalls = 0
    redvisitmeetings = 0
    orangevisitmeetings = 0
    greenvisitmeetings = 0
    forgotenApprenticCount = 0
    forgotenApprenticeList = []
    # update apprentices call
    no_visit_call = report_status_apprentice_mosad(
        all_Apprentices, 30, report_model.reports_as_call
    )
    for k, v in no_visit_call.items():
        if v > 100:
            forgotenApprenticeList.append(k)
        if v >= 60:
            redvisitcalls += 1
        if 60 > v > 30:
            orangevisitcalls += 1
    greenvisitcalls = len(all_Apprentices) - redvisitcalls - orangevisitcalls

    no_visit_meet = report_status_apprentice_mosad(
        all_Apprentices, 60, report_model.report_as_meet
    )
    for k, v in no_visit_meet.items():
        if v > 100:
            if k in forgotenApprenticeList:
                forgotenApprenticCount += 1
        if v > 100:
            redvisitmeetings += 1
        if 100 > v > 60:
            orangevisitmeetings += 1
    greenvisitmeetings = len(all_Apprentices) - redvisitmeetings - orangevisitmeetings

    return (
        greenvisitmeetings,
        orangevisitmeetings,
        redvisitmeetings,
        greenvisitcalls,
        orangevisitcalls,
        redvisitcalls,
        forgotenApprenticCount,
    )


def get_mosad_Coordinators_score(cluster_id="0"):
    if cluster_id != "0":
        all_Mosad_coord = (
            db.session.query(User.id, User.institution_id, User.name)
            .filter(User.role_ids.contains("1"), User.cluster_id == cluster_id)
            .all()
        )
    else:
        all_Mosad_coord = (
            db.session.query(User.id, User.institution_id, User.name)
            .filter(User.role_ids.contains("1"))
            .all()
        )
    mosad_Cooordinator_score_dict = dict()
    score_MosadCoordProfile = []
    for mosad_coord in all_Mosad_coord:
        mosadCoordinator = mosad_coord[0]
        (
            mosad_Coordinators_score1,
            visitprofessionalMeet_melave_avg,
            avg_matzbarMeeting_gap,
            total_avg_call,
            total_avg_meet,
            groupNeeting_gap_avg,
        ) = mosad_Coordinators_score(mosadCoordinator)
        mosad_Cooordinator_score_dict[mosad_Coordinators_score1] = (
            mosad_Cooordinator_score_dict.get(mosad_Coordinators_score1, 0) + 1
        )
        score_MosadCoordProfile.append(
            {"id": mosadCoordinator, "score": mosad_Coordinators_score1}
        )
    ####compuite precentage of deacrese/increase ######
    too_old = datetime.today() - timedelta(days=365)
    mosad_corrdintors_score_csv = (
        db.session.query(SystemReport)
        .filter(
            SystemReport.type == system_report_model.mosad_corrdintors_score_csv,
            SystemReport.creation_date > too_old,
        )
        .all()
    )
    month, score_avg = score_avg_monthly_diagram(
        mosad_corrdintors_score_csv, all_Mosad_coord, 2, 1
    )
    return (month, score_avg), score_MosadCoordProfile


def score_avg_monthly_diagram(
    mosad_corrdintors_score_csv, all_melave, value_index, id_index
):
    month = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    score_avg = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    all_melave_ids = [str(i.id) for i in all_melave]
    for record in mosad_corrdintors_score_csv:
        total_melave_score = 0
        if record is not None:
            f = StringIO(record.value)
            reader = csv.reader(f, delimiter=",")
            next(reader, None)  # skip the headers
            num_of_melaves=0
            for row in reader:
                if row and str(row[id_index]) in all_melave_ids:
                    num_of_melaves+=1
                    total_melave_score += int(float(row[value_index]))
            i = month.index(get_hebrew_date_from_greg_date(record.creation_date)[1])+1

            melave_score_avg = total_melave_score / num_of_melaves if num_of_melaves else 0
            score_avg[i] = int(melave_score_avg)
    return month, score_avg


def get_melave_score(cluster_id="0", mosad="0"):
    # compute score diagram
    score_melaveProfile = []
    if cluster_id != "0" and mosad != "0":
        all_melave = (
            db.session.query(User.id, User.name, User.institution_id)
            .filter(
                User.role_ids.contains("0"),
                User.cluster_id == cluster_id,
                User.institution_id == mosad,
            )
            .all()
        )
    elif cluster_id != "0":
        all_melave = (
            db.session.query(User.id, User.name, User.institution_id)
            .filter(User.role_ids.contains("0"), User.cluster_id == cluster_id)
            .all()
        )
    elif mosad != "0":
        all_melave = (
            db.session.query(User.id, User.name, User.institution_id)
            .filter(User.role_ids.contains("0"), User.institution_id == mosad)
            .all()
        )
    else:
        all_melave = (
            db.session.query(User.id, User.name, User.institution_id)
            .filter(User.role_ids.contains("0"))
            .all()
        )
    for melave in all_melave:
        melaveId = melave[0]
        melave_score1, call_gap_avg, meet_gap_avg, group_meeting_gap_avg = melave_score(
            melaveId
        )
        score_melaveProfile.append(
            {"melave_score1": melave_score1, "melaveId": melaveId}
        )
    ####compuite precentage of deacrese/increase ######
    too_old = datetime.today() - timedelta(days=365)
    mosad_corrdintors_score_csv = (
        db.session.query(SystemReport)
        .filter(
            SystemReport.type == system_report_model.melave_score_csv,
            SystemReport.creation_date > too_old,
        )
        .all()
    )
    month, score_avg = score_avg_monthly_diagram(
        mosad_corrdintors_score_csv, all_melave, 2, 3
    )
    return (month, score_avg), score_melaveProfile
