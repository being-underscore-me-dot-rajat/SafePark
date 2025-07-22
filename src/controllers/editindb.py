from .dbconnect import getconnection
from flask import jsonify
# from .getfromdb import parse_iso_time
from datetime import datetime

from datetime import datetime
import re

def parse_iso_time(value):
    if isinstance(value, datetime):
        return value

    if not isinstance(value, str):
        return None

    # Remove 'Z' if present (ISO UTC designator)
    value = value.strip().replace("Z", "")

    time_formats = [
        "%Y-%m-%d %H:%M:%S",       # SQLite default
        "%Y-%m-%dT%H:%M:%S.%f",    # ISO with microseconds
        "%Y-%m-%dT%H:%M:%S",       # ISO without microseconds
        "%Y-%m-%dT%H:%M",          # fallback
    ]

    for fmt in time_formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue

    return None  # failed to parse


def edit_lot(data):
    try:
        lot_id = data.get('id')
        name = data.get('name')
        total_spots = data.get('totalSpots')
        price = data.get('pricePerHour')
        ad1 = data.get('addressLine1')
        ad2 = data.get('addressLine2')
        lat = data.get('latitude')
        longi = data.get('longitude')

        conn = getconnection()
        cursor = conn.cursor()

        # Delete old records
        cursor.execute("DELETE FROM parking_spots WHERE lot_id=?", (lot_id,))
        cursor.execute("DELETE FROM addresses WHERE lot_id=?", (lot_id,))
        cursor.execute("DELETE FROM parking_lots WHERE id=?", (lot_id,))

        # Reinsert with same id
        cursor.execute(
            "INSERT INTO parking_lots (id, name, total_spots, price_per_hour) VALUES (?, ?, ?, ?)",
            (lot_id, name, total_spots, price)
        )
        cursor.execute(
            "INSERT INTO addresses (lot_id, address_line1, address_line2, latitude, longitude) VALUES (?, ?, ?, ?, ?)",
            (lot_id, ad1, ad2, lat, longi)
        )

        for i in range(1, total_spots + 1):
            spot_name = f"{name}_{i}"
            cursor.execute(
                "INSERT INTO parking_spots (lot_id, spot_number) VALUES (?, ?)",
                (lot_id, spot_name)
            )

        conn.commit()
        return {"message": "Lot updated successfully"}, 200

    except Exception as e:
        conn.rollback()
        print(f"❌ Error editing lot: {e}")
        return {"error": str(e)}, 500

    finally:
        conn.close()



def delete_lot(lot_id):
    try:
        conn = getconnection()
        cursor = conn.cursor()

        # Delete spots and address first due to FK constraints
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
    import math
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
    start_dt = parse_iso_time(start_time_str)
    end_dt = parse_iso_time(end_time_str)

    print(start_dt,end_dt)

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

    # Update the booking
    cursor.execute(
        "UPDATE bookings SET end_time = ?, cost = ? WHERE id = ?",
        (end_time_str, cost, booking_id)
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "End time and cost updated successfully", "cost": cost}), 200
