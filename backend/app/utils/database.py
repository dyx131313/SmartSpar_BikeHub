from app import db
import pymysql
from flask import current_app

def get_db_connection():
    """
    获取数据库连接
    这里为了兼容 chat.py 中的原生 SQL 写法，返回一个类似 DB-API 2.0 的连接对象
    """
    # 如果配置的是 SQLite，SQLAlchemy 底层连接就是 sqlite3.Connection
    # 如果配置的是 MySQL，SQLAlchemy 底层连接可能是 pymysql 或 mysqlclient 的连接
    
    # 方式1: 从 SQLAlchemy 获取原生连接 (推荐，能复用连接池)
    # 注意: raw_connection() 返回的是驱动层面的连接对象
    return db.engine.raw_connection()

    # 方式2: 如果需要完全独立的连接（不推荐，因为会增加连接开销），可以重新 connect
    # 但考虑到 chat.py 中使用了 cursor(dictionary=True)，这通常是 mysql-connector 或 pymysql 的特性
    # 如果是 sqlite，是不支持 dictionary=True 参数的。
    
    # 既然 chat.py 里有 cursor(dictionary=True)，说明这段代码原本就是为 MySQL 设计的。
    # 我们需要确保返回的连接能支持这个参数，或者修改 chat.py。
    # 暂时先返回 raw_connection，并在 chat.py 中做适配可能更稳妥，
    # 但为了不改 chat.py，我们尽量模拟。


