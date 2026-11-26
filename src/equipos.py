RUTA_DB_POR_DEFECTO = "laboratorio.db"


def registrar_equipo(
    codigo_equipo: str,
    tipo: str,
    descripcion: str,
    ruta_db: str = RUTA_DB_POR_DEFECTO,
) -> dict:
    raise NotImplementedError
