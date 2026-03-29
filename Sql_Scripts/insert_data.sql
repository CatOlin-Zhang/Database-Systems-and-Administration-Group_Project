USE ecommerce_platform;

INSERT INTO vendors (vendor_id, business_name, avg_rating, geo_location) VALUES
    (1, '晨光数码', 0, '深圳'),
    (2, '北辰家居', 0, '上海'),
    (3, '海岸生活', 0, '广州');

INSERT INTO customers (customer_id, contact_num, shipping_address) VALUES
    (1, '13800000001', '北京市海淀区学院路 1 号'),
    (2, '13800000002', '上海市浦东新区张江路 8 号');

INSERT INTO products (product_id, product_name, price, stock_quantity, vendor_id) VALUES
    (1, '机械键盘', 299.00, 18, 1),
    (2, '无线鼠标', 89.00, 35, 1),
    (3, '书桌台灯', 129.00, 22, 2),
    (4, '实木书架', 399.00, 10, 2),
    (5, '保温水杯', 59.00, 50, 3),
    (6, '旅行双肩包', 189.00, 16, 3);

INSERT INTO tags (tag_id, tag_name) VALUES
    (1, '办公'),
    (2, '电竞'),
    (3, '便携'),
    (4, '家居'),
    (5, '护眼'),
    (6, '收纳'),
    (7, '出行');

INSERT INTO product_tags (protag_id, product_id, tag_id) VALUES
    (1, 1, 1),
    (2, 1, 2),
    (3, 2, 1),
    (4, 2, 3),
    (5, 3, 4),
    (6, 3, 5),
    (7, 4, 4),
    (8, 4, 6),
    (9, 5, 3),
    (10, 5, 7),
    (11, 6, 3),
    (12, 6, 7);

INSERT INTO ratings (rating_id, customer_id, vendor_id, score) VALUES
    (1, 1, 1, 5),
    (2, 2, 1, 4),
    (3, 1, 2, 4),
    (4, 2, 2, 5),
    (5, 1, 3, 4);

UPDATE vendors v
LEFT JOIN (
    SELECT vendor_id, ROUND(AVG(score), 2) AS avg_score
    FROM ratings
    GROUP BY vendor_id
) r ON r.vendor_id = v.vendor_id
SET v.avg_rating = COALESCE(r.avg_score, 0);

INSERT INTO orders (order_id, customer_id, order_date, total_price, order_status) VALUES
    (1, 1, '2026-03-25 14:30:00', 428.00, 'PENDING_SHIP');

INSERT INTO order_items (item_id, order_id, product_id, buy_quantity, unit_price) VALUES
    (1, 1, 1, 1, 299.00),
    (2, 1, 3, 1, 129.00);

INSERT INTO transactions (transaction_id, order_id, vendor_id, pay_amount, transaction_time) VALUES
    (1, 1, 1, 299.00, '2026-03-25 14:30:00'),
    (2, 1, 2, 129.00, '2026-03-25 14:30:00');
