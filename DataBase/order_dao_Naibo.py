from DataBase.db_connector_Naibo import get_db_connection
from database.sql_statements import EcommerceSQL

def create_order(customer_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(EcommerceSQL.CREATE_ORDER, (customer_id,))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def add_order_item(order_id, product_id, buy_quantity):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(EcommerceSQL.ADD_ORDER_ITEM, (order_id, product_id, buy_quantity, product_id))
        conn.commit()
    finally:
        conn.close()

def get_customer_orders(customer_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(EcommerceSQL.GET_CUSTOMER_ORDERS, (customer_id,))
        return cursor.fetchall()
    finally:
        conn.close()

def cancel_order(order_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(EcommerceSQL.CANCEL_ORDER, (order_id,))
        conn.commit()
    finally:
        conn.close()

def get_order_details(order_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(EcommerceSQL.GET_ORDER_DETAILS, (order_id,))
        return cursor.fetchone()
    finally:
        conn.close()
