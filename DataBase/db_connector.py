from contextlib import contextmanager

import pymysql

from config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER


def get_connection():
    # 建立并返回一个新的数据库连接对象
    return pymysql.connect(
        host=DB_HOST,           # 数据库主机地址
        user=DB_USER,           # 数据库用户名
        password=DB_PASSWORD,   # 数据库密码
        database=DB_NAME,       # 数据库名称
        port=DB_PORT,           # 数据库端口
        charset="utf8mb4",      # 字符集设置为 utf8mb4 以支持完整的 Unicode（包括 emoji）
        cursorclass=pymysql.cursors.DictCursor, # 使用字典游标，使查询结果以字典形式返回
        autocommit=False,       # 关闭自动提交，以便手动控制事务
    )


@contextmanager
def get_managed_connection():
    # 获取一个新的数据库连接
    conn = get_connection()
    try:
        # 将连接对象 yield 给调用者使用
        yield conn
        # 如果代码块执行成功，则提交事务
        conn.commit()
    except Exception:
        # 如果代码块执行过程中发生异常，则回滚事务
        conn.rollback()
        # 重新抛出异常，让调用者处理
        raise
    finally:
        # 无论是否发生异常，最后都关闭数据库连接
        conn.close()