# import sqlite3
# import dbconnect

# def get_user(email,password):
#     connection=dbconnect.get_connection()
#     cursor=connection.cursor()
#     cursor.execute("Select name,role from  users where email=? and password=?",(email,password,))
#     cursor.fetchone()
#     print()
