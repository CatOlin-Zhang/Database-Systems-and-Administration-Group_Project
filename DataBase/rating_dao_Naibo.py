from DataBase.db_connector import get_connection
from database.sql_statements import EcommerceSQL

# 添加或更新评分
def add_or_update_rating(customer_id, vendor_id, score, conn=None):
    try:
        score = float(score)
        if not (1 <= score <= 5):
            raise ValueError
    except (TypeError, ValueError):
        raise ValueError("Score must be a number between 1 and 5")

    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(EcommerceSQL.ADD_RATING, (customer_id, vendor_id, score, score))
        if own_conn:
            conn.commit()
        return True
    except Exception as e:
        if own_conn:
            conn.rollback()
        raise RuntimeError(f"Failed to add or update rating: {e}")
    finally:
        if own_conn:
            conn.close()

# 获取某个供应商的所有评分
def get_vendor_ratings(vendor_id, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(EcommerceSQL.GET_VENDOR_RATINGS, (vendor_id,))
            return cursor.fetchall()
    finally:
        if own_conn:
            conn.close()

# 获取客户对某个供应商的评分
def get_customer_vendor_rating(customer_id, vendor_id, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(EcommerceSQL.GET_CUSTOMER_VENDOR_RATING, (customer_id, vendor_id))
            return cursor.fetchone()
    finally:
        if own_conn:
            conn.close()
