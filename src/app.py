from flask import Flask, request, jsonify
from flask_cors import CORS
import controllers.getfromdb as get
import controllers.auth as auth
from controllers.Celery.celery_worker import make_celery

app = Flask(__name__)
CORS(app)

celery = make_celery(app)
auth.celery = celery 


@app.route('/register', methods=['GET','POST'])
def register():
    return auth.signup(request.get_json())

@app.route('/login', methods=['GET','POST'])
def login():
    return auth.login(request.get_json())

@app.route('/verify-otp', methods=['GET','POST'])
def verify_otp():
    return auth.verify_otp(request.get_json())


if __name__ == '__main__':
    app.run(debug=True)
