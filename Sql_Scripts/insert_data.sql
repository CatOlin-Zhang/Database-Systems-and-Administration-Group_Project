USE ecommerce_platform;

-- 1. Update and Expand Vendors
-- Replaced original Chinese vendors with English equivalents and added new ones
INSERT INTO vendors (vendor_id, business_name, avg_rating, geo_location) VALUES
    (1, 'Chenguang Digital', 0, 'Shenzhen'),
    (2, 'Beichen Home', 0, 'Shanghai'),
    (3, 'Coastal Living', 0, 'Guangzhou'),
    -- New Vendors
    (4, 'Urban Fashion', 0, 'Beijing'),
    (5, 'TechNova Gadgets', 0, 'Hangzhou');

-- 2. Update and Expand Customers
-- Replaced original Chinese addresses with English and added new customers
INSERT INTO customers (customer_id, contact_num, shipping_address) VALUES
    (1, '13800000001', 'No. 1 Xueyuan Road, Haidian District, Beijing'),
    (2, '13800000002', 'No. 8 Zhangjiang Road, Pudong New Area, Shanghai'),
    -- New Customers
    (3, '13900000003', 'No. 15 Tianhe Road, Guangzhou, Guangdong'),
    (4, '13900000004', 'No. 66 Yanan Road, Hangzhou, Zhejiang'),
    (5, '13700000005', 'No. 88 Century Avenue, Shenzhen, Guangdong');

-- 3. Update and Expand Products
-- Translated names and added new products for new vendors
INSERT INTO products (product_id, product_name, price, stock_quantity, vendor_id) VALUES
    -- Original Products (Translated)
    (1, 'Mechanical Keyboard', 299.00, 18, 1),
    (2, 'Wireless Mouse', 89.00, 35, 1),
    (3, 'Desk Lamp', 129.00, 22, 2),
    (4, 'Solid Wood Bookshelf', 399.00, 10, 2),
    (5, 'Insulated Water Bottle', 59.00, 50, 3),
    (6, 'Travel Backpack', 189.00, 16, 3),
    -- New Products
    (7, 'Cotton T-Shirt', 49.00, 100, 4),
    (8, 'Slim Fit Jeans', 129.00, 60, 4),
    (9, 'Noise Cancelling Headphones', 599.00, 15, 5),
    (10, 'Smart Watch Series 5', 899.00, 8, 5),
    (11, 'USB-C Hub', 79.00, 40, 1),
    (12, 'Yoga Mat', 39.00, 25, 3);

-- 4. Update and Expand Tags
-- Translated tags and added relevant new ones
INSERT INTO tags (tag_id, tag_name) VALUES
    (1, 'Office'),
    (2, 'Gaming'),
    (3, 'Portable'),
    (4, 'Home'),
    (5, 'Eye-care'),
    (6, 'Storage'),
    (7, 'Travel'),
    -- New Tags
    (8, 'Fashion'),
    (9, 'Audio'),
    (10, 'Wearable'),
    (11, 'Fitness');

-- 5. Update Product-Tag Relationships
-- Updated existing mappings and added mappings for new products
INSERT INTO product_tags (protag_id, product_id, tag_id) VALUES
    -- Original Mappings (Translated context)
    (1, 1, 1), (2, 1, 2),   -- Keyboard: Office, Gaming
    (3, 2, 1), (4, 2, 3),   -- Mouse: Office, Portable
    (5, 3, 4), (6, 3, 5),   -- Lamp: Home, Eye-care
    (7, 4, 4), (8, 4, 6),   -- Bookshelf: Home, Storage
    (9, 5, 3), (10, 5, 7),  -- Bottle: Portable, Travel
    (11, 6, 3), (12, 6, 7), -- Backpack: Portable, Travel
    -- New Mappings
    (13, 7, 8), (14, 7, 3), -- T-Shirt: Fashion, Portable
    (15, 8, 8),             -- Jeans: Fashion
    (16, 9, 9), (17, 9, 3), -- Headphones: Audio, Portable
    (18, 10, 10), (19, 10, 9), -- Smart Watch: Wearable, Audio
    (20, 11, 1), (21, 11, 3),  -- USB Hub: Office, Portable
    (22, 12, 11), (23, 12, 4); -- Yoga Mat: Fitness, Home

-- 6. Update and Expand Ratings
-- Added more ratings to ensure average calculation is meaningful
INSERT INTO ratings (rating_id, customer_id, vendor_id, score) VALUES
    -- Original Ratings
    (1, 1, 1, 5),
    (2, 2, 1, 4),
    (3, 1, 2, 4),
    (4, 2, 2, 5),
    (5, 1, 3, 4),
    -- New Ratings
    (6, 3, 4, 5), -- Customer 3 rates Urban Fashion
    (7, 4, 5, 3), -- Customer 4 rates TechNova
    (8, 5, 1, 4), -- Customer 5 rates Chenguang Digital
    (9, 3, 3, 5), -- Customer 3 rates Coastal Living
    (10, 2, 5, 5);-- Customer 2 rates TechNova

-- 7. Recalculate Vendor Average Ratings
UPDATE vendors v
LEFT JOIN (
    SELECT vendor_id, ROUND(AVG(score), 2) AS avg_score
    FROM ratings
    GROUP BY vendor_id
) r ON r.vendor_id = v.vendor_id
SET v.avg_rating = COALESCE(r.avg_score, 0);

-- 8. Update and Expand Orders
-- Added more orders with varied statuses
INSERT INTO orders (order_id, customer_id, order_date, total_price, order_status) VALUES
    -- Original Order
    (1, 1, '2026-03-25 14:30:00', 428.00, 'PENDING_SHIP'),
    -- New Orders
    (2, 2, '2026-03-26 09:15:00', 599.00, 'COMPLETED'),
    (3, 3, '2026-03-27 16:45:00', 178.00, 'SHIPPED'),
    (4, 1, '2026-03-28 11:00:00', 899.00, 'PENDING_PAY'),
    (5, 4, '2026-03-29 13:20:00', 108.00, 'COMPLETED');

-- 9. Update and Expand Order Items
INSERT INTO order_items (item_id, order_id, product_id, buy_quantity, unit_price) VALUES
    -- Original Items
    (1, 1, 1, 1, 299.00),
    (2, 1, 3, 1, 129.00),
    -- New Items
    (3, 2, 9, 1, 599.00),                -- Order 2: Headphones
    (4, 3, 5, 2, 59.00),                 -- Order 3: 2x Water Bottles
    (5, 3, 12, 1, 39.00),                -- Order 3: Yoga Mat
    (6, 3, 2, 1, 89.00),                 -- Order 3: Mouse (Wait, 59+59+39+89 = 246... logic check: 2*59+39+89 = 246. Let's adjust price in Order 3 table or items. Let's add another item to match 178. 59+59+39+21? No. Let's just trust the insert for now or assume a discount. Let's fix the math: 59*2 + 39 + 21? No product 21. Let's change Order 3 total to 246.00 in a real scenario, but here we just insert data.)
    -- Let's fix Order 3 items to match a logical total: 2 Water Bottles (118) + 1 Yoga Mat (39) + 1 Mouse (89) = 246.
    -- Let's add a distinct item for Order 4
    (7, 4, 10, 1, 899.00),               -- Order 4: Smart Watch
    (8, 5, 7, 2, 49.00),                 -- Order 5: 2x T-Shirts
    (9, 5, 11, 1, 79.00);                -- Order 5: USB Hub (Total 98+79 = 177. Let's update Order 5 total to 177.00)

-- Correcting Order Totals based on new items above
UPDATE orders SET total_price = 246.00 WHERE order_id = 3;
UPDATE orders SET total_price = 177.00 WHERE order_id = 5;

-- 10. Update and Expand Transactions
INSERT INTO transactions (transaction_id, order_id, vendor_id, pay_amount, transaction_time) VALUES
    -- Original Transactions
    (1, 1, 1, 299.00, '2026-03-25 14:30:00'),
    (2, 1, 2, 129.00, '2026-03-25 14:30:00'),
    -- New Transactions
    (3, 2, 5, 599.00, '2026-03-26 09:15:00'), -- TechNova
    (4, 3, 3, 118.00, '2026-03-27 16:45:00'), -- Coastal Living (2 bottles)
    (5, 3, 3, 39.00, '2026-03-27 16:45:00'),  -- Coastal Living (Mat)
    (6, 3, 1, 89.00, '2026-03-27 16:45:00'),  -- Chenguang (Mouse)
    (7, 5, 4, 98.00, '2026-03-29 13:20:00'),  -- Urban Fashion (2 Shirts)
    (8, 5, 1, 79.00, '2026-03-29 13:20:00');  -- Chenguang (Hub)


INSERT INTO users (username, password, role, linked_id) VALUES
('admin', '123456', 'admin', NULL);

-- --- Customer Data (linked_id matches customer_id in customers table) ---
INSERT INTO users (username, password, role, linked_id) VALUES
('user1', '123456', 'customer', 1),
('user2', '123456', 'customer', 2),
('user3', '123456', 'customer', 3),
('user4', '123456', 'customer', 4),
('user5', '123456', 'customer', 5);

-- --- Vendor Data (linked_id matches vendor_id in vendors table) ---
INSERT INTO users (username, password, role, linked_id) VALUES
('sup1', '123456', 'vendor', 1),
('sup2', '123456', 'vendor', 2),
('sup3', '123456', 'vendor', 3),
('sup4', '123456', 'vendor', 4),
('sup5', '123456', 'vendor', 5);

DELETE FROM users WHERE username IN ('sup2', 'sup3', 'sup4', 'sup5', 'sup6');

DROP TABLE users;
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(50) NOT NULL,
    role ENUM('admin', 'customer', 'vendor') NOT NULL,
    linked_id INT NOT NULL COMMENT 'Stores customer_id OR vendor_id',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
DELETE FROM users WHERE username LIKE 'sup%' OR username LIKE 'user%';
INSERT INTO users (username, password, role, linked_id) VALUES
('sup1', '123456', 'vendor', 1),
('sup2', '123456', 'vendor', 2),
('sup3', '123456', 'vendor', 3),
('sup4', '123456', 'vendor', 4),
('sup5', '123456', 'vendor', 5),
('sup6', '123456', 'vendor', 6);
INSERT INTO users (username, password, role, linked_id) VALUES
('user1', '123456', 'customer', 7),
('user2', '123456', 'customer', 8),
('user3', '123456', 'customer', 9),
('user4', '123456', 'customer', 10),
('user5', '123456', 'customer', 11);

ALTER TABLE users DROP FOREIGN KEY fk_user_customer;

ALTER TABLE users DROP FOREIGN KEY fk_user_vendor;

ALTER TABLE users MODIFY COLUMN linked_id INT NOT NULL;
INSERT INTO users (username, password, role, linked_id) VALUES
('admin', 'admin123', 'admin', 999);
