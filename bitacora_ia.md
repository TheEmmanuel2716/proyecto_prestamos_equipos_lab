# Bitácora de uso de IA

- **Proyecto:** Documentar y probar las reglas de negocio de un sistema monolítico para la gestión de préstamos de equipos en laboratorios de informática
- **Estudiante:** Emmanuel Steven González Muñoz
- **Funcionalidad:** HU-01. Registrar equipos (`registrar_equipo`), consulta de disponibles (`consultar_disponibles`) y registro de préstamos (`registrar_prestamo`)
- **Asistente usado:** Claude y Gemini

> Commits del historial:
> `34b87be` Contrato en README · `3996491` Pruebas en rojo · `f250843` Implementación en verde · `e82f600` Refactor

---

## Entradas

### Entrada 1. Elección de la historia de usuario

- **Fecha:** 2026-11-26
- **Prompt o sugerencia:** Claude recomendó trabajar HU-04 (impedir préstamos de equipos ocupados) por su relación con RNF-01 y por tener más casos límite.
- **Decisión:** Rechazada
- **Por qué:** Elegí HU-01 porque es la base del modelo de datos (tabla EQUIPO) y las demás historias dependen de que existan equipos registrados.
- **Verificación:** Revisión de las historias en el README y del orden de dependencias del modelo de datos.
- **Commit relacionado:** `34b87be`

### Entrada 2. Contrato de la función en el README

- **Fecha:** 2026-11-26
- **Prompt o sugerencia:** Claude redactó la sección "Funcionalidad de la semana 5": firma con type hints, parámetros, retorno, excepciones, casos límite y 4 ejemplos. Incluía un parámetro opcional `ruta_db` que no estaba en el contrato de la Semana 4.
- **Decisión:** Aceptada
- **Por qué:** `ruta_db` permite que cada prueba use una base SQLite temporal sin contaminar a las demás, y no rompe el contrato original porque tiene valor por defecto. Se mantiene el diseño ADR-001 (monolito Python + SQLite).
- **Verificación:** Se comprobó que los ejemplos del README coinciden con las pruebas escritas después.
- **Commit relacionado:** `34b87be`

### Entrada 3. Pruebas antes de implementar

- **Fecha:** 2026-11-26
- **Prompt o sugerencia:** Claude propuso 12 casos de prueba (3 normales, 4 límite, 2 de error, algunos parametrizados) y un esqueleto de `src/equipos.py` que solo lanza `NotImplementedError`, para que `pytest` pudiera importar la función y mostrar pruebas en rojo.
- **Decisión:** Aceptada
- **Por qué:** Cubre la rúbrica (≥2 normales, ≥2 límite, ≥1 error) y el escenario de error del criterio de aceptación (duplicado). Se usan datos ficticios (RNF-06).
- **Verificación:** `python -m pytest -v` mostró `12 failed`, todas con `NotImplementedError`. También corregí el nombre de la carpeta de `test/` a `tests/` antes del commit para cumplir con lo que pide la tarea.
- **Commit relacionado:** `3996491`

### Entrada 4. Implementación con SQLite

- **Fecha:** 2026-11-26
- **Prompt o sugerencia:** Claude entregó la implementación: validar antes de abrir la base, `codigo_equipo` como `PRIMARY KEY` para detectar duplicados con `sqlite3.IntegrityError` (traducido a `ValueError`), consultas con parámetros `?` y `try/finally` para cerrar la conexión.
- **Decisión:** Aceptada
- **Por qué:** Cumple el contrato, usa solo la librería estándar (ADR-001) y deja que la base garantice la unicidad. Los parámetros `?` evitan inyección SQL.
- **Verificación:** `python -m pytest -v` pasó las 12 pruebas sin modificar ninguna. `git status` no mostró archivos `.db` ni `.venv/`.
- **Commit relacionado:** `f250843`

### Entrada 5. Entorno virtual y `.env`

- **Fecha:** 2026-11-26
- **Prompt o sugerencia:** Claude indicó crear un entorno virtual `.venv`, instalar `pytest` y generar `requirements.txt`. También indicó que no era necesario un archivo `.env` porque el proyecto no usa claves, y que bastaba dejarlo en el `.gitignore`.
- **Decisión:** Aceptada
- **Por qué:** El proyecto no maneja secretos (solo SQLite local), y `.gitignore` con `.env`, `.venv/`, `__pycache__/`, `.pytest_cache/` y `*.db` cumple la regla de uso responsable.
- **Verificación:** `git status` antes de cada commit confirmó que no se subían el entorno virtual ni bases de datos.
- **Commit relacionado:** `3996491`

### Entrada 6. Refactorización

- **Fecha:** 2026-11-26
- **Prompt o sugerencia:** Claude propuso dividir `registrar_equipo` en `_normalizar_y_validar` y `_guardar_equipo`, mover el `INSERT` a la constante `SQL_INSERTAR_EQUIPO` y eliminar la duplicación del diccionario del equipo.
- **Decisión:** Aceptada
- **Por qué:** Cada función tiene una sola responsabilidad, el código es más fácil de explicar en sustentación y no se agregó sobreingeniería (sin clases ni capas nuevas).
- **Verificación:** `python -m pytest -v` pasó las 12 pruebas sin tocarlas; `git diff --stat HEAD -- tests/` no mostró cambios.
- **Commit relacionado:** `e82f600`

---

## Tabla resumen de decisiones

| Decisión              | Cantidad | Entradas      |
| --------------------- | -------- | ------------- |
| Aceptadas             | 5        | 2, 3, 4, 5, 6 |
| Aceptadas con cambios | 0        | -             |
| Rechazadas            | 1        | 1             |

---

## Errores que atraparon las pruebas

- **Fallo detectado:** al ejecutar `pytest` por primera vez, con solo el esqueleto de la función, las 12 pruebas fallaron con `NotImplementedError` (`12 failed in 0.15s`).
- **Qué prueba falló y por qué:** todas, porque la función aún no tenía lógica. Incluso las pruebas que esperan `ValueError` fallaron, lo que confirma que ninguna pasa por casualidad.
- **Cómo se corrigió:** al implementar la función en el commit `f250843`, las 12 pasaron sin modificar ninguna prueba.
- **Nota honesta:** en la fase de implementación no se presentaron errores: ninguna prueba reveló un error de lógica y las 12 pasaron a la primera.
- **Limitación conocida (no cubierta por las pruebas):** si se pasa `None` o un número en lugar de texto, la función lanza `AttributeError` y no `ValueError`.

---

## Reflexión final

Trabajar con pruebas primero me obligó a definir el contrato antes de pensar en el código. Ver las 12 pruebas en rojo me dio confianza de que realmente comprobaban algo. Claude me ayudó a identificar casos límite que yo no había considerado, como el código en minúsculas y los espacios en los campos. Aun así, tuve que entender cada decisión (la clave primaria, los parámetros `?`, el orden de validación) para poder explicarla. Rechacé una recomendación porque prefería empezar por la base del modelo de datos. Aprendí que la IA acelera el trabajo, pero la responsabilidad de revisar y sustentar el código sigue siendo mía.

---

# Semana 6: revisión de código y seguridad

- **Funcionalidad revisada:** HU-01. Registrar equipos (`registrar_equipo`)
- **Asistente usado:** Claude
- **Agente de código:** no se usó; todas las correcciones se aplicaron a mano en `main` y se revisaron con `pytest`, `ruff` y `git diff`.

## Entradas

### Entrada 7. Segunda revisión de código y seguridad con IA

- **Fecha:** 2026-11-25
- **Prompt o sugerencia:** Se le pidió a Claude actuar como auditor de seguridad y calidad (guía de la semana 6): revisar `src/equipos.py` y las pruebas con archivo, línea y severidad, separando problemas reales de falsos positivos. Claude entregó 8 hallazgos reales (H-01 a H-08) y 4 sospechas descartadas.
- **Decisión:** Aceptada con cambios
- **Por qué:** Acepté corregir H-01, H-02, H-03, H-05 y H-07 porque afectan el contrato, el linter o la cobertura. No corregí H-04, H-06 y H-08 porque implicaban modificar pruebas ya entregadas por mejoras menores; quedaron en Pendientes del informe. El hallazgo H-09 (README desactualizado) lo encontré yo y la IA no lo había señalado.
- **Verificación:** H-01 y H-02 reproducidos con `python -c` (traceback encadenado y `AttributeError` con `None`); H-03 confirmado por el aviso E501 de `ruff`; los falsos positivos descartados leyendo el código (`finally`, `PRIMARY KEY`, consultas con parámetros).
- **Commit relacionado:** `341614f` (commit revisado)

### Entrada 8. Corrección de H-02 con pruebas primero

- **Fecha:** 2026-11-25
- **Prompt o sugerencia:** Claude propuso escribir primero 4 pruebas nuevas (`None` en cada campo y un número como código) y luego implementar `_limpiar_texto` más una validación de `tipo` obligatorio, para que los datos que no son texto lancen `ValueError` y no `AttributeError`.
- **Decisión:** Aceptada
- **Por qué:** El contrato dice que los datos faltantes lanzan `ValueError`. Seguir el orden rojo, verde mantiene el mismo método de la semana 5 y no se tocó ninguna prueba existente.
- **Verificación:** las 4 pruebas nuevas fallaron antes de la corrección; después pasaron las 18 pruebas del proyecto y `ruff` quedó sin avisos nuevos.
- **Commit relacionado:** `05b3b9e` (rojo) y `b787ff8` (verde)

### Entrada 9. Prueba de abuso para el campo `tipo` (H-07)

- **Fecha:** 2026-11-25
- **Prompt o sugerencia:** Claude propuso agregar una prueba de que un `tipo` con SQL malicioso es rechazado y no toca la tabla, y predijo que pasaría a la primera.
- **Decisión:** Aceptada con cambios
- **Por qué:** La idea es válida porque ese campo no tenía prueba de abuso. Al ejecutarla, falló con `NameError: name 'pytest' is not defined`: faltaba `import pytest` en el archivo. La predicción de que pasaría a la primera fue incorrecta. Agregué el import (y dejé el espaciado estándar entre funciones) antes de hacer el commit.
- **Verificación:** `pytest` pasó con 19 pruebas y `ruff check` sin avisos.
- **Commit relacionado:** `ff8424d`

### Entrada 10. No modificar pruebas existentes (excepto el formato de H-03)

- **Fecha:** 2026-11-25
- **Prompt o sugerencia:** Claude recomendó no tocar las pruebas ya entregadas por H-04, H-06 y H-08, y limitar el único cambio en una prueba existente a partir una línea larga (E501), sin cambiar argumentos ni `assert`.
- **Decisión:** Aceptada
- **Por qué:** La regla es nunca modificar pruebas para que pasen. El cambio de H-03 es solo de formato: la prueba pasaba antes y después.
- **Verificación:** `git log -p -1 -- tests/test_registrar_equipo.py` mostró que solo se partió la línea, con los mismos argumentos; `pytest` y `ruff` limpios.
- **Commit relacionado:** `60ed760`

## Tabla resumen de decisiones (semana 6)

| Decisión              | Cantidad | Entradas |
| --------------------- | -------- | -------- |
| Aceptadas             | 2        | 8, 10    |
| Aceptadas con cambios | 2        | 7, 9     |
| Rechazadas            | 0        | -        |

## Errores que atraparon las pruebas (semana 6)

- **Pruebas en rojo de H-02:** las 4 pruebas nuevas de `tests/test_validacion_entradas.py` fallaron antes de la corrección, lo que confirmó que `registrar_equipo` no manejaba datos que no son texto según el contrato. Pasaron tras el commit `b787ff8`.
- **`NameError` en la prueba de H-07:** `test_tipo_con_sql_malicioso_es_rechazado_y_no_toca_la_tabla` falló con `NameError: name 'pytest' is not defined` (`1 failed, 18 passed`). La causa fue un import omitido en la prueba, no el código; se corrigió antes del commit.

---

# Semana 7: particiones, valores límite y tablas de decisión

- **Funcionalidades probadas:** `registrar_equipo`, `consultar_disponibles` y `registrar_prestamo`
- **Asistentes usados:** Claude y Gemini

## Entradas

### Entrada 11. Diseño de casos, límites y tabla de decisión (Actividad 7)

- **Fecha:** 2026-11-26
- **Prompt o sugerencia:** Se diseñaron tablas de particiones de equivalencia, valores límite, ambigüedades y una tabla de decisión para `registrar_prestamo` combinando existencia del equipo, disponibilidad y validez de los datos.
- **Decisión:** Aceptada con cambios
- **Por qué:** Se ajustaron las reglas de oráculo y ambigüedades para que lo esperado salga de la regla y las decisiones de diseño, sin alterar pruebas anteriores.
- **Verificación:** Documentado en la Sección 1 de `registro_pruebas.md`.

### Entrada 12. Implementación de funciones faltantes y pruebas con `pytest`

- **Fecha:** 2026-11-26
- **Prompt o sugerencia:** Se implementaron `consultar_disponibles` y `registrar_prestamo` en `src/equipos.py` y se crearon las pruebas parametrizadas en `tests/test_reglas_negocio_s7.py`.
- **Decisión:** Aceptada con cambios
- **Por qué:** Inicialmente `pytest` reportó `ImportError` porque `src/equipos.py` solo tenía `registrar_equipo`; al completar las funciones y revisar los casos con las tres preguntas, la suite quedó sólida sin borrar pruebas previas.
- **Verificación:** `python -m pytest -v` ejecutó 48 pruebas en estado `PASSED`.

### Entrada 13. Datos sintéticos y pruebas de rotura intencional

- **Fecha:** 2026-11-26
- **Prompt o sugerencia:** Se incorporó el fixture `datos_sinteticos_s7` con caracteres difíciles (`José Muñoz`, `María Peña`, `D'Marco Peña`) y se aplicaron tres cambios intencionales en `src/equipos.py` para verificar la detección de fallos.
- **Decisión:** Aceptada
- **Por qué:** Permite comprobar que las pruebas fallan ante defectos reales (estado inicial, omisión de `.upper()` y omisión de validación de equipo ya prestado) y luego restaurar el código limpio.
- **Verificación:** Registrado en las Secciones 3 y 4 de `registro_pruebas.md` y verificado con `python -m pytest -v` tras restaurar `src/equipos.py`.

## Tabla resumen de decisiones (semana 7)

| Decisión              | Cantidad | Entradas |
| --------------------- | -------- | -------- |
| Aceptadas             | 1        | 13       |
| Aceptadas con cambios | 2        | 11, 12   |
| Rechazadas            | 0        | -        |
