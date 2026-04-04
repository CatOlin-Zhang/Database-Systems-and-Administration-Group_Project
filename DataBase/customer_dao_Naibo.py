from DataBase.db_connector import get_connection
from database.sql_statements import EcommerceSQL

# 添加客户
def add_customer(contact_num, shipping_address, conn=None):
    contact_num = contact_num.strip()
    shipping_address = shipping_address.strip()
    if not contact_num or not shipping_address:
        raise ValueError("Contact number and shipping address cannot be empty")

    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(EcommerceSQL.ADD_CUSTOMER, (contact_num, shipping_address))
        if own_conn:
            conn.commit()
        return True
    except Exception:
        if own_conn:
            conn.rollback()
        raise
    finally:
        if own_conn:
            conn.close()

# 根据ID查询顾客信息
def get_customer_by_id(customer_id, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(EcommerceSQL.GET_CUSTOMER_BY_ID, (customer_id,))
            return cursor.fetchone()
    finally:
        if own_conn:
            conn.close()

# 更新顾客地址
def update_customer_address(customer_id, shipping_address, conn=None):
    shipping_address = shipping_address.strip()
    if not shipping_address:
        raise ValueError("Shipping address cannot be empty")

    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(EcommerceSQL.UPDATE_CUSTOMER_ADDRESS, (shipping_address, customer_id))
        if own_conn:
            conn.commit()
        return True
    except Exception:
        if own_conn:
            conn.rollback()
        raise
    finally:
        if own_conn:
            conn.close()

# 验证顾客
def validate_customer(customer_id, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(EcommerceSQL.VALIDATE_CUSTOMER, (customer_id,))
            return cursor.fetchone()
    finally:
        if own_conn:
            conn.close()
