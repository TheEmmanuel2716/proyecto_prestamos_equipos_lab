import sqlite3

RUTA_DB_POR_DEFECTO = "laboratorio.db"
TIPOS_PERMITIDOS = ("computador", "proyector", "tableta")
ESTADO_INICIAL = "disponible"

SQL_CREAR_TABLA = """
CREATE TABLE IF NOT EXISTS equipo (
    codigo_equipo TEXT PRIMARY KEY,
    tipo          TEXT NOT NULL,
    descripcion   TEXT NOT NULL,
    estado        TEXT NOT NULL
)
"""

SQL_INSERTAR_EQUIPO = """
INSERT INTO equipo (codigo_equipo, tipo, descripcion, estado)
VALUES (:codigo_equipo, :tipo, :descripcion, :estado)
"""


def _normalizar_y_validar(codigo_equipo: str, tipo: str, descripcion: str) -> dict:
    """Limpia los datos de entrada, valida las reglas y arma el equipo.

    Raises:
        ValueError: si falta el código o la descripción, o si el tipo no es permitido.
    """
    codigo = codigo_equipo.strip().upper()
    tipo_normalizado = tipo.strip().lower()
    descripcion_limpia = descripcion.strip()

    if not codigo:
        raise ValueError("El campo codigo_equipo es obligatorio.")
    if not descripcion_limpia:
        raise ValueError("El campo descripcion es obligatorio.")
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


def _guardar_equipo(equipo: dict, ruta_db: str) -> None:
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
) -> dict:
    """Registra un equipo nuevo en el inventario con estado 'disponible'.

    Args:
        codigo_equipo: Identificador único del equipo (ej. "EQ-01").
            Se eliminan espacios y se convierte a mayúsculas.
        tipo: "computador", "proyector" o "tableta".
            Se eliminan espacios y se convierte a minúsculas.
        descripcion: Información básica del equipo (no vacía).
        ruta_db: Ruta del archivo SQLite donde se guarda el equipo.

    Returns:
        dict con las claves codigo_equipo, tipo, descripcion y estado.

    Raises:
        ValueError: si falta el código o la descripción, si el tipo no es
            permitido o si el código ya está registrado.
    """
    equipo = _normalizar_y_validar(codigo_equipo, tipo, descripcion)
    _guardar_equipo(equipo, ruta_db)
    return equipo
