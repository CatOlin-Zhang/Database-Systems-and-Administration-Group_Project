import pymysql

def get_db_connection():
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="", 
        database="ecommerce_platform",
        charset="utf8mb4"
    )
    return conn
