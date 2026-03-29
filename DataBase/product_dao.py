from DataBase.db_connector import get_connection


def get_products_by_supplier(supplier_id=None, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT
                    p.product_id,
                    p.product_name,
                    p.price,
                    p.stock_quantity,
                    p.vendor_id,
                    v.business_name AS supplier_name,
                    COALESCE(GROUP_CONCAT(DISTINCT t.tag_name ORDER BY t.tag_name SEPARATOR ', '), '') AS tags_text
                FROM products p
                JOIN vendors v ON v.vendor_id = p.vendor_id
                LEFT JOIN product_tags pt ON pt.product_id = p.product_id
                LEFT JOIN tags t ON t.tag_id = pt.tag_id
            """
            params = []
            if supplier_id is not None:
                sql += " WHERE p.vendor_id = %s"
                params.append(supplier_id)
            sql += """
                GROUP BY
                    p.product_id, p.product_name, p.price,
                    p.stock_quantity, p.vendor_id, v.business_name
                ORDER BY p.product_id
            """
            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        if own_conn:
            conn.close()


def get_product_by_id(product_id, conn=None, for_update=False):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT
                    p.product_id,
                    p.product_name,
                    p.price,
                    p.stock_quantity,
                    p.vendor_id,
                    v.business_name AS supplier_name,
                    COALESCE(GROUP_CONCAT(DISTINCT t.tag_name ORDER BY t.tag_name SEPARATOR ', '), '') AS tags_text
                FROM products p
                JOIN vendors v ON v.vendor_id = p.vendor_id
                LEFT JOIN product_tags pt ON pt.product_id = p.product_id
                LEFT JOIN tags t ON t.tag_id = pt.tag_id
                WHERE p.product_id = %s
                GROUP BY
                    p.product_id, p.product_name, p.price,
                    p.stock_quantity, p.vendor_id, v.business_name
            """
            if for_update:
                sql += " FOR UPDATE"
            cursor.execute(sql, (product_id,))
            return cursor.fetchone()
    finally:
        if own_conn:
            conn.close()


def add_product(name, price, stock, tags_list, supplier_id, conn=None):
    if len(tags_list) > 3:
        raise ValueError("每个商品最多绑定 3 个标签")

    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO products (product_name, price, stock_quantity, vendor_id)
                VALUES (%s, %s, %s, %s)
                """,
                (name, price, stock, supplier_id),
            )
            product_id = cursor.lastrowid
            _bind_tags(cursor, product_id, tags_list)
        if own_conn:
            conn.commit()
        return get_product_by_id(product_id, conn=conn)
    except Exception:
        if own_conn:
            conn.rollback()
        raise
    finally:
        if own_conn:
            conn.close()


def search_products(keyword, tag_filter, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    keyword = (keyword or "").strip()
    tag_filter = [tag.strip() for tag in (tag_filter or []) if tag.strip()]
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT
                    p.product_id,
                    p.product_name,
                    p.price,
                    p.stock_quantity,
                    p.vendor_id,
                    v.business_name AS supplier_name,
                    COALESCE(GROUP_CONCAT(DISTINCT t.tag_name ORDER BY t.tag_name SEPARATOR ', '), '') AS tags_text
                FROM products p
                JOIN vendors v ON v.vendor_id = p.vendor_id
                LEFT JOIN product_tags pt ON pt.product_id = p.product_id
                LEFT JOIN tags t ON t.tag_id = pt.tag_id
                WHERE 1 = 1
            """
            params = []
            if keyword:
                sql += """
                    AND (
                        p.product_name LIKE %s
                        OR EXISTS (
                            SELECT 1
                            FROM product_tags pt2
                            JOIN tags t2 ON t2.tag_id = pt2.tag_id
                            WHERE pt2.product_id = p.product_id
                              AND t2.tag_name LIKE %s
                        )
                    )
                """
                like_keyword = f"%{keyword}%"
                params.extend([like_keyword, like_keyword])
            if tag_filter:
                placeholders = ", ".join(["%s"] * len(tag_filter))
                sql += f"""
                    AND EXISTS (
                        SELECT 1
                        FROM product_tags pt3
                        JOIN tags t3 ON t3.tag_id = pt3.tag_id
                        WHERE pt3.product_id = p.product_id
                          AND t3.tag_name IN ({placeholders})
                    )
                """
                params.extend(tag_filter)

            sql += """
                GROUP BY
                    p.product_id, p.product_name, p.price,
                    p.stock_quantity, p.vendor_id, v.business_name
                ORDER BY p.product_name, p.product_id
            """
            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        if own_conn:
            conn.close()


def update_stock(product_id, quantity_change, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE products
                SET stock_quantity = stock_quantity + %s
                WHERE product_id = %s
                  AND stock_quantity + %s >= 0
                """,
                (quantity_change, product_id, quantity_change),
            )
            if cursor.rowcount == 0:
                raise ValueError("库存不足或商品不存在")
        if own_conn:
            conn.commit()
    except Exception:
        if own_conn:
            conn.rollback()
        raise
    finally:
        if own_conn:
            conn.close()


def _bind_tags(cursor, product_id, tags_list):
    for tag_name in tags_list:
        normalized = tag_name.strip()
        if not normalized:
            continue
        cursor.execute(
            """
            SELECT tag_id
            FROM tags
            WHERE tag_name = %s
            """,
            (normalized,),
        )
        row = cursor.fetchone()
        if row:
            tag_id = row["tag_id"]
        else:
            cursor.execute(
                """
                INSERT INTO tags (tag_name)
                VALUES (%s)
                """,
                (normalized,),
            )
            tag_id = cursor.lastrowid
        cursor.execute(
            """
            INSERT INTO product_tags (product_id, tag_id)
            VALUES (%s, %s)
            """,
            (product_id, tag_id),
        )
