import sqlite3, os, bcrypt, jwt, datetime
from . import dbconnect
from flask import request, jsonify, g
import random, smtplib
import redis
from controllers.Celery.celery_worker import celery
from functools import wraps

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

JWT_SECRET = 'RcFaMGQ0/Zj4pVAeXn9GHaiixdOlWe0PsMtMmVZZUHg='  
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 3600 #Token Expiration time

def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')

        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'error': 'Authorization token is missing'}), 401

        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            g.user_id = payload['user_id']
            g.user_role = payload.get('role', 'user')
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return f(*args, **kwargs)
    return decorated_function

@celery.task(name='controllers.auth.send_email')
def send_email(subject, recipient, html_body):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    try:
        # Create message container
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = 'safepark123@gmail.com'
        msg['To'] = recipient

        # Attach HTML content
        msg.attach(MIMEText(html_body, 'html'))

        # Send the message
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('safepark123@gmail.com', 'ssww fanb mqkj nqrs')
        server.sendmail(msg['From'], [recipient], msg.as_string())
        server.quit()

        print(f"Email sent successfully to {recipient}")
    except Exception as e:
        print("Email failed:", str(e))

def sendotp(recipient, otp):
    print("OTP Task: Sending email to", recipient, "with OTP:", otp)
    message = f"Subject: Your OTP Verification Code\n\nYour OTP is: {otp}"
    send_email.delay(message,recipient)


def generate_token(user_id, role):
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1) 
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def login(data):
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Missing fields'}), 400

    conn = dbconnect.getconnection()
    cursor = conn.cursor()
    cursor.execute("SELECT id,name, email, password, role, is_verified FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return {"error": "Invalid email or password"}, 401

    user_id,name, email, hashed_pw, role, is_verified = user

    if not bcrypt.checkpw(password.encode('utf-8'), hashed_pw.encode('utf-8')):
        return {"error": "Invalid email or password"}, 401

    if not is_verified:
        sending_otp(email)
        return {
            "error": "Email not verified",
            "require_otp": True
        }, 403

    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return {
        "message": "Login successful",
        "token": token,
        "user": {
            "id":user_id,
            "name": name,
            "email": email,
            "role": role
        }
    }, 200


def signup(data):
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    print("registered name, email, password",name,email,password)

    if not name or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    conn = dbconnect.getconnection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users (name, email, password, role, is_verified) VALUES (?, ?, ?, ?, ?)",
                       (name, email, hashed_pw, 'user', 0))
        conn.commit()
        print("User got registered")
        user_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        print("Email already exists")
        return jsonify({"error": "Email already exists"}), 400
    finally:
        conn.close()

    sending_otp(email)
    return jsonify({
        "message": "User registered. OTP sent to email for verification."
    }), 201

def sending_otp(email):
    import random
    otp = str(random.randint(100000, 999999))
    print("otp",otp)
    redis_client.setex(f"otp:{email}", 300, otp)  

    sendotp(email, otp)

    return jsonify({
        "message": "Please enter the OTP sent to email for verification."
    }), 201


def verify_otp(data):
    email = data.get('email')
    otp = data.get('otp')

    stored_otp = redis_client.get(f"otp:{email}")
    if stored_otp is None:
        return jsonify({"error": "OTP expired or invalid"}), 400

    if otp != stored_otp:
        return jsonify({"error": "Invalid OTP"}), 400

    # OTP is valid → mark user as verified
    conn = dbconnect.getconnection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_verified = 1 WHERE email = ?", (email,))
    conn.commit()
    conn.close()

    # Delete OTP from Redis (optional, since it will expire anyway)
    redis_client.delete(f"otp:{email}")

    return jsonify({"message": "Email verified successfully"}), 200