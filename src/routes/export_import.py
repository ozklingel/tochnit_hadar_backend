import csv
import datetime
import uuid

from openpyxl.reader.excel import load_workbook
from pyluach import dates, hebrewcal, parshios
#sudo pip install pyluach
from flask import Blueprint, request, jsonify, send_file
from http import HTTPStatus
from datetime import datetime,date,timedelta

from sqlalchemy import func

from app import db, red
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
    import csv
    my_list = []
    #/home/ubuntu/flaskapp/
    with open('/home/ubuntu/flaskapp/cities_add.csv', 'r', encoding="utf8") as f:
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


@export_import_blueprint.route('/upload_baseDB', methods=['PUT'])
def upload_baseDB():
    import csv
    my_list = []
    #/home/ubuntu/flaskapp/
    with open('/home/ubuntu/flaskapp/base_add.csv', 'r', encoding="utf8") as f:
        reader = csv.reader(f)
        for row in reader:
            print(row[1].strip())
            ent=Base(int(str(uuid.uuid4().int)[:5]), row[0].strip(), row[1].strip())
            db.session.add(ent)
    db.session.commit()
    return jsonify({"result": "success"}), HTTPStatus.OK

@export_import_blueprint.route("/export_dict", methods=['post'])
def export_dict():
    data = request.json
    to_csv = data['list']
    keys = to_csv[0].keys()
    with open('/home/ubuntu/flaskapp/to_csv.csv', 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(to_csv)
    return send_file("/home/ubuntu/flaskapp/to_csv.csv", as_attachment=True, download_name="/home/ubuntu/flaskapp/dict2.csv")

    # data = request.json
    # print(data)
    # my_dict = data['dict']
    # print(my_dict)
    # with open('/home/ubuntu/flaskapp/dict2.csv', 'w') as f:
    #     w = csv.DictWriter(f, my_dict.keys())
    #     w.writeheader()
    #     w.writerow(my_dict)
    # return send_file("/home/ubuntu/flaskapp/dict2.csv", as_attachment=True, download_name="/home/ubuntu/flaskapp/dict2.csv")

@export_import_blueprint.route("/add_giftCode_excel", methods=['put'])
def add_giftCode_excel():
    from openpyxl import workbook
    path = 'gift.xlsx'
    wb = load_workbook(filename=path)
    ws = wb.get_sheet_by_name('Sheet1')
    for row in ws.iter_rows(min_row=2):
        code = row[0].value
        was_used = row[1].value
        print(code)
        print(was_used)
        gift1 = gift( code=code,was_used=was_used)
        db.session.add(gift1)

    try:
        db.session.commit()
    except Exception as e:
        return jsonify({'result': 'error while inserting' + str(e)}), HTTPStatus.BAD_REQUEST
    return jsonify({'result': 'success'}), HTTPStatus.OK

@export_import_blueprint.route('/getGift', methods=['GET'])
def getGift():
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

@export_import_blueprint.route('/monthly', methods=['GET'])
def monthly():
    all_melave = db.session.query(user1.id,user1.name,user1.institution_id).filter(user1.role_id == "0").all()
    for melave in all_melave:
        melaveId = melave[0]
        all_melave_Apprentices = db.session.query(Apprentice.id).filter(
            Apprentice.accompany_id == melaveId).all()
        melave_score1, call_gap_avg, meet_gap_avg = md.melave_score(melaveId)
        system_report1 = system_report(
            id=int(str(uuid.uuid4().int)[:5]),
            related_id=melaveId,
            type="melave_Score",
            value=melave_score1,
            creation_date=date.today(),
        )
        db.session.add(system_report1)
        system_report1 = system_report(
            id=int(str(uuid.uuid4().int)[:5]),
            related_id=melaveId,
            type="call_gap_avg",
            value=call_gap_avg,
            creation_date=date.today(),
        )
        db.session.add(system_report1)
        system_report1 = system_report(
            id=int(str(uuid.uuid4().int)[:5]),
            related_id=melaveId,
            type="meet_gap_avg",
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
                type="avg_apprenticeCall_gap_mosad",
                value=res['avg_apprenticeCall_gap'],
                creation_date=date.today(),
            )
            db.session.add(system_report1)
            system_report1 = system_report(
                id=int(str(uuid.uuid4().int)[:5]),
                related_id=mosadCoord_id,
                type="avg_apprenticeMeeting_gap",
                value=res['avg_apprenticeMeeting_gap'],
                creation_date=date.today(),
            )
            db.session.add(system_report1)

    try:
        db.session.commit()
        return jsonify({'result': 'success'}), HTTPStatus.OK

    except Exception as e:
        return jsonify({'result': 'error'+str(e)}), HTTPStatus.BAD_REQUEST

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
        newvisit_professional = db.session.query(Visit.user_id).filter(Visit.user_id == melaveId,
                                                                       Visit.title == "מפגש_מקצועי",
                                                                       Visit.visit_date > start_Of_Rivon).all()
        system_report1 = system_report(
            id=int(str(uuid.uuid4().int)[:5]),
            related_id=melaveId,
            type="professionalmeeting",
            value=len(newvisit_professional),
            creation_date=date.today(),
        )
        db.session.add(system_report1)
    too_old = datetime.today() - timedelta(days=100)
    Oldvisitcalls = db.session.query(Visit.ent_reported).distinct(Visit.ent_reported).filter(Visit.user_id==melaveId,Apprentice.id==Visit.ent_reported,Visit.title == "שיחה",
                                                                 Visit.visit_date > too_old).all()
    forgotenApprentices_count=len(all_melave_Apprentices)-len(Oldvisitcalls)
    system_report1 = system_report(
        id=int(str(uuid.uuid4().int)[:5]),
        related_id=melaveId,
        type="forgotenApprentices_count",
        value=forgotenApprentices_count,
        creation_date=date.today(),
    )
    db.session.add(system_report1)

    #mosad Madadim:
    all_MosadCoordinator = db.session.query(user1.id,user1.institution_id).filter(user1.role_id=="1").all()
    for mosadCoord in all_MosadCoordinator:
        mosadCoord_id=mosadCoord[0]
        res=md.mosadCoordinator(mosadCoord_id)[0].json
        print("res",res['avg_apprenticeCall_gap'])
        system_report1 = system_report(
            id=int(str(uuid.uuid4().int)[:5]),
            related_id=mosadCoord_id,
            type="avg_apprenticeCall_gap_mosad",
            value=res['avg_apprenticeCall_gap'],
            creation_date=date.today(),
        )
        db.session.add(system_report1)
        system_report1 = system_report(
            id=int(str(uuid.uuid4().int)[:5]),
            related_id=mosadCoord_id,
            type="Apprentice_forgoten_count",
            value=res['Apprentice_forgoten_count'],
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
                type="cenes_yearly",
                value=100,
                creation_date=date.today(),
            )
            db.session.add(system_report1)
        Horim_meeting = db.session.query(Visit.ent_reported, func.max(Visit.visit_date).label("visit_date")).group_by(
            Visit.ent_reported).filter(Visit.title == "מפגש_הורים", Visit.user_id == melaveId,
                                        Visit.visit_date >start_Of_year).all()
        if Horim_meeting:
            system_report1 = system_report(
                id=int(str(uuid.uuid4().int)[:5]),
                related_id=melaveId,
                type="Horim_meeting",
                value=Horim_meeting,
                creation_date=date.today(),
            )
            db.session.add(system_report1)
        too_old = datetime.today() - timedelta(days=365)
        base_meeting = db.session.query(Visit.visit_date).distinct(Visit.visit_date).filter(Visit.title == "מפגש",
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
def compute_visit_score(all_children,visits,maxScore,expected_gap):
    all_children_ids = [r[0] for r in all_children]

    from collections import defaultdict
    visitcalls_melave_list = defaultdict(list)
    # key is apprenticeId and value is list of  gaps visits date
    for index in range(1, len(visits)):
        gap = (visits[index][1] - visits[index - 1][1]).days if visits[index] is not None else 21
        visitcalls_melave_list[visits[index][0]].append(gap)
    visitcalls_melave_avg = 0
    for k, v in visitcalls_melave_list.items():
        if k in all_children_ids:
            all_children_ids.remove(k)
        visitcalls_melave_avg += (sum(v) / len(v))
    #t least one apprentice with no calls
    if len(all_children_ids) != 0:
        visitcalls_melave_avg = 0
    else:
        visitcalls_melave_avg = visitcalls_melave_avg / len(visitcalls_melave_list) if len(
            visitcalls_melave_list) != 0 else 0
    call_panish = visitcalls_melave_avg - expected_gap


    if call_panish > 0:
        call_score = maxScore - call_panish / 2
    else:
        call_score = maxScore
    if call_score<0:
        call_score=0
    return call_score,visitcalls_melave_avg
