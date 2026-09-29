# database/db_connection.py
# Data Access Layer (Transactional CRUD operations and connection handling).

import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

CONFIG_DB = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "charset": os.getenv("DB_CHARSET", "utf8mb4"),
    "autocommit": False,
}

if not CONFIG_DB["user"] or not CONFIG_DB["password"]:
    raise EnvironmentError("Database credentials not configured in .env file")

def get_db_connection():
    try:
        connection = mysql.connector.connect(**CONFIG_DB)
        if connection is None:
            raise ConnectionError("No connection to database")
        return connection
    except Error as db_err:
        errno_code = getattr(db_err, "errno", -1)
        if errno_code == 1045:
            raise PermissionError("Invalid database credentials") from db_err
        elif errno_code == 1049:
            raise NameError("Database not found") from db_err
        elif errno_code in (2002, 2003):
            raise ConnectionError("MySQL server unreachable") from db_err
        else:
            raise RuntimeError("Database connection error") from db_err

def close_db_connection(connection):
    if connection and connection.is_connected():
        try:
            connection.close()
        except Exception:
            pass

def close_db_cursor(cursor):
    if cursor:
        try:
            cursor.close()
        except Exception:
            pass

def commit_transaction(connection):
    if connection is None:
        raise ValueError("Null connection cannot be committed.")
    connection.commit()

def rollback_transaction(connection):
    if connection:
        try:
            connection.rollback()
        except Exception:
            pass

def execute_single_query(sql, params=()):
    connection = None
    cursor = None
    row = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(sql, params)
        row = cursor.fetchone()
    finally:
        close_db_cursor(cursor)
        close_db_connection(connection)
    return row

def execute_multiple_query(sql, params=()):
    connection = None
    cursor = None
    rows = []
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(sql, params)
        rows = cursor.fetchall()
    finally:
        close_db_cursor(cursor)
        close_db_connection(connection)
    return rows

def execute_write_operation(sql, params=()):
    connection = None
    cursor = None
    affected_rows = 0
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(sql, params)
        affected_rows = cursor.rowcount
        commit_transaction(connection)
    except Exception:
        rollback_transaction(connection)
        raise
    finally:
        close_db_cursor(cursor)
        close_db_connection(connection)
    return affected_rows

def execute_write_operation_returning_id(sql, params=()):
    connection = None
    cursor = None
    affected_rows = 0
    last_id = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(sql, params)
        affected_rows = cursor.rowcount
        last_id = cursor.lastrowid
        commit_transaction(connection)
    except Exception:
        rollback_transaction(connection)
        raise
    finally:
        close_db_cursor(cursor)
        close_db_connection(connection)
    return affected_rows, last_id