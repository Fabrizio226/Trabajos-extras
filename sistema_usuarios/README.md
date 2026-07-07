''Sistema de Gestión de Usuarios''

-- Descripción del Proyecto --

Este proyecto es una aplicación de consola en Python que implementa un sistema de control de acceso basado en roles utilizando el paradigma de Programación Orientada a Objetos. El sistema se conecta a una base de datos MySQL mediante un conector puro para administrar de forma segura las credenciales de los usuarios.

El sistema cuenta con dos niveles de acceso diferenciados:
* ADMIN (Administrador): Tiene permisos totales para realizar operaciones CRUD (Crear, Leer, Actualizar y Eliminar) sobre cualquier cuenta.
* USER (Usuario Común): Solo tiene permitido autenticarse, visualizar los datos de su propio perfil y cerrar la sesión.

---

-- Tecnologías Utilizadas --
* Lenguaje de Programación: Python 
* Motor de Base de Datos: MySQL Server
* Librería de Conexión: mysql-connector-python
* Paradigma de Diseño: Programación Orientada a Objetos

---

-- Instrucciones de Instalación y Ejecución --

-- 1. Preparación de la Base de Datos --

Antes de ejecutar el código, monte la base de datos en su servidor local (MySQL Workbench) ejecutando en orden los archivos de la carpeta `resources/`:
1. Ejecute `crear_bd.sql` para generar la estructura de las tablas.
2. Ejecute `poblar_datos.sql` para cargar los roles y los usuarios de prueba iniciales.

-- 2. Instalación de Dependencias --

Abre la terminal en la raíz del proyecto e instale el conector oficial de MySQL con el siguiente comando:
```bash
python -m pip install mysql-connector-python


:D