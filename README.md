## Funcionalidad de la semana 5

### HU-01. Registrar equipos (Prioridad: Must)

**Historia:** Como responsable del laboratorio, quiero registrar los equipos con su información básica, para mantener un inventario de los recursos disponibles.

**Criterios de aceptación:**

- **Positivo:** Dado que ingreso un identificador y los datos requeridos de un equipo que no existe, cuando guardo el registro, entonces el equipo queda almacenado y aparece en el listado.
- **Error:** Dado que intento registrar un equipo usando un identificador que ya está registrado, cuando guardo, entonces el sistema rechaza el registro duplicado e informa el motivo.

### Contrato de la función

```python
def registrar_equipo(
    codigo_equipo: str,
    tipo: str,
    descripcion: str,
    ruta_db: str = RUTA_DB_POR_DEFECTO,
) -> dict:
```

**Módulo:** `src/equipos.py`

**Parámetros:**
| Parámetro | Tipo | Descripción |
|---|---|---|
| `codigo_equipo` | `str` | Identificador único del equipo (ej. `"EQ-01"`). |
| `tipo` | `str` | Uno de: `"computador"`, `"proyector"`, `"tableta"`. |
| `descripcion` | `str` | Información básica del equipo (no vacía). |
| `ruta_db` | `str` | Ruta del archivo SQLite. Opcional; permite que las pruebas usen una base temporal. |

**Retorna:** un `dict` con las claves `codigo_equipo`, `tipo`, `descripcion` y `estado`. El estado inicial siempre es `"disponible"`.

**Validaciones y excepciones (`ValueError` con mensaje claro):**

- `codigo_equipo` o `descripcion` vacíos o solo con espacios.
- `tipo` fuera de los tres valores permitidos.
- `codigo_equipo` ya registrado.

**Supuestos:**

- Si la base o la tabla `equipo` no existen, la función las crea.
- El equipo se guarda en SQLite y persiste al reiniciar (RNF-03).
- Todos los datos son ficticios (RNF-06).

**Casos límite:**

- Espacios al inicio o final en `codigo_equipo`, `tipo` o `descripcion` se eliminan antes de validar y guardar.
- El código se normaliza a mayúsculas: `"eq-01"` y `"EQ-01"` son el mismo equipo.
- El `tipo` se normaliza a minúsculas: `"Computador"` es válido.
- Registrar un equipo duplicado no modifica el original.

**Ejemplos:**

| Entrada                                                            | Salida                                                                                                        |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------- |
| `registrar_equipo("EQ-01", "computador", "PC Dell ficticio")`      | `{"codigo_equipo": "EQ-01", "tipo": "computador", "descripcion": "PC Dell ficticio", "estado": "disponible"}` |
| `registrar_equipo("  eq-02 ", "Proyector", "  Epson ficticio ")`   | `{"codigo_equipo": "EQ-02", "tipo": "proyector", "descripcion": "Epson ficticio", "estado": "disponible"}`    |
| `registrar_equipo("EQ-01", "tableta", "Otra tableta")` (ya existe) | `ValueError`: el código ya está registrado                                                                    |
| `registrar_equipo("EQ-03", "impresora", "HP ficticia")`            | `ValueError`: tipo no permitido                                                                               |

### Cómo ejecutar las pruebas

```bash
python -m pytest -v
```
