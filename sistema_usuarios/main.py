from usuario import Usuario
import os

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

# --- FUNCIONES DEL ADMINISTRADOR ---
def ejecutar_registrar():
    print("\n--- Registrar Nuevo Usuario ---")
    usuario = input("Usuario: ").strip()
    password = input("Contraseña: ").strip()
    tipo = input("Tipo (ADMIN/USER): ").strip().upper()
    
    if tipo not in ["ADMIN", "USER"]:
        print("[ERROR] Tipo de usuario inválido. Debe ser ADMIN o USER.")
        return

    servicio = Usuario()
    if servicio.crear_usuario(usuario, password, tipo):
        print("[OK] Usuario registrado con éxito.")

def ejecutar_listar():
    print("\n--- Listado de Usuarios ---")
    usuarios = Usuario().obtener_listado()
    if not usuarios:
        print("No hay usuarios registrados.")
        return
    
    print(f"{'ID':<5} {'Usuario':<15} {'Tipo':<10}")
    print("-" * 32)
    for u in usuarios:
        print(f"{u['id']:<5} {u['usuario']:<15} {u['tipo']:<10}")
    print(f"\nTotal de usuarios: {len(usuarios)}") 

def ejecutar_buscar():
    print("\n--- Buscar Usuario ---")
    id_buscar = input("Ingrese el ID del usuario: ")
    u = Usuario().buscar_por_id(id_buscar)
    if u:
        print(f"\nID: {u['id']}")
        print(f"Usuario: {u['usuario']}")
        print(f"Tipo: {u['tipo']}")
        print(f"Creado el: {u['fecha_creacion']}")
    else:
        print("[ERROR] Usuario no encontrado.")

def ejecutar_modificar():
    print("\n--- Modificar Usuario ---")
    id_modificar = input("Ingrese el ID a modificar: ")
    u = Usuario().buscar_por_id(id_modificar)
    if not u:
        print("[ERROR] Usuario no encontrado.")
        return
    
    print(f"Modificando a: {u['usuario']}")
    nuevo_user = input(f"Nuevo usuario (actual: {u['usuario']}): ").strip()
    nueva_pass = input("Nueva contraseña: ").strip()
    nuevo_tipo = input("Nuevo tipo (ADMIN/USER): ").strip().upper()

    if nuevo_tipo not in ["ADMIN", "USER"]:
        print("[ERROR] Tipo inválido.")
        return

    if Usuario().modificar_usuario(id_modificar, nuevo_user, nueva_pass, nuevo_tipo):
        print("[OK] Usuario actualizado correctamente.")
    else:
        print("[ERROR] No se pudieron realizar los cambios.")

def ejecutar_eliminar():
    print("\n--- Eliminar Usuario ---")
    id_eliminar = input("Ingrese el ID a eliminar: ")
    u = Usuario().buscar_por_id(id_eliminar)
    if not u:
        print("[ERROR] Usuario no encontrado.")
        return

    confirmar = input(f"¿Seguro que deseas eliminar a {u['usuario']}? (s/n): ").lower()
    if confirmar == 's':
        if Usuario().eliminar_usuario(id_eliminar):
            print("[OK] Usuario eliminado.")
        else:
            print("[ERROR] No se pudo eliminar.")
    else:
        print("Operación cancelada.")


# --- MENÚS DE ROLES ---
def menu_admin(usuario_logueado):
    while True:
        print(f"\n==============================")
        print(f"Bienvenido Administrador:\n{usuario_logueado.usuario}")
        print(f"==============================")
        print("1. Registrar usuario")
        print("2. Listar usuarios")
        print("3. Buscar usuario")
        print("4. Modificar usuario")
        print("5. Eliminar usuario")
        print("6. Cerrar sesión")
        
        opcion = input("Seleccione una opción: ")
        if opcion == "1": ejecutar_registrar()
        elif opcion == "2": ejecutar_listar()
        elif opcion == "3": ejecutar_buscar()
        elif opcion == "4": ejecutar_modificar()
        elif opcion == "5": ejecutar_eliminar()
        elif opcion == "6":
            print("Cerrando sesión de administrador...")
            break
        else:
            print("Opción inválida.")

def menu_user(usuario_logueado):
    while True:
        print(f"\n==============================")
        print(f"Bienvenido\n\n{usuario_logueado.usuario}\n")
        print(f"Tipo de usuario:\n{usuario_logueado.tipo}")
        print(f"==============================")
        print("1. Cerrar sesión")
        
        opcion = input("Seleccione una opción: ")
        if opcion == "1":
            print("Cerrando sesión...")
            break
        else:
            print("Opción inválida.")


# --- FLUJO PRINCIPAL ---
def inicio_sesion():
    print("\n==============================")
    print("       INICIO DE SESIÓN")
    print("==============================")
    username = input("Usuario: ").strip()
    password = input("Contraseña: ").strip()
    
    usuario_valido = Usuario().validar_inicio_sesion(username, password)
    
    if usuario_valido:
        limpiar_pantalla()
        if usuario_valido.tipo == "ADMIN":
            menu_admin(usuario_valido)
        elif usuario_valido.tipo == "USER":
            menu_user(usuario_valido)
    else:
        print("\n[ERROR] Usuario o contraseña incorrectos.")

def main():
    while True:
        print("\n==============================")
        print("      SISTEMA DE USUARIOS")
        print("==============================")
        print("1. Iniciar sesión")
        print("2. Salir")
        
        opcion = input("Seleccione una opción: ")
        if opcion == "1":
            inicio_sesion()
        elif opcion == "2":
            print("¡Gracias por utilizar el sistema!")
            break
        else:
            print("Opción inválida.")

if __name__ == "__main__":
    main()