# File Description:
#   This file defines all the SQL statements required for the entire e-commerce platform.
#   All SQL statements use parameterized queries (using %s placeholders) to prevent SQL injection attacks. 
#
# Usage:
#   1. Import this module in other Python files: 
#      from database.sql_statements import EcommerceSQL
#
# 2. Execute SQL using PyMySQL:
#      cursor.execute(EcommerceSQL.GET_ALL_VENDORS)
#      cursor.execute(EcommerceSQL.ADD_VENDOR, (name, location))
#
#  3. For searches with LIKE, the % wildcard symbol needs to be manually added: 
#      keyword = "laptop"
#      cursor.execute(EcommerceSQL.SEARCH_PRODUCTS, (f'%{keyword}%', f'%{keyword}%'))


class EcommerceSQL:
    # ========== Vendor Management ==========

    # Get all vendors list
    GET_ALL_VENDORS = """
        SELECT vendor_id, business_name, avg_rating, geo_location 
        FROM Vendor 
        ORDER BY business_name
    """

    # Add new vendor
    ADD_VENDOR = """
        INSERT INTO Vendor (business_name, geo_location) 
        VALUES (%s, %s)
    """

    # Get vendor by ID
    GET_VENDOR_BY_ID = """
        SELECT vendor_id, business_name, avg_rating, geo_location 
        FROM Vendor 
        WHERE vendor_id = %s
    """

    # Search vendors by name
    SEARCH_VENDORS = """
        SELECT vendor_id, business_name, avg_rating, geo_location 
        FROM Vendor 
        WHERE business_name LIKE %s
        ORDER BY business_name
    """

    # ========== Product Catalog Management ==========

    # Get all products by vendor
    GET_PRODUCTS_BY_VENDOR = """
        SELECT p.product_id, p.product_name, p.price, p.stock_quantity,
               GROUP_CONCAT(t.tag_name SEPARATOR ', ') as tags
        FROM Product p
        LEFT JOIN ProductTag pt ON p.product_id = pt.product_id
        LEFT JOIN Tag t ON pt.tag_id = t.tag_id
        WHERE p.vendor_id = %s
        GROUP BY p.product_id
        ORDER BY p.product_name
    """

    # Add new product
    ADD_PRODUCT = """
        INSERT INTO Product (product_name, price, stock_quantity, vendor_id) 
        VALUES (%s, %s, %s, %s)
    """

    # Get last inserted product ID
    GET_LAST_PRODUCT_ID = """
        SELECT LAST_INSERT_ID()
    """

    # Add tag to product
    ADD_PRODUCT_TAG = """
        INSERT INTO ProductTag (product_id, tag_id) 
        VALUES (%s, %s)
    """

    # Get all available tags
    GET_ALL_TAGS = """
        SELECT tag_id, tag_name 
        FROM Tag 
        ORDER BY tag_name
    """

    # Search tags for autocomplete
    SEARCH_TAGS = """
        SELECT tag_id, tag_name 
        FROM Tag 
        WHERE tag_name LIKE %s 
        LIMIT 10
    """

    # ========== Product Discovery (Tag Search) ==========

    # Search products by keyword (matches product name or tags)
    SEARCH_PRODUCTS_BY_TAG = """
        SELECT DISTINCT 
            p.product_id, 
            p.product_name, 
            p.price, 
            p.stock_quantity,
            v.business_name as vendor_name,
            v.vendor_id,
            GROUP_CONCAT(DISTINCT t.tag_name SEPARATOR ', ') as tags
        FROM Product p
        JOIN Vendor v ON p.vendor_id = v.vendor_id
        LEFT JOIN ProductTag pt ON p.product_id = pt.product_id
        LEFT JOIN Tag t ON pt.tag_id = t.tag_id
        WHERE p.product_name LIKE %s 
           OR t.tag_name LIKE %s
        GROUP BY p.product_id
        ORDER BY p.product_name
    """

    # Search products by exact tag ID
    SEARCH_PRODUCTS_BY_TAG_ID = """
        SELECT DISTINCT 
            p.product_id, 
            p.product_name, 
            p.price, 
            p.stock_quantity,
            v.business_name as vendor_name,
            v.vendor_id,
            GROUP_CONCAT(DISTINCT t.tag_name SEPARATOR ', ') as tags
        FROM Product p
        JOIN Vendor v ON p.vendor_id = v.vendor_id
        LEFT JOIN ProductTag pt ON p.product_id = pt.product_id
        LEFT JOIN Tag t ON pt.tag_id = t.tag_id
        WHERE pt.tag_id = %s
        GROUP BY p.product_id
        ORDER BY p.product_name
    """

    # Get product details
    GET_PRODUCT_DETAILS = """
        SELECT p.product_id, p.product_name, p.price, p.stock_quantity,
               v.vendor_id, v.business_name as vendor_name,
               GROUP_CONCAT(t.tag_name SEPARATOR ', ') as tags
        FROM Product p
        JOIN Vendor v ON p.vendor_id = v.vendor_id
        LEFT JOIN ProductTag pt ON p.product_id = pt.product_id
        LEFT JOIN Tag t ON pt.tag_id = t.tag_id
        WHERE p.product_id = %s
        GROUP BY p.product_id
    """

    # ========== Shopping Cart and Orders ==========

    # Check product stock
    CHECK_PRODUCT_STOCK = """
        SELECT product_id, product_name, price, stock_quantity 
        FROM Product 
        WHERE product_id = %s
    """

    # Create new order
    CREATE_ORDER = """
        INSERT INTO Orders (customer_id, order_date, order_status, total_price) 
        VALUES (%s, NOW(), 'PENDING_PAY', 0)
    """

    # Get last created order ID
    GET_LAST_ORDER_ID = """
        SELECT LAST_INSERT_ID()
    """

    # Add item to order
    ADD_ORDER_ITEM = """
        INSERT INTO OrderItem (order_id, product_id, buy_quantity, unit_price) 
        VALUES (%s, %s, %s, (SELECT price FROM Product WHERE product_id = %s))
    """

    # Update order total price
    UPDATE_ORDER_TOTAL = """
        UPDATE Orders 
        SET total_price = %s 
        WHERE order_id = %s
    """

    # Deduct product stock
    UPDATE_PRODUCT_STOCK = """
        UPDATE Product 
        SET stock_quantity = stock_quantity - %s 
        WHERE product_id = %s AND stock_quantity >= %s
    """

    # Create transaction record
    CREATE_TRANSACTION = """
        INSERT INTO Transaction (order_id, vendor_id, pay_amount, transaction_time) 
        VALUES (%s, %s, %s, NOW())
    """

    # Get vendor totals by order
    GET_VENDOR_TOTALS_BY_ORDER = """
        SELECT 
            p.vendor_id,
            SUM(oi.buy_quantity * oi.unit_price) as vendor_amount
        FROM OrderItem oi
        JOIN Product p ON oi.product_id = p.product_id
        WHERE oi.order_id = %s
        GROUP BY p.vendor_id
    """

    # Get products in an order
    GET_ORDER_PRODUCTS = """
        SELECT oi.item_id, oi.product_id, p.product_name, 
               oi.buy_quantity, oi.unit_price,
               (oi.buy_quantity * oi.unit_price) as subtotal
        FROM OrderItem oi
        JOIN Product p ON oi.product_id = p.product_id
        WHERE oi.order_id = %s
    """

    # ========== Order Management ==========

    # Get all orders for a customer
    GET_CUSTOMER_ORDERS = """
        SELECT o.order_id, o.order_date, o.total_price, o.order_status
        FROM Orders o
        WHERE o.customer_id = %s
        ORDER BY o.order_date DESC
    """

    # Get complete order details
    GET_ORDER_DETAILS = """
        SELECT o.order_id, o.order_date, o.order_status, o.total_price,
               c.customer_id, c.contact_num, c.shipping_address
        FROM Orders o
        JOIN Customer c ON o.customer_id = c.customer_id
        WHERE o.order_id = %s
    """

    # Check order status
    GET_ORDER_STATUS = """
        SELECT order_status FROM Orders WHERE order_id = %s
    """

    # Delete order item
    DELETE_ORDER_ITEM = """
        DELETE FROM OrderItem WHERE item_id = %s AND order_id = %s
    """

    # Cancel entire order
    CANCEL_ORDER = """
        UPDATE Orders SET order_status = 'CANCELLED' WHERE order_id = %s
    """

    # Restore stock for cancelled order
    RESTORE_ORDER_STOCK = """
        UPDATE Product p
        JOIN OrderItem oi ON p.product_id = oi.product_id
        SET p.stock_quantity = p.stock_quantity + oi.buy_quantity
        WHERE oi.order_id = %s
    """

    # Delete transactions for cancelled order
    DELETE_ORDER_TRANSACTIONS = """
        DELETE FROM Transaction WHERE order_id = %s
    """

    # Update order status to pending shipping
    UPDATE_ORDER_STATUS_TO_SHIPPING = """
        UPDATE Orders 
        SET order_status = 'PENDING_SHIP' 
        WHERE order_id = %s
    """

    # Update order status to shipped
    UPDATE_ORDER_STATUS_TO_SHIPPED = """
        UPDATE Orders 
        SET order_status = 'SHIPPED' 
        WHERE order_id = %s
    """

    # Update order status to completed
    UPDATE_ORDER_STATUS_TO_COMPLETED = """
        UPDATE Orders 
        SET order_status = 'COMPLETED' 
        WHERE order_id = %s
    """

    # Get order transactions
    GET_ORDER_TRANSACTIONS = """
        SELECT t.transaction_id, t.pay_amount, t.transaction_time,
               v.business_name as vendor_name
        FROM Transaction t
        JOIN Vendor v ON t.vendor_id = v.vendor_id
        WHERE t.order_id = %s
    """

    # ========== Rating Management ==========

    # Add or update rating
    ADD_RATING = """
        INSERT INTO Rating (customer_id, vendor_id, score, created_at) 
        VALUES (%s, %s, %s, NOW())
        ON DUPLICATE KEY UPDATE score = %s, created_at = NOW()
    """

    # Get all ratings for a vendor
    GET_VENDOR_RATINGS = """
        SELECT r.rating_id, r.score, r.created_at,
               c.customer_id, c.contact_num
        FROM Rating r
        JOIN Customer c ON r.customer_id = c.customer_id
        WHERE r.vendor_id = %s
        ORDER BY r.created_at DESC
    """

    # Get customer's rating for a vendor
    GET_CUSTOMER_VENDOR_RATING = """
        SELECT score FROM Rating 
        WHERE customer_id = %s AND vendor_id = %s
    """

    # ========== Statistics Queries ==========

    # Get vendor sales statistics
    GET_VENDOR_SALES_STATS = """
        SELECT * FROM VendorSalesView
    """

    # Get customer spending statistics
    GET_CUSTOMER_STATS = """
        SELECT * FROM CustomerStatsView
    """

    # Get popular products by sales volume
    GET_POPULAR_PRODUCTS = """
        SELECT 
            p.product_id,
            p.product_name,
            SUM(oi.buy_quantity) as total_sold,
            COUNT(DISTINCT oi.order_id) as order_count
        FROM Product p
        JOIN OrderItem oi ON p.product_id = oi.product_id
        JOIN Orders o ON oi.order_id = o.order_id
        WHERE o.order_status != 'CANCELLED'
        GROUP BY p.product_id
        ORDER BY total_sold DESC
        LIMIT %s
    """

    # Get all orders overview (admin)
    GET_ALL_ORDERS_OVERVIEW = """
        SELECT 
            o.order_id,
            o.order_date,
            o.order_status,
            o.total_price,
            c.customer_id,
            c.contact_num
        FROM Orders o
        JOIN Customer c ON o.customer_id = c.customer_id
        ORDER BY o.order_date DESC
        LIMIT %s OFFSET %s
    """

    # ========== Customer Management ==========

    # Add new customer
    ADD_CUSTOMER = """
        INSERT INTO Customer (contact_num, shipping_address) 
        VALUES (%s, %s)
    """

    # Get customer by ID
    GET_CUSTOMER_BY_ID = """
        SELECT customer_id, contact_num, shipping_address 
        FROM Customer 
        WHERE customer_id = %s
    """

    # Update customer address
    UPDATE_CUSTOMER_ADDRESS = """
        UPDATE Customer 
        SET shipping_address = %s 
        WHERE customer_id = %s
    """

    # Validate customer login
    VALIDATE_CUSTOMER = """
        SELECT customer_id, contact_num, shipping_address 
        FROM Customer 
        WHERE customer_id = %s
    """
