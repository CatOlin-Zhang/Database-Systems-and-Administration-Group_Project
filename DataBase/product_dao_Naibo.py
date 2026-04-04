from DataBase.db_connector import get_connection
from database.sql_statements import EcommerceSQL

# 根据供应商ID获取商品
def get_products_by_supplier(supplier_id, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(EcommerceSQL.GET_PRODUCTS_BY_VENDOR, (supplier_id,))
            return cursor.fetchall()
    finally:
        if own_conn:
            conn.close()

# 添加商品
def add_product(product_name, price, stock_quantity, vendor_id, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(EcommerceSQL.ADD_PRODUCT, (product_name, price, stock_quantity, vendor_id))
    finally:
        if own_conn:
            conn.close()

# 获取最后插入的商品ID
def get_last_product_id(conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(EcommerceSQL.GET_LAST_PRODUCT_ID)
            return cursor.fetchone()
    finally:
        if own_conn:
            conn.close()

# 为商品添加标签
def add_product_tag(product_id, tag_id, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(EcommerceSQL.ADD_PRODUCT_TAG, (product_id, tag_id))
    finally:
        if own_conn:
            conn.close()

# 获取所有标签
def get_all_tags(conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(EcommerceSQL.GET_ALL_TAGS)
            return cursor.fetchall()
    finally:
        if own_conn:
            conn.close()

# 搜索标签
def search_tags(keyword, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(EcommerceSQL.SEARCH_TAGS, (f"%{keyword}%",))
            return cursor.fetchall()
    finally:
        if own_conn:
            conn.close()

# 根据关键词搜索商品
def search_products_by_tag(keyword, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
            value = f"%{keyword}%"
            cursor.execute(EcommerceSQL.SEARCH_PRODUCTS_BY_TAG, (value, value))
            return cursor.fetchall()
    finally:
        if own_conn:
            conn.close()

# 根据标签ID搜索商品
def search_products_by_tag_id(tag_id, conn=None):
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cursor:
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
        with conn.cursor() as cursor:
            cursor.execute(EcommerceSQL.GET_PRODUCT_DETAILS, (product_id,))
            return cursor.fetchone()
    finally:
        if own_conn:
            conn.close()


