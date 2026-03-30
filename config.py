import os


# 数据库连接配置，优先读取环境变量，若不存在则使用默认值
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "ecommerce_platform")
DB_PORT = int(os.getenv("DB_PORT", "3306"))

# 应用程序配置
# 默认登录的客户ID
DEFAULT_CUSTOMER_ID = int(os.getenv("DEFAULT_CUSTOMER_ID", "1"))
# 是否使用演示数据模式（当环境变量 USE_DEMO_DATA 为 "1" 时启用）
USE_DEMO_DATA = os.getenv("USE_DEMO_DATA", "0") == "1"
