from flask import Flask, request, jsonify,Blueprint
from app import app, db
from model.models import user1,Apprentice
import time
from sqlalchemy import select,or_,and_,insert
from datetime import datetime, timedelta
from sqlalchemy.sql.expression import cast

views = Blueprint('app', __name__)



@app.route('/getApprenticeProfile/<int:id>', methods=['GET'])
def getProfile(id):
#currently return family and private name only
    if not validate_string(str(id)):
        status = False
        message = "Invalid id"
        response = construct_response(status=status, message=message)
        return jsonify(response)
    profile = db.session.query(Apprentice.privatename,Apprentice.familyname).filter(Apprentice.id==str(id)).all()
    if profile is None :
        status = False
        message = "profile  incorrect"
        response = construct_response(status=status, message=message)
        return jsonify(response)
    else:
        # Increase login count by 1
        status = True
        message = "profile valid"
        data = {"token" : str(profile)}
        response = construct_response(status=status, message=message, data=data)
        return jsonify(response)

@app.route('/getUser1Profile/<int:id>', methods=['GET'])
def getUser1Profile(id):
# currently return family and private name only
    if not validate_string(str(id)):
        status = False
        message = "Invalid id"
        response = construct_response(status=status, message=message)
        return jsonify(response)
    profile = db.session.query(user1.familyname,user1.privatename).filter(user1.id==str(id)).all()
    if profile is None :
        status = False
        message = "profile  incorrect"
        response = construct_response(status=status, message=message)
        return jsonify(response)
    else:
        # Increase login count by 1
        status = True
        message = "profile valid"
        data = {"token" : str(profile)}
        response = construct_response(status=status, message=message, data=data)
        return jsonify(response)
@app.route('/getBirthDays/<int:id>', methods=['GET'])
def getBirthDays(id):
# currently return family and private name and birthady in that their date is following 30 days
    if not validate_string(str(id)):
        status = False
        message = "Invalid id"
        response = construct_response(status=status, message=message)
        return jsonify(response)
    now = datetime.now()
    now_date = now.strftime('%Y-%m-%d')
    yesterday_datetime = datetime.now() + timedelta(days=30)
    yesterday_date = yesterday_datetime.strftime('%Y-%m-%d')
    qry = db.session.query(Apprentice.birthday,Apprentice.privatename,Apprentice.familyname).filter(and_(Apprentice.birthday.between(str(yesterday_date), str(now_date))),Apprentice.id==str(id)).all()
    #birthdays = db.session.query(Apprentice.birthday,Apprentice.privatename,Apprentice.familyname).filter(Apprentice.id==str(id)).all()
    if qry is None :
        status = False
        message = "birthdays  incorrect"
        response = construct_response(status=status, message=message)
        return jsonify(response)
    else:
        # Increase login count by 1
        status = True
        message = "birthdays valid"
        data = {"token" : str(qry)}
        response = construct_response(status=status, message=message, data=data)
        return jsonify(response)
@app.route('/getApprentice/<int:id>', methods=['GET'])
def getApprentice(id):
    if not validate_string(str(id)):
        status = False
        message = "Invalid data"
        response = construct_response(status=status, message=message)
        return jsonify(response)
    query = db.session.query(user1.apprentice).filter(and_(user1.id == str(id),user1.apprentice!="None")).all()
    print(query)
    if query is None :
        status = False
        message = "apprentice  incorrect"
        response = construct_response(status=status, message=message)
        return jsonify(response)
    else:
        # Increase login count by 1
        status = True
        message = "apprentice valid"
        data = {"token" : str(query).replace(" ","")}
        response = construct_response(status=status, message=message, data=data)
        return jsonify(response)

@app.route('/callsTodo/<int:id>', methods=['GET'])
def callsTodo(id):
    if not validate_string(str(id)):
        status = False
        message = "Invalid data"
        response = construct_response(status=status, message=message)
        return jsonify(response)

    current_time = datetime.datetime.utcnow()
    ten_weeks_ago = current_time - datetime.timedelta(days=3)

    result = db.session.query(Apprentice.id).filter(Apprentice.melavename == str(id),
                                                    Apprentice.lastconatctdate < ten_weeks_ago).all()
    if result is None :
        status = False
        message = "callstodo  incorrect"
        response = construct_response(status=status, message=message)
        return jsonify(response)
    else:
        # Increase login count by 1
        status = True
        message = "callstodo valid"
        data = {"token" : str(result)}
        response = construct_response(status=status, message=message, data=data)
        return jsonify(response)

@app.route('/meetingsTodo/<int:id>', methods=['GET'])
def meetingsTodo(id):
        if not validate_string(str(id)):
            status = False
            message = "Invalid data"
            response = construct_response(status=status, message=message)
            return jsonify(response)
        current_time = datetime.datetime.utcnow()
        ten_weeks_ago = current_time - datetime.timedelta(days=3)
        result = db.session.query(Apprentice.id).filter(Apprentice.melavename == str(id),
            Apprentice.lastvisitdate < ten_weeks_ago).all()

        if result is None:
            status = False
            message = "callstodo  incorrect"
            response = construct_response(status=status, message=message)
            return jsonify(response)
        else:

            # Increase login count by 1
            status = True
            message = "callstodo valid"
            data = {"token": str(result)}
            response = construct_response(status=status, message=message, data=data)
            return jsonify(response)


@app.route('/interaction/<int:ApprenticeId>/<int:type>', methods=['get'])
def interaction(ApprenticeId,type):
    print(ApprenticeId)
    if not validate_string(str(ApprenticeId)):
        status = False
        message = "Invalid data"
        response = construct_response(status=status, message=message)
        return jsonify(response)
    if type==1:
        db.session.query(Apprentice). \
            filter(Apprentice.id == ApprenticeId). \
            update({'lastvisitdate': "now"})
        db.session.commit()
        return jsonify(["Register success"])

    if type == 2:
        db.session.query(Apprentice). \
            filter(Apprentice.id == ApprenticeId). \
            update({'lastconatctdate': "now"})
        db.session.commit()
        status = True
        message = "Interaction valid for ApprenticeId: "+str(ApprenticeId)
        response = construct_response(status=status, message=message)
        return jsonify(response)

    return jsonify(["fail insert"])


######################not in use from here but u can take inspair#########################
@app.route('/API/test')
def test_api():
    time.sleep(1)
    return "Home Of T_H"

@app.route('/login', methods=['POST'])
def login():
    time.sleep(1)
    content = request.json

    username = get_value_from_dict(content,"email")
    password = get_value_from_dict(content,"password")

    if not validate_string(username) or not validate_string(password):
        status = False
        message = "Invalid data"
        response = construct_response(status=status, message=message)
        return jsonify(response)

    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(password):
        status = False
        message = "Username or password incorrect"
        response = construct_response(status=status, message=message)
        return jsonify(response)

    else:
        # Increase login count by 1
        user.login_counts = user.login_counts + 1
        db.session.commit()

        status = True
        message = "User logged in"
        data = {"token" : str(user.id)}
        response = construct_response(status=status, message=message, data=data)
        return jsonify(response)


@app.route('/API/get_profile', methods=['POST'])
def get_profile():
    time.sleep(1)
    content = request.json
    token = get_value_from_dict(content,"token")

    user = test.query.filter_by(id=token).first()
    if user is None:
        status = False
        message = "User not found"
        response = construct_response(status=status, message=message)
        return jsonify(response)

    else:
        status = True
        message = "User found"
        data = user.get_json_data()
        response = construct_response(status=status, message=message, data=data)
        return jsonify(response)


# Helpers
def validate_string(input):
    if input is None or not input.strip():
        return False
    return True


def validate_list_of_strings(list):
    for i in list:
        if not validate_string(i):
            return False
    return True

def get_value_from_dict(dict,key):
    if key not in dict:
        return None
    return dict[key]

def construct_response(status, message, data=None):
    return {
        "status": status,
            "message": message,
        "data": data
    }


@app.route('/')
#jsut print all contant of user1 table
def index():
    try:
        query1=db.select(Apprentice.birthday).where(Apprentice.melavename=="3")
        socks = db.session.execute(query1).scalars()
        sock_text = '<ul>'
        for sock in socks:
                sock_text += '<li>' + sock+ '</li>'
        sock_text += '</ul>'
        return sock_text
    except Exception as e:
        # e holds description of the error
        error_text = "<p>The error:<br>" + str(e) + "</p>"
        hed = '<h1>Something is broken.</h1>'
        return hed + error_text


@app.route('/register', methods=['POST'])
def register():
    d = {}
    if request.method == "POST":
        mail = request.form["email"]
        password = request.form["password"]
        print(mail)
        print(password)
        email = user1.query.filter_by(email=mail).first()
        if email is None:
            register = user1(email=mail, password=password)
            print(register)
            db.session.add(register)
            db.session.commit()
            return jsonify(["Register success"])
        else:
            # already exist
            return jsonify(["user alredy exist"])
