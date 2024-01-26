import csv
import datetime

from openpyxl.reader.excel import load_workbook
from pyluach import dates, hebrewcal, parshios
#sudo pip install pyluach
from flask import Blueprint, request, jsonify, send_file
from http import HTTPStatus
from datetime import datetime,date,timedelta

from sqlalchemy import func

from app import db, red
from src.models.apprentice_model import Apprentice
from src.models.gift import gift
from src.models.notification_model import notifications
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
