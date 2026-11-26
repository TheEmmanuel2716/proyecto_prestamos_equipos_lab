import sqlite3
from typing import TypedDict

RUTA_DB_POR_DEFECTO = "laboratorio.db"
TIPOS_PERMITIDOS = ("computador", "proyector", "tableta")
ESTADO_INICIAL = "disponible"
ESTADO_PRESTADO = "prestado"
ESTADO_PRESTAMO_ACTIVO = "activo"
MENSAJE_CAMPO_OBLIGATORIO = "El campo {campo} es obligatorio."

SQL_CREAR_TABLA = """
CREATE TABLE IF NOT EXISTS equipo (
    codigo_equipo TEXT PRIMARY KEY,
    tipo          TEXT NOT NULL,
    descripcion   TEXT NOT NULL,
    estado        TEXT NOT NULL
)
"""

SQL_CREAR_TABLA_PRESTAMO = """
CREATE TABLE IF NOT EXISTS prestamo (
    id_prestamo        INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_equipo      TEXT NOT NULL,
    solicitante_id     TEXT NOT NULL,
    solicitante_nombre TEXT NOT NULL,
    fecha_prestamo     TEXT NOT NULL,
    fecha_devolucion   TEXT,
    estado_prestamo    TEXT NOT NULL,
    FOREIGN KEY (codigo_equipo) REFERENCES equipo(codigo_equipo)
)
"""

SQL_INSERTAR_EQUIPO = """
INSERT INTO equipo (codigo_equipo, tipo, descripcion, estado)
VALUES (:codigo_equipo, :tipo, :descripcion, :estado)
"""

SQL_CONSULTAR_DISPONIBLES = """
SELECT codigo_equipo, tipo, descripcion, estado
FROM equipo
WHERE estado = 'disponible'
ORDER BY codigo_equipo ASC
"""

SQL_BUSCAR_EQUIPO = """
SELECT codigo_equipo, tipo, descripcion, estado
FROM equipo
WHERE codigo_equipo = :codigo_equipo
"""

SQL_TIENE_PRESTAMO_ACTIVO = """
SELECT 1
FROM prestamo
WHERE codigo_equipo = :codigo_equipo AND estado_prestamo = 'activo'
LIMIT 1
"""

SQL_INSERTAR_PRESTAMO = """
INSERT INTO prestamo (
    codigo_equipo,
    solicitante_id,
    solicitante_nombre,
    fecha_prestamo,
    fecha_devolucion,
    estado_prestamo
)
VALUES (
    :codigo_equipo,
    :solicitante_id,
    :solicitante_nombre,
    :fecha_prestamo,
    NULL,
    'activo'
)
"""

SQL_MARCAR_EQUIPO_PRESTADO = """
UPDATE equipo
SET estado = 'prestado'
WHERE codigo_equipo = :codigo_equipo
"""


class Equipo(TypedDict):
    """Datos de un equipo del inventario, tal como se guardan en SQLite."""

    codigo_equipo: str
    tipo: str
    descripcion: str
    estado: str


def _limpiar_texto(valor: object) -> str:
    """Devuelve el texto sin espacios en los extremos.

    Si el valor no es texto (por ejemplo None o un número), devuelve ''
    para que se trate como un dato faltante.
    """
    return valor.strip() if isinstance(valor, str) else ""


def _normalizar_y_validar(codigo_equipo: str, tipo: str, descripcion: str) -> Equipo:
    """Limpia los datos de entrada, valida las reglas y arma el equipo.

    Raises:
        ValueError: si falta el código, el tipo o la descripción (o no son
            texto), o si el tipo no es permitido.
    """
    codigo = _limpiar_texto(codigo_equipo).upper()
    tipo_normalizado = _limpiar_texto(tipo).lower()
    descripcion_limpia = _limpiar_texto(descripcion)

    if not codigo:
        raise ValueError(MENSAJE_CAMPO_OBLIGATORIO.format(campo="codigo_equipo"))
    if not descripcion_limpia:
        raise ValueError(MENSAJE_CAMPO_OBLIGATORIO.format(campo="descripcion"))
    if not tipo_normalizado:
        raise ValueError(MENSAJE_CAMPO_OBLIGATORIO.format(campo="tipo"))
    if tipo_normalizado not in TIPOS_PERMITIDOS:
        raise ValueError(
            f"El tipo '{tipo_normalizado}' no es permitido. "
            f"Use: {', '.join(TIPOS_PERMITIDOS)}."
        )

    return {
        "codigo_equipo": codigo,
        "tipo": tipo_normalizado,
        "descripcion": descripcion_limpia,
        "estado": ESTADO_INICIAL,
    }


def _guardar_equipo(equipo: Equipo, ruta_db: str) -> None:
    """Inserta el equipo en SQLite, creando la tabla si no existe.

    Raises:
        ValueError: si el código del equipo ya está registrado.
    """
    conexion = sqlite3.connect(ruta_db)
    try:
        conexion.execute(SQL_CREAR_TABLA)
        try:
            conexion.execute(SQL_INSERTAR_EQUIPO, equipo)
        except sqlite3.IntegrityError:
            raise ValueError(
                f"El equipo '{equipo['codigo_equipo']}' ya está registrado."
            ) from None
        conexion.commit()
    finally:
        conexion.close()


def registrar_equipo(
    codigo_equipo: str,
    tipo: str,
    descripcion: str,
    ruta_db: str = RUTA_DB_POR_DEFECTO,
) -> Equipo:
    """Registra un equipo nuevo en el inventario con estado 'disponible'.

    Args:
        codigo_equipo: Identificador único del equipo (ej. "EQ-01").
            Se eliminan espacios y se convierte a mayúsculas.
        tipo: "computador", "proyector" o "tableta".
            Se eliminan espacios y se convierte a minúsculas.
        descripcion: Información básica del equipo (no vacía).
        ruta_db: Ruta del archivo SQLite donde se guarda el equipo.

    Returns:
        Equipo: dict con las claves codigo_equipo, tipo, descripcion y estado.

    Raises:
        ValueError: si falta el código, el tipo o la descripción (o no son
            texto), si el tipo no es permitido o si el código ya está
            registrado.
    """
    equipo = _normalizar_y_validar(codigo_equipo, tipo, descripcion)
    _guardar_equipo(equipo, ruta_db)
    return equipo


def consultar_disponibles(ruta_db: str = RUTA_DB_POR_DEFECTO) -> list[Equipo]:
    """Retorna los equipos en estado 'disponible' ordenados por código.

    Args:
        ruta_db: Ruta del archivo SQLite del inventario.

    Returns:
        list[Equipo]: Lista de diccionarios con los equipos en estado
        'disponible', ordenados ascendentemente por codigo_equipo. Si la
        base o la tabla aún no existen o no hay equipos disponibles,
        retorna una lista vacía.
    """
    conexion = sqlite3.connect(ruta_db)
    try:
        try:
            filas = conexion.execute(SQL_CONSULTAR_DISPONIBLES).fetchall()
        except sqlite3.OperationalError:
            return []
        return [
            {
                "codigo_equipo": fila[0],
                "tipo": fila[1],
                "descripcion": fila[2],
                "estado": fila[3],
            }
            for fila in filas
        ]
    finally:
        conexion.close()


def registrar_prestamo(
    codigo_equipo: str,
    solicitante_id: str,
    solicitante_nombre: str,
    fecha_prestamo: str,
    ruta_db: str = RUTA_DB_POR_DEFECTO,
) -> dict[str, object]:
    """Crea un préstamo activo y actualiza el estado del equipo a 'prestado'.

    Args:
        codigo_equipo: Código del equipo a prestar (se limpia y pasa a
            mayúsculas).
        solicitante_id: Identificador del solicitante (no vacío).
        solicitante_nombre: Nombre del solicitante (no vacío).
        fecha_prestamo: Fecha del préstamo (no vacía).
        ruta_db: Ruta del archivo SQLite.

    Returns:
        dict[str, object]: Datos del préstamo creado con id_prestamo,
        codigo_equipo, solicitante_id, solicitante_nombre, fecha_prestamo,
        fecha_devolucion (None) y estado_prestamo ('activo').

    Raises:
        ValueError: si falta algún dato obligatorio o no es texto, si el equipo
            no existe o si ya está prestado / tiene un préstamo activo.
    """
    codigo = _limpiar_texto(codigo_equipo).upper()
    id_solicitante = _limpiar_texto(solicitante_id)
    nombre_solicitante = _limpiar_texto(solicitante_nombre)
    fecha = _limpiar_texto(fecha_prestamo)

    if not codigo:
        raise ValueError(MENSAJE_CAMPO_OBLIGATORIO.format(campo="codigo_equipo"))
    if not id_solicitante:
        raise ValueError(MENSAJE_CAMPO_OBLIGATORIO.format(campo="solicitante_id"))
    if not nombre_solicitante:
        raise ValueError(MENSAJE_CAMPO_OBLIGATORIO.format(campo="solicitante_nombre"))
    if not fecha:
        raise ValueError(MENSAJE_CAMPO_OBLIGATORIO.format(campo="fecha_prestamo"))

    conexion = sqlite3.connect(ruta_db)
    try:
        conexion.execute("PRAGMA foreign_keys = ON")
        conexion.execute(SQL_CREAR_TABLA)
        conexion.execute(SQL_CREAR_TABLA_PRESTAMO)

        try:
            fila_equipo = conexion.execute(
                SQL_BUSCAR_EQUIPO, {"codigo_equipo": codigo}
            ).fetchone()
            if fila_equipo is None:
                raise ValueError(f"El equipo '{codigo}' no existe.")

            estado_actual = fila_equipo[3]
            prestamo_activo = conexion.execute(
                SQL_TIENE_PRESTAMO_ACTIVO, {"codigo_equipo": codigo}
            ).fetchone()
            if estado_actual != ESTADO_INICIAL or prestamo_activo is not None:
                raise ValueError(f"El equipo '{codigo}' ya está prestado.")

            cursor = conexion.execute(
                SQL_INSERTAR_PRESTAMO,
                {
                    "codigo_equipo": codigo,
                    "solicitante_id": id_solicitante,
                    "solicitante_nombre": nombre_solicitante,
                    "fecha_prestamo": fecha,
                },
            )
            conexion.execute(SQL_MARCAR_EQUIPO_PRESTADO, {"codigo_equipo": codigo})
            conexion.commit()

            return {
                "id_prestamo": cursor.lastrowid,
                "codigo_equipo": codigo,
                "solicitante_id": id_solicitante,
                "solicitante_nombre": nombre_solicitante,
                "fecha_prestamo": fecha,
                "fecha_devolucion": None,
                "estado_prestamo": ESTADO_PRESTAMO_ACTIVO,
            }
        except Exception:
            conexion.rollback()
            raise
    finally:
        conexion.close()
