import sqlite3

import pytest

from src.equipos import registrar_equipo

CODIGO_MALICIOSO = "EQ-99'; DROP TABLE equipo; --"
DESCRIPCION_MALICIOSA = "x'); DELETE FROM equipo; --"
TIPO_MALICIOSO = "tableta'; DROP TABLE equipo; --"

def leer_codigos_y_descripciones(ruta_db: str) -> list[tuple]:
    """Lee la tabla equipo directamente, sin usar funciones del proyecto."""
    conexion = sqlite3.connect(ruta_db)
    try:
        return conexion.execute(
            "SELECT codigo_equipo, descripcion FROM equipo ORDER BY codigo_equipo"
        ).fetchall()
    finally:
        conexion.close()


def test_codigo_con_sql_malicioso_se_guarda_como_texto_y_no_se_ejecuta(tmp_path):
    ruta_db = str(tmp_path / "abuso.db")
    registrar_equipo("EQ-01", "computador", "PC ficticio", ruta_db)

    resultado = registrar_equipo(CODIGO_MALICIOSO, "tableta", "Tab ficticia", ruta_db)

    filas = leer_codigos_y_descripciones(ruta_db)
    codigos = [codigo for codigo, _ in filas]
    assert len(filas) == 2
    assert "EQ-01" in codigos
    assert resultado["codigo_equipo"] in codigos


def test_descripcion_con_sql_malicioso_no_borra_equipos_existentes(tmp_path):
    ruta_db = str(tmp_path / "abuso.db")
    registrar_equipo("EQ-01", "computador", "PC ficticio", ruta_db)

    registrar_equipo("EQ-02", "proyector", DESCRIPCION_MALICIOSA, ruta_db)

    assert leer_codigos_y_descripciones(ruta_db) == [
        ("EQ-01", "PC ficticio"),
        ("EQ-02", DESCRIPCION_MALICIOSA),
    ]

def test_tipo_con_sql_malicioso_es_rechazado_y_no_toca_la_tabla(tmp_path):
    ruta_db = str(tmp_path / "abuso.db")
    registrar_equipo("EQ-01", "computador", "PC ficticio", ruta_db)

    with pytest.raises(ValueError, match="tipo"):
        registrar_equipo("EQ-02", TIPO_MALICIOSO, "Tab ficticia", ruta_db)

    assert leer_codigos_y_descripciones(ruta_db) == [("EQ-01", "PC ficticio")]
