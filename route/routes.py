from flask import Flask, request, jsonify,Blueprint
from app import app, db
from model.models import user1
import time
views = Blueprint('views', __name__)

@app.route('/')
def index():
    try:
        socks = db.session.execute(db.select(user1)

            .order_by(user1.email)).scalars()

        sock_text = '<ul>'
        for sock in socks:
            sock_text += '<li>' + sock.email + ', ' + sock.password + '</li>'
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
