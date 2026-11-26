import sqlite3

import pytest

from src.equipos import registrar_equipo


@pytest.fixture
def ruta_db(tmp_path) -> str:
    """Base SQLite temporal, distinta para cada prueba."""
    return str(tmp_path / "prueba.db")


def leer_equipos(ruta_db: str) -> list[tuple]:
    """Lee la tabla equipo directamente, sin usar funciones del proyecto."""
    conexion = sqlite3.connect(ruta_db)
    try:
        return conexion.execute(
            "SELECT codigo_equipo, tipo, descripcion, estado FROM equipo"
        ).fetchall()
    finally:
        conexion.close()


# ---------- Casos normales ----------

def test_registrar_equipo_valido_retorna_dict_con_estado_disponible(ruta_db):
    resultado = registrar_equipo("EQ-01", "computador", "PC Dell ficticio", ruta_db)

    assert resultado == {
        "codigo_equipo": "EQ-01",
        "tipo": "computador",
        "descripcion": "PC Dell ficticio",
        "estado": "disponible",
    }


def test_registrar_equipo_valido_queda_guardado_en_sqlite(ruta_db):
    registrar_equipo("EQ-01", "computador", "PC Dell ficticio", ruta_db)

    assert leer_equipos(ruta_db) == [
        ("EQ-01", "computador", "PC Dell ficticio", "disponible")
    ]


@pytest.mark.parametrize("tipo", ["computador", "proyector", "tableta"])
def test_registrar_equipo_acepta_los_tres_tipos_permitidos(ruta_db, tipo):
    resultado = registrar_equipo("EQ-10", tipo, "Equipo ficticio", ruta_db)

    assert resultado["tipo"] == tipo


# ---------- Casos límite ----------

def test_registrar_equipo_elimina_espacios_y_normaliza_codigo_y_tipo(ruta_db):
    resultado = registrar_equipo(
        "  eq-02 ", "  Proyector ", "  Epson ficticio ", ruta_db
    )

    assert resultado == {
        "codigo_equipo": "EQ-02",
        "tipo": "proyector",
        "descripcion": "Epson ficticio",
        "estado": "disponible",
    }


def test_registrar_equipo_codigo_en_minusculas_duplica_el_existente(ruta_db):
    registrar_equipo("EQ-01", "computador", "PC ficticio", ruta_db)

    with pytest.raises(ValueError, match="registrado"):
        registrar_equipo("eq-01", "tableta", "Otra ficticia", ruta_db)


@pytest.mark.parametrize("codigo", ["", "   "])
def test_registrar_equipo_codigo_vacio_o_solo_espacios_falla(ruta_db, codigo):
    with pytest.raises(ValueError, match="obligatorio"):
        registrar_equipo(codigo, "computador", "PC ficticio", ruta_db)


def test_registrar_equipo_descripcion_solo_espacios_falla(ruta_db):
    with pytest.raises(ValueError, match="obligatorio"):
        registrar_equipo("EQ-03", "computador", "    ", ruta_db)


# ---------- Casos de error ----------

def test_registrar_equipo_duplicado_lanza_error_y_conserva_el_original(ruta_db):
    registrar_equipo("EQ-01", "computador", "PC original", ruta_db)

    with pytest.raises(ValueError, match="registrado"):
        registrar_equipo("EQ-01", "tableta", "Intento duplicado", ruta_db)

    assert leer_equipos(ruta_db) == [
        ("EQ-01", "computador", "PC original", "disponible")
    ]


def test_registrar_equipo_tipo_no_permitido_lanza_error_y_no_guarda(ruta_db):
    with pytest.raises(ValueError, match="tipo"):
        registrar_equipo("EQ-04", "impresora", "HP ficticia", ruta_db)

    # La tabla puede no existir si la validación ocurre antes de crear la base.
    try:
        assert leer_equipos(ruta_db) == []
    except sqlite3.OperationalError:
        pass
