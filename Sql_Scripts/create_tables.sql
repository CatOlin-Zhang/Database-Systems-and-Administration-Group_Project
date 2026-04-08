CREATE DATABASE IF NOT EXISTS ecommerce_platform
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE ecommerce_platform;

DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS product_tags;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS ratings;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS vendors;

CREATE TABLE vendors (
    vendor_id INT AUTO_INCREMENT PRIMARY KEY,
    business_name VARCHAR(100) NOT NULL UNIQUE,
    avg_rating DECIMAL(3, 2) DEFAULT 0,
    geo_location VARCHAR(100) NOT NULL
);

CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    contact_num VARCHAR(30) NOT NULL UNIQUE,
    shipping_address VARCHAR(255) NOT NULL
);

CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INT NOT NULL,
    vendor_id INT NOT NULL,
    CONSTRAINT uq_product_vendor UNIQUE (product_name, vendor_id),
    CONSTRAINT chk_product_price CHECK (price > 0),
    CONSTRAINT chk_product_stock CHECK (stock_quantity >= 0),
    CONSTRAINT fk_product_vendor FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id)
);

CREATE TABLE tags (
    tag_id INT AUTO_INCREMENT PRIMARY KEY,
    tag_name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE product_tags (
    protag_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    tag_id INT NOT NULL,
    CONSTRAINT uq_product_tag UNIQUE (product_id, tag_id),
    CONSTRAINT fk_product_tag_product FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    CONSTRAINT fk_product_tag_tag FOREIGN KEY (tag_id) REFERENCES tags(tag_id) ON DELETE CASCADE
);

CREATE TABLE ratings (
    rating_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    vendor_id INT NOT NULL,
    score TINYINT NOT NULL,
    CONSTRAINT chk_rating_score CHECK (score BETWEEN 1 AND 5),
    CONSTRAINT fk_rating_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    CONSTRAINT fk_rating_vendor FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id)
);

CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    order_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_price DECIMAL(10, 2) NOT NULL,
    order_status ENUM('PENDING_PAY', 'PENDING_SHIP', 'SHIPPED', 'COMPLETED', 'CANCELLED') NOT NULL,
    CONSTRAINT chk_order_total CHECK (total_price >= 0),
    CONSTRAINT fk_order_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE order_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    buy_quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    CONSTRAINT chk_item_quantity CHECK (buy_quantity >= 1),
    CONSTRAINT chk_item_price CHECK (unit_price > 0),
    CONSTRAINT fk_item_order FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    CONSTRAINT fk_item_product FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    vendor_id INT NOT NULL,
    pay_amount DECIMAL(10, 2) NOT NULL,
    transaction_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_transaction_amount CHECK (pay_amount > 0),
    CONSTRAINT fk_transaction_order FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    CONSTRAINT fk_transaction_vendor FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id)
);
USE ecommerce_platform;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE COMMENT 'Login Username',
    password VARCHAR(50) NOT NULL COMMENT 'Login Password',
    role ENUM('admin', 'customer', 'vendor') NOT NULL COMMENT 'User Role',
    linked_id INT COMMENT 'Linked Business ID (customer_id or vendor_id)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Key Constraints
    -- Note: linked_id can be NULL for admins
    CONSTRAINT fk_user_customer
        FOREIGN KEY (linked_id) REFERENCES customers(customer_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_user_vendor
        FOREIGN KEY (linked_id) REFERENCES vendors(vendor_id)
        ON DELETE CASCADE
);