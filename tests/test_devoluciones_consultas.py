import sqlite3

import pytest

from src.equipos import (
    consultar_disponibles,
    consultar_historial,
    consultar_historial_prestamos,
    consultar_prestamos,
    consultar_prestamos_activos,
    devolver_prestamo,
    inicializar_bd,
    registrar_devolucion,
    registrar_equipo,
    registrar_prestamo,
)


@pytest.fixture
def ruta_db(tmp_path) -> str:
    """Base SQLite aislada para cada prueba."""
    return str(tmp_path / "integral.db")


def prestar_equipo(ruta_db: str) -> dict:
    """Registra un equipo y crea un préstamo sintético."""
    registrar_equipo("EQ-01", "computador", "PC ficticio de prueba", ruta_db)
    return registrar_prestamo(
        "EQ-01",
        "EST-101",
        "José D'Marco Peña",
        "2026-11-26",
        ruta_db,
    )


def test_inicializar_bd_crea_tablas_indices_y_plantilla_vacia(ruta_db):
    inicializar_bd(ruta_db)

    conexion = sqlite3.connect(ruta_db)
    try:
        tablas = {
            fila[0]
            for fila in conexion.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        indices = {
            fila[0]
            for fila in conexion.execute(
                "SELECT name FROM sqlite_master WHERE type = 'index'"
            )
        }
    finally:
        conexion.close()

    assert {"equipo", "prestamo"} <= tablas
    assert {"idx_prestamo_codigo", "idx_prestamo_estado"} <= indices


def test_registrar_devolucion_libera_el_equipo_y_actualiza_historial(ruta_db):
    prestamo = prestar_equipo(ruta_db)

    devuelto = registrar_devolucion("  eq-01 ", "2026-11-27", ruta_db)

    assert devuelto["id_prestamo"] == prestamo["id_prestamo"]
    assert devuelto["fecha_devolucion"] == "2026-11-27"
    assert devuelto["estado_prestamo"] == "devuelto"
    assert consultar_prestamos_activos(ruta_db) == []
    assert [
        equipo["codigo_equipo"] for equipo in consultar_disponibles(ruta_db)
    ] == ["EQ-01"]
    assert consultar_prestamos(ruta_db, "EQ-01")[0]["estado_prestamo"] == "devuelto"


def test_devolver_prestamo_por_id_funciona(ruta_db):
    prestamo = prestar_equipo(ruta_db)

    devuelto = devolver_prestamo(
        prestamo["id_prestamo"], "2026-11-27", ruta_db
    )

    assert devuelto["codigo_equipo"] == "EQ-01"
    assert devuelto["estado_prestamo"] == "devuelto"


def test_devolver_prestamo_rechaza_id_inexistente(ruta_db):
    with pytest.raises(ValueError, match="no existe"):
        devolver_prestamo(999, "2026-11-27", ruta_db)


def test_segunda_devolucion_por_id_rechaza_sin_cambiar_historial(ruta_db):
    prestamo = prestar_equipo(ruta_db)
    devolver_prestamo(prestamo["id_prestamo"], "2026-11-27", ruta_db)

    with pytest.raises(ValueError, match="no tiene estado activo"):
        devolver_prestamo(prestamo["id_prestamo"], "2026-11-28", ruta_db)

    historial = consultar_prestamos(ruta_db)
    assert len(historial) == 1
    assert historial[0]["fecha_devolucion"] == "2026-11-27"


def test_aliases_de_historial_devuelven_el_mismo_conjunto(ruta_db):
    prestar_equipo(ruta_db)

    completo = consultar_prestamos(ruta_db)

    assert consultar_historial_prestamos(ruta_db) == completo
    assert consultar_historial(ruta_db) == completo


@pytest.mark.parametrize(
    "codigo,fecha,fragmento",
    [
        ("", "2026-11-27", "codigo_equipo"),
        ("EQ-01", "", "fecha_devolucion"),
        (None, "2026-11-27", "codigo_equipo"),
        ("EQ-01", None, "fecha_devolucion"),
    ],
)
def test_registrar_devolucion_rechaza_entradas_invalidas(
    ruta_db, codigo, fecha, fragmento
):
    with pytest.raises(ValueError, match=fragmento):
        registrar_devolucion(codigo, fecha, ruta_db)


def test_registrar_devolucion_rechaza_equipo_sin_prestamo_activo(ruta_db):
    registrar_equipo("EQ-02", "tableta", "Tableta ficticia", ruta_db)

    with pytest.raises(ValueError, match="no tiene un préstamo activo"):
        registrar_devolucion("EQ-02", "2026-11-27", ruta_db)


def test_segunda_devolucion_es_rechazada_sin_modificar_el_historial(ruta_db):
    prestar_equipo(ruta_db)
    registrar_devolucion("EQ-01", "2026-11-27", ruta_db)

    with pytest.raises(ValueError, match="no tiene un préstamo activo"):
        registrar_devolucion("eq-01", "2026-11-28", ruta_db)

    historial = consultar_prestamos(ruta_db)
    assert len(historial) == 1
    assert historial[0]["fecha_devolucion"] == "2026-11-27"


def test_consultar_prestamos_activos_devuelve_solo_activos(ruta_db):
    prestar_equipo(ruta_db)
    registrar_devolucion("EQ-01", "2026-11-27", ruta_db)

    registrar_equipo("EQ-02", "proyector", "Proyector ficticio", ruta_db)
    registrar_prestamo(
        "EQ-02", "EST-102", "María Peña", "2026-11-27", ruta_db
    )

    activos = consultar_prestamos_activos(ruta_db)
    assert [prestamo["codigo_equipo"] for prestamo in activos] == ["EQ-02"]


def test_consultar_prestamos_por_equipo_no_confunde_codigos(ruta_db):
    prestar_equipo(ruta_db)
    registrar_devolucion("EQ-01", "2026-11-27", ruta_db)
    registrar_equipo("EQ-10", "tableta", "Tableta ficticia", ruta_db)

    assert [p["codigo_equipo"] for p in consultar_prestamos(ruta_db, "eq-01")] == [
        "EQ-01"
    ]
    assert consultar_prestamos(ruta_db, "EQ-10") == []


@pytest.mark.parametrize("id_prestamo", [None, "1", 0, -1, True])
def test_devolver_prestamo_rechaza_id_invalido(ruta_db, id_prestamo):
    with pytest.raises(ValueError):
        devolver_prestamo(id_prestamo, "2026-11-27", ruta_db)


def test_prestamo_y_devolucion_con_inyeccion_solo_guardan_texto(ruta_db):
    registrar_equipo("EQ-20", "tableta", "Tableta segura", ruta_db)
    prestamo = registrar_prestamo(
        "EQ-20",
        "EST-'; DROP TABLE prestamo; --",
        "D'Marco Peña",
        "2026-11-26",
        ruta_db,
    )

    devuelto = registrar_devolucion(
        "EQ-20",
        "2026-11-27'; DELETE FROM prestamo; --",
        ruta_db,
    )

    historial = consultar_prestamos(ruta_db)
    assert len(historial) == 1
    assert historial[0]["solicitante_id"] == prestamo["solicitante_id"]
    assert devuelto["fecha_devolucion"] == (
        "2026-11-27'; DELETE FROM prestamo; --"
    )
