#!/usr/bin/env python3
"""Database and import smoke tests."""

import os

from dotenv import load_dotenv


load_dotenv()


def test_mysql_connection():
    """Verify the configured MySQL database is reachable."""
    try:
        import pymysql

        connection = pymysql.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", "ding1017ding"),
            database=os.getenv("MYSQL_DATABASE", "bikehub_dev"),
            port=int(os.getenv("MYSQL_PORT", "3306")),
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )

        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 AS ok")
            result = cursor.fetchone()
            assert result and result["ok"] == 1

            cursor.execute("SHOW TABLES LIKE 'chat_%'")
            tables = cursor.fetchall()
            table_names = [next(iter(table.values())) for table in tables]
            print(f"chat tables: {table_names}")

        connection.close()
        return True

    except Exception as exc:
        print(f"database connection failed: {exc}")
        return False


def test_api_imports():
    """Verify chat API modules can be imported."""
    try:
        from app.routes import api_bp
        from app.routes.chat import search_chat_users

        assert api_bp is not None
        assert search_chat_users is not None
        return True
    except Exception as exc:
        print(f"chat api import failed: {exc}")
        return False

