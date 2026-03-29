import os


DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "ecommerce_platform")
DB_PORT = int(os.getenv("DB_PORT", "3306"))

DEFAULT_CUSTOMER_ID = int(os.getenv("DEFAULT_CUSTOMER_ID", "1"))
USE_DEMO_DATA = os.getenv("USE_DEMO_DATA", "0") == "1"
