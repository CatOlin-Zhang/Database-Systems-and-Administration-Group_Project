from DataBase.db_connector import get_connection
from database.sql_statements import EcommerceSQL

#获取供应商的销售统计量
def get_vendor_sales_stats(conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(EcommerceSQL.GET_VENDOR_SALES_STATS)
            return cursor.fetchall()
    finally:
        if own_conn:
            conn.close()

#获取客户的消费统计量
def get_customer_stats(conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(EcommerceSQL.GET_CUSTOMER_STATS)
            return cursor.fetchall()
    finally:
        if own_conn:
            conn.close()

#根据销量获取热门商品
def get_popular_products(limit_count, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(EcommerceSQL.GET_POPULAR_PRODUCTS, (limit_count,))
            return cursor.fetchall()
    finally:
        if own_conn:
            conn.close()

# 管理员后台的订单概览页面
def get_all_orders_overview(limit_count, offset, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(EcommerceSQL.GET_ALL_ORDERS_OVERVIEW, (limit_count, offset))
            return cursor.fetchall()
    finally:
        if own_conn:
            conn.close()
