import sqlite3

def getconnection():
    dbname="src/models/safepark.db"
    connection=sqlite3.connect(dbname)
    return connection

