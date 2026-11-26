import pytest

from src.equipos import registrar_equipo, registrar_prestamo


@pytest.mark.parametrize(
    "codigo, tipo, descripcion",
    [
        (None, "computador", "PC ficticio"),
        ("EQ-01", None, "PC ficticio"),
        ("EQ-01", "computador", None),
        (123, "computador", "PC ficticio"),
    ],
)
def test_datos_que_no_son_texto_lanzan_value_error_y_no_crean_la_base(
    tmp_path, codigo, tipo, descripcion
):
    ruta_db = tmp_path / "entradas.db"

    with pytest.raises(ValueError, match="obligatorio"):
        registrar_equipo(codigo, tipo, descripcion, str(ruta_db))

    assert not ruta_db.exists()


@pytest.mark.parametrize(
    "codigo,solicitante_id,nombre,fecha,fragmento",
    [
        (None, "EST-101", "José Muñoz", "2026-11-26", "codigo_equipo"),
        ("EQ-01", None, "José Muñoz", "2026-11-26", "solicitante_id"),
        ("EQ-01", "EST-101", 123, "2026-11-26", "solicitante_nombre"),
        ("EQ-01", "EST-101", "José Muñoz", None, "fecha_prestamo"),
    ],
)
def test_prestamo_rechaza_datos_no_textuales(
    tmp_path, codigo, solicitante_id, nombre, fecha, fragmento
):
    ruta_db = str(tmp_path / "prestamo-entrada.db")

    with pytest.raises(ValueError, match=fragmento):
        registrar_prestamo(codigo, solicitante_id, nombre, fecha, ruta_db)

    assert not (tmp_path / "prestamo-entrada.db").exists()
