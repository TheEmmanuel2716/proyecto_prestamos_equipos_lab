# Préstamos de equipos de laboratorio

Sistema monolítico en Python con SQLite para registrar equipos, consultar
disponibilidad, crear préstamos, procesar devoluciones y consultar el historial.
Autor: Emmanuel Steven González Muñoz.

## 1. Estado funcional

El alcance implementado cubre el ciclo completo:

- Registrar equipos con código único, tipo permitido y descripción.
- Consultar equipos disponibles.
- Registrar préstamos activos verificando existencia y disponibilidad.
- Registrar devoluciones por código de equipo o por identificador de préstamo.
- Consultar préstamos activos e historial completo o por equipo.
- Inicializar de forma aislada las tablas, índices y relaciones SQLite.

No contiene interfaz web, autenticación, roles, reservas, pagos ni integraciones
externas. Todos los datos de pruebas son sintéticos.

## 2. Arquitectura

- Python estándar y `sqlite3`; no se usan servicios externos ni frameworks.
- Tablas principales: `equipo` y `prestamo`.
- Llave foránea de `prestamo.codigo_equipo` hacia `equipo.codigo_equipo`.
- Índices por código de equipo y estado del préstamo.
- Consultas SQL parametrizadas y transacciones `commit`/`rollback`.
- Conexiones cerradas en bloques `try/finally`.
- Entradas obligatorias validadas con `ValueError`.

## 3. Funciones públicas

Todas las funciones aceptan `ruta_db` como último parámetro opcional. El valor
predeterminado es `laboratorio.db`.

| Función | Resultado |
|---|---|
| `registrar_equipo(codigo, tipo, descripcion, ruta_db)` | Registra un equipo disponible. |
| `consultar_disponibles(ruta_db)` | Lista equipos disponibles ordenados por código. |
| `registrar_prestamo(codigo, solicitante_id, nombre, fecha, ruta_db)` | Crea un préstamo activo y marca el equipo prestado. |
| `registrar_devolucion(codigo, fecha_devolucion, ruta_db)` | Devuelve el préstamo activo del equipo y lo libera. |
| `devolver_prestamo(id_prestamo, fecha_devolucion, ruta_db)` | Variante por identificador de préstamo. |
| `consultar_prestamos_activos(ruta_db)` | Lista préstamos con estado activo. |
| `consultar_prestamos(ruta_db, codigo_equipo=None)` | Lista todo el historial o el de un equipo. |
| `consultar_historial_prestamos(ruta_db, codigo_equipo=None)` | Alias descriptivo del historial. |
| `inicializar_bd(ruta_db)` | Crea tablas e índices sin duplicarlos. |

Ejemplo completo:

```python
from src.equipos import (
    consultar_prestamos_activos,
    registrar_devolucion,
    registrar_equipo,
    registrar_prestamo,
)

ruta = "laboratorio.db"
registrar_equipo("EQ-01", "computador", "PC ficticio", ruta)
registrar_prestamo("EQ-01", "EST-101", "José Peña", "2026-11-26", ruta)
registrar_devolucion("EQ-01", "2026-11-27", ruta)
print(consultar_prestamos_activos(ruta))
```

Los códigos se normalizan a mayúsculas, los tipos a minúsculas y los textos se
recortan en sus extremos. Los tipos válidos son `computador`, `proyector` y
`tableta`.

## 4. Requisitos e instalación

Python 3.10 o superior y SQLite incluidos en la biblioteca estándar.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

Las dependencias están fijadas. `requirements.txt` incluye pytest y
`requirements-dev.txt` agrega el linter y herramientas de auditoría.

## 5. Pruebas y calidad

```bash
python -m pytest -v
ruff check .
pip-audit -r requirements.txt
```

Las pruebas usan `tmp_path`, datos sintéticos y bases independientes. Cubren
particiones válidas e inválidas, límites, decisiones de préstamo, estados,
duplicados, transacciones, caracteres especiales, entradas no textuales y
intentos de inyección SQL.

## 6. Estructura

```text
proyecto_prestamos_equipos_lab/
├── src/
│   ├── __init__.py
│   └── equipos.py
├── tests/
│   ├── test_registrar_equipo.py
│   ├── test_reglas_negocio_s7.py
│   ├── test_seguridad_equipo.py
│   ├── test_validacion_entradas.py
│   └── test_devoluciones_consultas.py
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── README.md
├── registro_pruebas.md
├── bitacora_ia.md
├── revision_seguridad.md
├── informe_final_integrador.md
└── LICENSE
```

## 7. Seguridad e higiene

- Las entradas dinámicas se pasan por parámetros nombrados.
- Las operaciones de préstamo/devolución hacen `BEGIN`, `commit` o `rollback`.
- No existen secretos, cuentas reales ni credenciales en el repositorio.
- `.env`, `.venv/`, `.db`, `.sqlite3`, `.sqlite`, cachés y `__pycache__/`
  están ignorados.
- Los identificadores numéricos de préstamo se validan antes de consultar.

## 8. Documentación complementaria

- [`registro_pruebas.md`](registro_pruebas.md): técnicas, casos y límites.
- [`bitacora_ia.md`](bitacora_ia.md): decisiones y verificaciones.
- [`revision_seguridad.md`](revision_seguridad.md): hallazgos y pendientes.
- [`informe_final_integrador.md`](informe_final_integrador.md): síntesis, reflexión
  y evidencias para la entrega.

## Autor y licencia

Emmanuel Steven González Muñoz. Licencia MIT: [`LICENSE`](LICENSE).
