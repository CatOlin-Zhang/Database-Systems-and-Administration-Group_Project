from DataBase.db_connector_Naibo import get_db_connection
from database.sql_statements import EcommerceSQL

#添加客户
def add_customer(contact_num, shipping_address):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(EcommerceSQL.ADD_CUSTOMER, (contact_num, shipping_address))
        conn.commit()
    finally:
        conn.close()
# 根据ID查询顾客信息
def get_customer_by_id(customer_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(EcommerceSQL.GET_CUSTOMER_BY_ID, (customer_id,))
        return cursor.fetchone()
    finally:
        conn.close()
# 更新顾客地址
def update_customer_address(customer_id, shipping_address):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(EcommerceSQL.UPDATE_CUSTOMER_ADDRESS, (shipping_address, customer_id))
        conn.commit()
    finally:
        conn.close()

# 验证顾客
def validate_customer(customer_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(EcommerceSQL.VALIDATE_CUSTOMER, (customer_id,))
        return cursor.fetchone()
    finally:
        conn.close()
