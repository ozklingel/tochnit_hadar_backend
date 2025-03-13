from ..models import report_model
from ..models.apprentice_model import Apprentice
from ..models.report_model import Report
from ..models.task_model_v2 import Task
from src.services import db
from ..models.user_model import User


def task_to_done(event_type, user, key):
    # all personas tasks that NOT related to specific persona
    if (
        event_type == report_model.basis_report
        or event_type == report_model.groupMeet_report
        or event_type == report_model.MelavimMeeting_report
        or event_type == report_model.tochnitMeeting_report
        or event_type == report_model.hazanatMachzor_report
        or event_type == report_model.doForBogrim_report
    ):
        task_ent = (
            db.session.query(Task)
            .filter(Task.user_id == user, Task.name == event_type)
            .order_by(Task.created_at.desc())
            .first()
        )

        task_ent.status = "DONE"
    # all personas tasks that  related to specific persona
    if key and key != "":
        if event_type in report_model.report_as_meet:
            event_type = report_model.personalMeet_report
        if event_type in report_model.reports_as_call:
            event_type = report_model.call_report
        task_ent = (
            db.session.query(Task)
            .filter(
                Task.subject_id == str(key),
                Task.name == event_type,
            )
            .all()
        )
        for t_ in task_ent:
            t_.status = "DONE"


def get_reports_as_dict(reportList):
    my_reports = []
    for report_ in reportList:
        reportedList = []
        reported_name_str = ""
        # get missed_reports because of paging
        #grouped_reports_ent_reported = [report_.ent_reported for r in grouped_reports]
        grouped_reports=[report_]
        missed_reports = (
            db.session.query(
                Report.ent_reported,
                Report.ent_group,
                Report.note,
                Report.visit_date,
                Report.id,
                Report.title,
                Report.description,
                Report.attachments,
                Report.allreadyread,
                Report.created_at,
                Report.user_id,
            )
            .filter(
                Report.id == report_.id, Report.ent_reported!=report_.ent_reported
            )
            .all()
        )
        if missed_reports:
            for missed_report_ in missed_reports:
                grouped_reports.append(missed_report_)
        for grouped_report_ in grouped_reports:
            reportedList.append(str(grouped_report_.ent_reported))
            reported_name = (
                db.session.query(Apprentice.name, Apprentice.last_name)
                .filter(Apprentice.id == grouped_report_.ent_reported)
                .first()
            )
            if reported_name is None:
                reported_name = (
                    db.session.query(User.name, User.last_name)
                    .filter(User.id == grouped_report_.ent_reported)
                    .first()
                )
            if reported_name:
                reported_name_str += (
                    reported_name.name + " " + reported_name.last_name + ","
                )
            reported_name = (
                db.session.query(User.name, User.last_name)
                .filter(User.id == grouped_report_.user_id)
                .first()
            )
            if reported_name:
                reported_name_str += (
                        reported_name.name + " " + reported_name.last_name + ","
                )
        Report_temp = Report(
            id=report_.id,
            created_at=report_.created_at,
            ent_group=report_.ent_group,
            description=report_.description,
            attachments=report_.attachments,
            allreadyread=report_.allreadyread,
            title=report_.title,
            note=report_.note,
            ent_reported=report_.ent_reported,
            user_id=report_.user_id,
            visit_date=report_.visit_date,
        )
        report_as_dict = Report_temp.to_attributes(reported_name_str[:-1], reportedList)
        my_reports.append(report_as_dict)

    return my_reports
