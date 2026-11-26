# Informe final del proyecto integrador

- **Proyecto:** Sistema monolítico de gestión de préstamos de equipos en laboratorios de informática
- **Estudiante:** Emmanuel Steven González Muñoz
- **Repositorio:** [TheEmmanuel2716/proyecto_prestamos_equipos_lab](https://github.com/TheEmmanuel2716/proyecto_prestamos_equipos_lab)
- **Fecha:** 26 de noviembre de 2026
- **Commit consolidado:** [`96f042d`](https://github.com/TheEmmanuel2716/proyecto_prestamos_equipos_lab/commit/96f042d44286db34842d660cc091a61d7e69baba)

## 1. Resumen

Este proyecto aborda el control manual y poco trazable del inventario y los préstamos de equipos en laboratorios de informática. Se desarrolló un sistema monolítico en Python con persistencia SQLite que permite registrar equipos, consultar disponibilidad, crear préstamos, procesar devoluciones y consultar el historial.

Se implementaron reglas de integridad, normalización de entradas, consultas parametrizadas y transacciones con `commit`/`rollback`. La inteligencia artificial fue utilizada como apoyo en fundamentos, requisitos, diseño, código, pruebas y revisión de seguridad. Todas las sugerencias fueron contrastadas mediante pruebas, análisis estático, auditoría de dependencias y revisión manual.

La [estructura del proyecto](https://github.com/TheEmmanuel2716/proyecto_prestamos_equipos_lab) separa la lógica pública en `src/equipos.py`, las pruebas en `tests/` y los informes técnicos en la raíz. El estado final fue validado con 72 pruebas aprobadas, Ruff sin errores y `pip-audit` sin vulnerabilidades conocidas.

## 2. Problema y usuario

El problema afecta a los encargados de laboratorios y a los estudiantes que solicitan equipos como computadores, proyectores y tabletas. Antes del sistema, disponibilidad, registros y préstamos podían gestionarse de forma manual o dispersa, con riesgo de prestar un equipo ocupado, duplicar registros o perder el historial de devoluciones.

Los usuarios principales son el encargado del laboratorio, que administra el inventario y los préstamos, y el solicitante, identificado por un ID y un nombre sintético. El alcance incluye el ciclo completo: equipo disponible, préstamo activo, devolución y consulta del historial. Los documentos de contexto disponibles en el repositorio son el [README](https://github.com/TheEmmanuel2716/proyecto_prestamos_equipos_lab/blob/main/README.md), la [bitácora de IA](https://github.com/TheEmmanuel2716/proyecto_prestamos_equipos_lab/blob/main/bitacora_ia.md) y el [registro de pruebas](https://github.com/TheEmmanuel2716/proyecto_prestamos_equipos_lab/blob/main/registro_pruebas.md). No se encontró en el repositorio una propuesta formal ni una transcripción de entrevista como archivos independientes.

## 3. La IA en el ciclo de vida

| Módulo y fase  | Qué hiciste con IA                                                                             | Herramienta     | Evidencia (enlace)                                                                                                                                                                                                                        | Cómo verificaste                                                                             |
| -------------- | ---------------------------------------------------------------------------------------------- | --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| 1. Fundamentos | Delimitar el problema del laboratorio, el alcance monolítico y los criterios iniciales         | Claude / Gemini | [README](https://github.com/TheEmmanuel2716/proyecto_prestamos_equipos_lab/blob/main/README.md)                                                                                                                                           | Contraste con el contexto del laboratorio y las reglas del seminario                         |
| 2. Requisitos  | Definir historias de usuario, reglas de negocio, datos obligatorios y criterios de rechazo     | Claude / Gemini | [README](https://github.com/TheEmmanuel2716/proyecto_prestamos_equipos_lab/blob/main/README.md)                                                                                                                                           | Revisión manual de reglas, validaciones y casos de borde                                     |
| 3. Diseño      | Modelar SQLite (`equipo` y `prestamo`), contratos de funciones y decisiones arquitectónicas    | Claude / Gemini | [src/equipos.py](https://github.com/TheEmmanuel2716/proyecto_prestamos_equipos_lab/blob/main/src/equipos.py)                                                                                                                              | Verificación de llaves, índices, transacciones y coherencia del contrato                     |
| 4. Código      | Implementar y refactorizar registro, consulta, préstamos y devoluciones                        | Claude / Gemini | [src/equipos.py](https://github.com/TheEmmanuel2716/proyecto_prestamos_equipos_lab/blob/main/src/equipos.py)                                                                                                                              | Ejecución de `pytest`, `ruff check` y revisión manual de cambios y commits                   |
| 5. Pruebas     | Diseñar particiones, valores límite, tablas de decisión, datos sintéticos y rotura intencional | Claude / Gemini | [tests](https://github.com/TheEmmanuel2716/proyecto_prestamos_equipos_lab/tree/main/tests) y [registro_pruebas.md](https://github.com/TheEmmanuel2716/proyecto_prestamos_equipos_lab/blob/main/registro_pruebas.md)                       | Ejecución de `python -m pytest -v` e inspección de fallos ante cambios deliberados           |
| 6. Operación   | Revisar seguridad, dependencias, higiene del repositorio y preparación de entrega              | Claude / Gemini | [revision_seguridad.md](https://github.com/TheEmmanuel2716/proyecto_prestamos_equipos_lab/blob/main/revision_seguridad.md) y [bitacora_ia.md](https://github.com/TheEmmanuel2716/proyecto_prestamos_equipos_lab/blob/main/bitacora_ia.md) | Auditoría con `ruff` y `pip-audit`, revisión de `.gitignore` y verificación del estado final |

## 4. Verificación: lo que la IA hizo mal y cómo lo encontraste

### Caso 1: Manejo de entradas que no son texto (`None` o números)

- **Fase:** Código / Pruebas
- **Qué propuso la IA:** Una implementación inicial de limpieza/validación de texto que asumía cadenas y provocaba `AttributeError` al recibir `None` u otros tipos no `str`.
- **Qué estaba mal:** El contrato exige rechazar datos faltantes o inválidos con `ValueError`, no dejar fallar con `AttributeError`.
- **Cómo lo detectaste:** Mediante revisión/auditoría del código y pruebas de validación con `None` y valores numéricos (`pytest`).
- **Qué hiciste:** Se incorporó `_limpiar_texto` y validaciones explícitas para lanzar `ValueError` de forma consistente. Evidencia: [bitácora de IA](https://github.com/TheEmmanuel2716/proyecto_prestamos_equipos_lab/blob/main/bitacora_ia.md) y [revisión de seguridad](https://github.com/TheEmmanuel2716/proyecto_prestamos_equipos_lab/blob/main/revision_seguridad.md).

### Caso 2: Prueba de abuso con import omitido y predicción errónea

- **Fase:** Pruebas
- **Qué propuso la IA:** Agregar una prueba de seguridad para el campo `tipo` con entrada SQL maliciosa, asegurando que pasaría sin inconvenientes en la primera ejecución.
- **Qué estaba mal:** La prueba omitía `import pytest` y la predicción de ejecución inmediata era incorrecta.
- **Cómo lo detectaste:** Al ejecutar `python -m pytest -v`, que arrojó `NameError: name 'pytest' is not defined`.
- **Qué hiciste:** Se agregó el import faltante y se ajustó el formato antes de confirmar el cambio. Evidencia: [Entrada 9 de la bitácora](https://github.com/TheEmmanuel2716/proyecto_prestamos_equipos_lab/blob/main/bitacora_ia.md).

### Caso 3: Documentación desactualizada frente a la evolución del proyecto

- **Fase:** Operación / Requisitos
- **Qué propuso la IA:** Sugerencias de auditoría centradas en detalles internos de código sin advertir que la documentación de referencia (`README.md`) había quedado desfasada respecto al avance y estructura del proyecto.
- **Qué estaba mal:** Mantener documentación desactualizada genera discrepancias entre lo documentado, el código y los requisitos de entrega.
- **Cómo lo detectaste:** Relectura crítica del `README.md` y contraste contra los archivos, pruebas y criterios de evaluación del proyecto.
- **Qué hiciste:** Se actualizó el [README](https://github.com/TheEmmanuel2716/proyecto_prestamos_equipos_lab/blob/main/README.md) para alinear el alcance, las funciones y las evidencias del repositorio.

## 5. Estado final del sistema

- **Arquitectura:** Sistema monolítico en Python con persistencia local SQLite, funciones de dominio, consultas parametrizadas y transacciones explícitas. El esquema contiene `equipo` y `prestamo`, índices, llave foránea y restricciones de estado.
- **Funcionalidades terminadas:** registro y normalización de equipos; consulta de disponibles; registro de préstamos; devolución por código de equipo o ID; consulta de activos e historial completo o por equipo; inicialización aislada de la base.
- **Pruebas:** suite final ejecutada con `python -m pytest -v`: **72 pruebas aprobadas en 0.27 s**. Ruff informó `All checks passed!` y `pip-audit` indicó `No known vulnerabilities found`.
- **Pendientes:** interfaz web o CLI, autenticación y roles, límites máximos de longitud definidos por el laboratorio y formatos especiales de calendario. No son parte del MVP monolítico implementado ni afectan las reglas de este entregable.
- **Evidencia principal:** [código](https://github.com/TheEmmanuel2716/proyecto_prestamos_equipos_lab/blob/main/src/equipos.py), [pruebas](https://github.com/TheEmmanuel2716/proyecto_prestamos_equipos_lab/tree/main/tests) y [configuración](https://github.com/TheEmmanuel2716/proyecto_prestamos_equipos_lab/blob/main/pyproject.toml).

## 6. Reflexión ética y legal

| Principio                               | Decisión en mi proyecto                                                                                                                                                    | Evidencia                                                                                                                                                                                                                                                         |
| --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Datos personales (Ley 1581 de 2012)     | Uso exclusivo de datos sintéticos y ficticios en pruebas y documentación; sin datos personales reales                                                                      | [registro_pruebas.md](https://github.com/TheEmmanuel2716/proyecto_prestamos_equipos_lab/blob/main/registro_pruebas.md) y [tests](https://github.com/TheEmmanuel2716/proyecto_prestamos_equipos_lab/tree/main/tests)                                               |
| Sesgo                                   | Inclusión deliberada de nombres y textos sintéticos variados y caracteres del español (`José Muñoz`, `María Peña`, `D'Marco Peña`) sin asumir formatos rígidos excluyentes | [test_reglas_negocio_s7.py](https://github.com/TheEmmanuel2716/proyecto_prestamos_equipos_lab/blob/main/tests/test_reglas_negocio_s7.py) y [registro_pruebas.md](https://github.com/TheEmmanuel2716/proyecto_prestamos_equipos_lab/blob/main/registro_pruebas.md) |
| Transparencia                           | Registro explícito de qué produjo o sugirió la IA, qué se aceptó, modificó o rechazó y qué quedó pendiente                                                                 | [bitacora_ia.md](https://github.com/TheEmmanuel2716/proyecto_prestamos_equipos_lab/blob/main/bitacora_ia.md) y [revision_seguridad.md](https://github.com/TheEmmanuel2716/proyecto_prestamos_equipos_lab/blob/main/revision_seguridad.md)                         |
| Responsabilidad                         | Validación humana de cada cambio, restauración tras pruebas de rotura y verificación con `pytest`, `ruff` y `pip-audit`                                                    | [bitacora_ia.md](https://github.com/TheEmmanuel2716/proyecto_prestamos_equipos_lab/blob/main/bitacora_ia.md) y [revision_seguridad.md](https://github.com/TheEmmanuel2716/proyecto_prestamos_equipos_lab/blob/main/revision_seguridad.md)                         |
| Propiedad intelectual y política de uso | Respeto a las reglas del seminario, uso responsable de herramientas de IA, exclusión de secretos y archivos locales mediante `.gitignore`                                  | [.gitignore](https://github.com/TheEmmanuel2716/proyecto_prestamos_equipos_lab/blob/main/.gitignore) y [bitacora_ia.md](https://github.com/TheEmmanuel2716/proyecto_prestamos_equipos_lab/blob/main/bitacora_ia.md)                                               |

El dilema ético más importante fue equilibrar la rapidez que ofrece la IA para generar código y pruebas con la responsabilidad de no dar por válida una salida sin comprobarla ni asumir que todo el sistema está terminado cuando aún existen pendientes. Resolverlo implicó someter las sugerencias de la IA a pruebas reales, auditoría de seguridad y rotura intencional, además de reportar con honestidad el alcance real implementado y los pendientes del sistema.

## 7. Aprendizajes

Aprendí a estructurar reglas de negocio antes de codificar, a escribir pruebas parametrizadas y de bordes con `pytest`, a auditar código y dependencias con `ruff` y `pip-audit`, y a documentar decisiones técnicas con trazabilidad. Confíe de más en la IA cuando asumí que sus propuestas o predicciones estaban listas sin revisar imports, casos borde o coherencia documental.

También aprendí que una prueba verde no es suficiente por sí sola: el código debe pasar revisión humana, el resultado debe coincidir con el contrato y las pruebas deben detectar cambios intencionales. Si comenzara de nuevo, definiría desde la primera semana los límites del sistema, los formatos de salida y los casos ambiguos. Mantendría la documentación sincronizada en cada hito para evitar discrepancias al consolidar.

## 8. Anexos

- [README del proyecto](https://github.com/TheEmmanuel2716/proyecto_prestamos_equipos_lab/blob/main/README.md)
- [Código principal](https://github.com/TheEmmanuel2716/proyecto_prestamos_equipos_lab/blob/main/src/equipos.py)
- [Bitácora de uso de IA](https://github.com/TheEmmanuel2716/proyecto_prestamos_equipos_lab/blob/main/bitacora_ia.md)
- [Registro de pruebas](https://github.com/TheEmmanuel2716/proyecto_prestamos_equipos_lab/blob/main/registro_pruebas.md)
- [Informe de revisión de código y seguridad](https://github.com/TheEmmanuel2716/proyecto_prestamos_equipos_lab/blob/main/revision_seguridad.md)
- [Pruebas automatizadas](https://github.com/TheEmmanuel2716/proyecto_prestamos_equipos_lab/tree/main/tests)
- [Configuración de Ruff](https://github.com/TheEmmanuel2716/proyecto_prestamos_equipos_lab/blob/main/pyproject.toml)
