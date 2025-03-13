import uuid

from src.logic.update_task_table import add_next_task_to_table
from src.models.apprentice_model import Apprentice
from src.models.notification_model import notifications, notification_schedule_dict
from src.models.task_model_v2 import  TaskStatusEnum,  Task
from datetime import datetime as dt, date, timedelta, datetime

from src.models.user_model import User
from src.routes.tasks import get_task_service
from src.routes.utils.firebase_service import send_push_notification
from src.routes.utils.hebrw_date_cust import start_of_current_rivon, start_of_year_greg_date, start_of_current_month, \
    get_hebrew_date_from_greg_date, get_last_sunday_date_greg
from src.routes.utils.notification_details import collated_notification_datils
from src.services import db




def get_candidate_notifications(user):
    # send  notifications.
    userEnt = (
        db.session.query(User.notifyStartWeek, User.notifyDayBefore, User.notifyMorning)
        .filter(User.id == user)
        .first()
    )
    tasks = db.session.query(Task).filter(Task.user_id == user,Task.status == TaskStatusEnum.TODO).all()  # to avoid alarm
    my_dict = []
    task_service = get_task_service()

    for noti in tasks:
        try:
            if  not is_need_create_notification(noti):
                continue
            daysFromNow = (
                (datetime.today() - noti.start_date).days
                if noti.start_date is not None
                else None
            )
            if noti.made_by_user == True and daysFromNow == 0:
                add_next_task_to_table(noti)
            if (userEnt.notifyStartWeek == True and date.today().weekday() ==6):#6 is sunday
                if 7 >= daysFromNow >= -7 :  # show row if start day in the next 7 days
                    my_dict.append(noti)
                    continue

            if userEnt.notifyDayBefore == True:
                is_shabat = (
                        date(
                            date.today().year, noti.start_date.month, noti.start_date.day
                        ).weekday()
                        == 5
                )

                if (
                        is_shabat and daysFromNow == -2
                ) or daysFromNow == -1:  # show row if start day in the next 1 days
                    my_dict.append(noti)
                    continue
            if userEnt.notifyMorning == True:
                is_shabat = (
                        date(
                            date.today().year, noti.start_date.month, noti.start_date.day
                        ).weekday()
                        == 5
                )
                if (
                        is_shabat and daysFromNow == -1
                ) or daysFromNow == 0:  # show row if start day is today
                    my_dict.append(noti)
                    continue
        except Exception as e:
            print(noti.id,str(e))
    noti_list=[]
    try:
        for task in my_dict:
            noti_list.append(task_service._task_to_data(task).to_dict())
    except Exception as e:
        print(task.id,str(e))
    return noti_list

def is_need_create_notification(task):
    try:

        type_=notification_schedule_dict[task.name] if task.name in notification_schedule_dict.keys() else None
        too_old=datetime.today()-timedelta(365)
        if type_=="rivon":
            too_old = start_of_current_rivon().strftime("%Y%m%d %H%M%S")

        elif type_=="month":
            too_old = start_of_current_month()
        elif type_=="2week":
            too_old = start_of_current_month() if get_hebrew_date_from_greg_date(datetime.today())[2]<15 else start_of_current_month()+timedelta(15)
        elif type_=="week":
            too_old = get_last_sunday_date_greg()
        elif type_=="elul":
            too_old = start_of_year_greg_date()
        elif task.made_by_user==True or task.name=="יום הולדת":
            return True
        last_noti_by_name = db.session.query(notifications).filter(notifications.user_id == task.user_id,
                                                                notifications.name.contains( task.name),
                                                                notifications.created_at > too_old) \
                                                                    .first()
        if last_noti_by_name is None:
            return True
        return False
    except Exception as e:
        print("is_need_create_notification"+" "+task.name+str(e))

def insert_notifications_for_user(user_):
    not_committed=[]
    result_list = []
    returned_noti = []
    output_details=""
    notification=None
    try:
        noti_list = get_candidate_notifications(user_.id)
        notification_per_name_dict = dict()
        for notification in noti_list:
            if notification["name"] not in notification_per_name_dict.keys():
                notification_per_name_dict[notification["name"]] = []
            notification_per_name_dict[notification["name"]].append(notification)
        for k, v in notification_per_name_dict.items():
            if k in collated_notification_datils.keys():
                output_details = collated_notification_datils[k].format(user_.name) + "\n"
                for noti in v:
                    Apprentice1 = (
                        db.session.query(
                            Apprentice.name,
                            Apprentice.last_name,
                        )
                        .filter(Apprentice.id == noti["subject_id"])
                        .first()
                    )
                    output_details += Apprentice1.name + " " + Apprentice1.last_name + "\n" if Apprentice1 else ""
            else:
                if k == "יום הולדת":
                    title=k+" לחניך שלך"
                    for r in v:
                        result_list.append({"name": title, "description": r["description"]}) 
                    continue
                else:
                    output_details = v[0]["description"]
            if v[0]["made_by_user"]==True:#issue - if same user made tasks name
                title=k
            elif v[0]["made_by_user"]==False and ("עידכון" in v[0]["name"] or "דוח" in v[0]["name"]):
                title=k
            else:
                title = "הגיע הזמן ל" + k
            result_list.append({"name": title, "description": output_details})
        today_start = datetime.today()
        today_end = today_start + timedelta(days=1)
        for notification in result_list:
            last_noti_by_name = db.session.query(notifications).filter(notifications.user_id == user_.id,
                                                                       notifications.name == notification["name"],
                                                                       notifications.description == notification["description"]
                                                                       ,notifications.created_at>=today_start,
                                                                       notifications.created_at<today_end)\
                                                                        .first()
            if last_noti_by_name is None:
                noti_id=uuid.uuid4()
                notification_ = notifications(
                    user_id=user_.id,
                    name=notification["name"],
                    description=notification["description"],
                    has_been_read=False,
                    id=noti_id
                )
                db.session.add(notification_)
                send_push_notification(
                    user_.fcmToken,
                    notification["name"],
                    notification["description"],
                    "alert",
                    str(noti_id),
                    {},
                )
                returned_noti.append(notification_)


    except Exception as e:
        not_committed.append(str(user_.id)+":"+str(e))
    db.session.commit()
    return not_committed,returned_noti