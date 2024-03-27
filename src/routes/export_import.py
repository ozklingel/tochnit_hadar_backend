import csv
import datetime
import uuid

import boto3
from openpyxl.reader.excel import load_workbook
from flask import Blueprint, request, jsonify, send_file
from http import HTTPStatus
from datetime import datetime,date,timedelta

from sqlalchemy import func, or_

from app import db, red
from config import AWS_access_key_id, AWS_secret_access_key, melave_Score, visitcalls_melave_avg, visitmeets_melave_avg, \
    proffesionalMeet_presence, forgotenApprentice_cnt, cenes_presence, horim_meeting, call_report, groupMeet_report, \
    personalMeet_report, professional_report, HorimCall_report
from src.models.apprentice_model import Apprentice
from src.models.base_model import Base
from src.models.city_model import City
from src.models.gift import gift
from src.models.system_report import system_report
from src.models.user_model import user1
from src.models.visit_model import Visit
import src.routes.madadim as md

export_import_blueprint = Blueprint('export_import', __name__, url_prefix='/export_import')
@export_import_blueprint.route('/upload_CitiesDB', methods=['PUT'])
def upload_CitiesDB():
    try:
        import csv
        my_list = []
        #/home/ubuntu/flaskapp/
        with open('/home/ubuntu/flaskapp/data/cities_add.csv', 'r', encoding="utf8") as f:
            reader = csv.reader(f)
            print(reader)
            for row in reader:
                print(row)
                my_list.append(City(row[0].strip(), row[1].strip(), row[2].strip()))
        for ent in my_list:
            db.session.add(ent)
        try:
            db.session.commit()
            return jsonify({"result": "success"}), HTTPStatus.OK
        except Exception as e:
            return jsonify({"result":str(e)}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.OK

@export_import_blueprint.route('/upload_baseDB', methods=['PUT'])
def upload_baseDB():
    try:
        import csv
        my_list = []
        #/home/ubuntu/flaskapp/
        with open('/home/ubuntu/flaskapp/data/base_add.csv', 'r', encoding="utf8") as f:
            reader = csv.reader(f)
            for row in reader:
                print(row[1].strip())
                ent=Base(int(str(uuid.uuid4().int)[:5]), row[0].strip(), row[1].strip())
                db.session.add(ent)
        db.session.commit()
        return jsonify({"result": "success"}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.OK
@export_import_blueprint.route("/export_dict", methods=['post'])
def export_dict():
    try:
        data = request.json
        to_csv = data['list']
        keys = to_csv[0].keys()
        with open('/home/ubuntu/flaskapp/data/to_csv.csv', 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(to_csv)
        return send_file("/home/ubuntu/flaskapp/data/to_csv.csv", as_attachment=True, download_name="/home/ubuntu/flaskapp/dict2.csv")
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST

@export_import_blueprint.route("/add_giftCode_excel", methods=['put'])
def add_giftCode_excel():
    try:
        file = request.files['file']

        wb = load_workbook(file)
        sheet = wb.active
        for row in sheet.iter_rows(min_row=2):
            code = row[0].value
            was_used = row[1].value
            print(code)
            print(was_used)
            gift1 = gift( code=code,was_used=was_used)
            db.session.add(gift1)

        try:
            db.session.commit()
        except Exception as e:
            return jsonify({'result': 'error while inserting' + str(e)}), HTTPStatus.OK
        return jsonify({'result': 'success'}), HTTPStatus.BAD_REQUEST
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST
@export_import_blueprint.route('/getGift', methods=['GET'])
def getGift():
    try:
        teudat_zehut = request.args.get('teudat_zehut')
        base = request.args.get('base')
        giftCode = db.session.query(gift).filter(gift.was_used == False).first()
        print(giftCode)
        if giftCode is not None:
            giftCode.was_used=True
            #res = db.session.query(gift).filter(gift.code == giftCode.code).delete()
            db.session.commit()

        if not giftCode:
            # acount not found
            return jsonify({'result': 'no code available'}), HTTPStatus.OK
        else:
            return jsonify({'result': str(giftCode.code)}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST
@export_import_blueprint.route('/monthly', methods=['GET'])
def monthly():
    try:
        all_melave = db.session.query(user1.id,user1.name,user1.institution_id).filter(user1.role_id == "0").all()
        for melave in all_melave:
            melaveId = melave[0]
            all_melave_Apprentices = db.session.query(Apprentice.id).filter(
                Apprentice.accompany_id == melaveId).all()
            melave_score1, call_gap_avg, meet_gap_avg = md.melave_score(melaveId)
            system_report1 = system_report(
                id=int(str(uuid.uuid4().int)[:5]),
                related_id=melaveId,
                type=melave_Score,
                value=melave_score1,
                creation_date=date.today(),
            )
            db.session.add(system_report1)
            system_report1 = system_report(
                id=int(str(uuid.uuid4().int)[:5]),
                related_id=melaveId,
                type=visitcalls_melave_avg,
                value=call_gap_avg,
                creation_date=date.today(),
            )
            db.session.add(system_report1)
            system_report1 = system_report(
                id=int(str(uuid.uuid4().int)[:5]),
                related_id=melaveId,
                type=visitmeets_melave_avg,
                value=meet_gap_avg,
                creation_date=date.today(),
            )
            db.session.add(system_report1)

            # mosad Madadim:
            all_MosadCoordinator = db.session.query(user1.id, user1.institution_id).filter(user1.role_id == "1").all()
            for mosadCoord in all_MosadCoordinator:
                mosadCoord_id = mosadCoord[0]
                res = md.mosadCoordinator(mosadCoord_id)[0].json
                print("res", res['avg_apprenticeCall_gap'])
                system_report1 = system_report(
                    id=int(str(uuid.uuid4().int)[:5]),
                    related_id=mosadCoord_id,
                    type=visitcalls_melave_avg,
                    value=res['avg_apprenticeCall_gap'],
                    creation_date=date.today(),
                )
                db.session.add(system_report1)
                system_report1 = system_report(
                    id=int(str(uuid.uuid4().int)[:5]),
                    related_id=mosadCoord_id,
                    type=visitmeets_melave_avg,
                    value=res['avg_apprenticeMeeting_gap'],
                    creation_date=date.today(),
                )
                db.session.add(system_report1)

        try:
            db.session.commit()
            return jsonify({'result': 'success'}), HTTPStatus.OK

        except Exception as e:
            return jsonify({'result': 'error'+str(e)}), HTTPStatus.BAD_REQUEST
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST
@export_import_blueprint.route('/rivony', methods=['GET'])
def rivony():
    current_month=date.today().month
    month4index=current_month%3
    start_Of_Rivon = datetime.today() - timedelta(days=30*month4index)
    #melave Madadim:
    all_melave = db.session.query(user1.id, user1.name, user1.institution_id).filter(user1.role_id == "0").all()
    for melave in all_melave:
        melaveId = melave[0]
        all_melave_Apprentices = db.session.query(Apprentice.id).filter(
            Apprentice.accompany_id == melaveId).all()
        if len(all_melave_Apprentices) == 0:
            continue
        #מפגש מקצועי מלווה
        newvisit_professional = db.session.query(Visit.user_id).filter(Visit.ent_reported == melaveId,
                                                                       Visit.title == professional_report,
                                                                       Visit.visit_date > start_Of_Rivon).all()
        system_report1 = system_report(
            id=int(str(uuid.uuid4().int)[:5]),
            related_id=melaveId,
            type=proffesionalMeet_presence,
            value=len(newvisit_professional),
            creation_date=date.today(),
        )
        db.session.add(system_report1)
        Apprentice_ids_forgoten = [r[0] for r in all_melave_Apprentices]
        too_old = datetime.today() - timedelta(days=100)
        Oldvisitcalls = db.session.query(Visit.ent_reported).filter(
                                                                     Apprentice.id == Visit.ent_reported,
                                                                     or_(Visit.title == call_report,Visit.title == groupMeet_report,Visit.title == personalMeet_report),
                                                                     Visit.visit_date < too_old).all()
        for i in Oldvisitcalls:
            if i[0] in Apprentice_ids_forgoten:
                Apprentice_ids_forgoten.remove(i[0])

        system_report1 = system_report(
            id=int(str(uuid.uuid4().int)[:5]),
            related_id=melaveId,
            type=forgotenApprentice_cnt,
            value=len(Apprentice_ids_forgoten),
            creation_date=date.today(),
        )
        db.session.add(system_report1)

    #mosad Madadim:
    all_MosadCoordinator = db.session.query(user1.id,user1.institution_id).filter(user1.role_id=="1").all()
    for mosadCoord in all_MosadCoordinator:
        mosadCoord_id=mosadCoord[0]
        inst=db.session.query(user1.institution_id).filter(user1.id==mosadCoord_id)
        all_Apprentices = db.session.query(Apprentice.id).filter(
            Apprentice.institution_id == inst).all()
        Apprentice_ids_forgoten = [r[0] for r in all_Apprentices]

        too_old = datetime.today() - timedelta(days=100)
        Oldvisitcalls = db.session.query(Visit.ent_reported).filter(
            Apprentice.id == Visit.ent_reported,
            or_(Visit.title == call_report, Visit.title == groupMeet_report, Visit.title == personalMeet_report),
            Visit.visit_date < too_old).all()
        for i in Oldvisitcalls:
            if i[0] in Apprentice_ids_forgoten:
                Apprentice_ids_forgoten.remove(i[0])

        system_report1 = system_report(
            id=int(str(uuid.uuid4().int)[:5]),
            related_id=mosadCoord_id,
            type=forgotenApprentice_cnt,
            value=len(Apprentice_ids_forgoten),
            creation_date=date.today(),
        )
        db.session.add(system_report1)


    #eshcol Madadim:
    all_eshcolCoordinator = db.session.query(user1.id,user1.eshcol).filter(user1.role_id=="2").all()
    for eshcolCoord in all_eshcolCoordinator:
        eshcolCoord_id=eshcolCoord[0]
        eshco=eshcolCoord[1]
        all_Apprentices = db.session.query(Apprentice.id).filter(
            Apprentice.eshcol == eshco).all()
        Apprentice_ids_forgoten = [r[0] for r in all_Apprentices]
        too_old = datetime.today() - timedelta(days=100)
        Oldvisitcalls = db.session.query(Visit.ent_reported).filter(
            Apprentice.id == Visit.ent_reported,
            or_(Visit.title == call_report, Visit.title == groupMeet_report, Visit.title == personalMeet_report),
            Visit.visit_date < too_old).all()
        for i in Oldvisitcalls:
            if i[0] in Apprentice_ids_forgoten:
                Apprentice_ids_forgoten.remove(i[0])

        system_report1 = system_report(
            id=int(str(uuid.uuid4().int)[:5]),
            related_id=eshcolCoord_id,
            type=forgotenApprentice_cnt,
            value=len(Apprentice_ids_forgoten),
            creation_date=date.today(),
        )
        db.session.add(system_report1)

    try:
        db.session.commit()
        return jsonify({'result': 'success'}), HTTPStatus.OK

    except Exception as e:
        return jsonify({'result': 'error' + str(e)}), HTTPStatus.BAD_REQUEST

@export_import_blueprint.route('/yearly', methods=['GET'])
def yearly():
    current_month=date.today().month
    start_Of_year = datetime.today() - timedelta(days=30*current_month)
    all_melave = db.session.query(user1.id, user1.name, user1.institution_id).filter(user1.role_id == "0").all()
    for melave in all_melave:
        melaveId = melave[0]
        all_melave_Apprentices = db.session.query(Apprentice.id).filter(
            Apprentice.accompany_id == melaveId).all()
        if len(all_melave_Apprentices) == 0:
            continue

        cenes_yearly = db.session.query(Visit.user_id, func.max(Visit.visit_date).label("visit_date")).group_by(
            Visit.user_id).filter(Visit.title == "כנס_שנתי", Visit.user_id == melaveId,Visit.visit_date>start_Of_year).first()
        if cenes_yearly:
            system_report1 = system_report(
                id=int(str(uuid.uuid4().int)[:5]),
                related_id=melaveId,
                type=cenes_presence,
                value=100,
                creation_date=date.today(),
            )
            db.session.add(system_report1)
        Horim_meeting = db.session.query(Visit.ent_reported, func.max(Visit.visit_date).label("visit_date")).group_by(
            Visit.ent_reported).filter(Visit.title == HorimCall_report, Visit.user_id == melaveId,
                                        Visit.visit_date >start_Of_year).all()
        if Horim_meeting:
            system_report1 = system_report(
                id=int(str(uuid.uuid4().int)[:5]),
                related_id=melaveId,
                type=horim_meeting,
                value=Horim_meeting,
                creation_date=date.today(),
            )
            db.session.add(system_report1)
        too_old = datetime.today() - timedelta(days=365)
        base_meeting = db.session.query(Visit.visit_date).distinct(Visit.visit_date).filter(or_(Visit.title == personalMeet_report,Visit.title==groupMeet_report),
                                                                                            Visit.visit_in_army == True,
                                                                                            Visit.visit_date > too_old,
                                                                                            Visit.user_id == melaveId).group_by(
            Visit.visit_date).count()
        base_meeting_score = 0
        if base_meeting > 2:
            base_meeting_score += 10
            system_report1 = system_report(
                id=int(str(uuid.uuid4().int)[:5]),
                related_id=melaveId,
                type="base_meeting",
                value=2,
                creation_date=date.today(),
            )
            db.session.add(system_report1)
    try:
        db.session.commit()
        return jsonify({'result': 'success'}), HTTPStatus.OK

    except Exception as e:
        return jsonify({'result': 'error' + str(e)}), HTTPStatus.BAD_REQUEST

@export_import_blueprint.route('/uploadfile', methods=['post'])
def uploadfile():
        #reportId = request.args.get('reportId')
        #print(reportId)
        #updatedEnt = Visit.query.get(reportId)
        try:
            images_list=[]
            for imagefile in request.files.getlist('file'):
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
            #if updatedEnt:
            #    updatedEnt.attachments=images_list
            #    db.session.commit()
            return jsonify({'result': 'success', 'image path': images_list}), HTTPStatus.OK
        except Exception:
            return jsonify({"result": str(Exception)}),HTTPStatus.BAD_REQUEST