import pytest

from src.equipos import registrar_equipo


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
