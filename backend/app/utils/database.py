"""
数据库连接工具
"""
import pymysql
from flask import current_app
import logging

logger = logging.getLogger(__name__)
from app import db
import pymysql
from flask import current_app

def get_db_connection():
    """
    获取数据库连接
    Returns:
        pymysql.Connection: 数据库连接对象
    """
    try:
        # 从配置获取数据库参数
        config = current_app.config

        connection = pymysql.connect(
            host=config.get('MYSQL_HOST', 'localhost'),
            user=config.get('MYSQL_USER', 'root'),
            password=config.get('MYSQL_PASSWORD', ''),
<<<<<<< HEAD
            database=config.get('MYSQL_DATABASE', 'bikehub'),
=======
            database=config.get('MYSQL_DATABASE', 'bikehub_dev'),
>>>>>>> main
            port=config.get('MYSQL_PORT', 3306),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False
        )

        return connection

    except Exception as e:
        logger.error(f"数据库连接失败: {str(e)}")
        raise Exception(f"数据库连接失败: {str(e)}")

def get_db_connection_without_dict():
    """
    获取数据库连接（不使用DictCursor）
    Returns:
        pymysql.Connection: 数据库连接对象
    """
    try:
        config = current_app.config

        connection = pymysql.connect(
            host=config.get('MYSQL_HOST', 'localhost'),
            user=config.get('MYSQL_USER', 'root'),
            password=config.get('MYSQL_PASSWORD', ''),
<<<<<<< HEAD
            database=config.get('MYSQL_DATABASE', 'bikehub'),
=======
            database=config.get('MYSQL_DATABASE', 'bikehub_dev'),
>>>>>>> main
            port=config.get('MYSQL_PORT', 3306),
            charset='utf8mb4',
            autocommit=False
        )

        return connection

    except Exception as e:
        logger.error(f"数据库连接失败: {str(e)}")
        raise Exception(f"数据库连接失败: {str(e)}")

def execute_query(query, params=None, fetch_one=False, fetch_all=True):
    """
    执行查询语句
    Args:
        query (str): SQL查询语句
        params (tuple): 查询参数
        fetch_one (bool): 是否只获取一条记录
        fetch_all (bool): 是否获取所有记录
    Returns:
        dict/list: 查询结果
    """
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(query, params or ())

        if fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
        else:
            result = None

        cursor.close()
        return result

    except Exception as e:
        logger.error(f"查询执行失败: {str(e)}")
        raise Exception(f"查询执行失败: {str(e)}")
    finally:
        if connection:
            connection.close()

def execute_update(query, params=None):
    """
    执行更新语句（INSERT, UPDATE, DELETE）
    Args:
        query (str): SQL更新语句
        params (tuple): 更新参数
    Returns:
        int: 受影响的行数
    """
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(query, params or ())
        connection.commit()

        affected_rows = cursor.rowcount
        last_id = cursor.lastrowid

        cursor.close()
        return affected_rows, last_id

    except Exception as e:
        logger.error(f"更新执行失败: {str(e)}")
        if connection:
            connection.rollback()
        raise Exception(f"更新执行失败: {str(e)}")
    finally:
        if connection:
            connection.close()

def execute_transaction(queries_and_params):
    """
    执行事务
    Args:
        queries_and_params (list): [(query1, params1), (query2, params2), ...]
    Returns:
        list: 每个查询的受影响行数
    """
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        results = []
        for query, params in queries_and_params:
            cursor.execute(query, params or ())
            results.append(cursor.rowcount)

        connection.commit()
        cursor.close()
        return results

    except Exception as e:
        logger.error(f"事务执行失败: {str(e)}")
        if connection:
            connection.rollback()
        raise Exception(f"事务执行失败: {str(e)}")
    finally:
        if connection:
            connection.close()

def test_connection():
    """
    测试数据库连接
    Returns:
        bool: 连接是否成功
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return result is not None
    except Exception as e:
        logger.error(f"数据库连接测试失败: {str(e)}")
        return False

class DatabaseManager:
    """数据库管理器类"""

    def __init__(self):
        self.connection = None

    def connect(self):
        """建立连接"""
        if not self.connection:
            self.connection = get_db_connection()
        return self.connection

    def close(self):
        """关闭连接"""
        if self.connection:
            self.connection.close()
            self.connection = None

    def execute(self, query, params=None):
        """执行SQL语句"""
        connection = self.connect()
        cursor = connection.cursor()
        try:
            cursor.execute(query, params or ())
            return cursor
        except Exception as e:
            logger.error(f"SQL执行失败: {str(e)}")
            raise

    def commit(self):
        """提交事务"""
        if self.connection:
            self.connection.commit()

    def rollback(self):
        """回滚事务"""
        if self.connection:
            self.connection.rollback()

    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        if exc_type:
            self.rollback()
        else:
            self.commit()
<<<<<<< HEAD
        self.close()
=======
        self.close()
>>>>>>> main
