from .dbconnect import getconnection
from flask import jsonify

def get_all_lots():
    conn=getconnection()
    cursor=conn.cursor()
    cursor.execute('''
    SELECT 
    parking_lots.id,
    parking_lots.name,
    parking_lots.total_spots,
    parking_lots.price_per_hour,
    addresses.address_line1,
    addresses.address_line2,
    addresses.latitude,
    addresses.longitude
    FROM parking_lots
    JOIN addresses ON parking_lots.id = addresses.lot_id;
    ''')
    rows=cursor.fetchall()
    lots = [
        {
            "id": row[0],
            "name": row[1],
            "total_spots": row[2],
            "price_per_hour": row[3],
            "address_line1": row[4],
            "address_line2": row[5],
            "latitude": row[6],
            "longitude": row[7]
        }
        for row in rows
    ]
    # print(lots)
    return jsonify(lots)

def get_lot_coordinates(lot_name):
    conn = getconnection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.latitude, a.longitude
        FROM addresses a
        JOIN parking_lots pl ON a.lot_id = pl.id
        WHERE pl.name = ? 
    """, (lot_name,))
    row = cursor.fetchone()
    conn.close()
    if row:
        # print(row)
        return {"latitude": row[0], "longitude": row[1]}
    return None


def parse_iso_time(raw_time):
    from datetime import datetime
    if not raw_time:
        return None
    if isinstance(raw_time, datetime):
        return raw_time  # already datetime object
    
    try:
        if "T" in raw_time and "+" in raw_time:
            # Example: 2025-07-26T10:30:00+05:30
            from dateutil import parser
            return parser.isoparse(raw_time)
        elif "T" in raw_time:
            return datetime.strptime(raw_time, "%Y-%m-%dT%H:%M:%S")
        else:
            return datetime.strptime(raw_time, "%Y-%m-%d %H:%M:%S")
    except Exception as e:
        # print("Time parsing failed:", e)
        return raw_time


def view_bookings(user_id):
    import os
    hour_format = "%#I:%M %p, %d %B %Y" if os.name == 'nt' else "%-I:%M %p, %d %B %Y"
    from datetime import datetime
    conn = getconnection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT b.id, b.spot_id, b.start_time, b.end_time, b.cost,
               ps.spot_number, pl.price_per_hour,pl.name lot_name
        FROM bookings b
        JOIN parking_spots ps ON b.spot_id = ps.id
        JOIN parking_lots pl ON ps.lot_id = pl.id
        WHERE b.user_id = ?
    ''', (user_id,))
    
    bookings = cursor.fetchall()
    formatted_bookings = []

    for b in bookings:
        start_time = b[2]
        end_time = b[3]

        dt = parse_iso_time(start_time)
        if isinstance(dt, datetime):
            start_time = dt.strftime(hour_format)   

        dt = parse_iso_time(end_time)
        if isinstance(dt, datetime):
            end_time = dt.strftime(hour_format)

        # print(start_time,end_time)

        formatted_bookings.append({
            "id": b[0],
            "spot_id": b[1],
            "start_time": start_time,
            "end_time": end_time,
            "cost": b[4],
            "spot_number": b[5],
            "price_per_hour":b[6],
            "lot_name": b[7],
        })

    conn.close()
    return jsonify(formatted_bookings)

def delete_booking(booking_id):
    conn = getconnection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM bookings WHERE id = ?', (booking_id,))
    conn.commit()
    conn.close()

def getusers():
    conn = getconnection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, email 
        FROM users
        where role='user'
    """)
    rows = cursor.fetchall()
    conn.close()

    users = [
        {"id": row[0], "name": row[1], "email": row[2]}
        for row in rows
    ]
    return users

def user_bookings(id):
    conn = getconnection()
    cursor = conn.cursor()
    cursor.execute('''SELECT 
        pl.name AS lot_name,
        ps.id AS spot_id,
        b.start_time,
        b.end_time,
        CASE 
            WHEN b.end_time > CURRENT_TIMESTAMP AND b.cost IS NULL THEN 'Ongoing'
            ELSE printf('%d', b.cost)
        END AS cost_status
    FROM 
        bookings b
    JOIN 
        parking_spots ps ON b.spot_id = ps.id
    JOIN 
        parking_lots pl ON ps.lot_id = pl.id
    WHERE 
        b.user_id = ?
    ORDER BY 
        b.start_time DESC;
    ''',(id,))
    rows=cursor.fetchall()
    conn.close()
    userhistory = [
        {"lot": row[0], "spot": row[1], "starttime": row[2],"endtime": row[3],'cost':row[4]}
        for row in rows
    ]
    return userhistory

def getallbookings():
    conn = getconnection()
    cursor = conn.cursor()
    cursor.execute('''SELECT 
        u.id,
        u.name,
        pl.name AS lot_name,
        ps.spot_number AS spot_id,
        b.start_time,
        b.end_time,
        CASE 
        WHEN b.end_time > CURRENT_TIMESTAMP AND b.cost IS NULL THEN 'Ongoing'
        ELSE printf('%d', b.cost)
        END AS cost_status,
        b.id
    FROM 
        bookings b
    JOIN 
        parking_spots ps ON b.spot_id = ps.id
    JOIN 
        parking_lots pl ON ps.lot_id = pl.id
    JOIN
        users u ON u.id=b.user_id
    ORDER BY 
        b.start_time DESC;
    ''')
    rows = cursor.fetchall()
    conn.close()
    bookinghistory = [
    {
        "user_id": row[0],
        "user_name": row[1],
        "lot": row[2],
        "spot": row[3],
        "starttime": row[4],
        "endtime": row[5],
        "cost": row[6],
        "Bid":row[7]
    }
    for row in rows
    ]
    return bookinghistory

# def getsomespots():
#     conn=getconnection()
#     cursor=conn.cursor()
#     cursor.execute('''
#     SELECT ps.spot_number, b.end_time
#     FROM bookings b
#     JOIN parking_spots ps ON b.spot_id = ps.id
#     WHERE ps.lot_id = 3;
#     ''')
#     print(cursor.fetchall())

# getsomespots()