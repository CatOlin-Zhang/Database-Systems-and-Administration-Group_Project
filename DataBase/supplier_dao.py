from DataBase.db_connector import get_connection


def get_all_suppliers(conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    v.vendor_id,
                    v.business_name,
                    v.geo_location,
                    COALESCE(ROUND(AVG(r.score), 2), v.avg_rating, 0) AS avg_rating
                FROM vendors v
                LEFT JOIN ratings r ON r.vendor_id = v.vendor_id
                GROUP BY v.vendor_id, v.business_name, v.geo_location, v.avg_rating
                ORDER BY v.vendor_id
                """
            )
            return cursor.fetchall()
    finally:
        if own_conn:
            conn.close()


def add_supplier(name, region, contact_info=None, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO vendors (business_name, avg_rating, geo_location)
                VALUES (%s, %s, %s)
                """,
                (name, 0, region),
            )
            supplier_id = cursor.lastrowid
        if own_conn:
            conn.commit()
        return get_supplier_by_id(supplier_id, conn=conn)
    except Exception:
        if own_conn:
            conn.rollback()
        raise
    finally:
        if own_conn:
            conn.close()


def get_supplier_by_id(supplier_id, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    v.vendor_id,
                    v.business_name,
                    v.geo_location,
                    COALESCE(ROUND(AVG(r.score), 2), v.avg_rating, 0) AS avg_rating
                FROM vendors v
                LEFT JOIN ratings r ON r.vendor_id = v.vendor_id
                WHERE v.vendor_id = %s
                GROUP BY v.vendor_id, v.business_name, v.geo_location, v.avg_rating
                """,
                (supplier_id,),
            )
            return cursor.fetchone()
    finally:
        if own_conn:
            conn.close()
