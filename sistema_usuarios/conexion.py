import mysql.connector
from mysql.connector import Error

class ConexionDB:

    def __init__(self):
        self.config = {
            "host": "localhost",
            "user": "root",
            "password": "1234",  
            "database": "usuarios_db",
        }

    def obtener_conexion(self):
        try:
            conexion = mysql.connector.connect(**self.config, use_pure=True)
            if conexion.is_connected():
                return conexion
            return None
        except Error as e:
            print(f"\n[ERROR BD] No se pudo conectar: {e}\n")
            return None

    def cerrar_conexion(self, conexion):
        """Cierra la conexión de forma segura."""
        if conexion and conexion.is_connected():
            conexion.close()