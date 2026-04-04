from DataBase.db_connector import get_connection
from database.sql_statements import EcommerceSQL

# 获取供应商的销售统计量
def get_vendor_sales_stats(conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(EcommerceSQL.GET_VENDOR_SALES_STATS)
            return cursor.fetchall()
    finally:
        if own_conn:
            conn.close()

# 获取客户的消费统计量
def get_customer_stats(conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(EcommerceSQL.GET_CUSTOMER_STATS)
            return cursor.fetchall()
    finally:
        if own_conn:
            conn.close()

# 根据销量获取热门商品
def get_popular_products(limit_count, conn=None):
    try:
        limit_count = int(limit_count)
        if limit_count <= 0:
            raise ValueError
    except (TypeError, ValueError):
        raise ValueError("Limit count must be a positive integer")

    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(EcommerceSQL.GET_POPULAR_PRODUCTS, (limit_count,))
            return cursor.fetchall()
    finally:
        if own_conn:
            conn.close()

# 管理员后台的订单概览页面
def get_all_orders_overview(limit_count, offset, conn=None):
    try:
        limit_count = int(limit_count)
        offset = int(offset)
        if limit_count <= 0 or offset < 0:
            raise ValueError
    except (TypeError, ValueError):
        raise ValueError("Invalid pagination parameters")

    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(EcommerceSQL.GET_ALL_ORDERS_OVERVIEW, (limit_count, offset))
            return cursor.fetchall()
    finally:
        if own_conn:
            conn.close()


