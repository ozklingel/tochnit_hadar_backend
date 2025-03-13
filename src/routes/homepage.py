import datetime
from flask import Blueprint, request, jsonify
from http import HTTPStatus
from datetime import datetime, timedelta
from sqlalchemy import  or_
from src.logic.home_page import (
    red_green_orange_status,
    get_melave_score,
    get_mosad_Coordinators_score,
    get_Eshcol_corrdintors_score, get_score_until_current_month,
)

from src.models.task_model_v2 import Task
from src.routes.tasks import get_task_service
from src.services import db
from src.models.apprentice_model import Apprentice
from src.models.user_model import User


homepage_form_blueprint = Blueprint("homepage", __name__, url_prefix="/homepage")


@homepage_form_blueprint.route("/get_closest_Events", methods=["GET"])
def get_closest_events():
    try:

        user = request.args.get("userId")
        too_old = datetime.today() - timedelta(days=7)

        task_list = (
            db.session.query(Task)
            .filter(
                Task.user_id == user,
                or_(Task.made_by_user == True, Task.name == "יום הולדת"),
                Task.start_date >= too_old,

            )
            .all()
        )
        my_dict = []
        for task_ in task_list:
            daysFromNow = (
                (datetime.today() - task_.start_date).days
                if task_.start_date is not None
                else None
            )
            if daysFromNow and daysFromNow<3:
                my_dict.append(task_)
                continue
        task_service = get_task_service()
        task_list = [task_service._task_to_data(task).to_dict() for task in my_dict]
        return jsonify(task_list), HTTPStatus.OK
    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST




@homepage_form_blueprint.route("/init_program_manager", methods=["GET"])
def init_program_manager():
    all_Apprentices = db.session.query(
        Apprentice.id,
        Apprentice.association_date,
    ).all()
    counts_melave_score, score_melaveProfile_list = get_melave_score()
    mosad_Cooordinator_score, score_MosadCoordProfile_list = (
        get_mosad_Coordinators_score()
    )
    eshcol_Cooordinator_score, score_EshcolCoordProfile_list = (
        get_Eshcol_corrdintors_score()
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
                "eshcol_Cooordinator_score": get_score_until_current_month(eshcol_Cooordinator_score) ,
                "Mosad_Cooordinator_score":  get_score_until_current_month(mosad_Cooordinator_score),
                "melave_score":   get_score_until_current_month(counts_melave_score),
                "totalApprentices": len(all_Apprentices),
                "forgotenApprenticCount": forgotenApprenticCount,
                "orangevisitmeetings": orangevisitmeetings,
                "redvisitmeetings": redvisitmeetings,
                "greenvisitmeetings": greenvisitmeetings,
                "greenvisitcalls": greenvisitcalls,
                "orangevisitcalls": orangevisitcalls,
                "redvisitcalls": redvisitcalls,
                # 'user_lastname':record.last_name,
                # 'user_name':record.name,
            }
        ),
        HTTPStatus.OK,
    )


@homepage_form_blueprint.route("/init_eshcol_coord", methods=["GET"])
def init_eshcol_coord():
    try:
        userId = request.args.get("userId")
        record = User.query.filter_by(id=userId).first()
        all_Apprentices = (
            db.session.query(
                Apprentice.id,
                Apprentice.association_date,
            )
            .filter(Apprentice.cluster_id == record.cluster_id)
            .all()
        )
        counts_melave_score, score_melaveProfile_list = get_melave_score(
            cluster_id=record.cluster_id
        )
        mosad_Cooordinator_score, score_MosadCoordProfile_list = (
            get_mosad_Coordinators_score()
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
                    "score_melaveProfile_list": score_melaveProfile_list,
                    "Mosad_Cooordinator_score": get_score_until_current_month(mosad_Cooordinator_score),
                    "melave_score": get_score_until_current_month(counts_melave_score),
                    "totalApprentices": len(all_Apprentices),
                    "forgotenApprenticCount": forgotenApprenticCount,
                    "orangevisitmeetings": orangevisitmeetings,
                    "redvisitmeetings": redvisitmeetings,
                    "greenvisitmeetings": greenvisitmeetings,
                    "greenvisitcalls": greenvisitcalls,
                    "orangevisitcalls": orangevisitcalls,
                    "redvisitcalls": redvisitcalls,
                    # 'user_lastname':record.last_name,
                    # 'user_name':record.name,
                }
            ),
            HTTPStatus.OK,
        )
    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST


@homepage_form_blueprint.route("/init_mosad_coord", methods=["GET"])
def init_mosad_coord():
    try:
        userId = request.args.get("userId")
        record = User.query.filter_by(id=userId).first()
        all_Apprentices = (
            db.session.query(
                Apprentice.id,
                Apprentice.association_date,
            )
            .filter(Apprentice.institution_id == record.institution_id)
            .all()
        )
        counts_melave_score, score_melaveProfile_list = get_melave_score(
            mosad=record.institution_id
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
                    "score_melaveProfile_list": score_melaveProfile_list,
                    "melave_score": get_score_until_current_month(counts_melave_score),
                    "totalApprentices": len(all_Apprentices),
                    "forgotenApprenticCount": forgotenApprenticCount,
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
