# Reinicio de empresas y postulaciones

El generador `backend/scripts/seed_jobs.py` crea diez empresas ficticias, diez ofertas por empresa y cien ofertas distribuidas en diez categorías. Las credenciales de testing se mantienen: `seed.branchit.v1.0@example.com` hasta `seed.branchit.v1.9@example.com`, contraseña **contraseña**.

Cada cuenta incluye RUT chileno ficticio con dígito verificador válido, teléfono, fecha de creación, nombre y giro. Cada oferta incluye sueldo mensual bruto CLP, funciones, información del cargo, perfiles canónicos de egreso, condiciones laborales, modalidad y respuesta sobre adaptación para discapacidad. Las preguntas alternan entre ninguna, texto corto, texto largo, número, selección única y selección múltiple. Todas comienzan abiertas, sin postulantes ni candidatos seleccionados.

## Alcance del reinicio

El modo de reinicio elimina de las tablas activas **todas** las cuentas de empresa, perfiles de empresa, ofertas, postulaciones y metadatos de archivos pertenecientes a empresas. Conserva las cuentas, perfiles, contraseñas, RUT, portafolios y archivos de egresados. No reinicia secuencias ni reutiliza a propósito identificadores de cuentas; las cuentas demo nuevas usan versiones de sesión nuevas. No borra los objetos físicos de Vercel Blob: conserva sus referencias en el respaldo privado.

Los datos anteriores se respaldan antes de borrar. Si falla una inserción o una verificación, se revierte la transacción completa. Se comprueba que los datos de egresados permanezcan exactamente iguales y que el resultado sea 10 empresas, 100 ofertas y cero postulaciones. Requiere la migración `0006_cierre_convocatorias`.

## Ejecución desde terminal

Desde `backend`, con `DATABASE_URL` configurada para la base elegida:

```powershell
# Vista previa, sin escribir en la BD
.\.venv\Scripts\python.exe scripts/seed_jobs.py

# Añadir datos demo sin borrar ni modificar ofertas existentes
.\.venv\Scripts\python.exe scripts/seed_jobs.py --apply

# Reinicio completo solicitado; respaldo JSON privado en .vercel/
.\.venv\Scripts\python.exe scripts/seed_jobs.py --apply --reset-companies --confirm-reset BORRAR_EMPRESAS_Y_POSTULACIONES
```

La consola muestra el host y la base de destino sin credenciales. Si existen empresas demo de la versión anterior, no se sobrescriben con `--apply`; se utiliza el reinicio explícito.

Para generar el bloque SQL equivalente para Neon, sin ejecutarlo:

```powershell
.\.venv\Scripts\python.exe scripts/seed_jobs.py --sql ../.vercel/reset-empresas-v2.sql --backup-schema branchit_backup_20261018_reset_v2
```

Ese SQL crea un esquema privado de respaldo con las cuentas de empresa, perfiles, ofertas, postulaciones y metadatos anteriores. No cambies el nombre del esquema por uno ya existente. El archivo SQL y los respaldos locales se mantienen fuera de Git mediante `.vercel/`.

Se puede añadir `--accounts-csv ../.vercel/empresas_testing.csv` para exportar las credenciales y datos ficticios; no se exportan datos de cuentas reales.

## Verificación y estado

Reinicio ejecutado y verificado en Neon el **18 de octubre de 2026**, después de la confirmación del usuario:

| Verificación | Cantidad |
| --- | ---: |
| Empresas nuevas | 10 |
| Ofertas completas y abiertas | 100 |
| Postulaciones actuales | 0 |
| Egresados conservados | 2 |
| Empresas anteriores respaldadas | 13 |
| Ofertas anteriores respaldadas | 101 |
| Postulaciones anteriores respaldadas | 3 |
| Registros de archivos de empresa respaldados | 2 |

Respaldo privado en el esquema **`branchit_backup_20261018_reset_v2`** de la misma base Neon. La transacción verificó que las cuentas, perfiles y archivos de egresados permanecieran iguales. No se cambiaron las migraciones ni se reiniciaron secuencias.

Las **35 pruebas de backend** pasan, incluyendo registro y ofertas con los esquemas actuales, idempotencia, respaldo, conservación de egresados y reversión ante fallo. También se completó el mapeo de áreas para carreras del catálogo que aún no coincidían: redes/telecomunicaciones, tecnología médica, fonoaudiología, recursos humanos, artes visuales, marketing y bibliotecología.

Comprobación contra la API publicada: los diez accesos demo funcionan, cada empresa consulta sus diez ofertas y el listado público devuelve las cien ofertas completas. Esta verificación no creó postulaciones ni cerró convocatorias.

El reinicio de datos ya está aplicado en Neon. Los cambios del generador, pruebas y mapeo de carreras quedan locales para publicarlos en GitHub.
