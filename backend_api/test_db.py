print("INICIO TEST")
import mysql.connector
from mysql.connector import Error

try:
    print("Intentando conectar...")

    conn = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="",
        database="sistema_matricula",
        port=3306,
        connection_timeout=5
    )

    print("➡ Después del connect()")

    if conn.is_connected():
        print("✅ Conectado!")
        conn.close()
    else:
        print("❌ No conectado")

except Exception as e:
    print("\n🔥 ERROR:")
    print(e)
