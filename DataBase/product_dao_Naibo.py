from DataBase.db_connector import get_connection
from database.sql_statements import EcommerceSQL

# 根据供应商ID获取商品
def get_products_by_supplier(supplier_id, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(EcommerceSQL.GET_PRODUCTS_BY_VENDOR, (supplier_id,))
            return cursor.fetchall()
    finally:
        if own_conn:
            conn.close()

# 添加商品
def add_product(product_name, price, stock_quantity, vendor_id, conn=None):
    product_name = (product_name or "").strip()
    if not product_name:
        raise ValueError("Product name cannot be empty")
    try:
        price = float(price)
        stock_quantity = int(stock_quantity)
        if price < 0 or stock_quantity < 0:
            raise ValueError("Price and stock quantity must be non-negative")
    except (TypeError, ValueError):
        raise ValueError("Invalid price or stock quantity")

    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(EcommerceSQL.ADD_PRODUCT, (product_name, price, stock_quantity, vendor_id))
        if own_conn:
            conn.commit()
        return True
    except Exception as e:
        if own_conn:
            conn.rollback()
        raise RuntimeError(f"Failed to add product: {e}")
    finally:
        if own_conn:
            conn.close()

# 获取最后插入的商品ID
def get_last_product_id(conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(EcommerceSQL.GET_LAST_PRODUCT_ID)
            return cursor.fetchone()['LAST_INSERT_ID()']
    finally:
        if own_conn:
            conn.close()

# 为商品添加标签（简单去重）
def add_product_tag(product_id, tag_id, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            
            cursor.execute("SELECT 1 FROM ProductTag WHERE product_id = %s AND tag_id = %s", (product_id, tag_id))
            if cursor.fetchone():
                return False
            cursor.execute(EcommerceSQL.ADD_PRODUCT_TAG, (product_id, tag_id))
        if own_conn:
            conn.commit()
        return True
    except Exception as e:
        if own_conn:
            conn.rollback()
        raise RuntimeError(f"Failed to add product tag: {e}")
    finally:
        if own_conn:
            conn.close()

# 获取所有标签
def get_all_tags(conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(EcommerceSQL.GET_ALL_TAGS)
            return cursor.fetchall()
    finally:
        if own_conn:
            conn.close()

# 搜索标签
def search_tags(keyword, conn=None):
    keyword = (keyword or "").strip()
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(EcommerceSQL.SEARCH_TAGS, (f"%{keyword}%",))
            return cursor.fetchall()
    finally:
        if own_conn:
            conn.close()

# 根据关键词搜索商品
def search_products_by_tag(keyword, conn=None):
    keyword = (keyword or "").strip()
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(EcommerceSQL.SEARCH_PRODUCTS_BY_TAG, (f"%{keyword}%", f"%{keyword}%"))
            return cursor.fetchall()
    finally:
        if own_conn:
            conn.close()

# 根据标签ID搜索商品
def search_products_by_tag_id(tag_id, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(EcommerceSQL.SEARCH_PRODUCTS_BY_TAG_ID, (tag_id,))
            return cursor.fetchall()
    finally:
        if own_conn:
            conn.close()

# 获取商品详情
def get_product_detail(product_id, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(EcommerceSQL.GET_PRODUCT_DETAILS, (product_id,))
            return cursor.fetchone()
    finally:
        if own_conn:
            conn.close()

# 检查商品库存（返回字典，包含 product_id, product_name, price, stock_quantity, vendor_id）
def check_product_stock(product_id, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            
            cursor.execute("""
                SELECT p.product_id, p.product_name, p.price, p.stock_quantity, p.vendor_id
                FROM Product p
                WHERE p.product_id = %s
            """, (product_id,))
            return cursor.fetchone()
    finally:
        if own_conn:
            conn.close()


