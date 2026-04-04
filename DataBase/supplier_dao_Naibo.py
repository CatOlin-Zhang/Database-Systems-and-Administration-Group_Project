from DataBase.db_connector_Naibo import get_db_connection
from database.sql_statements import EcommerceSQL

def get_all_suppliers():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(EcommerceSQL.GET_ALL_VENDORS)
        return cursor.fetchall()
    finally:
        conn.close()

def add_supplier(business_name, geo_location):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(EcommerceSQL.ADD_VENDOR, (business_name, geo_location))
        conn.commit()
    finally:
        conn.close()

def get_supplier_by_id(supplier_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(EcommerceSQL.GET_VENDOR_BY_ID, (supplier_id,))
        return cursor.fetchone()
    finally:
        conn.close()

def search_suppliers_by_name(keyword):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(EcommerceSQL.SEARCH_VENDORS, (f'%{keyword}%',))
        return cursor.fetchall()
    finally:
        conn.close()
