from DataBase.db_connector import get_connection
from database.sql_statements import EcommerceSQL

# 获取所有供应商列表
def get_all_suppliers(conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(EcommerceSQL.GET_ALL_VENDORS)
            return cursor.fetchall()
    finally:
        if own_conn:
            conn.close()

# 添加供应商
def add_supplier(business_name, geo_location, conn=None):
    business_name = (business_name or "").strip()
    geo_location = (geo_location or "").strip()
    if not business_name or not geo_location:
        raise ValueError("Business name and geo location cannot be empty")

    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(EcommerceSQL.ADD_VENDOR, (business_name, geo_location))
        if own_conn:
            conn.commit()
        return True
    except Exception as e:
        if own_conn:
            conn.rollback()
        raise RuntimeError(f"Failed to add supplier: {e}")
    finally:
        if own_conn:
            conn.close()

# 根据ID获取供应商
def get_supplier_by_id(supplier_id, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(EcommerceSQL.GET_VENDOR_BY_ID, (supplier_id,))
            return cursor.fetchone()
    finally:
        if own_conn:
            conn.close()

# 根据供应商名搜索供应商
def search_suppliers_by_name(keyword, conn=None):
    keyword = (keyword or "").strip()
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(EcommerceSQL.SEARCH_VENDORS, (f"%{keyword}%",))
            return cursor.fetchall()
    finally:
        if own_conn:
            conn.close()
           
