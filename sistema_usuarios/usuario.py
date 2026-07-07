from conexion import ConexionDB
from mysql.connector import Error

class Usuario:
    def __init__(self, id=None, usuario=None, password=None, tipo=None):
        self.id = id
        self.usuario = usuario
        self.password = password
        self.tipo = tipo  

    def validar_inicio_sesion(self, usuario, password):
        db = ConexionDB()
        con = db.obtener_conexion()
        if not con: return None
        try:
            with con.cursor(dictionary=True) as cursor:
                sql = """
                    SELECT u.id, u.usuario, r.nombre AS tipo 
                    FROM usuarios u
                    JOIN roles r ON u.tipo_usuario_id = r.id
                    WHERE u.usuario = %s AND u.password = %s
                """
                cursor.execute(sql, (usuario, password))
                res = cursor.fetchone()
                if res:
                    return Usuario(res['id'], res['usuario'], None, res['tipo'])
                return None
        except Error as e:
            print(f"[ERROR] En Login: {e}")
            return None
        finally:
            db.cerrar_conexion(con)

    def crear_usuario(self, usuario, password, tipo):
        if self.buscar_por_usuario(usuario):
            print("[ERROR] El nombre de usuario ya existe.")
            return False

        db = ConexionDB()
        con = db.obtener_conexion()
        if not con: return False
        try:
            with con.cursor() as cursor:
                sql_rol = "SELECT id FROM roles WHERE nombre = %s"
                cursor.execute(sql_rol, (tipo,))
                rol_id = cursor.fetchone()[0]

                sql = "INSERT INTO usuarios (usuario, password, tipo_usuario_id) VALUES (%s, %s, %s)"
                cursor.execute(sql, (usuario, password, rol_id))
                con.commit()
                return True
        except Error as e:
            print(f"[ERROR] Al crear usuario: {e}")
            return False
        finally:
            db.cerrar_conexion(con)

    def obtener_listado(self):
        db = ConexionDB()
        con = db.obtener_conexion()
        if not con: return []
        try:
            with con.cursor(dictionary=True) as cursor:
                sql = """
                    SELECT u.id, u.usuario, r.nombre AS tipo 
                    FROM usuarios u
                    JOIN roles r ON u.tipo_usuario_id = r.id
                """
                cursor.execute(sql)
                return cursor.fetchall()
        except Error as e:
            print(f"[ERROR] Al listar usuarios: {e}")
            return []
        finally:
            db.cerrar_conexion(con)

    def buscar_por_id(self, id_usuario):
        db = ConexionDB()
        con = db.obtener_conexion()
        if not con: return None
        try:
            with con.cursor(dictionary=True) as cursor:
                sql = """
                    SELECT u.id, u.usuario, r.nombre AS tipo, u.fecha_creacion 
                    FROM usuarios u
                    JOIN roles r ON u.tipo_usuario_id = r.id
                    WHERE u.id = %s
                """
                cursor.execute(sql, (id_usuario,))
                return cursor.fetchone()
        except Error as e:
            print(f"[ERROR] Al buscar usuario: {e}")
            return None
        finally:
            db.cerrar_conexion(con)

    def buscar_por_usuario(self, username):
        db = ConexionDB()
        con = db.obtener_conexion()
        if not con: return None
        try:
            with con.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT id FROM usuarios WHERE usuario = %s", (username,))
                return cursor.fetchone()
        except Error:
            return None
        finally:
            db.cerrar_conexion(con)

    def modificar_usuario(self, id_usuario, nuevo_usuario, nueva_password, nuevo_tipo):
        db = ConexionDB()
        con = db.obtener_conexion()
        if not con: return False
        try:
            with con.cursor() as cursor:
                sql_rol = "SELECT id FROM roles WHERE nombre = %s"
                cursor.execute(sql_rol, (nuevo_tipo,))
                rol_id = cursor.fetchone()[0]

                sql = """
                    UPDATE usuarios 
                    SET usuario = %s, password = %s, tipo_usuario_id = %s 
                    WHERE id = %s
                """
                cursor.execute(sql, (nuevo_usuario, nueva_password, rol_id, id_usuario))
                con.commit()
                return cursor.rowcount > 0
        except Error as e:
            print(f"[ERROR] Al modificar: {e}")
            return False
        finally:
            db.cerrar_conexion(con)

    def eliminar_usuario(self, id_usuario):
        db = ConexionDB()
        con = db.obtener_conexion()
        if not con: return False
        try:
            with con.cursor() as cursor:
                sql = "DELETE FROM usuarios WHERE id = %s"
                cursor.execute(sql, (id_usuario,))
                con.commit()
                return cursor.rowcount > 0
        except Error as e:
            print(f"[ERROR] Al eliminar: {e}")
            return False
        finally:
            db.cerrar_conexion(con)