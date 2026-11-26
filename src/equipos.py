import sqlite3
from typing import TypedDict

RUTA_DB_POR_DEFECTO = "laboratorio.db"
TIPOS_PERMITIDOS = ("computador", "proyector", "tableta")
ESTADO_INICIAL = "disponible"
MENSAJE_CAMPO_OBLIGATORIO = "El campo {campo} es obligatorio."

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
