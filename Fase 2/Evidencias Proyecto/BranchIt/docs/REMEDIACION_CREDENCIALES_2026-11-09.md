# Remediación de credenciales · 9 de noviembre de 2026

## Hallazgo y alcance revisado

El commit `8370dc7` añadió archivos temporales de `.vercel/` y `frontend/.vercel/` que debían permanecer locales. Se detectaron valores de claves de aplicación y archivos de cuentas de prueba en ese conjunto. Este informe no contiene valores, fragmentos de secretos, cadenas de conexión, tokens, correos ni contraseñas.

La revisión fue local: nombres, presencia, longitudes, forma de los valores y patrones. No se probaron las credenciales contra servicios externos ni se verificó que coincidan con las variables actuales de producción. Una clave presente en un archivo histórico no acredita que siga vigente; debe tratarse como expuesta si estuvo en uso.

## Inventario sin valores

| Archivo o variable | Resultado de clasificación | Acción necesaria |
| --- | --- | --- |
| `.vercel/forms-production.env`: `SECRET_KEY` | Valor presente de 64 caracteres. No se comparó con producción. | Rotar la clave JWT si corresponde a un entorno utilizado; invalidar sesiones anteriores y retirar despliegues que aún la acepten. |
| Mismo archivo: `DATA_ENCRYPTION_KEY` | Valor presente de 44 caracteres con formato Fernet válido. | Preparar respaldo y recifrado completo antes de cambiar la clave de lectura. No sustituirla directamente. |
| Mismo archivo: `MEDIA_SERVICE_SECRET` y `.vercel/media-service-key` | Valores presentes de 64 caracteres; ambas copias coinciden. | Rotar en los dos proyectos que comparten la validación de archivos y redesplegarlos coordinadamente. |
| Mismo archivo: `DATABASE_URL` | Es un marcador enmascarado; no es una URI PostgreSQL utilizable. | No se acreditó exposición de la contraseña Neon en este archivo. Revisar las demás ubicaciones y los despliegues antiguos; rotar si se confirma exposición o no se pueden retirar entornos con acceso anterior. |
| Mismo archivo: `GEMINI_API_KEY` | Es un marcador enmascarado; no tiene forma de una clave Google API. | No se acreditó exposición de la clave real aquí. Revisar en AI Studio/Google Cloud y revocar o rotar si aparece en otra ubicación. |
| Mismo archivo: `VERCEL_OIDC_TOKEN` | JWT presente; su campo `exp` ya estaba vencido al revisarlo. Solo se decodificó el payload localmente, sin verificar firma. | No afirmarlo vigente ni reutilizarlo. Revisar sesiones, despliegues y acceso de la cuenta; el vencimiento no elimina la necesidad de limpiar el repositorio. |
| `.vercel/company_accounts.json`, `.vercel/demo-credentials.json`, CSV de testing | Contienen estructuras de cuentas y campos de contraseña de demostración. | Retirar del repositorio y cambiar las contraseñas de cuentas que todavía permitan acceso, especialmente si tienen datos o funciones de producción. |
| JSON de creación/despliegue y `frontend/.vercel/project.json` | Metadatos de proyecto y despliegue, no equivalen por sí solos a una clave de API. | Mantener locales cuando no sean necesarios para la entrega; revisar permisos de la cuenta sin publicar identificadores adicionales. |

Se comprobaron patrones locales de GitHub PAT (`gh…_` y `github_pat_`), Vercel PAT prefijado (`vcp_`), Google API (`AIza…`) y Vercel Blob de lectura/escritura en 49 archivos inmediatos de tipo JSON, env, Python, JavaScript y CSV de las carpetas temporales revisadas. No hubo coincidencias. **Esto no acredita ausencia total de secretos**: tokens sin prefijo, otros formatos, subcarpetas, binarios, historial y copias externas pueden requerir revisión adicional. No se enviaron los archivos a un escáner externo.

## Secuencia de remediación

1. **Contener la publicación.** Mantener pospuesto el despliegue pendiente mientras se ordenan las credenciales. Retirar del seguimiento de Git los temporales, conservando las copias privadas necesarias en el PC. La eliminación de un commit posterior no borra el historial ni invalida claves.
2. **Revisar accesos y despliegues anteriores.** Proteger o retirar vistas previas y despliegues que todavía utilicen las claves viejas. Una API antigua con el JWT anterior y acceso a la misma BD puede seguir aceptando sesiones firmadas con la clave expuesta, aunque el alias principal ya use una nueva. Registrar qué entornos fueron retirados y cuáles todavía requieren intervención.
3. **Cambiar JWT y secreto de archivos.** Generar valores nuevos fuera de Git. Cambiar `SECRET_KEY` en la API y `MEDIA_SERVICE_SECRET` tanto en `branchit` como en `branchit-api`. Redesplegar los consumidores correspondientes, probar acceso autorizado y rechazo de firmas/sesiones antiguas. El cambio JWT obliga a iniciar sesión otra vez. No borrar datos para revocar sesiones.
4. **Preparar la rotación Fernet sin pérdida de información.** Seguir el procedimiento específico de abajo; no cambiar primero `DATA_ENCRYPTION_KEY` en Vercel. El código actual utiliza una sola clave y no tiene lectura automática con claves anteriores.
5. **Revisar proveedores.** En Neon, comprobar roles, conexiones y contraseñas que usan los entornos afectados; cambiar la contraseña o el rol si estuvo expuesto o si un despliegue anterior aún puede acceder. Actualizar la conexión privada y reiniciar los consumidores para no conservar pools viejos. En Gemini, revisar claves y actividad; crear una nueva y revocar la anterior si se confirma exposición o se decide rotar preventivamente. Revisar también tokens de Blob, Vercel y GitHub si aparecen en la revisión ampliada. No se han rotado ni revocado desde esta inspección.
6. **Limpiar historial y copias.** Tras revocar o rotar, evaluar la retirada de los archivos sensibles del historial remoto con el equipo. La reescritura afecta ramas y clones; requiere coordinarla para que otros colaboradores no reintroduzcan los archivos. Incluso una limpieza correcta no permite recuperar copias que alguien ya haya descargado.
7. **Verificar y registrar.** Ejecutar pruebas sin secretos reales, revisar el nuevo diff y repetir la detección local. Confirmar que las claves antiguas ya no autorizan acceso a entornos vivos y que los datos cifrados siguen legibles con la nueva clave. Guardar evidencias con resultados y fechas, sin incluir valores.

## Cambio de DATA_ENCRYPTION_KEY y recifrado

El modelo actual tiene `datos_cifrados` en `postulaciones`, `entrevistas_ia` y `seguimiento_laboral`. Una revisión del esquema vigente debe confirmar todas las columnas cifradas antes de ejecutar el cambio. Los archivos binarios en Blob no se recifran mediante esta clave; sí deben revisarse sus permisos y credenciales de acceso por separado.

- Preparar una ventana de mantenimiento que impida escrituras y cierres de sesión de entrevista concurrentes. Inventariar las filas y guardar un respaldo de BD con acceso restringido y cifrado independiente. La clave anterior se conserva temporalmente solo en un medio privado para permitir recuperación y pruebas, nunca en el repositorio ni en logs.
- Ensayar primero sobre una copia aislada: descifrar cada fila con la clave anterior, comprobar que el JSON es válido, cifrar con la nueva y verificar su lectura. Registrar únicamente tabla, conteos y estado; no volcar texto privado, tokens ni nombres de usuarios.
- Definir una operación transaccional, o una estrategia por lotes con seguimiento que permita revertir sin mezclar claves de forma indetectable. Si una fila no puede descifrarse, detener el proceso e investigar; no borrarla ni reemplazarla con datos vacíos.
- Con escrituras detenidas, aplicar el recifrado validado y comprobar que todas las filas esperadas se pueden leer con la nueva clave. Coordinar entonces la variable del backend y el despliegue que la consume. Reabrir escrituras después de verificar lecturas y nuevas escrituras.
- Guardar una copia de recuperación protegida y sus instrucciones. Los respaldos antiguos cifrados con una clave expuesta necesitan medidas adicionales de almacenamiento y acceso; rotar la BD actual no vuelve seguros los ciphertexts antiguos que ya estén fuera de control.
- Eliminar o archivar de forma restringida la clave anterior una vez resuelta la retención y la recuperación. No prometer que una clave expuesta queda secreta de nuevo por borrar el archivo de Git.

## Prevención en Git

La raíz de BranchIT ya contiene reglas para `.vercel/`, `.env` y `.env.*`, y permite únicamente `.env.example` como plantilla. El frontend también excluye `.vercel` y `.env*`. Estas reglas **no dejan de rastrear archivos que ya se añadieron**, ni impiden un añadido forzado. Revisar siempre el diff preparado antes de publicar; las plantillas deben incluir solo nombres y marcadores de ejemplo.

No publicar carpetas de QA, credenciales de demostración, capturas con datos privados ni exportaciones de variables. Los informes compartibles deben contener resultados agregados y datos ficticios, como este documento.

## Estado de ejecución

| Acción | Estado de esta revisión |
| --- | --- |
| Clasificar localmente archivos y patrones sin revelar valores | Realizada. |
| Retirar temporales del seguimiento | Preparación a cargo del agente principal; verificar el commit resultante. |
| Cambiar JWT y secreto compartido de archivos | Pendiente de configuración y comprobación. |
| Respaldar y recifrar con nueva clave Fernet | Pendiente. No se modificaron filas ni claves. |
| Revisar/rotar credenciales Neon y Gemini según alcance confirmado | Pendiente. |
| Retirar o proteger despliegues antiguos | Pendiente de inventario y ejecución. |
| Limpiar historial remoto y coordinar clones | Pendiente de decisión y ejecución coordinada. |
| Verificar producción y registrar evidencia posterior | Pendiente. |

Esta inspección no consultó registros de producción, no hizo cobros, no cambió contraseñas y no revocó tokens. El estado pendiente debe actualizarse solo después de observar la acción y su resultado.
