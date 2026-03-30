from DataBase.db_connector import get_connection


def get_customer_by_id(customer_id, conn=None):
    # 标记是否需要由当前函数负责关闭数据库连接
    own_conn = conn is None
    # 如果未传入连接对象，则获取一个新的连接
    conn = conn or get_connection()
    try:
        # 使用上下文管理器获取游标
        with conn.cursor() as cursor:
            # 执行SQL查询，根据客户ID查找对应的客户信息
            cursor.execute(
                """
                SELECT customer_id, contact_num, shipping_address
                FROM customers
                WHERE customer_id = %s
                """,
                (customer_id,),
            )
            # 返回查询到的单条记录
            return cursor.fetchone()
    finally:
        # 如果连接是由当前函数创建的，则在操作完成后关闭连接
        if own_conn:
            conn.close()


def get_first_customer(conn=None):
    # 标记是否需要由当前函数负责关闭数据库连接
    own_conn = conn is None
    # 如果未传入连接对象，则获取一个新的连接
    conn = conn or get_connection()
    try:
        # 使用上下文管理器获取游标
        with conn.cursor() as cursor:
            # 执行SQL查询，按ID排序并获取第一条客户记录
            cursor.execute(
                """
                SELECT customer_id, contact_num, shipping_address
                FROM customers
                ORDER BY customer_id
                LIMIT 1
                """
            )
            # 返回查询到的单条记录
            return cursor.fetchone()
    finally:
        # 如果连接是由当前函数创建的，则在操作完成后关闭连接
        if own_conn:
            conn.close()