# backend_api/db.py

import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

def get_connection():
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            port=DB_CONFIG.get("port", 3306)
        )

        if conn.is_connected():
            print("✔ Conexión MySQL establecida")
            return conn
        else:
            print("❌ No se pudo conectar a MySQL")
            return None

    except Error as e:
        print("🔥 ERROR DE CONEXIÓN MYSQL:", e)
        return None
