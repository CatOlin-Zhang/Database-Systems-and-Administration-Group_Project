from DataBase.db_connector import get_connection

def get_all_suppliers(conn=None):
    # 标记当前函数是否拥有数据库连接的所有权（即是否由当前函数负责关闭连接）
    own_conn = conn is None
    # 如果未传入连接对象，则获取一个新的数据库连接
    conn = conn or get_connection()
    try:
        # 使用上下文管理器获取游标，确保游标在使用后自动关闭
        with conn.cursor() as cursor:
            # 执行SQL查询：获取所有供应商的信息
            # 查询包含供应商ID、名称、地理位置，并计算平均评分
            # 平均评分优先使用评分表的平均值，若无评分则回退到供应商表的默认值，默认为0
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
            # 返回查询到的所有供应商记录
            return cursor.fetchall()
    finally:
        # 如果连接是由当前函数创建的，则在操作完成后关闭连接
        if own_conn:
            conn.close()


def add_supplier(name, region, contact_info=None, conn=None):
    # 标记连接所有权
    own_conn = conn is None
    # 使用传入的连接或创建新连接
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            # 执行SQL插入新供应商记录
            # 初始平均评分设为0，传入名称和地理位置
            cursor.execute(
                """
                INSERT INTO vendors (business_name, avg_rating, geo_location)
                VALUES (%s, %s, %s)
                """,
                (name, 0, region),
            )
            # 获取自增生成的供应商ID
            supplier_id = cursor.lastrowid
        # 如果连接由当前函数管理，则提交事务
        if own_conn:
            conn.commit()
        # 返回新创建的供应商的完整信息
        return get_supplier_by_id(supplier_id, conn=conn)
    except Exception:
        # 发生异常时回滚事务
        if own_conn:
            conn.rollback()
        # 重新抛出异常
        raise
    finally:
        # 清理资源：仅关闭当前函数创建的连接
        if own_conn:
            conn.close()


def get_supplier_by_id(supplier_id, conn=None):
    # 标记连接所有权
    own_conn = conn is None
    # 使用传入的连接或创建新连接
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            # 根据供应商ID查询单个供应商的详细信息
            # 同样包含平均评分的计算逻辑
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
            # 返回查询到的单条记录
            return cursor.fetchone()
    finally:
        # 清理资源：仅关闭当前函数创建的连接
        if own_conn:
            conn.close()