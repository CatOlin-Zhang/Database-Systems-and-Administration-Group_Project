from DataBase.db_connector import get_connection


def get_customer_by_id(customer_id, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT customer_id, contact_num, shipping_address
                FROM customers
                WHERE customer_id = %s
                """,
                (customer_id,),
            )
            return cursor.fetchone()
    finally:
        if own_conn:
            conn.close()


def get_first_customer(conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT customer_id, contact_num, shipping_address
                FROM customers
                ORDER BY customer_id
                LIMIT 1
                """
            )
            return cursor.fetchone()
    finally:
        if own_conn:
            conn.close()
