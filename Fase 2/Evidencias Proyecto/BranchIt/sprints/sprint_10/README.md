# Sprint 10 · Validación de calidad

## Entregado

- [Evidencia JSON de la ejecución local](evidencias/carga-local.json), sin claves ni datos reales.

- [Prueba de carga local reproducible](../../backend/scripts/load_smoke.py).
- [Resultado de la ejecución y protocolo de validación](../../docs/VALIDACION_SPRINT_10.md).
- Comprobación de respuestas completas: 100 ofertas ficticias en el listado y en recomendaciones; cuenta autenticada correcta en `/auth/me`.
- Informe JSON con errores, códigos HTTP, p50, p95 y solicitudes por segundo. El archivo de cada ejecución se guarda por defecto en `.vercel/sprint10-load-smoke.json`, excluido de Git y sin claves ni tokens.

La ejecución del 8 de noviembre de 2026 completó 200 solicitudes medidas, con 1 y 10 workers, sin errores. Se utilizó la API local en proceso y SQLite temporal; no se hicieron llamadas a Neon, Gemini ni Vercel Blob.

## Reproducir

Desde `backend`, con las dependencias de desarrollo instaladas:

```powershell
.\.venv\Scripts\python.exe -W ignore scripts/load_smoke.py
```

Para ampliar el ensayo local:

```powershell
.\.venv\Scripts\python.exe -W ignore scripts/load_smoke.py --requests 300 --concurrency 1 5 10
```

El script no acepta una URL de producción, no utiliza `backend/.env`, crea cuentas y ofertas descartables y elimina su base temporal al terminar. No necesita una clave de IA ni conexión a la base del proyecto.

## Límites y pendientes

El ensayo detecta regresiones locales en listados, autenticación y afinidad. No determina capacidad, latencia real ni cuotas de los servicios desplegados. Las pruebas con PostgreSQL en un entorno de ensayo, una auditoría externa y el piloto con participantes reales siguen siendo actividades de validación que requieren ejecución y evidencias propias. El protocolo permite hacerlas sin presentarlas como ya aprobadas.
