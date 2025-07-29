from .dbconnect import getconnection

def addlot(data):
    lot_name=data.get('name')
    total_spots=data.get('totalSpots')
    price=data.get('pricePerHour')
    ad1=data.get('addressLine1')
    ad2=data.get('addressLine2')
    lat=data.get('latitude')
    longi=data.get('longitude')
    print(lot_name,total_spots,price,ad1,ad2,lat,longi)
    conn=getconnection()
    cursor=conn.cursor()
    try:
        cursor.execute('''
        Insert into parking_lots (name, total_spots,price_per_hour) VALUES (?,?,?)      
        ''',(lot_name,total_spots,price,))
        if (cursor.rowcount==0):
            return("Couldn't register the new lot")

        cursor.execute('''
        Select id from parking_lots where name=?
        ''',(lot_name,))

        lot_id=cursor.fetchone()
        lot_id = lot_id[0]

        cursor.execute('''
        Insert into addresses (lot_id,address_line1,address_line2,latitude,longitude) Values(?,?,?,?,?)
        ''',(lot_id,ad1,ad2,lat,longi))
        if (cursor.rowcount==0):
            return("Couldn't register the address for the new lot")

        for i in range(1,total_spots+1):
            spot_name=f"{lot_name}_{i}"
            cursor.execute('''
            Insert into parking_spots (lot_id,spot_number) Values (?,?)
            ''',(lot_id,spot_name))

        conn.commit()    

        return({"message": "Lot added successfully",
        }, 200) 
    except Exception as e:
        conn.rollback()
        print(f"❌ Error adding lot: {e}")
        return {"error": str(e)}, 500

    finally:
        conn.close()


from flask import jsonify,g
from datetime import datetime

def add_booking(data):
    from .editindb import parse_iso_time
    lot_id = data.get("spot_id")  
    start_time = data.get("start_time")
    end_time = data.get("end_time")
    cost = data.get("cost")
    # print(lot_id,start_time,end_time,cost)
    user_id = g.user_id 
    conn = getconnection()
    cursor = conn.cursor()

    spot_id = book_spot(lot_id, start_time)

    if end_time and cost == None:
        # print("cost updation called")
        from datetime import datetime
        import math

        # Parse times
        start_dt = parse_iso_time(start_time)
        end_dt = parse_iso_time(end_time)

        if not isinstance(start_dt, datetime) or not isinstance(end_dt, datetime):
            conn.close()
            return jsonify({"error": "Invalid datetime format"}), 400

        if end_dt <= start_dt:
            conn.close()
            return jsonify({"error": "End time must be after start time"}), 400

        cursor.execute("SELECT price_per_hour FROM parking_lots WHERE id = ?", (lot_id,))
        price_row = cursor.fetchone()
        if not price_row:
            conn.close()
            return jsonify({"error": "Lot not found"}), 404

        price_per_hour = price_row[0]
        duration_hours = (end_dt - start_dt).total_seconds() / 3600.0
        cost = math.ceil(duration_hours) * price_per_hour

            
        cursor.execute("SELECT name FROM parking_lots WHERE id=?", (lot_id,))
        lot_name = cursor.fetchone()[0]

        cursor.execute("SELECT email FROM users WHERE id=?", (user_id,))
        user_email = cursor.fetchone()[0]

        cursor.execute('''Select spot_number from parking_spots where id=?''',(spot_id,))
        spot_number=cursor.fetchone()[0]

        from controllers.Celery.tasks import booking_confirmation_email_with_cost
        booking_confirmation_email_with_cost(user_email, lot_name, spot_number, start_time, end_time, cost)

    elif cost == None:
        # print("Nill Cost updated")
        cost = None  
        cursor.execute("SELECT name FROM parking_lots WHERE id=?", (lot_id,))
        lot_name = cursor.fetchone()[0]

        cursor.execute("SELECT email FROM users WHERE id=?", (user_id,))
        user_email = cursor.fetchone()[0]

        cursor.execute('''Select spot_number from parking_spots where id=?''',(spot_id,))
        spot_number=cursor.fetchone()[0]

        from controllers.Celery.tasks import booking_confirmation_email_without_cost
        booking_confirmation_email_without_cost(user_email, lot_name, spot_number, start_time)

    # Insert booking
    cursor.execute('''
        INSERT INTO bookings (user_id, spot_id, start_time, end_time, cost)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, spot_id, start_time, end_time, cost))

    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({"message": "Booking failed"}), 500

    return jsonify({"message": "Booking successful"}), 200


def book_spot(lot_id, requested_start_time):
    import random
    conn = getconnection()
    cursor = conn.cursor()

    try:
        requested_dt = datetime.fromisoformat(requested_start_time)

        cursor.execute("SELECT id FROM parking_spots WHERE lot_id = ?", (lot_id,))
        spot_ids = [row[0] for row in cursor.fetchall()]

        available_spots = []

        for spot_id in spot_ids:

            cursor.execute("""
                SELECT end_time FROM bookings
                WHERE spot_id = ?
                ORDER BY start_time DESC
                LIMIT 1
            """, (spot_id,))
            row = cursor.fetchone()

            if not row:
                # No bookings → free
                available_spots.append(spot_id)
            else:
                end_time = row[0]
                try:
                    # If end_time exists and is valid, check if it's before requested time
                    if end_time and datetime.fromisoformat(end_time) < requested_dt:
                        available_spots.append(spot_id)
                except ValueError:
                    # If end_time is invalid (non-integer, wrong format), consider it blocked
                    continue

        if not available_spots:
            return None

        return random.choice(available_spots)

    finally:
        conn.close()

