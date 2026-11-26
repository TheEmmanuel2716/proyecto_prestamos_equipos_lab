# Bitácora de uso de IA

- **Proyecto:** Documentar y probar las reglas de negocio de un sistema monolítico para la gestión de préstamos de equipos en laboratorios de informática
- **Estudiante:** Emmanuel Steven González Muñoz
- **Funcionalidad:** HU-01. Registrar equipos (`registrar_equipo`)
- **Asistente usado:** Claude

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
