

from flask import Blueprint
from http import HTTPStatus

from src.routes.utils.firebase_service import send_push_notification
from ..logic.notifications import insert_notifications_for_user

from ..logic.update_task_table import add_next_task_to_table, add_tasks_to_table

from ..models.notification_model import notifications

from ..models.user_model import User
from src.services import db
from flask import request, jsonify

notification_form_blueprint = Blueprint(
    "notifications", __name__, url_prefix="/notifications"
)




@notification_form_blueprint.route("/send_notification", methods=["POST"])
def send_notification():
    data = request.json
    userId = data.get("userId")
    title = data.get("title")
    body = data.get("body")
    notification_type = data.get("notification_type")  # Optional
    notification_id = data.get("notification_id")  # Optional
    extra = data.get("extra", {})  # Optional, defaults to an empty map
    user_ent = (
        db.session.query(User.id, User.fcmToken).filter(User.id == userId).first()
    )
    if not user_ent or not str(user_ent.fcmToken) or not title or not body:
        return jsonify({"error": "Missing token, title, or body"}), 400

    # Call the service to send notification
    response = send_push_notification(
        user_ent.fcmToken, title, body, notification_type, notification_id, extra
    )

    if response:
        return (
            jsonify(
                {"message": "Notification sent successfully", "response": response}
            ),
            200,
        )
    else:
        return jsonify({"error": "Failed to send notification"}), 500




@notification_form_blueprint.route("/add_tasks_to_table", methods=["GET"])
def add_task_to_table_all_users():
    try:
        user_ent_list = db.session.query(User.id, User.fcmToken,User.name).all()
        not_committed=[]
        for user_ in user_ent_list:
            try:
                print(user_.id)
                add_tasks_to_table(user_.id)
                print("add_tasks_to_table finished")
                not_committed1,result_list=insert_notifications_for_user(user_)
                print("insert_notifications_for_user finished")
                not_committed=not_committed+not_committed1

            except Exception as e:
                not_committed.append(str(user_.id)+":"+str(e))
        return jsonify({"result":"success","not commited":not_committed}), HTTPStatus.OK
    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST

@notification_form_blueprint.route("/add_tasks_to_table_user", methods=["GET"])
def add_tasks_to_table_user():
    try:
        userId = request.args.get("userId")
        add_tasks_to_table(userId)

        return jsonify({"result":"success"}), HTTPStatus.OK
    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST

@notification_form_blueprint.route("/add_notifications_to_table_user", methods=["GET"])
def add_notifications_to_table_user():
    try:
        userId = request.args.get("userId")
        user_ent = (
            db.session.query(User.id, User.fcmToken, User.name).filter(User.id == userId).first()
        )
        not_committed1,result_list=insert_notifications_for_user(user_ent)
        noti_to_attributes=[noti_.to_attributes() for noti_ in result_list ]
        return jsonify(noti_to_attributes), HTTPStatus.OK
    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST

@notification_form_blueprint.route("", methods=["GET"])
def get_notifications_one_user():
    try:
        userId = request.args.get("userId")
        user_ent = (
            db.session.query(User.id, User.fcmToken,User.name).filter(User.id == userId).first()
        )
        #not_committed, result_list = insert_notifications_for_user(user_ent)
        notifications_ = db.session.query(notifications).filter(notifications.user_id==user_ent.id).all()
        noti_to_attributes=[noti_.to_attributes() for noti_ in notifications_ ]
        return jsonify(noti_to_attributes), HTTPStatus.OK
    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST


@notification_form_blueprint.route("/set_setting", methods=["post"])
def set_setting_notification_form():

    data = request.json

    notifyMorningval = data["notifyMorning"]
    notifyDayBeforeval = data["notifyDayBefore"]
    notifyStartWeekval = data["notifyStartWeek"]
    notifyMorning_weekly_report = data["notifyMorning_weekly_report"]
    notifyMorning_sevev = data["notifyMorning_sevev"]
    notifyDayBefore_sevev = data["notifyDayBefore_sevev"]
    notifyStartWeek_sevev = data["notifyStartWeek_sevev"]

    user = data["userId"]
    user = User.query.get(user)
    user.notifyStartWeek = notifyStartWeekval == "true" or notifyStartWeekval == "True"
    user.notifyDayBefore = notifyDayBeforeval == "true" or notifyDayBeforeval == "True"
    user.notifyMorning = notifyMorningval == "true" or notifyMorningval == "True"
    user.notifyMorning_weekly_report = (
        notifyMorning_weekly_report == "true" or notifyMorning_weekly_report == "True"
    )
    user.notifyMorning_sevev = (
        notifyMorning_sevev == "true" or notifyMorning_sevev == "True"
    )
    user.notifyDayBefore_sevev = (
        notifyDayBefore_sevev == "true" or notifyDayBefore_sevev == "True"
    )
    user.notifyStartWeek_sevev = (
        notifyStartWeek_sevev == "true" or notifyStartWeek_sevev == "True"
    )

    try:
        db.session.commit()
    except:
        return jsonify({"result": "wrong id "}), HTTPStatus.OK

    if user:
        # TODO: add contact form to DB
        return jsonify({"result": "success"}), HTTPStatus.OK


@notification_form_blueprint.route("/get_all_setting", methods=["GET"])
def get_notification_setting_form():
    try:

        user = request.args.get("userId")
        notiSettingList = (
            db.session.query(
                User.notifyMorning,
                User.notifyDayBefore,
                User.notifyStartWeek,
                User.notifyMorning_weekly_report,
                User.notifyMorning_sevev,
                User.notifyDayBefore_sevev,
                User.notifyStartWeek_sevev,
            )
            .filter(User.id == user)
            .first()
        )
        if not notiSettingList:
            # acount not found
            return jsonify(["Wrong id or emty list"])
        else:
            return (
                jsonify(
                    {
                        "notifyMorning": notiSettingList.notifyMorning,
                        "notifyDayBefore": notiSettingList.notifyDayBefore,
                        "notifyStartWeek": notiSettingList.notifyStartWeek,
                        "notifyStartWeek_sevev": notiSettingList.notifyStartWeek_sevev,
                        "notifyDayBefore_sevev": notiSettingList.notifyDayBefore_sevev,
                        "notifyMorning_sevev": notiSettingList.notifyMorning_sevev,
                        "notifyMorning_weekly_report": notiSettingList.notifyMorning_weekly_report,
                    }
                ),
                HTTPStatus.OK,
            )
    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST

@notification_form_blueprint.route("/delete/<string:notification_id>", methods=["DELETE"])
def delete_notification(notification_id):
    notification = notifications.query.get(notification_id)

    if not notification:
        return jsonify({"error": "Notification not found"}), 404

    db.session.delete(notification)
    db.session.commit()

    return jsonify({"message": "success"}), 200

@notification_form_blueprint.route("/<string:notification_id>", methods=["PUT"])
def update_notification(notification_id):
    try:
        notification = notifications.query.get(notification_id)

        if not notification:
            return jsonify({"error": "Notification not found"}), 404

        data = request.json
        if "has_been_read" in data:
            notification.has_been_read = data["has_been_read"]
        
        db.session.commit()
        return jsonify({"message": "success"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST

    # Run the Flask app
