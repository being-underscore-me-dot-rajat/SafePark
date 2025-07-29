import sqlite3

def getconnection():
    dbname="src/models/safepark.db"
    connection=sqlite3.connect(dbname)
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection

