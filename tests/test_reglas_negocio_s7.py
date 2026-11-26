import sqlite3

import pytest

from src.equipos import consultar_disponibles, registrar_equipo, registrar_prestamo


@pytest.fixture
def ruta_db(tmp_path) -> str:
    """Base de datos SQLite temporal por prueba."""
    return str(tmp_path / "lab_s7.db")


@pytest.fixture
def datos_sinteticos_s7() -> dict:
    """Datos sintéticos locales (incluyendo tildes, ñ y apóstrofo)."""
    return {
        "equipos": [
            ("EQ-01", "computador", "PC portátil sala 3", "disponible"),
            ("EQ-02", "proyector", "Proyector aula 5", "disponible"),
            ("EQ-03", "tableta", "Tableta de D'Marco, aula Peña", "disponible"),
        ],
        "solicitantes": [
            ("EST-101", "José Muñoz", "2026-11-26"),
            ("EST-102", "María Peña", "2026-11-26"),
            ("EST-103", "D'Marco Peña", "2026-11-26"),
        ],
    }


def _marcar_prestado(ruta_db: str, codigo_equipo: str) -> None:
    """Auxiliar de prueba para simular un equipo ya prestado."""
    conexion = sqlite3.connect(ruta_db)
    try:
        conexion.execute(
            "UPDATE equipo SET estado = 'prestado' WHERE codigo_equipo = ?",
            (codigo_equipo,),
        )
        conexion.commit()
    finally:
        conexion.close()


# --- Regla 1: registrar_equipo ---


@pytest.mark.parametrize(
    "codigo, tipo, descripcion, esperado_codigo, esperado_tipo, esperado_desc",
    [
        # Caso normal: computador válido
        (
            "EQ-01",
            "computador",
            "PC portátil sala 3",
            "EQ-01",
            "computador",
            "PC portátil sala 3",
        ),
        # Caso normal: proyector válido
        (
            "EQ-02",
            "proyector",
            "Proyector aula 5",
            "EQ-02",
            "proyector",
            "Proyector aula 5",
        ),
        # Caso normal: tableta válida
        (
            "EQ-03",
            "tableta",
            "Tableta de préstamo",
            "EQ-03",
            "tableta",
            "Tableta de préstamo",
        ),
        # Normalización: tipo en mayúsculas y con espacios
        (
            "EQ-04",
            "  Tableta ",
            "Tableta 10 pulgadas",
            "EQ-04",
            "tableta",
            "Tableta 10 pulgadas",
        ),
        # Normalización: código con espacios en extremos
        (
            "  EQ-05  ",
            "computador",
            "PC de escritorio",
            "EQ-05",
            "computador",
            "PC de escritorio",
        ),
        # Normalización: código en minúsculas
        (
            "eq-07",
            "proyector",
            "Proyector portátil",
            "EQ-07",
            "proyector",
            "Proyector portátil",
        ),
        # Caracteres difíciles: tilde, ñ y apóstrofo
        (
            "EQ-08",
            "tableta",
            "Tableta de D'Marco, aula Peña",
            "EQ-08",
            "tableta",
            "Tableta de D'Marco, aula Peña",
        ),
        # Límite: longitud mínima de código (1 carácter)
        ("A", "computador", "PC", "A", "computador", "PC"),
        # Límite: longitud mínima de descripción (1 carácter)
        ("EQ-09", "computador", "x", "EQ-09", "computador", "x"),
    ],
)
def test_registrar_equipo_casos_validos_y_limites(
    ruta_db, codigo, tipo, descripcion, esperado_codigo, esperado_tipo, esperado_desc
):
    resultado = registrar_equipo(codigo, tipo, descripcion, ruta_db)
    assert resultado == {
        "codigo_equipo": esperado_codigo,
        "tipo": esperado_tipo,
        "descripcion": esperado_desc,
        "estado": "disponible",
    }


@pytest.mark.parametrize(
    "codigo, tipo, descripcion, fragmento_error",
    [
        # Inválido: código vacío
        ("", "computador", "PC", "obligatorio"),
        # Inválido: código solo espacios
        ("   ", "computador", "PC", "obligatorio"),
        # Inválido: código None
        (None, "computador", "PC", "obligatorio"),
        # Inválido: código numérico
        (123, "computador", "PC", "obligatorio"),
        # Inválido: tipo vacío
        ("EQ-10", "", "PC", "obligatorio"),
        # Inválido: tipo fuera de los permitidos
        ("EQ-10", "impresora", "HP", "tipo"),
        # Inválido: tipo None
        ("EQ-10", None, "PC", "obligatorio"),
        # Inválido: descripción vacía
        ("EQ-10", "computador", "", "obligatorio"),
        # Inválido: descripción solo espacios
        ("EQ-10", "computador", "    ", "obligatorio"),
        # Inválido: descripción None
        ("EQ-10", "computador", None, "obligatorio"),
    ],
)
def test_registrar_equipo_entradas_invalidas_lanzan_value_error(
    ruta_db, codigo, tipo, descripcion, fragmento_error
):
    with pytest.raises(ValueError, match=fragmento_error):
        registrar_equipo(codigo, tipo, descripcion, ruta_db)


def test_registrar_equipo_rechaza_duplicado_tras_normalizar(ruta_db):
    registrar_equipo("EQ-01", "computador", "PC original", ruta_db)
    with pytest.raises(ValueError, match="registrado"):
        registrar_equipo("  eq-01 ", "tableta", "Duplicado", ruta_db)


# --- Regla 2: consultar_disponibles ---


def test_consultar_disponibles_base_sin_equipos_retorna_vacio(ruta_db):
    assert consultar_disponibles(ruta_db) == []


def test_consultar_disponibles_ordena_y_filtra_prestados(ruta_db, datos_sinteticos_s7):
    for codigo, tipo, desc, _ in reversed(datos_sinteticos_s7["equipos"]):
        registrar_equipo(codigo, tipo, desc, ruta_db)
    _marcar_prestado(ruta_db, "EQ-02")

    disponibles = consultar_disponibles(ruta_db)
    assert [eq["codigo_equipo"] for eq in disponibles] == ["EQ-01", "EQ-03"]


def test_consultar_disponibles_todos_prestados_retorna_vacio(ruta_db):
    registrar_equipo("EQ-01", "computador", "PC 1", ruta_db)
    _marcar_prestado(ruta_db, "EQ-01")
    assert consultar_disponibles(ruta_db) == []


# --- Regla 3: registrar_prestamo ---


def test_registrar_prestamo_valido_cambia_estado_a_prestado(
    ruta_db, datos_sinteticos_s7
):
    registrar_equipo("EQ-01", "computador", "PC sala 1", ruta_db)
    sol_id, sol_nombre, fecha = datos_sinteticos_s7["solicitantes"][0]

    prestamo = registrar_prestamo("  eq-01 ", sol_id, sol_nombre, fecha, ruta_db)

    assert prestamo == {
        "id_prestamo": 1,
        "codigo_equipo": "EQ-01",
        "solicitante_id": sol_id,
        "solicitante_nombre": sol_nombre,
        "fecha_prestamo": fecha,
        "fecha_devolucion": None,
        "estado_prestamo": "activo",
    }
    assert [eq["codigo_equipo"] for eq in consultar_disponibles(ruta_db)] == []


@pytest.mark.parametrize(
    "codigo, sol_id, sol_nombre, fecha, preparar_equipo",
    [
        # R2: equipo existe y está disponible, pero falta solicitante
        ("EQ-01", "", "José Muñoz", "2026-11-26", "disponible"),
        # R3: equipo existe y ya está prestado, datos válidos
        ("EQ-01", "EST-102", "María Peña", "2026-11-26", "prestado"),
        # R4: equipo prestado y además falta fecha
        ("EQ-01", "EST-102", "María Peña", "", "prestado"),
        # R5: equipo inexistente, datos válidos
        ("EQ-99", "EST-101", "José Muñoz", "2026-11-26", None),
        # R6: equipo inexistente y falta nombre
        ("EQ-99", "EST-101", "", "2026-11-26", None),
    ],
)
def test_registrar_prestamo_reglas_de_rechazo(
    ruta_db, codigo, sol_id, sol_nombre, fecha, preparar_equipo
):
    if preparar_equipo is not None:
        registrar_equipo("EQ-01", "computador", "PC base", ruta_db)
        if preparar_equipo == "prestado":
            _marcar_prestado(ruta_db, "EQ-01")

    with pytest.raises(ValueError):
        registrar_prestamo(codigo, sol_id, sol_nombre, fecha, ruta_db)
