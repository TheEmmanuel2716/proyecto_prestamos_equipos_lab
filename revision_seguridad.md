# Informe de revisión de código y seguridad

Proyecto: Documentar y probar las reglas de negocio de un sistema monolítico para la gestión de préstamos de equipos
Estudiante: Emmanuel Steven González Muñoz
Fecha: 2026-11-26
Commit revisado: 341614f

## 1. Herramientas y criterios

- **Linter:** ruff 0.17.6 con las reglas E, F, B, S. Configuración en `pyproject.toml`.
- **Auditoría de dependencias:** pip-audit sobre `requirements.txt` — resultado: sin vulnerabilidades conocidas.
- **Lista de revisión:** la de la semana 6 (corrección y pruebas, diseño y legibilidad, seguridad).
- **Revisión con IA:** Claude con el prompt de revisión de la semana (ver sección 3).

### Puntos de seguridad revisados

| Punto | ¿Aplica? | Resultado |
|---|---|---|
| Inyección (consultas con parámetros) | Sí (consultas SQLite) | Sin hallazgos: el `INSERT` usa parámetros nombrados y los f-strings solo arman mensajes de error. Se agregaron pruebas de abuso (código, descripción y tipo con SQL malicioso). |
| Secretos (código, historial, .gitignore, .env.example) | Sí | Sin secretos en el código ni en el historial (`git log -p` revisado; única coincidencia: la palabra "secretos" en un texto de la bitácora). `.env` en `.gitignore` y `.env.example` creado. |
| Contraseñas (scrypt, bcrypt o argon2 con sal) | No aplica | El MVP no tiene autenticación ni almacena contraseñas (gestión avanzada de usuarios fuera del alcance, Semana 3); solo se manejan datos ficticios. |
| Control de acceso (rol verificado y prueba de abuso) | No aplica | No hay rutas Flask, roles ni sesiones: `registrar_equipo` es una función local. Se cubrió la validación de entradas con pruebas de abuso (H-02, H-07). |
| Dependencias (existen, necesarias, versión fijada, pip-audit) | Sí | `requirements.txt` solo tiene `pytest` y sus dependencias, todas con `==`. Flask no se incluye porque aún no se usa. `ruff` y `pip-audit` están en `requirements-dev.txt`. pip-audit: sin vulnerabilidades. |

## 2. Tabla de hallazgos

| Id | Archivo y línea | Problema | Categoría | Severidad | Corrección | Commit |
|---|---|---|---|---|---|---|
| H-01 | src/equipos.py:62 | `raise ValueError` dentro de `except` encadena el `IntegrityError` interno de SQLite en el traceback (B904). | Manejo de errores | Baja | Se agregó `from None`. | 7b5c3a1 |
| H-02 | src/equipos.py:28 | `None` o un número en lugar de texto lanzaba `AttributeError` y no `ValueError`, contra el contrato. | Validación de entradas | Media | Función `_limpiar_texto` y validación de `tipo` obligatorio. Pruebas nuevas primero (4 fallaron). | 05b3b9e (rojo), b787ff8 (verde) |
| H-03 | tests/test_registrar_equipo.py:56 | Línea de 90 caracteres (E501). | Estilo | Baja | Se partió la línea; mismos argumentos y asserts. | 60ed760 |
| H-05 | src/equipos.py | `dict` sin tipar y mensaje "campo obligatorio" repetido tres veces. | Legibilidad | Baja | `TypedDict` `Equipo` y constante `MENSAJE_CAMPO_OBLIGATORIO`. | bda9c24 |
| H-07 | tests/test_seguridad_equipo.py | Sin prueba de abuso para el campo `tipo`. | Cobertura (inyección) | Baja | Prueba nueva con `tipo` malicioso. | ff8424d |
| H-09 | README.md | Solo documentaba la semana 5; sin las 8 secciones y con el contrato desactualizado. | Documentación | Baja | README reescrito con las 8 secciones y contrato actualizado. | e97a9c4 |

**Severidad:** alta (permite acceder o cambiar datos sin permiso, o expone secretos), media (error probable o riesgo con condiciones), baja (estilo o mantenibilidad).

No se encontraron hallazgos de severidad alta. Los hallazgos H-04, H-06 y H-08 (mejoras menores en pruebas) están en la sección 4.

### Avisos del linter no corregidos

| Regla | Archivo y línea | Por qué se mantiene |
|---|---|---|
| S101 | tests/*.py (todas las líneas con `assert`) | `assert` es el mecanismo estándar de verificación en pytest. Se excluye con `per-file-ignores` en `pyproject.toml` solo para `tests/`. |

## 3. Revisión con IA

**Prompt usado:** guía de la semana 6 con el rol de auditor de seguridad y calidad: revisar el código con archivo, línea y severidad, separando problemas reales de falsos positivos (entrada 7 de `bitacora_ia.md`).

| Hallazgo de la IA | ¿Real o falso positivo? | Cómo lo verifiqué |
|---|---|---|
| H-01: error encadenado en el `raise` | Real | Ejecución manual con dos registros iguales (traceback con "During handling...") y regla B904 de ruff. |
| H-02: `None` lanza `AttributeError` | Real | Ejecución manual con `registrar_equipo(None, ...)`: salió `AttributeError`. |
| H-03: línea de 90 caracteres | Real | Aviso E501 de ruff. |
| H-04, H-06, H-08: debilidades menores en pruebas | Reales (baja) | Lectura del código de las pruebas. |
| H-05, H-07: legibilidad y hueco de cobertura | Reales (baja) | Lectura del código y de las pruebas. |
| SQL inyectable por f-strings | Falso positivo | Los f-strings solo arman mensajes; S608 no se activó; las pruebas de abuso lo respaldan. |
| `ruta_db` permite escribir en rutas arbitrarias | Falso positivo | Solo lo pasa el código o las pruebas; no hay capa web que lo exponga. |
| Condición de carrera al detectar duplicados | Falso positivo | La `PRIMARY KEY` hace que SQLite rechace el segundo `INSERT` de forma atómica. |
| Conexión que no se cierra | Falso positivo | El `finally` siempre cierra la conexión. |

**Lo que la IA no encontró:** el `README.md` estaba desactualizado respecto al código y a la tarea (H-09): solo documentaba la semana 5, no tenía las 8 secciones y su contrato no reflejaba las correcciones posteriores. Lo detecté yo al releerlo.

## 4. Pendientes

| Pendiente | Por qué no se corrigió todavía | Plan |
|---|---|---|
| H-04: `try/except OperationalError: pass` debilita una comprobación en la última prueba de tests/test_registrar_equipo.py (tipo no permitido) | Corregirlo implica modificar una prueba ya entregada; riesgo bajo. | Reemplazarlo por una comprobación explícita en una revisión posterior. |
| H-06 y H-08: comprobación circular y duplicación del helper de lectura en tests/test_seguridad_equipo.py | Mejoras de mantenibilidad sin riesgo de seguridad. | Mover el helper a un `conftest.py` cuando se implementen las demás historias. |
| Función única de inicialización de la base de datos | Hoy solo hay una tabla y una función; no hay duplicación todavía. | Crearla al implementar préstamos y devoluciones. |
| Límite de longitud en código y descripción | Cambiaría el contrato de la función; riesgo bajo en un sistema local. | Definir límites con el responsable del laboratorio. |
| Gestión de roles y autenticación (P-02/Alcance) | Fuera del alcance del MVP monolítico definido en la semana 3. | Incorporar en una fase posterior tras validar requisitos con el responsable del laboratorio. |
| Servidor Flask (ADR-001) | Aún no se implementa; no hay rutas que proteger. | Al agregarlo, revisar `ruta_db`, escape de mensajes de error y control de acceso. |

**Claves expuestas:** Ninguna.
