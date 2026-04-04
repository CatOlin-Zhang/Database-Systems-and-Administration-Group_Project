from DataBase.db_connector import get_connection
from database.sql_statements import EcommerceSQL

#添加或更新评分
def add_or_update_rating(customer_id, vendor_id, score, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(EcommerceSQL.ADD_RATING, (customer_id, vendor_id, score, score))
    finally:
        if own_conn:
            conn.close()

# 获取一个供应商的所有评分
def get_vendor_ratings(vendor_id, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(EcommerceSQL.GET_VENDOR_RATINGS, (vendor_id,))
            return cursor.fetchall()
    finally:
        if own_conn:
            conn.close()

# 获取某客户对某个供应商的评分
def get_customer_vendor_rating(customer_id, vendor_id, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(EcommerceSQL.GET_CUSTOMER_VENDOR_RATING, (customer_id, vendor_id))
            return cursor.fetchone()
    finally:
        if own_conn:
            conn.close()
