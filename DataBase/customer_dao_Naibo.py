from DataBase.db_connector_Naibo import get_db_connection

def add_customer(contact_num, shipping_address):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        sql = """
            INSERT INTO Customer (contact_num, shipping_address)
            VALUES (%s, %s)
        """
        cursor.execute(sql, (contact_num, shipping_address))
        conn.commit()
    finally:
        conn.close()

def get_customer_by_id(customer_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        sql = """
            SELECT customer_id, contact_num, shipping_address
            FROM Customer
            WHERE customer_id = %s
        """
        cursor.execute(sql, (customer_id,))
        return cursor.fetchone()
    finally:
        conn.close()
