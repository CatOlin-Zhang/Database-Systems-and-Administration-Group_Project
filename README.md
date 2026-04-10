# E-commerce Platform - Database Systems and Administration Group Project

---
![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![MySQL](https://img.shields.io/badge/Database-MySQL-orange?logo=mysql)
![GUI](https://img.shields.io/badge/GUI-Tkinter-green)
![Architecture](https://img.shields.io/badge/Architecture-MVC-purple)
##  Project Overview

This project is a comprehensive **E-commerce Platform** designed to manage interactions between multiple vendors and customers. The system focuses on robust database design to handle vendor profiles, product inventories, customer information, and complex order workflows.

**Core Features:**
- **Multi-Vendor Support:** Manage multiple vendors and their product catalogs.
- **Customer Experience:** Browse products, search via tags, place purchases, and track orders.
- **Transaction Management:** Handles cross-vendor settlements and order history.

---

##  Project Structure

The project follows a modular architecture, separating the user interface, business logic, and database operations.

### Root Directory
- `main.py`: The entry point of the application. It initializes the GUI and starts the program loop.
- `config.py`: Configuration file for database connection settings and other global variables.
- `requirements.txt`: Lists Python dependencies required to run the project.
- `ER.jpg` / `ER.docx`: Entity-Relationship Diagram and documentation for the database schema.
- `group10_insert_sql.txt`: Supplementary SQL script for data insertion.
- `sql_statements.py`: Python file containing specific SQL query strings used throughout the application.

###  GUI (User Interface)
Contains all files related to the graphical user interface.
- `app_window.py`: Defines the main application window and top-level layout.
- `entry_view.py`: Handles the login and registration screens.
- `product_view.py`: Interface for displaying product listings and details.
- `search_view.py`: Interface for the search functionality.
- `cart_view.py`: Displays the shopping cart and allows item management.
- `order_history_view.py`: Shows the customer's past orders.
- `supplier_view.py`: Interface specifically for vendor/supplier operations.
- `mock_service.py`: Simulates backend services.

### logic (Business Logic)
Contains the core processing logic (middleware) between the GUI and the database.
- `app_service.py`: Main service layer coordinating data flow between views and data access objects.
- `order_manager.py`: Handles complex logic related to order creation, processing, and status updates.
- `search_engine.py`: Implements the logic for searching products and filtering results.

###  DataBase (Data Access Layer)
Handles direct communication with the SQL database.
- `db_connector.py`: Manages the connection to the database.
- `customer_dao.py`: Data Access Object for Customer-related SQL operations.
- `supplier_dao.py`: Data Access Object for Supplier-related SQL operations.
- `product_dao.py`: Data Access Object for Product-related SQL operations.
- `order_dao.py`: Data Access Object for Order-related SQL operations.

### Sql_Scripts
Contains raw SQL files for database setup.
- `create_tables.sql`: SQL script to create the database schema.
- `insert_data.sql`: SQL script to populate the database with initial data.

---

##  How to Run

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Database Setup:**
    - Ensure your SQL server is running.
    - Execute `Sql_Scripts/create_tables.sql` to create the schema.
    - Execute `Sql_Scripts/insert_data.sql` to populate initial data.
    - Update `config.py` with your database credentials.

3.  **Launch Application:**
    ```bash
    python main.py