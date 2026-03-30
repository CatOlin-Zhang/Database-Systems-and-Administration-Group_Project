from DataBase.db_connector import get_connection


def get_products_by_supplier(supplier_id=None, conn=None):
    # 标记是否由当前函数负责管理连接生命周期
    own_conn = conn is None
    # 使用传入的连接或创建新连接
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            # 初始化基础查询SQL，联查产品、供应商及标签信息
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
            # 如果指定了供应商ID，则添加过滤条件
            if supplier_id is not None:
                sql += " WHERE p.vendor_id = %s"
                params.append(supplier_id)
            # 添加分组和排序语句
            sql += """
                GROUP BY
                    p.product_id, p.product_name, p.price,
                    p.stock_quantity, p.vendor_id, v.business_name
                ORDER BY p.product_id
            """
            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        # 仅在当前函数创建连接时关闭连接
        if own_conn:
            conn.close()


def get_product_by_id(product_id, conn=None, for_update=False):
    # 标记连接所有权
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            # 查询指定ID的商品详情，包含关联的供应商名称和标签
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
            # 如果需要行级锁（用于并发更新），添加 FOR UPDATE 子句
            if for_update:
                sql += " FOR UPDATE"
            cursor.execute(sql, (product_id,))
            return cursor.fetchone()
    finally:
        if own_conn:
            conn.close()


def add_product(name, price, stock, tags_list, supplier_id, conn=None):
    # 校验业务规则：每个商品最多绑定3个标签
    if len(tags_list) > 3:
        raise ValueError("每个商品最多绑定 3 个标签")

    # 标记连接所有权
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            # 插入新产品记录
            cursor.execute(
                """
                INSERT INTO products (product_name, price, stock_quantity, vendor_id)
                VALUES (%s, %s, %s, %s)
                """,
                (name, price, stock, supplier_id),
            )
            # 获取自增生成的商品ID
            product_id = cursor.lastrowid
            # 调用内部函数绑定标签
            _bind_tags(cursor, product_id, tags_list)
        # 仅在当前函数创建连接时提交事务
        if own_conn:
            conn.commit()
        # 返回新创建的商品完整信息
        return get_product_by_id(product_id, conn=conn)
    except Exception:
        # 发生异常时回滚事务
        if own_conn:
            conn.rollback()
        raise
    finally:
        if own_conn:
            conn.close()


def search_products(keyword, tag_filter, conn=None):
    # 标记连接所有权
    own_conn = conn is None
    conn = conn or get_connection()
    # 清理搜索关键词和标签过滤器
    keyword = (keyword or "").strip()
    tag_filter = [tag.strip() for tag in (tag_filter or []) if tag.strip()]
    try:
        with conn.cursor() as cursor:
            # 初始化基础查询SQL
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
                JOIN vendors v ON v.vendor_id = p.product_id
                LEFT JOIN product_tags pt ON pt.product_id = p.product_id
                LEFT JOIN tags t ON t.tag_id = pt.tag_id
                WHERE 1 = 1
            """
            params = []
            # 如果有关键词，添加模糊匹配条件（匹配商品名或标签名）
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
            # 如果有标签过滤器，添加标签匹配条件
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

            # 添加分组和排序
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
    # 标记连接所有权
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            # 更新库存数量，并确保库存不为负数
            cursor.execute(
                """
                UPDATE products
                SET stock_quantity = stock_quantity + %s
                WHERE product_id = %s
                  AND stock_quantity + %s >= 0
                """,
                (quantity_change, product_id, quantity_change),
            )
            # 如果影响行数为0，说明商品不存在或库存不足
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
    # 内部函数：处理商品与标签的绑定逻辑
    for tag_name in tags_list:
        normalized = tag_name.strip()
        if not normalized:
            continue
        # 查询标签是否存在
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
            # 如果标签存在，使用现有ID
            tag_id = row["tag_id"]
        else:
            # 如果标签不存在，插入新标签并获取ID
            cursor.execute(
                """
                INSERT INTO tags (tag_name)
                VALUES (%s)
                """,
                (normalized,),
            )
            tag_id = cursor.lastrowid
        # 建立商品与标签的关联记录
        cursor.execute(
            """
            INSERT INTO product_tags (product_id, tag_id)
            VALUES (%s, %s)
            """,
            (product_id, tag_id),
        )