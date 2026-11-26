import sqlite3
from typing import TypedDict

RUTA_DB_POR_DEFECTO = "laboratorio.db"
TIPOS_PERMITIDOS = ("computador", "proyector", "tableta")
ESTADO_INICIAL = "disponible"
ESTADO_PRESTADO = "prestado"
ESTADO_PRESTAMO_ACTIVO = "activo"
ESTADO_PRESTAMO_DEVUELTO = "devuelto"
MENSAJE_CAMPO_OBLIGATORIO = "El campo {campo} es obligatorio."

SQL_CREAR_TABLA = """
CREATE TABLE IF NOT EXISTS equipo (
    codigo_equipo TEXT PRIMARY KEY,
    tipo          TEXT NOT NULL,
    descripcion   TEXT NOT NULL,
    estado        TEXT NOT NULL
        CHECK (estado IN ('disponible', 'prestado'))
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
        CHECK (estado_prestamo IN ('activo', 'devuelto')),
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

SQL_MARCAR_EQUIPO_DISPONIBLE = """
UPDATE equipo
SET estado = 'disponible'
WHERE codigo_equipo = :codigo_equipo
"""

SQL_MARCAR_PRESTAMO_DEVUELTO = """
UPDATE prestamo
SET fecha_devolucion = :fecha_devolucion,
    estado_prestamo = 'devuelto'
WHERE id_prestamo = :id_prestamo
  AND estado_prestamo = 'activo'
"""

SQL_BUSCAR_PRESTAMO_ACTIVO_POR_EQUIPO = """
SELECT id_prestamo, codigo_equipo, solicitante_id,
       solicitante_nombre, fecha_prestamo, fecha_devolucion,
       estado_prestamo
FROM prestamo
WHERE codigo_equipo = :codigo_equipo
  AND estado_prestamo = 'activo'
ORDER BY id_prestamo DESC
LIMIT 1
"""

SQL_BUSCAR_PRESTAMO_POR_ID = """
SELECT id_prestamo, codigo_equipo, solicitante_id,
       solicitante_nombre, fecha_prestamo, fecha_devolucion,
       estado_prestamo
FROM prestamo
WHERE id_prestamo = :id_prestamo
"""

SQL_CONSULTAR_PRESTAMOS_ACTIVOS = """
SELECT id_prestamo, codigo_equipo, solicitante_id,
       solicitante_nombre, fecha_prestamo, fecha_devolucion,
       estado_prestamo
FROM prestamo
WHERE estado_prestamo = 'activo'
ORDER BY id_prestamo ASC
"""

SQL_CONSULTAR_HISTORIAL = """
SELECT id_prestamo, codigo_equipo, solicitante_id,
       solicitante_nombre, fecha_prestamo, fecha_devolucion,
       estado_prestamo
FROM prestamo
ORDER BY id_prestamo ASC
"""

SQL_CONSULTAR_HISTORIAL_POR_EQUIPO = """
SELECT id_prestamo, codigo_equipo, solicitante_id,
       solicitante_nombre, fecha_prestamo, fecha_devolucion,
       estado_prestamo
FROM prestamo
WHERE codigo_equipo = :codigo_equipo
ORDER BY id_prestamo ASC
"""


class Equipo(TypedDict):
    """Datos de un equipo del inventario, tal como se guardan en SQLite."""

    codigo_equipo: str
    tipo: str
    descripcion: str
    estado: str


class Prestamo(TypedDict):
    """Datos completos de un préstamo almacenado en SQLite."""

    id_prestamo: int
    codigo_equipo: str
    solicitante_id: str
    solicitante_nombre: str
    fecha_prestamo: str
    fecha_devolucion: str | None
    estado_prestamo: str


def _limpiar_texto(valor: object) -> str:
    """Devuelve el texto sin espacios en los extremos.

    Si el valor no es texto (por ejemplo None o un número), devuelve ''
    para que se trate como un dato faltante.
    """
    return valor.strip() if isinstance(valor, str) else ""


def _validar_ruta_db(ruta_db: object) -> str:
    """Valida y devuelve la ruta SQLite usada por las operaciones públicas."""
    ruta = _limpiar_texto(ruta_db)
    if not ruta:
        raise ValueError(MENSAJE_CAMPO_OBLIGATORIO.format(campo="ruta_db"))
    return ruta


def inicializar_bd(ruta_db: str = RUTA_DB_POR_DEFECTO) -> None:
    """Crea de forma aislada las tablas, índices y relaciones del sistema."""
    ruta = _validar_ruta_db(ruta_db)
    conexion = sqlite3.connect(ruta)
    try:
        conexion.execute("PRAGMA foreign_keys = ON")
        conexion.execute(SQL_CREAR_TABLA)
        conexion.execute(SQL_CREAR_TABLA_PRESTAMO)
        conexion.execute(
            "CREATE INDEX IF NOT EXISTS idx_prestamo_codigo "
            "ON prestamo(codigo_equipo)"
        )
        conexion.execute(
            "CREATE INDEX IF NOT EXISTS idx_prestamo_estado "
            "ON prestamo(estado_prestamo)"
        )
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


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
    ruta = _validar_ruta_db(ruta_db)
    inicializar_bd(ruta)
    conexion = sqlite3.connect(ruta)
    try:
        conexion.execute("PRAGMA foreign_keys = ON")
        conexion.execute("BEGIN")
        try:
            conexion.execute(SQL_INSERTAR_EQUIPO, equipo)
        except sqlite3.IntegrityError:
            fila_existente = conexion.execute(
                SQL_BUSCAR_EQUIPO,
                {"codigo_equipo": equipo["codigo_equipo"]},
            ).fetchone()
            conexion.rollback()
            if fila_existente is not None:
                raise ValueError(
                    f"El equipo '{equipo['codigo_equipo']}' ya está registrado."
                ) from None
            raise
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
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
    ruta = _validar_ruta_db(ruta_db)
    inicializar_bd(ruta)
    conexion = sqlite3.connect(ruta)
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

    ruta = _validar_ruta_db(ruta_db)
    inicializar_bd(ruta)
    conexion = sqlite3.connect(ruta)
    try:
        conexion.execute("PRAGMA foreign_keys = ON")
        conexion.execute("BEGIN")

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


def _fila_a_prestamo(fila: tuple[object, ...]) -> Prestamo:
    """Convierte una fila SQLite completa a un diccionario de préstamo."""
    return {
        "id_prestamo": int(fila[0]),
        "codigo_equipo": str(fila[1]),
        "solicitante_id": str(fila[2]),
        "solicitante_nombre": str(fila[3]),
        "fecha_prestamo": str(fila[4]),
        "fecha_devolucion": fila[5] if fila[5] is None else str(fila[5]),
        "estado_prestamo": str(fila[6]),
    }


def registrar_devolucion(
    codigo_equipo: str,
    fecha_devolucion: str,
    ruta_db: str = RUTA_DB_POR_DEFECTO,
) -> Prestamo:
    """Devuelve el préstamo activo de un equipo y lo vuelve disponible."""
    codigo = _limpiar_texto(codigo_equipo).upper()
    fecha = _limpiar_texto(fecha_devolucion)
    if not codigo:
        raise ValueError(MENSAJE_CAMPO_OBLIGATORIO.format(campo="codigo_equipo"))
    if not fecha:
        raise ValueError(MENSAJE_CAMPO_OBLIGATORIO.format(campo="fecha_devolucion"))

    ruta = _validar_ruta_db(ruta_db)
    inicializar_bd(ruta)
    conexion = sqlite3.connect(ruta)
    try:
        conexion.execute("PRAGMA foreign_keys = ON")
        conexion.execute("BEGIN")
        fila_prestamo = conexion.execute(
            SQL_BUSCAR_PRESTAMO_ACTIVO_POR_EQUIPO,
            {"codigo_equipo": codigo},
        ).fetchone()
        if fila_prestamo is None:
            raise ValueError(
                f"El equipo '{codigo}' no tiene un préstamo activo."
            )

        id_prestamo = int(fila_prestamo[0])
        cursor = conexion.execute(
            SQL_MARCAR_PRESTAMO_DEVUELTO,
            {"id_prestamo": id_prestamo, "fecha_devolucion": fecha},
        )
        if cursor.rowcount != 1:
            raise ValueError(
                f"El equipo '{codigo}' no tiene un préstamo activo."
            )
        conexion.execute(
            SQL_MARCAR_EQUIPO_DISPONIBLE,
            {"codigo_equipo": codigo},
        )
        conexion.commit()
        devuelto = _fila_a_prestamo(fila_prestamo)
        devuelto["fecha_devolucion"] = fecha
        devuelto["estado_prestamo"] = ESTADO_PRESTAMO_DEVUELTO
        return devuelto
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def devolver_prestamo(
    id_prestamo: int,
    fecha_devolucion: str,
    ruta_db: str = RUTA_DB_POR_DEFECTO,
) -> Prestamo:
    """Devuelve un préstamo identificado por su clave primaria."""
    if isinstance(id_prestamo, bool) or not isinstance(id_prestamo, int):
        raise ValueError(MENSAJE_CAMPO_OBLIGATORIO.format(campo="id_prestamo"))
    if id_prestamo <= 0:
        raise ValueError("El id_prestamo debe ser un entero positivo.")
    fecha = _limpiar_texto(fecha_devolucion)
    if not fecha:
        raise ValueError(MENSAJE_CAMPO_OBLIGATORIO.format(campo="fecha_devolucion"))

    ruta = _validar_ruta_db(ruta_db)
    inicializar_bd(ruta)
    conexion = sqlite3.connect(ruta)
    try:
        conexion.execute("PRAGMA foreign_keys = ON")
        conexion.execute("BEGIN")
        fila = conexion.execute(
            SQL_BUSCAR_PRESTAMO_POR_ID,
            {"id_prestamo": id_prestamo},
        ).fetchone()
        if fila is None:
            raise ValueError(f"El préstamo '{id_prestamo}' no existe.")
        if str(fila[6]) != ESTADO_PRESTAMO_ACTIVO:
            raise ValueError(
                f"El préstamo '{id_prestamo}' no tiene estado activo."
            )

        codigo = str(fila[1])
        cursor = conexion.execute(
            SQL_MARCAR_PRESTAMO_DEVUELTO,
            {"id_prestamo": id_prestamo, "fecha_devolucion": fecha},
        )
        if cursor.rowcount != 1:
            raise ValueError(
                f"El préstamo '{id_prestamo}' no tiene estado activo."
            )
        conexion.execute(
            SQL_MARCAR_EQUIPO_DISPONIBLE,
            {"codigo_equipo": codigo},
        )
        conexion.commit()
        devuelto = _fila_a_prestamo(fila)
        devuelto["fecha_devolucion"] = fecha
        devuelto["estado_prestamo"] = ESTADO_PRESTAMO_DEVUELTO
        return devuelto
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def consultar_prestamos_activos(
    ruta_db: str = RUTA_DB_POR_DEFECTO,
) -> list[Prestamo]:
    """Retorna los préstamos activos ordenados por identificador."""
    ruta = _validar_ruta_db(ruta_db)
    inicializar_bd(ruta)
    conexion = sqlite3.connect(ruta)
    try:
        filas = conexion.execute(SQL_CONSULTAR_PRESTAMOS_ACTIVOS).fetchall()
        return [_fila_a_prestamo(fila) for fila in filas]
    finally:
        conexion.close()


def consultar_prestamos(
    ruta_db: str = RUTA_DB_POR_DEFECTO,
    codigo_equipo: str | None = None,
) -> list[Prestamo]:
    """Retorna el historial completo o el historial de un equipo."""
    ruta = _validar_ruta_db(ruta_db)
    inicializar_bd(ruta)
    conexion = sqlite3.connect(ruta)
    try:
        if codigo_equipo is None:
            filas = conexion.execute(SQL_CONSULTAR_HISTORIAL).fetchall()
        else:
            codigo = _limpiar_texto(codigo_equipo).upper()
            if not codigo:
                raise ValueError(
                    MENSAJE_CAMPO_OBLIGATORIO.format(campo="codigo_equipo")
                )
            filas = conexion.execute(
                SQL_CONSULTAR_HISTORIAL_POR_EQUIPO,
                {"codigo_equipo": codigo},
            ).fetchall()
        return [_fila_a_prestamo(fila) for fila in filas]
    finally:
        conexion.close()


def consultar_historial_prestamos(
    ruta_db: str = RUTA_DB_POR_DEFECTO,
    codigo_equipo: str | None = None,
) -> list[Prestamo]:
    """Alias explícito para consultar el historial de préstamos."""
    return consultar_prestamos(ruta_db, codigo_equipo)


def consultar_historial(
    ruta_db: str = RUTA_DB_POR_DEFECTO,
    codigo_equipo: str | None = None,
) -> list[Prestamo]:
    """Alias corto para consultar el historial de préstamos."""
    return consultar_prestamos(ruta_db, codigo_equipo)
