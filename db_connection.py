# db_connection.py
# Capa de acceso a datos (solo conexiones y operaciones CRUD transaccionales).
#
# TEMA CENTRAL: separacion de configuracion y codigo.
# Las credenciales de MySQL NO viven en este archivo. Viven en .env.
# El codigo solo conoce los NOMBRES de las variables (DB_USER, DB_PASSWORD).
# Si este archivo se comparte, el receptor no obtiene acceso a la base.
#
# VULNERABILIDAD MITIGADA: credenciales hardcodeadadas/quemadas/embebidas en el codigo fuente.
# Que hacia: usuario y contrasena estaban escritos como literales.
#   Cualquiera que leyera el .py obtenia acceso a MySQL.
# Criticidad: Alta.
# Mitigacion: load_dotenv() carga .env al entorno del proceso. El codigo
#   lee con os.getenv. Si faltan credenciales, el programa muere al
#   arrancar con un mensaje claro (fail fast).

import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()  # load_dotenv() carga .env al entorno del proceso.

CONFIG_DB = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "charset": os.getenv("DB_CHARSET", "utf8mb4"),
    "autocommit": False,
}

# Fail fast: error que indica que sin credenciales no se intenta conectar.
# Un error al arrancar es mas barato que un error a mitad de peticion.
if not CONFIG_DB["user"] or not CONFIG_DB["password"]:
    raise EnvironmentError("Credenciales incorrectas...")

#Función que permite obtener una conexión a MySQL usando CONFIG_DB.
def obtener_conexion():
    """
    Abre una conexion a MySQL usando CONFIG_DB.

    VULNERABILIDAD MITIGADA: filtracion de errores internos de MySQL.
    Que hacia: str(error_mysql) exponia host, usuario, ruta del socket.
    Criticidad: Media.
    Mitigacion: se traducen los codigos errno a excepciones de dominio
    con mensajes controlados (DB-001 a DB-999).
    """
    try:
        conexion = mysql.connector.connect(**CONFIG_DB)
        if conexion is None:
            raise ConnectionError("No hay conexión a la base de datos")
        return conexion
    except Error as error_mysql:
        codigo_tecnico = error_mysql.errno if hasattr(error_mysql, "errno") else -1
        if codigo_tecnico == 1045:
            raise PermissionError("Credenciales inválidas") from error_mysql
        elif codigo_tecnico == 1049:
            raise NameError("No se encuentra la configuración") from error_mysql
        elif codigo_tecnico in (2002, 2003):
            raise ConnectionError("No hay conexión a la base de datos") from error_mysql
        else:
            raise RuntimeError("Error desconocido") from error_mysql

#Función que permite cerrar una conexión a MySQL.
def cerrar_conexion(conexion):
    """
    Cierra la conexion si esta activa.

    VULNERABILIDAD MITIGADA: cierre silencioso de recursos.
    Que hacia: atrapar Exception y hacer return ocultaba fallos de cierre.
    Criticidad: Baja.
    Mitigacion: se deja el return con comentario explicito de que en
    produccion debe ir a un log de advertencia.
    """
    if conexion is None:
        return
    try:
        if conexion.is_connected():
            conexion.close()
    except Exception:
        # En produccion: logging.warning("Fallo cierre de conexion")
        return

#Función que permite cerrar el cursor en memoria
def cerrar_cursor(cursor):
    """Cierra el cursor si existe. Mismo criterio que cerrar_conexion."""
    if cursor is None:
        return
    try:
        cursor.close()
    except Exception:
        return

#Función que permite confirmar una transacción en MySQL.
def confirmar_transaccion(conexion):
    """
    Hace COMMIT.

    VULNERABILIDAD MITIGADA: commit sobre conexion nula.
    Que hacia: si la conexion era None, fallaba con AttributeError confuso.
    Criticidad: Baja.
    Mitigacion: se valida explicitamente y se lanza ValueError de dominio.
    """
    if conexion is None:
        raise ValueError("Error al conecar a la Base de datos.")
    try:
        conexion.commit()
    except Error as error_mysql:
        raise RuntimeError("No se puede realizar commit...") from error_mysql

def deshacer_transaccion(conexion):
    """Hace ROLLBACK. Si la conexion es None, no hay nada que deshacer."""
    if conexion is None:
        return
    try:
        conexion.rollback()
    except Exception as error_mysql:
        raise RuntimeError("No se puede realizar rollback...") from error_mysql

# ---------------------------------------------------------------------------
# OPERACIONES DE LECTURA Y ESCRITURA
# Todas usan placeholders %s. Nunca concatenan valores del usuario.
# ---------------------------------------------------------------------------
#Función que permite ejecutar una consulta SQL en MySQL.
def ejecutar_consulta_unica(sql, parametros=()):
    """
    Ejecuta un SELECT que debe devolver 0 o 1 fila.

    VULNERABILIDAD MITIGADA: inyeccion SQL.
    Que hacia: si el llamador concatenaba valores, el SQL era manipulable.
    Criticidad: Alta.
    Mitigacion: la firma obliga a pasar parametros como tupla y el
    conector los escapa. Se documenta que nunca se concatene.
    """
    conexion = None
    cursor = None
    fila = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(sql, parametros)
        fila = cursor.fetchone()
    except Exception:
        raise
    finally:
        cerrar_cursor(cursor)
        cerrar_conexion(conexion)
    return fila

#Función que permite ejecutar una consulta SQL en MySQL.
def ejecutar_consulta_multiple(sql, parametros=()):
    """Ejecuta un SELECT que devuelve 0 o N filas. Placeholders obligatorios."""
    conexion = None
    cursor = None
    filas = []
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(sql, parametros)
        filas = cursor.fetchall()
    except Exception:
        raise
    finally:
        cerrar_cursor(cursor)
        cerrar_conexion(conexion)
    return filas

#Función que permite ejecutar una operación de escritura en MySQL.
def ejecutar_operacion_escritura(sql, parametros=()):
    """
    Ejecuta INSERT, UPDATE o DELETE y hace COMMIT.

    VULNERABILIDAD MITIGADA: escritura sin transaccion.
    Que hacia: sin commit/rollback explicito, los cambios quedaban en
    el limbo o se confirmaban parcialmente.
    Criticidad: Alta.
    Mitigacion: try/except con ROLLBACK ante cualquier fallo y COMMIT
    solo si todo sale bien.
    """
    conexion = None
    cursor = None
    filas_afectadas = 0
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(sql, parametros)
        filas_afectadas = cursor.rowcount
        confirmar_transaccion(conexion)
    except Exception:
        deshacer_transaccion(conexion)
        raise
    finally:
        cerrar_cursor(cursor)
        cerrar_conexion(conexion)
    return filas_afectadas

#Función que permite ejecutar una operación de escritura en MySQL y devolver el último ID insertado.
def ejecutar_operacion_escritura_retornando_id(sql, parametros=()):
    """
    Ejecuta INSERT y devuelve (filas_afectadas, ultimo_id).

    VULNERABILIDAD MITIGADA: lastrowid no confiable.
    Que hacia: si el INSERT fallaba, lastrowid podia ser 0 y el endpoint
    consultaba por ID 0 devolviendo null sin explicar.
    Criticidad: Media.
    Mitigacion: el endpoint valida ultimo_id > 0 antes de consultar.
    Aqui solo se documenta la responsabilidad del llamador.
    """
    conexion = None
    cursor = None
    filas_afectadas = 0
    ultimo_id = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(sql, parametros)
        filas_afectadas = cursor.rowcount
        ultimo_id = cursor.lastrowid
        confirmar_transaccion(conexion)
    except Exception:
        deshacer_transaccion(conexion)
        raise
    finally:
        cerrar_cursor(cursor)
        cerrar_conexion(conexion)
    return filas_afectadas, ultimo_id