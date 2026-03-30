from DataBase.db_connector import get_connection


def create_order(customer_id, total_price, status, conn=None):
    # 标记是否由当前函数负责管理连接生命周期
    own_conn = conn is None
    # 使用传入的连接或创建新连接
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            # 执行SQL插入新订单记录，使用NOW()获取当前时间
            cursor.execute(
                """
                INSERT INTO orders (customer_id, order_date, total_price, order_status)
                VALUES (%s, NOW(), %s, %s)
                """,
                (customer_id, total_price, status),
            )
            # 获取自增生成的订单ID
            order_id = cursor.lastrowid
            # 仅在当前函数创建连接时提交事务
            if own_conn:
                conn.commit()
            return order_id
    except Exception:
        # 发生异常时回滚事务
        if own_conn:
            conn.rollback()
        raise
    finally:
        # 仅在当前函数创建连接时关闭连接
        if own_conn:
            conn.close()


def add_order_item(order_id, product_id, quantity, price_at_purchase, conn=None):
    # 标记连接所有权
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            # 插入订单明细项（商品ID、购买数量、单价）
            cursor.execute(
                """
                INSERT INTO order_items (order_id, product_id, buy_quantity, unit_price)
                VALUES (%s, %s, %s, %s)
                """,
                (order_id, product_id, quantity, price_at_purchase),
            )
            item_id = cursor.lastrowid
            if own_conn:
                conn.commit()
            return item_id
    except Exception:
        if own_conn:
            conn.rollback()
        raise
    finally:
        if own_conn:
            conn.close()


def get_order_by_id(order_id, conn=None, for_update=False):
    # 标记连接所有权
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            # 构建基础查询SQL
            sql = """
                SELECT order_id, customer_id, order_date, total_price, order_status
                FROM orders
                WHERE order_id = %s
            """
            # 如果需要行级锁（用于并发控制），添加FOR UPDATE子句
            if for_update:
                sql += " FOR UPDATE"
            cursor.execute(sql, (order_id,))
            return cursor.fetchone()
    finally:
        if own_conn:
            conn.close()


def get_orders_by_customer(customer_id, conn=None):
    # 标记连接所有权
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            # 查询指定客户的所有订单，按日期倒序排列
            cursor.execute(
                """
                SELECT order_id, customer_id, order_date, total_price, order_status
                FROM orders
                WHERE customer_id = %s
                ORDER BY order_date DESC, order_id DESC
                """,
                (customer_id,),
            )
            return cursor.fetchall()
    finally:
        if own_conn:
            conn.close()


def get_order_details(order_id, conn=None):
    # 标记连接所有权
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            # 联合查询订单项与产品信息，计算小计
            cursor.execute(
                """
                SELECT 
                    oi.item_id, 
                    oi.order_id, 
                    oi.product_id, 
                    p.product_name AS name,
                    oi.buy_quantity AS quantity, 
                    oi.unit_price AS price_at_purchase,
                    oi.buy_quantity * oi.unit_price AS subtotal
                FROM order_items oi
                JOIN products p ON p.product_id = oi.product_id
                WHERE oi.order_id = %s
                ORDER BY oi.item_id
                """,
                (order_id,),
            )
            return cursor.fetchall()
    finally:
        if own_conn:
            conn.close()


def get_order_item_by_id(order_id, item_id, conn=None, for_update=False):
    # 标记连接所有权
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            # 查询特定的订单明细项
            sql = """
                SELECT item_id, order_id, product_id, buy_quantity, unit_price
                FROM order_items
                WHERE order_id = %s AND item_id = %s
            """
            if for_update:
                sql += " FOR UPDATE"
            cursor.execute(sql, (order_id, item_id))
            return cursor.fetchone()
    finally:
        if own_conn:
            conn.close()


def cancel_order(order_id, conn=None):
    # 标记连接所有权
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            # 将订单状态更新为已取消
            cursor.execute(
                """
                UPDATE orders
                SET order_status = 'CANCELLED'
                WHERE order_id = %s
                """,
                (order_id,),
            )
            if own_conn:
                conn.commit()
    except Exception:
        if own_conn:
            conn.rollback()
        raise
    finally:
        if own_conn:
            conn.close()


def remove_item_from_order(order_id, product_id, conn=None):
    # 标记连接所有权
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            # 从订单中删除指定商品（限制仅删除一条记录）
            cursor.execute(
                """
                DELETE FROM order_items
                WHERE order_id = %s AND product_id = %s
                LIMIT 1
                """,
                (order_id, product_id),
            )
            if own_conn:
                conn.commit()
    except Exception:
        if own_conn:
            conn.rollback()
        raise
    finally:
        if own_conn:
            conn.close()


def remove_order_item_by_id(order_id, item_id, conn=None):
    # 标记连接所有权
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            # 根据订单ID和明细项ID删除特定记录
            cursor.execute(
                """
                DELETE FROM order_items
                WHERE order_id = %s AND item_id = %s
                """,
                (order_id, item_id),
            )
            if own_conn:
                conn.commit()
    except Exception:
        if own_conn:
            conn.rollback()
        raise
    finally:
        if own_conn:
            conn.close()


def update_order_total(order_id, conn=None):
    # 标记连接所有权
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            # 使用子查询重新计算订单总金额并更新
            cursor.execute(
                """
                UPDATE orders o
                LEFT JOIN (
                    SELECT order_id, COALESCE(SUM(buy_quantity * unit_price), 0) AS total_amount
                    FROM order_items
                    WHERE order_id = %s
                    GROUP BY order_id
                ) x ON x.order_id = o.order_id
                SET o.total_price = COALESCE(x.total_amount, 0)
                WHERE o.order_id = %s
                """,
                (order_id, order_id),
            )
            if own_conn:
                conn.commit()
    except Exception:
        if own_conn:
            conn.rollback()
        raise
    finally:
        if own_conn:
            conn.close()


def update_order_status(order_id, status, conn=None):
    # 标记连接所有权
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            # 更新订单状态
            cursor.execute(
                """
                UPDATE orders
                SET order_status = %s
                WHERE order_id = %s
                """,
                (status, order_id),
            )
            if own_conn:
                conn.commit()
    except Exception:
        if own_conn:
            conn.rollback()
        raise
    finally:
        if own_conn:
            conn.close()


def delete_transactions_by_order(order_id, conn=None):
    # 标记连接所有权
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            # 删除指定订单的所有交易记录
            cursor.execute(
                """
                DELETE FROM transactions
                WHERE order_id = %s
                """,
                (order_id,),
            )
            if own_conn:
                conn.commit()
    except Exception:
        if own_conn:
            conn.rollback()
        raise
    finally:
        if own_conn:
            conn.close()


def create_transaction(order_id, vendor_id, pay_amount, conn=None):
    # 标记连接所有权
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            # 创建新的交易记录
            cursor.execute(
                """
                INSERT INTO transactions (order_id, vendor_id, pay_amount, transaction_time)
                VALUES (%s, %s, %s, NOW())
                """,
                (order_id, vendor_id, pay_amount),
            )
            transaction_id = cursor.lastrowid
            if own_conn:
                conn.commit()
            return transaction_id
    except Exception:
        if own_conn:
            conn.rollback()
        raise
    finally:
        if own_conn:
            conn.close()


def rebuild_transactions_for_order(order_id, conn=None):
    # 标记连接所有权
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            # 1. 删除旧的交易记录
            cursor.execute(
                """
                DELETE FROM transactions
                WHERE order_id = %s
                """,
                (order_id,),
            )
            # 2. 查询该订单下所有商品，按供应商分组计算应付金额
            cursor.execute(
                """
                SELECT p.vendor_id, SUM(oi.buy_quantity * oi.unit_price) AS pay_amount
                FROM order_items oi
                JOIN products p ON p.product_id = oi.product_id
                WHERE oi.order_id = %s
                GROUP BY p.vendor_id
                ORDER BY p.vendor_id
                """,
                (order_id,),
            )
            rows = cursor.fetchall()
            # 3. 为每个供应商插入新的交易记录
            for row in rows:
                cursor.execute(
                    """
                    INSERT INTO transactions (order_id, vendor_id, pay_amount, transaction_time)
                    VALUES (%s, %s, %s, NOW())
                    """,
                    (order_id, row["vendor_id"], row["pay_amount"]),
                )
            if own_conn:
                conn.commit()
    except Exception:
        if own_conn:
            conn.rollback()
        raise
    finally:
        if own_conn:
            conn.close()