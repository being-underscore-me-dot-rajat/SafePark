import sqlite3
from datetime import datetime

DB_NAME = "src/models/safepark.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT CHECK(role IN ('admin', 'user')) NOT NULL
    );
    ''')

    cursor.execute('''
    INSERT INTO users (email, password, name, role)
    SELECT '21f3002175@ds.study.iitm.ac.in', 'admin123', 'Admin SafePark', 'admin'
    WHERE NOT EXISTS (SELECT 1 FROM users WHERE role='admin');
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS parking_lots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    total_spots INTEGER NOT NULL,
    price_per_hour REAL NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS addresses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lot_id INTEGER NOT NULL,
    address_line1 TEXT NOT NULL,
    address_line2 TEXT,
    pincode TEXT NOT NULL,
    latitude REAL,
    longitude REAL,
    FOREIGN KEY (lot_id) REFERENCES parking_lots(id) ON DELETE CASCADE
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS parking_spots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lot_id INTEGER NOT NULL,
    spot_number TEXT NOT NULL,
    status TEXT CHECK(status IN ('available', 'occupied')) NOT NULL DEFAULT 'available',
    FOREIGN KEY (lot_id) REFERENCES parking_lots(id) ON DELETE CASCADE,
    UNIQUE (lot_id, spot_number)
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    spot_id INTEGER NOT NULL,
    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    end_time DATETIME,
    cost REAL,
    remarks TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (spot_id) REFERENCES parking_spots(id) ON DELETE CASCADE
    );
    ''')

    conn.commit()
    conn.close()
    print("✅ SQLite tables created.")

if __name__ == "__main__":
    init_db()
