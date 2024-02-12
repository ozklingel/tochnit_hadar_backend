import datetime
import json
from datetime import datetime,date

import boto3
from flask import Blueprint, request, jsonify
from http import HTTPStatus
from os import sys, path

from config import AWS_access_key_id, AWS_secret_access_key
from ..models.ent_group import ent_group

pth = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(pth)
from app import app, db
import uuid
from ..models.visit_model import Visit

reports_form_blueprint = Blueprint('reports_form', __name__, url_prefix='/reports_form')

@reports_form_blueprint.route('/add', methods=['post'])
def add_reports_form():

    data = request.json
    user = str(data['userId'])[3:]
    updatedEnt = None
    ent_group1=None
    attachments=[]
    if user:
        List_of_apprentices = data['List_of_apprentices']
        visitId=int(str(uuid.uuid4().int)[:5])
        if len(List_of_apprentices)>1:
            ent_group1=ent_group(
                id=visitId,
                group_name="בהד1",
                table_name="Apprentice",
                ent_id_list=[str(key['id'])[3:] for key in List_of_apprentices],
            )
            db.session.add(ent_group1)
        # print("files")
        # files =request.files['file']
        # print(files)
        # for file in files:
        #     print(file)
        #     new_filename = uuid.uuid4().hex + '.' + file.filename.rsplit('.', 1)[1].lower()
        #     bucket_name = "th01-s3"
        #     session = boto3.Session()
        #     s3_client = session.client('s3',
        #                                aws_access_key_id=AWS_access_key_id,
        #                                aws_secret_access_key=AWS_secret_access_key)
        #     s3 = boto3.resource('s3',
        #                         aws_access_key_id=AWS_access_key_id,
        #                         aws_secret_access_key=AWS_secret_access_key)
        #     print(new_filename)
        #     try:
        #         s3_client.upload_fileobj(file, bucket_name, new_filename)
        #         attachments.append(new_filename)
        #     except:
        #         return jsonify({'result': 'faild', 'image path': new_filename}), HTTPStatus.OK

        for key in List_of_apprentices:
            Visit1 = Visit(
                user_id=user,
                apprentice_id=str(key['id'])[3:],
                note=data['event_details'],
                visit_in_army=bool(data['event_type']),
                visit_date=data['date'],
                allreadyread=False,
                id=visitId,
                title=data['event_type'],
                attachments=attachments,
                description=data['description']

            )

            db.session.add(Visit1)

    try:
        db.session.commit()

    except Exception as e:
        return jsonify({'result': 'error'+str(e)}), HTTPStatus.BAD_REQUEST
    return jsonify({'result': str(visitId)}), HTTPStatus.OK


@reports_form_blueprint.route('/getAll', methods=['GET'])
def getAll_reports_form():
    user = request.args.get('userId')[3:]
    print(user)
    reportList = db.session.query(Visit).filter(Visit.user_id == user).all()
    ent_group_list = db.session.query(ent_group.id).filter(ent_group.user_id == user).all()
    ent_group_list_ids= [r[o] for r in ent_group_list]
    my_dict = []
    for noti in reportList:
        daysFromNow = (date.today() - noti.visit_date).days if noti.visit_date is not None else None
        if noti.id in ent_group_list_ids:
            ent_group_item = db.session.query(ent_group.group_name).filter(ent_group.id == noti.id).first()
            my_dict.append(
                {"id": str(noti.id), "from": ent_group_item.group_name,
                 "date": toISO(noti.visit_date),
                 "days_from_now": daysFromNow, "title": str(noti.title), "allreadyread": str(noti.allreadyread),
                 "description": str(noti.note), "attachments": noti.attachments})

        else:
            my_dict.append(
            {"id": str(noti.id), "from":str(noti.apprentice_id), "date":toISO(noti.visit_date),
             "days_from_now": daysFromNow , "title": str(noti.title), "allreadyread": str(noti.allreadyread), "description": str(noti.note),"attachments": noti.attachments})
    if not reportList :
        # acount not found
        return jsonify([])
    else:
        # print(f' notifications: {my_dict}]')
        # TODO: get Noti form to DB
        return jsonify(my_dict), HTTPStatus.OK
        # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK


@reports_form_blueprint.route('/setWasRead', methods=['post'])
def setWasRead_report_form():
    data = request.json
    report_id = data['report_id']
    print(report_id)
    try:
        noti = Visit.query.get(report_id)
        noti.allreadyread = True
        db.session.commit()
        if report_id:
            # print(f'setWasRead form: subject: [{subject}, notiId: {notiId}]')
            # TODO: add contact form to DB
            return jsonify({'result': 'success'}), HTTPStatus.OK
    except:
        return jsonify({'result': 'wrong id'}), HTTPStatus.OK
def toISO(d):
    if d:
        return datetime(d.year, d.month, d.day).isoformat()
    else:
        return None

@reports_form_blueprint.route('/uploadPhoto', methods=['post'])
def uploadPhoto_form():
        reportId = request.args.get('reportId')
        print(reportId)
        updatedEnt = Visit.query.get(reportId)

        images_list=[]
        for imagefile in request.files.getlist('image'):
            new_filename = uuid.uuid4().hex + '.' + imagefile.filename.rsplit('.', 1)[1].lower()
            bucket_name = "th01-s3"
            session = boto3.Session()
            s3_client = session.client('s3',
                                aws_access_key_id=AWS_access_key_id,
                                aws_secret_access_key=AWS_secret_access_key)
            s3 = boto3.resource('s3',
                                aws_access_key_id=AWS_access_key_id,
                                aws_secret_access_key=AWS_secret_access_key)
            print(new_filename)
            try:
                s3_client.upload_fileobj(imagefile, bucket_name, new_filename)
            except:
                return jsonify({'result': 'faild', 'image path': new_filename}), HTTPStatus.OK
            images_list.append("https://th01-s3.s3.eu-north-1.amazonaws.com/"+new_filename)
        if updatedEnt:
            updatedEnt.attachments=images_list
            db.session.commit()
        #head = s3_client.head_object(Bucket=bucket_name, Key=new_filename)
            return jsonify({'result': 'success', 'image path': updatedEnt.attachments}), HTTPStatus.OK
        return jsonify({"result": "error"}),HTTPStatus.BAD_REQUEST

@reports_form_blueprint.route('/delete', methods=['POST'])
def delete():
    try:
        data = request.json
        reportId = data['reportId']
        res = db.session.query(Visit).filter(Visit.id == reportId).delete()
        db.session.commit()
    except Exception as e:
        return jsonify({"result": str(e)}),HTTPStatus.BAD_REQUEST
    return jsonify({"result":"success"}), HTTPStatus.OK
        # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK

@reports_form_blueprint.route("/update", methods=['put'])
def updateTask():
    # get tasksAndEvents
    reportId = request.args.get("reportId")
    data = request.json
    updatedEnt = Visit.query.get(reportId)
    for key in data:
        setattr(updatedEnt, key, data[key])
    db.session.commit()
    if updatedEnt:
        # print(f'setWasRead form: subject: [{subject}, notiId: {notiId}]')
        # TODO: add contact form to DB
        return jsonify({'result': 'success'}), HTTPStatus.OK
    return jsonify({'result': 'error'}), HTTPStatus.OK
