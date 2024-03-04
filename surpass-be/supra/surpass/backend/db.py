import pymysql
from typing import List, Union

def list_tables(host: str, port: int, user: str, password: str, database: str) -> Union[List[str], str]:
    """
    连接到MySQL数据库并列出所有表。

    参数:
    - host: MySQL服务器地址。
    - port: MySQL服务器端口号。
    - user: 用户名。
    - password: 密码。
    - database: 数据库名。

    返回:
    - 成功时返回表名的列表（List[str]）。
    - 失败时返回错误信息（str）。
    """
    config = {
        'host': host,
        'port': port,
        'user': user,
        'password': password,
        'database': database,
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }

    try:
        connection = pymysql.connect(**config)
        with connection.cursor() as cursor:
            # SQL查询语句
            sql = "SHOW TABLES"
            cursor.execute(sql)
            # 获取所有表名
            tables = cursor.fetchall()
            # 提取表名，假设结果是字典形式
            return [list(table.values())[0] for table in tables]
    except (pymysql.MySQLError, Exception) as e:
        # 返回错误信息
        return f"数据库连接或查询失败，错误信息: {e}"
    finally:
        # 确保无论如何都关闭数据库连接
        if 'connection' in locals() and connection:
            connection.close()

# 使用示例
if __name__ == "__main__":
    host = 'your_host'
    port = 3306
    user = 'your_username'
    password = 'your_password'
    database = 'your_database'

    result = list_tables(host, port, user, password, database)
    if isinstance(result, list):
        print("数据库中的表包括：")
        for table in result:
            print(table)
    else:
        print(result)
