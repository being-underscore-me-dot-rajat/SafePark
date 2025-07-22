from flask import Flask, request, jsonify,g
from flask_cors import CORS
from controllers.Celery.celery_worker import celery


app = Flask(__name__)
CORS(app)

celery.conf.update(app.config)
import controllers.auth as auth
from controllers.auth import jwt_required


from controllers import getfromdb
from controllers import addtodb
from controllers import editindb


@app.route('/register', methods=['GET','POST'])
def register():
    return auth.signup(request.get_json())

@app.route('/login', methods=['GET','POST'])
def login():
    return auth.login(request.get_json())

@app.route('/verify-otp', methods=['GET','POST'])
def verify_otp():
    return auth.verify_otp(request.get_json())

@app.route('/parkinglots',methods=['GET','POST'])
@jwt_required
def get_ports():
    return getfromdb.get_all_lots()

@app.route('/addparkinglots',methods=['GET','POST'])
def add_lots():
    return addtodb.addlot(request.get_json())

@app.route('/editlot', methods=['POST'])
def edit_lot():
    return editindb.edit_lot(request.get_json())

@app.route('/deletelot/<int:lot_id>', methods=['POST'])
def delete_lot(lot_id):
    return editindb.delete_lot(lot_id)

@app.route('/addbooking', methods=['POST'])
@jwt_required
def add_booking():
    return addtodb.add_booking(request.get_json())

@app.route("/viewbookings", methods=["GET"])
@jwt_required
def get_user_bookings():
    return(getfromdb.view_bookings(g.user_id))

@app.route("/deletebooking/<int:booking_id>", methods=["DELETE"])
@jwt_required
def remove_booking(booking_id):
    getfromdb.delete_booking(booking_id)
    return jsonify({"message": "Booking deleted successfully."}), 200

@app.route("/getlotcoords/<lot_name>", methods=["GET"])
def get_lot_coords(lot_name):
    result = getfromdb.get_lot_coordinates(lot_name) 
    if result:
        return jsonify(result)
    else:
        return jsonify({"error": "Lot not found"}), 404
    
@app.route("/provideendtime", methods=["POST"])
@jwt_required
def update_booking_end_time():
    return editindb.provide_end_time_and_cost(request.get_json())


if __name__ == '__main__':
    app.run(debug=True)
