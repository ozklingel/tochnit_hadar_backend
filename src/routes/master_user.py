import uuid
from http import HTTPStatus

from flask import Blueprint, request, jsonify
from openpyxl.reader.excel import load_workbook

import config
from src.models.cluster_model import Cluster
from src.models.madadim_setting_model import MadadimSetting
from src.routes.user_profile import correct_auth
from src.services import db
from src.models.apprentice_model import Apprentice
from src.models.base_model import Base
from src.models.city_model import City
from src.models.message_model import Message
from src.models.gift_model import Gift
from src.models.institution_model import Institution
from src.models.task_model import Task
from src.models.user_model import User
from src.models.report_model import Report

master_user_form_blueprint = Blueprint('master_user', __name__, url_prefix='/master_user')
base_dir = "" #"/home/ubuntu/flaskapp/"


@master_user_form_blueprint.route('/setSetting_madadim', methods=['post'])
def setSetting_madadim():
    if correct_auth() == False:
        return jsonify({'result': "wrong access token"}), HTTPStatus.OK
    data = request.json
    madadim_setting1 = db.session.query(MadadimSetting).first()
    if madadim_setting1 is None:
        rep = MadadimSetting(
            call_madad_date='1995-09-09'
            , cenes_madad_date='1995-09-09'
            , tochnitMeet_madad_date='1995-09-09'
            , eshcolMosadMeet_madad_date='1995-09-09'
            , mosadYeshiva_madad_date='1995-09-09'
            , hazana_madad_date='1995-09-09'
            , professionalMeet_madad_date='1995-09-09'
            , doForBogrim_madad_date='1995-09-09'
            , basis_madad_date='1995-09-09'
            , callHorim_madad_date='1995-09-09'
            , groupMeet_madad_date='1995-09-09'
            , matzbarmeet_madad_date='1995-09-09'

            , meet_madad_date='1995-09-09'
        )
        db.session.add(rep)

    madadim_setting1.call_madad_date.get('call_madad_date')
    madadim_setting1.meet_madad_date.get('meet_madad_date')
    madadim_setting1.groupMeet_madad_date.get('groupMeet_madad_date')
    madadim_setting1.callHorim_madad_date.get('callHorim_madad_date')
    madadim_setting1.basis_madad_date.get('basis_madad_date')
    madadim_setting1.doForBogrim_madad_date.get('doForBogrim_madad_date')
    madadim_setting1.matzbarmeet_madad_date.get('matzbarmeet_madad_date')
    madadim_setting1.professionalmeet_madad_date.get('professionalMeet_madad_date')
    madadim_setting1.hazana_madad_date.get('hazana_madad_date')
    madadim_setting1.mosadYeshiva_madad_date.get('mosadYeshiva_madad_date')
    madadim_setting1.eshcolMosadMeet_madad_date.get('eshcolMosadMeet_madad_date')
    madadim_setting1.tochnitMeet_madad_date.get('tochnitMeet_madad_date')
    madadim_setting1.cenes_madad_date.get('cenes_madad_date')

    db.session.commit()

    return jsonify({'result': 'success'}), HTTPStatus.OK


@master_user_form_blueprint.route('/getAllSetting_madadim', methods=['GET'])
def getNotificationSetting_form():
    try:
        if correct_auth()==False:
            return jsonify({'result': "wrong access token"}), HTTPStatus.OK
        madadim_setting1 = db.session.query(MadadimSetting).first()

        return jsonify({"call_madad_date": str(madadim_setting1.call_madad_date),
                        "meet_madad_date": str(madadim_setting1.meet_madad_date)
                           , "groupMeet_madad_date": str(madadim_setting1.groupMeet_madad_date),
                        "callHorim_madad_date": str(madadim_setting1.callHorim_madad_date),
                        "basis_madad_date": str(madadim_setting1.basis_madad_date)

                           , "doForBogrim_madad_date": str(madadim_setting1.doForBogrim_madad_date),
                        "matzbarmeet_madad_date": str(madadim_setting1.matzbarmeet_madad_date),
                        "professionalMeet_madad_date": str(madadim_setting1.professionalMeet_madad_date)
                           , "hazana_madad_date": str(madadim_setting1.hazana_madad_date)
                           , "mosadYeshiva_madad_date": str(madadim_setting1.mosadYeshiva_madad_date),

                        "eshcolMosadMeet_madad_date": str(madadim_setting1.eshcolMosadMeet_madad_date)
                           , "tochnitMeet_madad_date": str(madadim_setting1.tochnitMeet_madad_date)
                           , "cenes_madad_date": str(madadim_setting1.cenes_madad_date)
                        }), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST


def addApperntice(wb):
    sheet = wb.active
    uncommited_ids = []
    for row in sheet.iter_rows(min_row=2):
        if row[0].value is None or row[1].value is None:
            uncommited_ids.append(row[2].value)
            continue
        first_name = row[0].value.strip()
        last_name = row[1].value.strip()
        phone = row[2].value
        city = row[3].value.strip() if not row[3].value is None else "לא ידוע"
        address = row[4].value.strip() if not row[4].value is None else ""
        teudatZehut = row[5].value if not row[5].value is None else ""
        birthday_Ivry_month = row[6].value.strip() if not row[6].value is None else ""
        birthday_Ivry_day = row[7].value.strip() if not row[7].value is None else ""
        birthday_Ivry = birthday_Ivry_day + " " + birthday_Ivry_month
        birthday_loazi = row[8].value if not row[8].value is None else None
        mail = row[9].value.strip() if not row[9].value is None else ""
        marriage_status = row[10].value.strip() if not row[10].value is None else ""
        serve_type = row[11].value.strip() if not row[11].value is None else ""
        hadar_plan_session = row[12].value if not row[12].value is None else ""
        contact1_first_relation = row[13].value.strip() if not row[13].value is None else ""
        contact1_first_name = row[14].value.strip() if not row[14].value is None else ""
        contact1_phone = row[15].value if not row[15].value is None else ""
        contact1_email = row[16].value.strip() if not row[16].value is None else ""
        contact2_first_relation = row[17].value.strip() if not row[17].value is None else ""
        contact2_first_name = row[18].value.strip() if not row[18].value is None else ""
        contact2_phone = row[19].value if not row[19].value is None else ""
        contact2_email = row[20].value.strip() if not row[20].value is None else ""
        contact3_first_relation = row[21].value.strip() if not row[21].value is None else ""
        contact3_first_name = row[22].value.strip() if not row[22].value is None else ""
        contact3_phone = row[23].value if not row[23].value is None else ""
        contact3_email = row[24].value.strip() if not row[24].value is None else ""
        marriage_date_month = row[25].value if not row[25].value is None else ""
        marriage_date_day = row[26].value if not row[26].value is None else ""
        marriage_date = marriage_date_day + " " + marriage_date_month
        marriage_date_loazi = row[27].value if not row[27].value is None else None
        institution_mahzor = row[28].value if not row[28].value is None else ""
        teacher_grade_a = row[29].value.strip() if not row[29].value is None else ""
        teacher_grade_a_phone = row[30].value if not row[30].value is None else ""
        teacher_grade_b = row[31].value.strip() if not row[31].value is None else ""
        teacher_grade_b_phone = row[32].value if not row[32].value is None else ""
        paying = row[33].value if not row[33].value is None else ""
        matzbar = row[34].value.strip() if not row[34].value is None else ""
        high_school_name = row[35].value.strip() if not row[35].value is None else ""
        high_school_teacher = row[36].value if not row[36].value is None else ""
        high_school_teacher_phone = row[37].value if not row[37].value is None else ""
        workstatus = row[38].value.strip() if not row[38].value is None else ""
        workplace = row[39].value.strip() if not row[39].value is None else ""
        educationfaculty = row[40].value.strip() if not row[40].value is None else ""
        workoccupation = row[41].value.strip() if not row[41].value is None else ""
        # worktype = row[42].value.strip()  #
        army_role = row[42].value.strip() if not row[43].value is None else ""  # סיירות
        unit_name = row[43].value.strip() if not row[42].value is None else ""  # צנחנים
        militaryPositionNew = row[45].value.strip() if not row[45].value is None else ""  # מפקד כיתה
        militaryPositionOld = row[46].value.strip() if not row[46].value is None else ""  # צנחנים
        recruitment_date = row[47].value if not row[47].value is None else None  # צנחנים
        release_date = row[48].value if not row[48].value is None else None  # צנחנים
        base_name = row[49].value.strip() if not row[49].value is None else "לא ידוע"
        institution_name = row[50].value.strip() if not row[50].value is None else ""
        accompany_id = row[51].value if not row[51].value is None else ""  # מפקד?

        CityId = db.session.query(City.id).filter(City.name == city).first()
        militaryCompoundId = db.session.query(Base.id).filter(Base.name == base_name).first()
        institution_id = db.session.query(Institution.id).filter(Institution.name == institution_name).first()
        if institution_id is None or CityId is None or militaryCompoundId is None:
            uncommited_ids.append(row[2].value)
            continue
        cluster_id = db.session.query(Institution.cluster_id).filter(Institution.id == institution_id.id).first()
        if institution_id is None or cluster_id is None or CityId is None or militaryCompoundId is None:
            uncommited_ids.append(row[2].value)
            continue

        try:
            institution_id = db.session.query(Institution.id).filter(Institution.name == str(institution_name)).first()
            Apprentice1 = Apprentice(
                email=mail,
                high_school_teacher=high_school_teacher,
                release_date=release_date,
                recruitment_date=recruitment_date,
                militaryPositionOld=militaryPositionOld,
                militaryPositionNew=militaryPositionNew,
                institution_mahzor=institution_mahzor,
                teacher_grade_a_phone=teacher_grade_a_phone,
                teacher_grade_b_phone=teacher_grade_b_phone,
                city_id=CityId.id,
                id=phone,
                cluster_id=cluster_id.cluster_id,
                base_address=militaryCompoundId.id,
                institution_id=institution_id.id if institution_id is not None else 0,
                address=address,
                serve_type=serve_type,
                name=first_name,
                last_name=last_name,
                phone=str(phone),
                army_role=army_role,
                marriage_status=marriage_status,
                contact1_email=contact1_email,
                teacher_grade_b=teacher_grade_b,
                teacher_grade_a=teacher_grade_a,
                hadar_plan_session=hadar_plan_session,
                contact2_phone=contact2_phone,
                contact2_first_name=contact2_first_name,
                contact1_phone=contact1_phone,
                contact1_first_name=contact1_first_name,
                teudatZehut=teudatZehut,
                birthday_ivry=birthday_Ivry,
                birthday=birthday_loazi,
                unit_name=unit_name,
                accompany_id=accompany_id,
                contact3_email=contact3_email,
                contact3_first_name=contact3_first_name,
                contact3_phone=contact3_phone,
                marriage_date_ivry=marriage_date,
                marriage_date=marriage_date_loazi,
                spirit_status=matzbar,
                contact2_email=contact2_email,
                # worktype=worktype,
                workoccupation=workoccupation,
                educationfaculty=educationfaculty,
                workplace=workplace,
                workstatus=workstatus,
                high_school_teacher_phone=high_school_teacher_phone,
                high_school_name=high_school_name,
                paying=paying,
                contact1_relation=contact1_first_relation,
                contact2_relation=contact2_first_relation,
                contact3_relation=contact3_first_relation

            )
            db.session.add(Apprentice1)
        except Exception as e:
            return jsonify({'result': 'error while inserting' + str(e)}), HTTPStatus.BAD_REQUEST
    db.session.commit()
    return [x for x in uncommited_ids if x is not None]


def addUsers(wb):
    sheet = wb.active
    uncommited_ids = []
    for row in sheet.iter_rows(min_row=2):
        if row[0].value is None or row[1].value is None or row[2].value is None or row[5].value is None:
            uncommited_ids.append(row[5].value)
            continue
        role_ids = ""
        if "מלווה" in row[2].value.strip():
            role_ids += "0,"
        if "רכז מוסד" in row[2].value.strip():
            role_ids += "1,"
        if "רכז אשכול" in row[2].value.strip():
            role_ids += "2,"
        if "אחראי תוכנית" in row[2].value.strip():
            role_ids += "3,"
        role_ids = role_ids[:-1]
        first_name = row[0].value.strip()
        last_name = row[1].value.strip()
        institution_name = row[3].value.strip() if not row[3].value is None else "לא ידוע"
        cluster_name = row[4].value.strip() if not row[4].value is None else None
        phone = str(row[5].value).replace("-", "").strip()
        # email = row[3].value.strip()
        try:
            institution_id = db.session.query(Institution.id).filter(
                Institution.name == str(institution_name)).first()
            cluster_id = db.session.query(Cluster.id).filter(
                Cluster.name == cluster_name).first()


            user = User(
                id=int(str(phone).replace("-", "")),
                name=first_name,
                last_name=last_name,
                role_ids=role_ids,
                # email=str(email),
                cluster_id=cluster_id.id,
                institution_id=institution_id.id if institution_id else None,
            )

            db.session.add(user)

            db.session.commit()
        except Exception as e:
            print(str(e))
            return jsonify({'result': 'error while inserting' + str(e)}), HTTPStatus.BAD_REQUEST
    return [x for x in uncommited_ids if x is not None]


@master_user_form_blueprint.route("/initDB", methods=['put'])
def initDB():
    try:
        type = request.args.get('type')
        total = request.args.get('total')

        giftCode = db.session.query(Gift).delete()
        giftCode = db.session.query(Report).delete()
        giftCode = db.session.query(Message).delete()
        giftCode = db.session.query(Task).delete()
        giftCode = db.session.query(User).delete()
        giftCode = db.session.query(Apprentice).delete()
        giftCode = db.session.query(Base).delete()

        db.session.commit()
        uncommited_ids = []
        if total:
            path = base_dir + 'data/citiesToAdd.xlsx'
            wb = load_workbook(filename=path)
            res = db.session.query(City).delete()
            upload_CitiesDB(wb)
            path = base_dir + 'data/mosad.xlsx'
            wb = load_workbook(filename=path)
            res = db.session.query(Institution).delete()
            add_mosad_excel(wb)
            upload_baseDB()
        if type == "lab":
            path = 'data/apprentice_enter_lab.xlsx'
            wb = load_workbook(filename=path)
            for i in addApperntice(wb):
                uncommited_ids.append(i)
            for row in db.session.query(Apprentice).all():
                setattr(row, "association_date", '2023-05-01')
            db.session.commit()
            print("appretice lab loaded")
            path = 'data/user_enter_lab.xlsx'
            wb = load_workbook(filename=path)
            for i in addUsers(wb):
                uncommited_ids.append(i)
            print("user  lab loaded")
        else:
            path = 'data/user_PROD.xlsx'
            wb = load_workbook(filename=path)
            for i in addUsers(wb):
                uncommited_ids.append(i)
            print("user  loaded")
            path = 'data/apprentice_PROD.xlsx'
            wb = load_workbook(filename=path)
            for i in addApperntice(wb):
                uncommited_ids.append(i)
            print("appretice  loaded")
            path = 'data/messages.xlsx'
            wb = load_workbook(filename=path)
            add_message(wb)
            print("message  loaded")
            path = 'data/report.xlsx'
            wb = load_workbook(filename=path)
            add_report(wb)
            print("report  loaded")
            print(uncommited_ids)
        return jsonify({'result': 'success', "uncommited_ids": uncommited_ids}), HTTPStatus.OK
    except Exception as e:
        print(str(e))
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST


def add_message(wb):
    # /home/ubuntu/flaskapp/

    sheet = wb.active
    for row in sheet.iter_rows(min_row=2):
        created_by_id = row[0].value
        created_for_id = row[1].value
        created_at = row[2].value
        subject = row[3].value
        content = row[4].value
        ent_group = row[6].value.strip() if row[6].value else ""
        attachments = str(row[5].value).split(",")
        icon = row[7].value.strip()
        type = row[8].value.strip()

        if attachments == ["None"]:
            attachments = []
        rep = Message(
            icon=icon,
            id=int(str(uuid.uuid4().int)[:5]),
            type=type,
            created_by_id=created_by_id or "",
            created_at=created_at,
            ent_group=ent_group or "",
            content=content or "",
            subject=subject or "",
            attachments=attachments,
            allreadyread=False,
            created_for_id=created_for_id or ""
        )
        db.session.add(rep)
    try:
        db.session.commit()
    except Exception as e:
        return jsonify({'result': 'error while inserting' + str(e)}), HTTPStatus.BAD_REQUEST

    return jsonify({'result': 'success'}), HTTPStatus.OK


def add_report(wb):
    # /home/ubuntu/flaskapp/
    sheet = wb.active
    for row in sheet.iter_rows(min_row=2):
        user_id = row[0].value
        ent_reported = row[1].value
        visit_date = row[2].value
        title = row[3].value
        visit_in_army = row[4].value
        description = row[5].value
        attachments = str(row[6].value).split(",")
        ent_group = row[7].value
        if attachments == ["None"]:
            attachments = []
        rep = Report(

            id=int(str(uuid.uuid4().int)[:5]),
            user_id=user_id,
            ent_reported=ent_reported,
            visit_date=visit_date,
            title=title,
            visit_in_army=visit_in_army,
            description=description,
            attachments=attachments,
            allreadyread=False,
            ent_group=ent_group
        )
        db.session.add(rep)
    try:
        db.session.commit()
    except Exception as e:
        return jsonify({'result': 'error while inserting' + str(e)}), HTTPStatus.BAD_REQUEST

    return jsonify({'result': 'success'}), HTTPStatus.OK


def upload_CitiesDB(wb):
    try:
        import csv
        my_list = []
        sheet = wb.active
        for row in sheet.iter_rows(min_row=2):
                my_list.append(City(row[2].value, row[1].value.strip(), row[0].value))
        for ent in my_list:
            db.session.add(ent)
            db.session.commit()

        return jsonify({"result": "success"}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.OK


def add_mosad_excel(wb):
    sheet = wb.active
    not_commited = []
    for row in sheet.iter_rows(min_row=2):
        name = row[0].value.strip()
        phone = str(row[1].value)
        email = row[2].value.strip()
        eshcol = row[3].value.strip()
        roshYeshiva_phone = row[4].value
        roshYeshiva_name = row[5].value.strip()
        admin_phone = row[6].value.strip()
        admin_name = row[7].value.strip()
        owner_id = row[8].value
        logo_path = row[9].value.strip() if row[9].value else ""
        address = row[10].value.strip()
        city = row[11].value.strip()
        contact_name = row[12].value.strip()
        contact_phone = row[13].value
        try:
            CityId = db.session.query(City.id).filter(City.name == city).first()
            Institution1 = db.session.query(Institution.id).filter(Institution.name == name).first()
            if Institution1:
                not_commited.append(name)
                continue
            Cluster1 = db.session.query(Cluster.id).filter(Cluster.name == eshcol).first()
            if Cluster1:
                cluster_id1=Cluster1.id
            else:
                cluster_id1=uuid.uuid4()
                Cluster1=Cluster(id=cluster_id1,name=eshcol)
                db.session.add(Cluster1)
            Institution1 = Institution(
                # email=email,
                id=str(uuid.uuid4().int)[:5],
                cluster_id=cluster_id1,
                roshYeshiva_phone=roshYeshiva_phone,
                roshYeshiva_name=roshYeshiva_name,
                admin_phone=admin_phone,
                admin_name=admin_name,
                name=name,
                owner_id=owner_id,
                logo_path=logo_path,
                contact_phone=str(contact_phone),
                contact_name=str(contact_name),
                phone=phone,
                city_id=CityId.id,
                address=address
            )
            db.session.add(Institution1)
            db.session.commit()
        except Exception as e:
            print(str(e))
            not_commited.append(name)
    return jsonify({'result': 'success', "not_commited": not_commited}), HTTPStatus.OK


def upload_baseDB():
    try:
        import csv
        my_list = []
        # /home/ubuntu/flaskapp/
        with open(base_dir + 'data/base_add.csv', 'r', encoding="utf8") as f:
            reader = csv.reader(f)
            for row in reader:
                ent = Base(str(uuid.uuid4().int)[:5], row[0].strip(), row[1].strip())
                db.session.add(ent)
        db.session.commit()
        return jsonify({"result": "success"}), HTTPStatus.OK
    except Exception as e:
        print(str(e))
        return jsonify({'result': str(e)}), HTTPStatus.OK
