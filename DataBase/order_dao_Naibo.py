from DataBase.db_connector import get_connection
from database.sql_statements import EcommerceSQL

# 检查商品库存
def check_product_stock(product_id, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(EcommerceSQL.CHECK_PRODUCT_STOCK, (product_id,))
            return cursor.fetchone()
    finally:
        if own_conn:
            conn.close()

# 创建新订单
def create_order(customer_id, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(EcommerceSQL.CREATE_ORDER, (customer_id,))
            last_id = cursor.lastrowid
        if own_conn:
            conn.commit()
        return last_id
    except Exception:
        if own_conn:
            conn.rollback()
        raise
    finally:
        if own_conn:
            conn.close()

# 获取最后创建的订单ID
def get_last_order_id(conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(EcommerceSQL.GET_LAST_ORDER_ID)
            return cursor.fetchone()
    finally:
        if own_conn:
            conn.close()

# 为订单添加商品
def add_order_item(order_id, product_id, buy_quantity, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(EcommerceSQL.ADD_ORDER_ITEM, (order_id, product_id, buy_quantity, product_id))
        if own_conn:
            conn.commit()
    except Exception:
        if own_conn:
            conn.rollback()
        raise
    finally:
        if own_conn:
            conn.close()

# 更新订单总价格
def update_order_total(order_id, total_price, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(EcommerceSQL.UPDATE_ORDER_TOTAL, (total_price, order_id))
        if own_conn:
            conn.commit()
    except Exception:
        if own_conn:
            conn.rollback()
        raise
    finally:
        if own_conn:
            conn.close()

# 扣减商品库存
def update_product_stock(product_id, quantity, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(EcommerceSQL.UPDATE_PRODUCT_STOCK, (quantity, product_id, quantity))
        if own_conn:
            conn.commit()
    except Exception:
        if own_conn:
            conn.rollback()
        raise
    finally:
        if own_conn:
            conn.close()

# 创建交易记录
def create_transaction(order_id, vendor_id, pay_amount, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(EcommerceSQL.CREATE_TRANSACTION, (order_id, vendor_id, pay_amount))
        if own_conn:
            conn.commit()
    except Exception:
        if own_conn:
            conn.rollback()
        raise
    finally:
        if own_conn:
            conn.close()

# 根据订单ID统计各供应商金额
def get_vendor_totals_by_order(order_id, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(EcommerceSQL.GET_VENDOR_TOTALS_BY_ORDER, (order_id,))
            return cursor.fetchall()
    finally:
        if own_conn:
            conn.close()

# 获取订单中所有的商品
def get_order_products(order_id, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(EcommerceSQL.GET_ORDER_PRODUCTS, (order_id,))
            return cursor.fetchall()
    finally:
        if own_conn:
            conn.close()

# 获取指定顾客的所有订单
def get_customer_orders(customer_id, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(EcommerceSQL.GET_CUSTOMER_ORDERS, (customer_id,))
            return cursor.fetchall()
    finally:
        if own_conn:
            conn.close()

# 获取订单完整详情
def get_order_details(order_id, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(EcommerceSQL.GET_ORDER_DETAILS, (order_id,))
            return cursor.fetchone()
    finally:
        if own_conn:
            conn.close()

# 获取订单状态
def get_order_status(order_id, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(EcommerceSQL.GET_ORDER_STATUS, (order_id,))
            return cursor.fetchone()
    finally:
        if own_conn:
            conn.close()

# 删除订单中的指定商品
def delete_order_item(item_id, order_id, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(EcommerceSQL.DELETE_ORDER_ITEM, (item_id, order_id))
        if own_conn:
            conn.commit()
    except Exception:
        if own_conn:
            conn.rollback()
        raise
    finally:
        if own_conn:
            conn.close()

# 取消订单
def cancel_order(order_id, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(EcommerceSQL.CANCEL_ORDER, (order_id,))
        if own_conn:
            conn.commit()
    except Exception:
        if own_conn:
            conn.rollback()
        raise
    finally:
        if own_conn:
            conn.close()

# 取消订单后恢复商品的库存
def restore_order_stock(order_id, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(EcommerceSQL.RESTORE_ORDER_STOCK, (order_id,))
        if own_conn:
            conn.commit()
    except Exception:
        if own_conn:
            conn.rollback()
        raise
    finally:
        if own_conn:
            conn.close()

# 删除订单关联的交易记录
def delete_order_transactions(order_id, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(EcommerceSQL.DELETE_ORDER_TRANSACTIONS, (order_id,))
        if own_conn:
            conn.commit()
    except Exception:
        if own_conn:
            conn.rollback()
        raise
    finally:
        if own_conn:
            conn.close()

# 将订单状态更新为待发货
def update_order_status_to_shipping(order_id, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(EcommerceSQL.UPDATE_ORDER_STATUS_TO_SHIPPING, (order_id,))
        if own_conn:
            conn.commit()
    except Exception:
        if own_conn:
            conn.rollback()
        raise
    finally:
        if own_conn:
            conn.close()

# 将订单状态更新为已发货
def update_order_status_to_shipped(order_id, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(EcommerceSQL.UPDATE_ORDER_STATUS_TO_SHIPPED, (order_id,))
        if own_conn:
            conn.commit()
    except Exception:
        if own_conn:
            conn.rollback()
        raise
    finally:
        if own_conn:
            conn.close()

# 将订单状态更新为已完成
def update_order_status_to_completed(order_id, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(EcommerceSQL.UPDATE_ORDER_STATUS_TO_COMPLETED, (order_id,))
        if own_conn:
            conn.commit()
    except Exception:
        if own_conn:
            conn.rollback()
        raise
    finally:
        if own_conn:
            conn.close()

# 获取订单的交易记录
def get_order_transactions(order_id, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(EcommerceSQL.GET_ORDER_TRANSACTIONS, (order_id,))
            return cursor.fetchall()
    finally:
        if own_conn:
            conn.close()
