from DataBase.db_connector_Naibo import get_db_connection
from database.sql_statements import EcommerceSQL

def get_products_by_supplier(supplier_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(EcommerceSQL.GET_PRODUCTS_BY_VENDOR, (supplier_id,))
        return cursor.fetchall()
    finally:
        conn.close()

def search_products_by_tag(keyword):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(EcommerceSQL.SEARCH_PRODUCTS_BY_TAG, (f'%{keyword}%', f'%{keyword}%'))
        return cursor.fetchall()
    finally:
        conn.close()

def add_product(product_name, price, stock_quantity, supplier_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(EcommerceSQL.ADD_PRODUCT, (product_name, price, stock_quantity, supplier_id))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def get_product_details(product_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(EcommerceSQL.GET_PRODUCT_DETAILS, (product_id,))
        return cursor.fetchone()
    finally:
        conn.close()

def get_all_tags():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(EcommerceSQL.GET_ALL_TAGS)
        return cursor.fetchall()
    finally:
        conn.close()
