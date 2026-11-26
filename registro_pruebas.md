# Registro de pruebas: tabla de casos y pruebas de la IA

- **Proyecto:** Documentar y probar las reglas de negocio de un sistema monolítico para la gestión de préstamos de equipos en laboratorios de informática
- **Estudiante:** Emmanuel Steven González Muñoz
- **Fecha:** 2026-11-26

---

## 1. Tabla de casos

### Regla 1: `registrar_equipo` — registra un equipo nuevo disponible y rechaza duplicados o datos faltantes

**Regla completa (el oráculo):** Registra un equipo nuevo con estado inicial `disponible`. Si `codigo_equipo` ya existe o faltan datos obligatorios (`codigo_equipo`, `tipo`, `descripcion` vacíos, solo espacios, inválidos o no texto), rechaza el registro lanzando `ValueError`.

| Técnica            | Partición o límite                                                           | Entrada (`codigo`, `tipo`, `descripcion`)                 | Esperado                                             | Prueba que lo cubre                                                                |
| :----------------- | :--------------------------------------------------------------------------- | :-------------------------------------------------------- | :--------------------------------------------------- | :--------------------------------------------------------------------------------- |
| Partición válida   | Tipo `computador`                                                            | `"EQ-01"`, `"computador"`, `"PC portátil sala 3"`         | Dict con estado `disponible`                         | `test_registrar_equipo_casos_validos_y_limites[EQ-01...]`                          |
| Partición válida   | Tipo `proyector`                                                             | `"EQ-02"`, `"proyector"`, `"Proyector aula 5"`            | Dict con estado `disponible`                         | `test_registrar_equipo_casos_validos_y_limites[EQ-02...]`                          |
| Partición válida   | Tipo `tableta`                                                               | `"EQ-03"`, `"tableta"`, `"Tableta de préstamo"`           | Dict con estado `disponible`                         | `test_registrar_equipo_casos_validos_y_limites[EQ-03...]`                          |
| Partición válida   | Tipo con mayúsculas y espacios                                               | `"EQ-04"`, `"  Tableta "`, `"Tableta 10 pulgadas"`        | Tipo normalizado a `"tableta"`                       | `test_registrar_equipo_casos_validos_y_limites[EQ-04...]`                          |
| Partición válida   | Código con espacios en los extremos                                          | `"  EQ-05  "`, `"computador"`, `"PC de escritorio"`       | Código normalizado a `"EQ-05"`                       | `test_registrar_equipo_casos_validos_y_limites[  EQ-05  ...]`                      |
| Partición válida   | Código en minúsculas                                                         | `"eq-07"`, `"proyector"`, `"Proyector portátil"`          | Código normalizado a `"EQ-07"`                       | `test_registrar_equipo_casos_validos_y_limites[eq-07...]`                          |
| Partición válida   | Descripción con tildes, `ñ` y apóstrofo                                      | `"EQ-08"`, `"tableta"`, `"Tableta de D'Marco, aula Peña"` | Descripción exacta, sin alterar                      | `test_registrar_equipo_casos_validos_y_limites[EQ-08...]`                          |
| Límite             | Código con longitud mínima válida (1 carácter)                               | `"A"`, `"computador"`, `"PC"`                             | Código `"A"` guardado                                | `test_registrar_equipo_casos_validos_y_limites[A-...]`                             |
| Límite             | Descripción con longitud mínima válida (1 carácter)                          | `"EQ-09"`, `"computador"`, `"x"`                          | Descripción `"x"` guardada                           | `test_registrar_equipo_casos_validos_y_limites[EQ-09...]`                          |
| Límite             | Inventario con 0 equipos (primer registro) y con 1 equipo (segundo registro) | `"EQ-01"` y luego `"EQ-02"`                               | Ambos quedan guardados                               | `test_registrar_equipo_valido_queda_guardado_en_sqlite`                            |
| Partición inválida | Código vacío (primer valor inválido tras el mínimo de 1)                     | `""`, `"computador"`, `"PC"`                              | `ValueError` (`"obligatorio"`)                       | `test_registrar_equipo_entradas_invalidas_lanzan_value_error[-...]`                |
| Partición inválida | Código solo espacios                                                         | `"   "`, `"computador"`, `"PC"`                           | `ValueError` (`"obligatorio"`)                       | `test_registrar_equipo_entradas_invalidas_lanzan_value_error[   -...]`             |
| Partición inválida | Código `None`                                                                | `None`, `"computador"`, `"PC"`                            | `ValueError` (`"obligatorio"`)                       | `test_registrar_equipo_entradas_invalidas_lanzan_value_error[None-...]`            |
| Partición inválida | Código que no es texto                                                       | `123`, `"computador"`, `"PC"`                             | `ValueError` (`"obligatorio"`)                       | `test_registrar_equipo_entradas_invalidas_lanzan_value_error[123-...]`             |
| Partición inválida | Tipo vacío                                                                   | `"EQ-10"`, `""`, `"PC"`                                   | `ValueError` (`"obligatorio"`)                       | `test_registrar_equipo_entradas_invalidas_lanzan_value_error[EQ-10--PC...]`        |
| Partición inválida | Tipo fuera de los tres permitidos                                            | `"EQ-10"`, `"impresora"`, `"HP"`                          | `ValueError` (`"tipo"`)                              | `test_registrar_equipo_entradas_invalidas_lanzan_value_error[EQ-10-impresora...]`  |
| Partición inválida | Tipo `None`                                                                  | `"EQ-10"`, `None`, `"PC"`                                 | `ValueError` (`"obligatorio"`)                       | `test_registrar_equipo_entradas_invalidas_lanzan_value_error[EQ-10-None...]`       |
| Partición inválida | Descripción vacía (primer valor inválido tras el mínimo de 1)                | `"EQ-10"`, `"computador"`, `""`                           | `ValueError` (`"obligatorio"`)                       | `test_registrar_equipo_entradas_invalidas_lanzan_value_error[...--obligatorio]`    |
| Partición inválida | Descripción solo espacios                                                    | `"EQ-10"`, `"computador"`, `"    "`                       | `ValueError` (`"obligatorio"`)                       | `test_registrar_equipo_entradas_invalidas_lanzan_value_error[...    -...]`         |
| Partición inválida | Descripción `None`                                                           | `"EQ-10"`, `"computador"`, `None`                         | `ValueError` (`"obligatorio"`)                       | `test_registrar_equipo_entradas_invalidas_lanzan_value_error[...None-obligatorio]` |
| Partición inválida | Código duplicado exacto (con 1 equipo previo)                                | `"EQ-01"` ya registrado                                   | `ValueError` (`"registrado"`); el original no cambia | `test_registrar_equipo_duplicado_lanza_error_y_conserva_el_original`               |
| Partición inválida | Código duplicado tras normalizar                                             | `"  eq-01 "` con `"EQ-01"` ya registrado                  | `ValueError` (`"registrado"`); el original no cambia | `test_registrar_equipo_rechaza_duplicado_tras_normalizar`                          |

**Ambigüedades encontradas (`registrar_equipo`):**

- **Espacios y mayúsculas en el código:** la regla original no lo especifica. Decisión: se quitan espacios extremos y se convierte a mayúsculas, de modo que `"eq-01"` y `"EQ-01"` representan el mismo equipo.
- **Qué es un tipo inválido:** la regla no lo detalla. Decisión: cualquier valor que, tras limpiar espacios y pasar a minúsculas, no sea `"computador"`, `"proyector"` o `"tableta"` lanza `ValueError`.
- **Longitud máxima del código y de la descripción:** la regla no define un tope máximo. Decisión: no se impone límite superior arbitrario y se prueba el borde mínimo de 1 carácter frente a vacío/espacios.

---

### Regla 2: `consultar_disponibles` — retorna solo los equipos sin préstamo activo

**Regla completa (el oráculo):** Retorna únicamente los equipos cuyo estado es `disponible` (sin préstamo activo). Si no hay equipos registrados o todos están prestados, retorna una lista vacía `[]`.

| Técnica                    | Partición o límite                                           | Estado del inventario                           | Esperado                                         | Prueba que lo cubre                                               |
| :------------------------- | :----------------------------------------------------------- | :---------------------------------------------- | :----------------------------------------------- | :---------------------------------------------------------------- |
| Partición válida           | Varios equipos, todos disponibles (registrados desordenados) | `EQ-03`, `EQ-01`, `EQ-02` disponibles           | Lista con `EQ-01`, `EQ-02`, `EQ-03` en ese orden | `test_consultar_disponibles_ordena_y_filtra_prestados`            |
| Partición válida           | Mezcla de disponibles y prestados                            | `EQ-02` prestado; `EQ-01` y `EQ-03` disponibles | Solo `EQ-01` y `EQ-03`                           | `test_consultar_disponibles_ordena_y_filtra_prestados`            |
| Partición inválida (vacío) | Todos los equipos prestados                                  | `EQ-01` prestado                                | `[]`                                             | `test_consultar_disponibles_todos_prestados_retorna_vacio`        |
| Partición inválida (vacío) | No hay equipos registrados (base sin datos/tabla)            | Base vacía o sin tabla `equipo`                 | `[]`                                             | `test_consultar_disponibles_base_sin_equipos_retorna_vacio`       |
| Límite                     | Exactamente 1 equipo disponible (`0` → `1`)                  | `EQ-01` disponible                              | Lista con solo `EQ-01`                           | `test_registrar_equipo_valido_retorna_dict_con_estado_disponible` |
| Límite                     | Exactamente 1 equipo prestado (`1` → `0` disponibles)        | `EQ-01` prestado                                | `[]`                                             | `test_consultar_disponibles_todos_prestados_retorna_vacio`        |

**Ambigüedades encontradas (`consultar_disponibles`):**

- **Orden de la lista:** la regla no lo fija. Decisión: ordenar ascendentemente por `codigo_equipo` para tener resultados deterministas.
- **Base o tabla inexistente:** la regla no lo menciona. Decisión: equivale a inventario sin disponibles y retorna `[]` sin error.
- **Campos de cada elemento:** la regla no lo especifica. Decisión: devolver diccionarios con `codigo_equipo`, `tipo`, `descripcion` y `estado`.

---

### Regla 3: `registrar_prestamo` — crea un préstamo activo solo si el equipo existe, está disponible y los datos están completos

**Regla completa (el oráculo):** Crea un préstamo en estado `activo` y cambia el estado del equipo a `prestado` solo si el equipo existe, está disponible (no tiene préstamo activo) y los datos obligatorios de la persona solicitante y la fecha están completos. Si el equipo no existe, ya está prestado o faltan datos obligatorios, rechaza la operación lanzando `ValueError` sin alterar registros previos.

| Técnica            | Partición o límite                             | Entrada (`codigo`, `id`, `nombre`, `fecha`)               | Esperado                                                                 | Prueba que lo cubre                                          |
| :----------------- | :--------------------------------------------- | :-------------------------------------------------------- | :----------------------------------------------------------------------- | :----------------------------------------------------------- |
| Partición válida   | Datos completos, equipo existente y disponible | `"  eq-01 "`, `"EST-101"`, `"José Muñoz"`, `"2026-11-26"` | Dict con préstamo `activo`, `fecha_devolucion` `None`; equipo `prestado` | `test_registrar_prestamo_valido_cambia_estado_a_prestado`    |
| Límite             | Equipo con 0 préstamos activos (`disponible`)  | `"EQ-01"` disponible                                      | Se acepta y cambia a `prestado`                                          | `test_registrar_prestamo_valido_cambia_estado_a_prestado`    |
| Límite             | Equipo ya prestado (`1` préstamo activo)       | `"EQ-01"` prestado                                        | `ValueError`; estado previo intacto                                      | `test_registrar_prestamo_reglas_de_rechazo[...prestado...]`  |
| Partición inválida | Identificador vacío                            | `"EQ-01"`, `""`, `"José Muñoz"`, `"2026-11-26"`           | `ValueError`                                                             | `test_registrar_prestamo_reglas_de_rechazo[EQ-01--...]`      |
| Partición inválida | Equipo prestado y además falta fecha           | `"EQ-01"`, `"EST-102"`, `"María Peña"`, `""`              | `ValueError`                                                             | `test_registrar_prestamo_reglas_de_rechazo[...--prestado]`   |
| Partición inválida | Equipo inexistente, datos válidos              | `"EQ-99"`, `"EST-101"`, `"José Muñoz"`, `"2026-11-26"`    | `ValueError`                                                             | `test_registrar_prestamo_reglas_de_rechazo[EQ-99-...-None]`  |
| Partición inválida | Equipo inexistente y falta nombre              | `"EQ-99"`, `"EST-101"`, `""`, `"2026-11-26"`              | `ValueError`                                                             | `test_registrar_prestamo_reglas_de_rechazo[EQ-99-...--None]` |

**Tabla de decisión (`registrar_prestamo`):**

| Condición / Acción                               |                            R1                             |               R2                |                 R3                  |                 R4                 |                 R5                  |                  R6                  |
| :----------------------------------------------- | :-------------------------------------------------------: | :-----------------------------: | :---------------------------------: | :--------------------------------: | :---------------------------------: | :----------------------------------: |
| ¿El equipo existe?                               |                            Sí                             |               Sí                |                 Sí                  |                 Sí                 |                 No                  |                  No                  |
| ¿El equipo está disponible?                      |                            Sí                             |               Sí                |                 No                  |                 No                 |                  —                  |                  —                   |
| ¿Datos del solicitante y fecha válidos?          |                            Sí                             |               No                |                 Sí                  |                 No                 |                 Sí                  |                  No                  |
| **Acción esperada**                              |                                                           |                                 |                                     |                                    |                                     |                                      |
| Crea préstamo `activo` y marca equipo `prestado` |                           **X**                           |                —                |                  —                  |                 —                  |                  —                  |                  —                   |
| Lanza `ValueError` sin alterar registros previos |                             —                             |              **X**              |                **X**                |               **X**                |                **X**                |                **X**                 |
| **Prueba que lo cubre**                          | `test_registrar_prestamo_valido_cambia_estado_a_prestado` | `reglas_de_rechazo[EQ-01--...]` | `reglas_de_rechazo[...prestado...]` | `reglas_de_rechazo[...--prestado]` | `reglas_de_rechazo[EQ-99-...-None]` | `reglas_de_rechazo[EQ-99-...--None]` |

**Ambigüedades encontradas (`registrar_prestamo`):**

- **Varias condiciones inválidas a la vez (R4 y R6):** la regla solo exige `ValueError` y no alterar el estado. Decisión: verificar `ValueError` sin exigir un orden fijo entre validaciones.
- **Normalización del código:** la regla no lo menciona. Decisión: aplicar `.strip().upper()` igual que en `registrar_equipo`.
- **Formato de `fecha_prestamo`:** la regla solo pide que esté completa. Decisión: exigir texto no vacío tras `.strip()` sin imponer formato de calendario adicional.
- **Campos de retorno:** la regla no lo detalla. Decisión: retornar diccionario con `id_prestamo`, `codigo_equipo`, `solicitante_id`, `solicitante_nombre`, `fecha_prestamo`, `fecha_devolucion` y `estado_prestamo`.

---

## 2. Revisión de las pruebas generadas

| Prueba generada                                                           | Decisión   | Por qué                                                                                                      | En su lugar                                                                                          |
| :------------------------------------------------------------------------ | :--------- | :----------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------- |
| Casos válidos repetidos de tipos básicos ya cubiertos por pruebas previas | Descartada | Redundantes con `test_registrar_equipo_acepta_los_tres_tipos_permitidos` en `tests/test_registrar_equipo.py` | Conservé casos de normalización, caracteres difíciles y límites en `tests/test_reglas_negocio_s7.py` |
| `test_registrar_prestamo_reglas_de_rechazo`                               | Corregida  | Verificaba `ValueError`, pero convenía asegurar que el estado no cambie en rechazos                          | Se mantiene con `pytest.raises(ValueError)` y preparación explícita del estado del equipo            |
| `test_registrar_prestamo_valido_cambia_estado_a_prestado`                 | Conservada | Comprueba el diccionario retornado y que el equipo ya no figure en `consultar_disponibles`                   | Se conserva sin modificaciones                                                                       |

---

## 3. Romper el código a propósito

| Cambio introducido                                                        | Archivo y línea                         | ¿Alguna prueba falló?                                                               | Qué hice                                                                            |
| :------------------------------------------------------------------------ | :-------------------------------------- | :---------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------- |
| Cambiar `ESTADO_INICIAL` de `"disponible"` a `"prestado"`                 | `src/equipos.py` (`ESTADO_INICIAL`)     | Sí, fallaron las pruebas que esperan estado inicial `"disponible"` y disponibilidad | Verifiqué el fallo con `python -m pytest -v` y restauré `src/equipos.py`            |
| Quitar `.upper()` al normalizar `codigo_equipo` en `registrar_prestamo`   | `src/equipos.py` (`registrar_prestamo`) | Sí, falló la prueba con código `"  eq-01 "`                                         | Comprobé que la suite detecta la falta de normalización y restauré `src/equipos.py` |
| Comentar o eliminar la validación de equipo ya prestado / préstamo activo | `src/equipos.py` (`registrar_prestamo`) | Sí, falló la prueba de rechazo cuando el equipo ya está prestado                    | Confirmé que la regla queda protegida y restauré `src/equipos.py`                   |

---

## 4. Datos de prueba

**Origen:** Datos sintéticos creados para las pruebas del laboratorio con apoyo de IA (fixture `datos_sinteticos_s7` en `tests/test_reglas_negocio_s7.py`). Confirmo que no corresponden a personas reales.

**Casos difíciles incluidos:** Tildes (`José`, `María`, `portátil`, `préstamo`), `ñ` (`Muñoz`, `Peña`), apóstrofo (`D'Marco`), cadenas vacías, solo espacios, `None`, valores numéricos (`123`) y textos de longitud mínima de 1 carácter.
