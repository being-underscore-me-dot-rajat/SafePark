from .dbconnect import getconnection
from flask import jsonify
from datetime import datetime
import re

from datetime import datetime

def parse_iso_time(value):
    if isinstance(value, datetime):
        return value
    if not isinstance(value, str):
        return None

    value = value.strip()

    # # Handle UTC "Z" by replacing with +00:00 (Python 3.12 handles %z)
    # if value.endswith("Z"):
    #     value = value[:-1] + "+00:00"

    # # If time is without seconds, add ":00"
    # if "T" in value and len(value.split("T")[1].split(":")) == 2:
    #     value = value[:-6] + ":00" + value[-6:] if "+" in value else value + ":00"

    # Try multiple formats
    time_formats = [
        "%Y-%m-%dT%H:%M:%S.%f%z",  # e.g. 2025-07-27T18:35:00.000+05:30
        "%Y-%m-%dT%H:%M:%S%z",     # e.g. 2025-07-27T18:35:00+05:30
        "%Y-%m-%dT%H:%M%z",        # e.g. 2025-07-27T18:35+05:30
        "%Y-%m-%dT%H:%M:%S",       # fallback no tz
        "%Y-%m-%d %H:%M:%S"        # SQLite format
    ]

    for fmt in time_formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue

    return None


def edit_lot(data):
    from datetime import datetime
    try:
        lot_id = data.get('id')
        name = data.get('name')
        total_spots = data.get('totalSpots')
        price = data.get('pricePerHour')
        ad1 = data.get('addressLine1')
        ad2 = data.get('addressLine2')
        lat = data.get('latitude')
        longi = data.get('longitude')
        # print(data)
        conn = getconnection()
        cursor = conn.cursor()

        cursor.execute('SELECT name, total_spots, price_per_hour FROM parking_lots WHERE id=?', (lot_id,))
        old = cursor.fetchone()
        if not old:
            return {"error": "Lot not found"}, 404
        old_name, old_total_spots, old_price = old

        cursor.execute('SELECT spot_number FROM parking_spots WHERE lot_id=?', (lot_id,))
        all_spots = cursor.fetchall()
        spot_numbers = [spot[0] for spot in all_spots]
        # print(len(spot_numbers))

        cursor.execute('''
            SELECT ps.spot_number, b.end_time
            FROM bookings b
            JOIN parking_spots ps ON b.spot_id = ps.id
            WHERE ps.lot_id = ?
        ''', (lot_id,))
        rows = cursor.fetchall()
        # print(rows)

        now = datetime.now()
        # print(now)
        reserved_spots = []

        for spot_number, end_time in rows:
            if end_time is None:
                reserved_spots.append(spot_number)
                continue

            parsed_end = parse_iso_time(end_time)
            if parsed_end is None or parsed_end >= now:
                reserved_spots.append(spot_number)

        reserved_set = set(reserved_spots)
        # print(reserved_set)
        if old_name != name:
            # print("Name being changed")
            cursor.execute("UPDATE parking_lots SET name=? WHERE id=?", (name, lot_id))
            for idx, old_spot_number in enumerate(spot_numbers, start=1):
                new_spot_number = f"{name}_{idx}"
                cursor.execute(
                    "UPDATE parking_spots SET spot_number=? WHERE lot_id=? AND spot_number=?",
                    (new_spot_number, lot_id, old_spot_number)
                )

        cursor.execute("SELECT address_line1, address_line2, latitude, longitude FROM addresses WHERE lot_id=?", (lot_id,))
        a1, a2, la, lo = cursor.fetchone()
        if (ad1, ad2, lat, longi) != (a1, a2, la, lo):
            # print("Adress being changed")
            cursor.execute(
                "UPDATE addresses SET address_line1=?, address_line2=?, latitude=?, longitude=? WHERE lot_id=?",
                (ad1, ad2, lat, longi, lot_id)
            )

        delta_spots = total_spots - old_total_spots
        if delta_spots > 0:
            # print("No. of spots being changed")
            for i in range(old_total_spots + 1, total_spots + 1):
                spot_name = f"{name}_{i}"
                cursor.execute(
                    "INSERT INTO parking_spots (lot_id, spot_number) VALUES (?, ?)",
                    (lot_id, spot_name)
                )
        elif delta_spots < 0:
            all_current_spot_numbers = [f"{name}_{i}" for i in range(1, old_total_spots + 1)]
            unreserved_spots = [sn for sn in all_current_spot_numbers if sn not in reserved_set]
            num_to_remove = -delta_spots
            if len(unreserved_spots) >= num_to_remove:
                spots_to_remove = sorted(unreserved_spots, key=lambda s: int(s.split('_')[-1]), reverse=True)[:num_to_remove]
                for spot_number in spots_to_remove:
                    cursor.execute("DELETE FROM parking_spots WHERE lot_id=? AND spot_number=?", (lot_id, spot_number))
            else:
                return {"error": "Cannot decrease spots: not enough unreserved spots."}, 400

        if old_price != price:
            if reserved_spots:
                return {"error": "Price cannot be changed while spots are reserved."}, 400
            cursor.execute("UPDATE parking_lots SET price_per_hour=? WHERE id=?", (price, lot_id))

        conn.commit()
        return {"message": "Lot updated successfully"}, 200

    except Exception as e:
        conn.rollback()
        return {"error": str(e)}, 500
    finally:
        conn.close()



def delete_lot(lot_id):
    try:
        conn = getconnection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM parking_spots WHERE lot_id=?", (lot_id,))
        cursor.execute("DELETE FROM addresses WHERE lot_id=?", (lot_id,))
        cursor.execute("DELETE FROM parking_lots WHERE id=?", (lot_id,))

        conn.commit()
        return {"message": "Lot deleted successfully"}, 200

    except Exception as e:
        conn.rollback()
        print(f"❌ Error deleting lot: {e}")
        return {"error": str(e)}, 500
    finally:
        conn.close()

def provide_end_time_and_cost(data):
    print("this funcitn was called")
    import math
    from datetime import datetime
    booking_id = data.get("booking_id")
    end_time_str = data.get("end_time")
    if not booking_id or not end_time_str:
        return jsonify({"error": "Missing booking_id or end_time"}), 400

    conn = getconnection()
    cursor = conn.cursor()

    cursor.execute("SELECT start_time, spot_id FROM bookings WHERE id = ?", (booking_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return jsonify({"error": "Booking not found or already has end time"}), 404

    start_time_str, spot_id = row
    start_dt=start_time_str
    end_dt=end_time_str
    # print(start_dt)
    # print(end_dt)
    start_dt = parse_iso_time(start_time_str)
    end_dt = parse_iso_time(end_time_str)


    if not isinstance(start_dt, datetime) or not isinstance(end_dt, datetime):
        conn.close()
        return jsonify({"error": "Invalid datetime format"}), 400

    if end_dt <= start_dt:
        conn.close()
        return jsonify({"error": "End time must be after start time"}), 400

    cursor.execute("SELECT lot_id FROM parking_spots WHERE id = ?", (spot_id,))
    lot_row = cursor.fetchone()
    if not lot_row:
        conn.close()
        return jsonify({"error": "Spot not found"}), 404
    lot_id = lot_row[0]

    cursor.execute("SELECT price_per_hour FROM parking_lots WHERE id = ?", (lot_id,))
    price_row = cursor.fetchone()
    if not price_row:
        conn.close()
        return jsonify({"error": "Lot not found"}), 404
    price_per_hour = price_row[0]

    duration_hours = (end_dt - start_dt).total_seconds() / 3600.0
    cost = math.ceil(duration_hours) * price_per_hour

    # print(end_time_str,cost)

    cursor.execute("SELECT name FROM parking_lots WHERE id=?", (lot_id,))
    lot_name = cursor.fetchone()[0]
    from flask import g
    cursor.execute("SELECT email FROM users WHERE id=?", (g.user_id,))
    user_email = cursor.fetchone()[0]

    cursor.execute('''Select spot_number from parking_spots where id=?''',(spot_id,))
    spot_number=cursor.fetchone()[0]

    from controllers.Celery.tasks import Endtimeprovided
    Endtimeprovided(user_email, lot_name, spot_number, start_dt,end_dt,cost)

    cursor.execute(
        "UPDATE bookings SET end_time = ?, cost = ? WHERE id = ?",
        (end_time_str, cost, booking_id)
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "End time and cost updated successfully", "cost": cost}), 200