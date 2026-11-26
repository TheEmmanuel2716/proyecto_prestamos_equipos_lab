# Informe de revisión de código y seguridad

- **Proyecto:** Gestión monolítica de préstamos de equipos de laboratorio
- **Estudiante:** Emmanuel Steven González Muñoz
- **Fecha de la auditoría:** 26 de noviembre de 2026
- **Commit revisado:** `96f042d`
- **Herramientas:** `pytest`, `ruff`, `pip-audit`, `git` e inspección directa del
  código y las pruebas

## 1. Alcance y criterios

Se revisaron `src/equipos.py`, las cinco suites de `tests/`, la configuración,
los archivos técnicos y el estado de Git. La revisión comprobó normalización,
validaciones, transacciones, SQL parametrizado, estados, devoluciones,
historial, datos sintéticos y higiene del repositorio.

## 2. Riesgos revisados

| Punto | Resultado comprobado |
|---|---|
| Inyección SQL | Las consultas dinámicas usan parámetros nombrados o `?`. Los textos maliciosos se guardaron como datos en pruebas. |
| Validación de entradas | Textos vacíos y valores no textuales producen `ValueError`; no se abre una base para registros inválidos de equipo. |
| Integridad del préstamo | El equipo debe existir y estar disponible. Préstamo y cambio de estado se realizan dentro de una transacción. |
| Devoluciones | Segunda devolución y préstamo inexistente se rechazan sin alterar el registro activo. |
| Secretos y datos reales | No se encontraron credenciales ni datos reales de personas. Las pruebas usan nombres sintéticos. |
| Control de acceso | No aplica: no existe interfaz web ni autenticación en el MVP. |
| Dependencias | `pip-audit -r requirements.txt` no reportó vulnerabilidades conocidas. |
| Archivos residuales | `.env`, `.venv/`, cachés y archivos SQLite están excluidos por `.gitignore`. |

## 3. Hallazgos de la auditoría

| Id | Hallazgo | Severidad | Validación | Resultado |
|---|---|---|---|---|
| H-A1 | El manejo de `sqlite3.IntegrityError` podía traducir cualquier violación de integridad a “duplicado”. | Media | Lectura de `_guardar_equipo` y análisis de ramas. | Corregido: ahora se traduce a duplicado solo si la clave ya existe; las demás violaciones se propagan. |
| H-A2 | Faltaban pruebas para préstamos con campos no textuales y para devoluciones por ID inexistente o ya devuelto. | Baja | Inspección de `tests/` y ejecución de `pytest`. | Corregido: se agregaron casos de borde; las alias de historial también quedaron cubiertas. |
| H-A3 | El informe histórico conservaba pendientes ya resueltos y afirmaciones de una revisión anterior. | Baja | Contraste entre el documento, el código y el estado actual. | Corregido: este documento reemplaza el registro histórico obsoleto con resultados verificables de la auditoría actual. |
| H-A4 | El intento de una prueba podía colarse en el estado por falta de configuración estricta. | Sin riesgo encontrado | Revisión del código. | No aplica: no hay condiciones de red ni secretos. |

**Estado:** no quedan hallazgos críticos ni altos abiertos.

## 4. Resultado del linter

La configuración usa `ruff` con las familias `E`, `F`, `B` y `S`, y excluye `S101`
solo dentro de `tests/` porque `assert` es el mecanismo normal de pytest. Tras
la auditoría se volverá a ejecutar el linter completo.

## 5. Pendientes reales y fuera de alcance

- Interfaz web o CLI interactiva: no implementada en el MVP monolítico.
- Autenticación, contraseñas y roles: no requeridos por el modelo actual.
- Formato calendario avanzado y vencimientos: no se definió en el contrato vigente.
- Límites máximos de longitud: el laboratorio no entregó límites y no se impusieron
  arbitrariamente.

Estos elementos no afectan las funciones implementadas ni las reglas de entrega
ya validadas.
