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

import config
from app import db, red
from src.models.apprentice_model import Apprentice
from src.models.gift import gift
from src.models.notification_model import notifications
from src.models.system_report import system_report
from src.models.user_model import user1
from src.models.visit_model import Visit
from src.routes.notification_form_routes import getAll_notification_form

export_import_blueprint = Blueprint('export_import', __name__, url_prefix='/export_import')
@export_import_blueprint.route("/export_dict", methods=['post'])
def export_apprentice_score():
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
    path = '/home/ubuntu/flaskapp/gift.xlsx'
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
        res = db.session.query(gift).filter(gift.code == giftCode.code).delete()
        print("res",res)
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
        if len(all_melave_Apprentices) == 0:
            system_report1 = system_report(
                id=int(str(uuid.uuid4().int)[:5]),
                related_id=melaveId,
                type="melave_Score",
                value=100,
                creation_date=date.today(),
            )
            db.session.add(system_report1)
            continue
        visitcalls = db.session.query(Visit.apprentice_id, Visit.visit_date).filter(
            Visit.title == "שיחה", Visit.user_id == melaveId,Visit.visit_date>config.call_madad_date).order_by(Visit.visit_date).all()
        call_score ,visitcalls_melave_avg= compute_visit_score(all_melave_Apprentices, visitcalls, 12, 21)
        system_report1 = system_report(
            id=int(str(uuid.uuid4().int)[:5]),
            related_id=melaveId,
            type="visitcalls_melave_avg",
            value=visitcalls_melave_avg,
            creation_date=date.today(),
        )
        db.session.add(system_report1)
        visitmeetings,visitmeets_melave_avg = db.session.query(Visit.apprentice_id, Visit.visit_date).filter(
            Visit.title == "מפגש", Visit.user_id == melaveId,Visit.visit_date>config.meet_madad_date).order_by(Visit.visit_date).all()
        system_report1 = system_report(
            id=int(str(uuid.uuid4().int)[:5]),
            related_id=melaveId,
            type="visitmeets_melave_avg",
            value=visitmeets_melave_avg,
            creation_date=date.today(),
        )
        db.session.add(system_report1)
        personal_meet_score = compute_visit_score(all_melave_Apprentices, visitmeetings, 12, 90)
        group_meeting = db.session.query(Visit.apprentice_id, func.max(Visit.visit_date).label("visit_date")).group_by(
            Visit.apprentice_id).filter(Visit.title == "מפגש_קבוצתי", Visit.user_id == melaveId).first()
        gap = (date.today() - group_meeting.visit_date).days if group_meeting is not None else 100
        group_meeting_score = 0
        if gap <= 60:
            group_meeting_score += 12
        cenes_yearly = db.session.query(Visit.user_id, func.max(Visit.visit_date).label("visit_date")).group_by(
            Visit.user_id).filter(Visit.title == "כנס_שנתי", Visit.user_id == melaveId).all()
        gap = (date.today() - cenes_yearly.visit_date).days if group_meeting is not None else 400
        cenes_yearly_score = 0
        if gap < 365:
            cenes_yearly_score += 6.6
        yeshiva_monthly = db.session.query(Visit.user_id, func.max(Visit.visit_date).label("visit_date")).group_by(
            Visit.user_id).filter(Visit.title == "ישיבת_מלוים", Visit.user_id == melaveId).first()
        gap = (date.today() - yeshiva_monthly.visit_date).days if group_meeting is not None else 100
        yeshiva_monthly_score = 0
        if gap < 30:
            yeshiva_monthly_score += 6.6
        professional_2monthly = db.session.query(Visit.user_id,
                                                 func.max(Visit.visit_date).label("visit_date")).group_by(
            Visit.user_id).filter(Visit.title == "מפגש_מקצועי", Visit.user_id == melaveId).first()
        gap = (date.today() - professional_2monthly.visit_date).days if group_meeting is not None else 100
        professional_2monthly_score = 0
        if gap < 60:
            professional_2monthly_score += 6.6
        too_old = datetime.today() - timedelta(days=365)
        Horim_meeting = db.session.query(Visit.apprentice_id,func.max(Visit.visit_date).label("visit_date")).group_by(
            Visit.apprentice_id).filter(Visit.title == "מפגש_הורים",Visit.user_id == melaveId,Visit.visit_date>too_old).all()
        Horim_meeting_score = 0
        if len(Horim_meeting) == len(all_melave_Apprentices):
            Horim_meeting_score += 10
        too_old = datetime.today() - timedelta(days=365)
        base_meeting = db.session.query(Visit.visit_date).distinct(Visit.visit_date).filter(Visit.title == "מפגש",
                                                                                            Visit.visit_in_army == True,
                                                                                            Visit.visit_date > too_old,
                                                                                            Visit.user_id == melaveId).group_by(
            Visit.visit_date).count()
        base_meeting_score = 0
        if base_meeting >= 2:
            base_meeting_score += 10
        melave_score = base_meeting_score + Horim_meeting_score + professional_2monthly_score + yeshiva_monthly_score + \
                       cenes_yearly_score + \
                       group_meeting_score + personal_meet_score + call_score
        system_report1 = system_report(
            id=int(str(uuid.uuid4().int)[:5]),
            related_id=melaveId,
            type="melave_Score",
            value=melave_score,
            creation_date=date.today(),
        )
        db.session.add(system_report1)
    try:
        db.session.commit()
        return jsonify({'result': 'success'}), HTTPStatus.OK

    except Exception as e:
        return jsonify({'result': 'error'+str(e)}), HTTPStatus.BAD_REQUEST


@export_import_blueprint.route('/two_monthly', methods=['GET'])
def two_monthly():
    all_melave = db.session.query(user1.id,user1.name,user1.institution_id).filter(user1.role_id == "0").all()
    for melave in all_melave:
        melaveId = melave[0]
        all_melave_Apprentices = db.session.query(Apprentice.id).filter(
            Apprentice.accompany_id == melaveId).all()
        if len(all_melave_Apprentices) == 0:
            continue

        professional_2monthly = db.session.query(Visit.user_id,
                                                 func.max(Visit.visit_date).label("visit_date")).group_by(
            Visit.user_id).filter(Visit.title == "מפגש_מקצועי", Visit.user_id == melaveId).first()
        gap = (date.today() - professional_2monthly.visit_date).days if professional_2monthly is not None else 100
        professional_2monthly_score = 0
        if gap < 60:
            professional_2monthly_score += 6.6
            system_report1 = system_report(
                id=int(str(uuid.uuid4().int)[:5]),
                related_id=melaveId,
                type="professional_2monthly",
                value=100,
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
    all_melave = db.session.query(user1.id, user1.name, user1.institution_id).filter(user1.role_id == "0").all()
    for melave in all_melave:
        melaveId = melave[0]
        all_melave_Apprentices = db.session.query(Apprentice.id).filter(
            Apprentice.accompany_id == melaveId).all()
        if len(all_melave_Apprentices) == 0:
            continue
    try:
        db.session.commit()
        return jsonify({'result': 'success'}), HTTPStatus.OK

    except Exception as e:
        return jsonify({'result': 'error' + str(e)}), HTTPStatus.BAD_REQUEST

@export_import_blueprint.route('/yearly', methods=['GET'])
def yearly():
    all_melave = db.session.query(user1.id, user1.name, user1.institution_id).filter(user1.role_id == "0").all()
    for melave in all_melave:
        melaveId = melave[0]
        all_melave_Apprentices = db.session.query(Apprentice.id).filter(
            Apprentice.accompany_id == melaveId).all()
        if len(all_melave_Apprentices) == 0:
            continue

        cenes_yearly = db.session.query(Visit.user_id, func.max(Visit.visit_date).label("visit_date")).group_by(
            Visit.user_id).filter(Visit.title == "כנס_שנתי", Visit.user_id == melaveId).all()
        gap = (date.today() - cenes_yearly.visit_date).days if group_meeting is not None else 400
        cenes_yearly_score = 0
        if gap < 365:
            cenes_yearly_score += 6.6
            system_report1 = system_report(
                id=int(str(uuid.uuid4().int)[:5]),
                related_id=melaveId,
                type="cenes_yearly",
                value=100,
                creation_date=date.today(),
            )
            db.session.add(system_report1)
        too_old = datetime.today() - timedelta(days=365)
        Horim_meeting = db.session.query(Visit.apprentice_id, func.max(Visit.visit_date).label("visit_date")).group_by(
            Visit.apprentice_id).filter(Visit.title == "מפגש_הורים", Visit.user_id == melaveId,
                                        Visit.visit_date >too_old).all()
        Horim_meeting_score = 0
        if len(Horim_meeting) == len(all_melave_Apprentices):
            Horim_meeting_score += 10
        system_report1 = system_report(
            id=int(str(uuid.uuid4().int)[:5]),
            related_id=melaveId,
            type="Horim_meeting",
            value=Horim_meeting_score,
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
