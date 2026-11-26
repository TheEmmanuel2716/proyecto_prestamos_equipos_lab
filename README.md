# Préstamos de equipos de laboratorio

## 1. Qué es

Sistema monolítico en Python para gestionar el inventario y los préstamos de equipos (computadores, proyectores y tabletas) de laboratorios de informática. El proyecto documenta y prueba las reglas de negocio del sistema.

**Alcance del MVP:**

1. Registrar equipos.
2. Consultar equipos disponibles.
3. Registrar préstamos (validando que el equipo esté disponible).
4. Procesar devoluciones (liberando el equipo).

**Estado actual:** solo está implementada la historia **HU-01 (registrar equipos)**. Las demás historias del MVP están pendientes.

**Fuera de alcance:** aplicación móvil, notificaciones, integración con sistemas externos, gestión avanzada de usuarios o roles, multas, fechas de vencimiento, reservas y estados adicionales como "en mantenimiento".

Todos los datos de equipos y solicitantes son **ficticios** (RNF-06). El sistema no maneja contraseñas ni claves.

## 2. Requisitos

- **Python:** 3.10 o superior (desarrollado y probado con Python 3.14).
- **SQLite:** viene incluido en la librería estándar de Python (módulo `sqlite3`); no requiere instalación aparte.
- **Sistema operativo:** desarrollado y probado en Linux. No se probó en Windows ni macOS.

## 3. Instalación

```bash
git clone https://github.com/TheEmmanuel2716/proyecto_prestamos_equipos_lab.git
cd proyecto_prestamos_equipos_lab

python3 -m venv .venv
source .venv/bin/activate          # En Windows: .venv\Scripts\activate

pip install -r requirements-dev.txt
```

- `requirements.txt` contiene lo necesario para ejecutar las pruebas (`pytest`).
- `requirements-dev.txt` agrega las herramientas de desarrollo (`ruff` y `pip-audit`).
- Todas las versiones están fijadas con `==`.

No se necesita un archivo `.env`: el proyecto no usa claves. El archivo `.env.example` solo muestra el formato de ejemplo.

## 4. Ejecución

El sistema **todavía no tiene interfaz ni servidor web** (Flask forma parte del diseño, pero no se ha implementado). Por ahora se usa la función de negocio desde Python:

```bash
python -c "from src.equipos import registrar_equipo; print(registrar_equipo('EQ-01', 'computador', 'PC ficticio'))"
```

Salida esperada:

```
{'codigo_equipo': 'EQ-01', 'tipo': 'computador', 'descripcion': 'PC ficticio', 'estado': 'disponible'}
```

Esto crea el archivo `laboratorio.db` en la carpeta actual (está en `.gitignore`). Si se ejecuta dos veces, la segunda lanza `ValueError` porque el equipo ya está registrado.

## 5. Pruebas

```bash
python -m pytest -v          # 19 pruebas
ruff check                   # linter (reglas E, F, B, S; configurado en pyproject.toml)
pip-audit -r requirements.txt   # auditoría de dependencias
```

## 6. Estructura

```
proyecto_prestamos_equipos_lab/
├── src/
│   ├── __init__.py
│   └── equipos.py                    # Lógica de negocio y persistencia SQLite (HU-01)
├── tests/
│   ├── test_registrar_equipo.py      # Pruebas de HU-01 (normales, límite y error)
│   ├── test_seguridad_equipo.py      # Pruebas de abuso: inyección SQL
│   └── test_validacion_entradas.py   # Pruebas de abuso: datos que no son texto
├── .env.example                      # Ejemplo de variables (sin valores reales)
├── .gitignore
├── LICENSE
├── README.md
├── bitacora_ia.md                    # Registro del uso de IA
├── pyproject.toml                    # Configuración de ruff
├── requirements.txt
├── requirements-dev.txt
└── revision_seguridad.md             # Informe de revisión de código y seguridad
```

## 7. Uso de IA

Se usó **Claude** como asistente durante todo el proyecto: para redactar el contrato de la función, proponer las pruebas antes de implementar (TDD), implementar y refactorizar `registrar_equipo`, y realizar una revisión de código y seguridad. Cada sugerencia fue revisada y verificada con `pytest` y `ruff` antes de aceptarse. El detalle (prompts, decisiones, verificaciones y commits) está en [`bitacora_ia.md`](bitacora_ia.md), y los hallazgos de la revisión en [`revision_seguridad.md`](revision_seguridad.md).

## 8. Autor y licencia

**Autor:** Emmanuel Steven González Muñoz. Proyecto del seminario *Inteligencia Artificial Aplicada al Ciclo de Vida del Software*.

**Licencia:** MIT (ver [`LICENSE`](LICENSE)).

---

## Funcionalidad de la semana 5

### HU-01. Registrar equipos (Prioridad: Must)

**Historia:** Como responsable del laboratorio, quiero registrar los equipos con su información básica, para mantener un inventario de los recursos disponibles.

**Criterios de aceptación:**

- **Positivo:** Dado que ingreso un identificador y los datos requeridos de un equipo que no existe, cuando guardo el registro, entonces el equipo queda almacenado y aparece en el listado.
- **Error:** Dado que intento registrar un equipo usando un identificador que ya está registrado, cuando guardo, entonces el sistema rechaza el registro duplicado e informa el motivo.

> **Nota:** el listado de equipos corresponde a HU-02 y aún no está implementado. Por ahora, que el equipo "queda almacenado" se verifica leyendo la tabla `equipo` de SQLite en las pruebas.

### Contrato de la función

```python
def registrar_equipo(
    codigo_equipo: str,
    tipo: str,
    descripcion: str,
    ruta_db: str = RUTA_DB_POR_DEFECTO,
) -> Equipo:
```

**Módulo:** `src/equipos.py`

**Parámetros:**

| Parámetro | Tipo | Descripción |
|---|---|---|
| `codigo_equipo` | `str` | Identificador único del equipo (ej. `"EQ-01"`). |
| `tipo` | `str` | Uno de: `"computador"`, `"proyector"`, `"tableta"`. |
| `descripcion` | `str` | Información básica del equipo (no vacía). |
| `ruta_db` | `str` | Ruta del archivo SQLite. Opcional; permite que las pruebas usen una base temporal. |

**Retorna:** un `Equipo` (un `TypedDict`, que en ejecución es un `dict`) con las claves `codigo_equipo`, `tipo`, `descripcion` y `estado`. El estado inicial siempre es `"disponible"`.

**Validaciones y excepciones (`ValueError` con mensaje claro):**

- `codigo_equipo`, `tipo` o `descripcion` vacíos, solo con espacios, o que no sean texto (por ejemplo `None` o un número).
- `tipo` fuera de los tres valores permitidos.
- `codigo_equipo` ya registrado.

**Supuestos:**

- Si la base o la tabla `equipo` no existen, la función las crea. Si la validación falla, no se crea la base.
- El equipo se guarda en SQLite y persiste al reiniciar (RNF-03).
- Todas las consultas usan parámetros, nunca texto armado con datos del usuario.
- Todos los datos son ficticios (RNF-06).

**Casos límite:**

- Espacios al inicio o final en `codigo_equipo`, `tipo` o `descripcion` se eliminan antes de validar y guardar.
- El código se normaliza a mayúsculas: `"eq-01"` y `"EQ-01"` son el mismo equipo.
- El `tipo` se normaliza a minúsculas: `"Computador"` es válido.
- Registrar un equipo duplicado no modifica el original.
- Un texto con SQL malicioso se guarda como texto y no se ejecuta.

**Ejemplos:**

| Entrada | Salida |
|---|---|
| `registrar_equipo("EQ-01", "computador", "PC Dell ficticio")` | `{"codigo_equipo": "EQ-01", "tipo": "computador", "descripcion": "PC Dell ficticio", "estado": "disponible"}` |
| `registrar_equipo("  eq-02 ", "Proyector", "  Epson ficticio ")` | `{"codigo_equipo": "EQ-02", "tipo": "proyector", "descripcion": "Epson ficticio", "estado": "disponible"}` |
| `registrar_equipo("EQ-01", "tableta", "Otra tableta")` (ya existe) | `ValueError`: el código ya está registrado |
| `registrar_equipo("EQ-03", "impresora", "HP ficticia")` | `ValueError`: tipo no permitido |
| `registrar_equipo(None, "computador", "PC ficticio")` | `ValueError`: el campo codigo_equipo es obligatorio |

### Cómo ejecutar las pruebas

```bash
python -m pytest -v
```
