# Remediación de credenciales · 9 de noviembre de 2026

## Hallazgo y alcance revisado

El commit `8370dc7` añadió archivos temporales de `.vercel/` y `frontend/.vercel/` que debían permanecer locales. Se detectaron valores de claves de aplicación y archivos de cuentas de prueba en ese conjunto. Este informe no contiene valores, fragmentos de secretos, cadenas de conexión, tokens, correos ni contraseñas.

La inspección inicial fue local: nombres, presencia, longitudes, forma de los valores y patrones. La intervención posterior, registrada más abajo, incluyó rotación de tres claves, recifrado en Neon y verificación de los despliegues nuevos. No se publica material privado de esas operaciones. Una clave presente en un archivo histórico no acredita que siga vigente; borrar su archivo tampoco la invalida.

## Inventario sin valores

| Archivo o variable | Resultado de clasificación inicial | Estado después de la intervención |
| --- | --- | --- |
| `.vercel/forms-production.env`: `SECRET_KEY` | Valor presente de 64 caracteres. | Clave nueva privada en la API; JWT anterior rechazado y sesión nueva válida. Despliegues antiguos retirados. |
| Mismo archivo: `DATA_ENCRYPTION_KEY` | Valor presente de 44 caracteres con formato Fernet válido. | Clave nueva privada; siete valores recifrados y verificados, con respaldo cifrado local privado. La clave anterior ya no descifra esos siete valores. |
| Mismo archivo: `MEDIA_SERVICE_SECRET` y `.vercel/media-service-key` | Valores presentes de 64 caracteres; ambas copias coinciden. | Clave nueva privada en `branchit` y `branchit-api`; ambos proyectos redesplegados y rechazo de la clave anterior comprobado. |
| Mismo archivo: `DATABASE_URL` | Es un marcador enmascarado; no es una URI PostgreSQL utilizable. | No se confirmó exposición de una credencial real de Neon; no se afirma que su contraseña se haya cambiado. Los despliegues antiguos fueron retirados. |
| Mismo archivo: `GEMINI_API_KEY` | Es un marcador enmascarado; no tiene forma de una clave Google API. | No se confirmó exposición de la clave real de Gemini ni se afirma que haya sido rotada. |
| Mismo archivo: `VERCEL_OIDC_TOKEN` | JWT presente; su campo `exp` ya estaba vencido al revisarlo. Solo se decodificó el payload localmente, sin verificar firma. | No afirmarlo vigente ni reutilizarlo. Revisar sesiones, despliegues y acceso de la cuenta; el vencimiento no elimina la necesidad de limpiar el repositorio. |
| `.vercel/company_accounts.json`, `.vercel/demo-credentials.json`, CSV de testing | Contienen estructuras de cuentas y campos de contraseña de demostración. | Fuera del seguimiento en el commit local de limpieza; conservados en el PC. No se cambiaron intencionalmente las contraseñas de prueba. Su eventual cambio requiere una decisión posterior. |
| JSON de creación/despliegue y `frontend/.vercel/project.json` | Metadatos de proyecto y despliegue, no equivalen por sí solos a una clave de API. | Retirados del seguimiento y mantenidos localmente cuando correspondía. |

Se comprobaron patrones locales de GitHub PAT (`gh…_` y `github_pat_`), Vercel PAT prefijado (`vcp_`), Google API (`AIza…`) y Vercel Blob de lectura/escritura en 49 archivos inmediatos de tipo JSON, env, Python, JavaScript y CSV de las carpetas temporales revisadas. No hubo coincidencias. **Esto no acredita ausencia total de secretos**: tokens sin prefijo, otros formatos, subcarpetas, binarios, historial y copias externas pueden requerir revisión adicional. No se enviaron los archivos a un escáner externo.

## Secuencia de remediación

Este procedimiento conserva el orden necesario para futuras intervenciones. El estado efectivamente ejecutado aparece en las secciones de resultados y pendientes; no debe leerse esta lista como una nueva rotación por realizar de las claves ya reemplazadas.

1. **Contener la publicación.** Mantener pospuesto el despliegue pendiente mientras se ordenan las credenciales. Retirar del seguimiento de Git los temporales, conservando las copias privadas necesarias en el PC. La eliminación de un commit posterior no borra el historial ni invalida claves.
2. **Revisar accesos y despliegues anteriores.** Proteger o retirar vistas previas y despliegues que todavía utilicen las claves viejas. Una API antigua con el JWT anterior y acceso a la misma BD puede seguir aceptando sesiones firmadas con la clave expuesta, aunque el alias principal ya use una nueva. Registrar qué entornos fueron retirados y cuáles todavía requieren intervención.
3. **Cambiar JWT y secreto de archivos.** Generar valores nuevos fuera de Git. Cambiar `SECRET_KEY` en la API y `MEDIA_SERVICE_SECRET` tanto en `branchit` como en `branchit-api`. Redesplegar los consumidores correspondientes, probar acceso autorizado y rechazo de firmas/sesiones antiguas. El cambio JWT obliga a iniciar sesión otra vez. No borrar datos para revocar sesiones.
4. **Preparar la rotación Fernet sin pérdida de información.** Seguir el procedimiento específico de abajo; no cambiar primero `DATA_ENCRYPTION_KEY` en Vercel. El código actual utiliza una sola clave y no tiene lectura automática con claves anteriores.
5. **Revisar proveedores.** En Neon, comprobar roles, conexiones y contraseñas que usan los entornos afectados; cambiar la contraseña o el rol si estuvo expuesto o si un despliegue anterior aún puede acceder. Actualizar la conexión privada y reiniciar los consumidores para no conservar pools viejos. En Gemini, revisar claves y actividad; crear una nueva y revocar la anterior si se confirma exposición o se decide rotar preventivamente. Revisar también tokens de Blob, Vercel y GitHub si aparecen en la revisión ampliada. En esta intervención se confirmaron marcadores enmascarados para Neon y Gemini, no sus claves reales.
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

El commit local `651ff5a` retira 200 archivos temporales del seguimiento sin borrar las copias del PC. También quedó activo un control local previo al commit para reducir la reintroducción de archivos privados. Ese control local no equivale a protección de todos los clones ni reemplaza revisar lo que se publica. El usuario hará el push; esta intervención no afirma que el commit de limpieza ya esté en GitHub.

## Resultados de la intervención en producción

Durante la ventana de mantenimiento se activó protección total de despliegues. Se reemplazaron como variables privadas `SECRET_KEY` y `DATA_ENCRYPTION_KEY` en la API, y `MEDIA_SERVICE_SECRET` en la API y el frontend. No se publican sus valores. Los despliegues nuevos quedaron en estado READY:

| Proyecto | Despliegue nuevo |
| --- | --- |
| API | `dpl_EJ6EPtTKZihX6PdtmFGVwMXXcsQr` |
| Frontend | `dpl_4n9MUn23LF8ty1UNMTUBnMCKUBh7` |

Se retiraron 57 despliegues anteriores: 29 de la API, incluido uno bloqueado, y 28 del frontend. El inventario posterior contiene solo el despliegue nuevo de cada proyecto. No se borraron los proyectos ni la base de datos.

El recifrado abarcó siete valores en Neon: en el esquema público, dos postulaciones y una entrevista; en respaldos existentes, tres postulaciones y una entrevista. Los siete se verificaron con la clave nueva y rechazaron la anterior. Se conservó un respaldo cifrado local privado para recuperación. No se incluyen datos descifrados ni rutas privadas del respaldo en este informe.

| Comprobación | Resultado registrado |
| --- | --- |
| Disponibilidad de la API: `/health/ready` | HTTP 200. |
| Listado público de ofertas | 100 ofertas conservadas. |
| Lectura autorizada de antecedentes | Dos postulaciones leídas por el reclutador de prueba después de iniciar sesión. |
| Sesión con JWT anterior | HTTP 401. |
| Sesión con JWT nuevo | HTTP 200. |
| Validación de archivos con secreto anterior | HTTP 403. |
| Validación con secreto nuevo e identificador de archivo inexistente | HTTP 404, coherente con validación del secreto y ausencia del recurso. No se modificaron archivos. |
| Cierre de la sesión de prueba | HTTP 204. |
| Bypass de automatización creado por la CLI durante la intervención | Revocado después de utilizarlo. |

Estas comprobaciones no constituyen una auditoría externa ni prueban que nunca se haya accedido al material histórico. No se realizaron cobros ni se cambiaron las contraseñas de las cuentas de demostración.

La rama de producción se actualizó mediante API a `main` en ambos proyectos y se confirmó con una lectura posterior. El repositorio enlazado y las carpetas de construcción se conservaron. Se restauró la protección original de las vistas previas y se comprobó la retirada del bypass temporal. La web pública mostró las 100 ofertas y la API quedó como producción actual en estado READY. Cambiar la rama no equivale a publicar en GitHub el commit local de limpieza.

## Estado de ejecución

| Acción | Estado de esta revisión |
| --- | --- |
| Clasificar localmente archivos y patrones sin revelar valores | Realizada. |
| Retirar temporales del seguimiento | Realizado en el commit local `651ff5a`; 200 archivos conservados localmente. Push pendiente a cargo del usuario. |
| Control local previo al commit | Activo localmente. No se afirma su instalación en otros clones. |
| Cambiar JWT y secreto compartido de archivos | Realizado y comprobado en los despliegues nuevos. |
| Respaldar y recifrar con nueva clave Fernet | Realizado: siete valores verificados con la clave nueva; la anterior no los descifra. Respaldo cifrado local privado conservado. |
| Credenciales reales de Neon y Gemini expuestas | No confirmado: los campos revisados eran marcadores enmascarados. No se atribuye una rotación no ejecutada. |
| Proteger la ventana y retirar despliegues antiguos | Protección total durante la intervención; 57 despliegues retirados, con uno nuevo por proyecto en el inventario posterior. |
| Actualizar rama de producción a `main` | Confirmada mediante lectura posterior en ambos proyectos; repositorio y carpetas de construcción conservados. |
| Verificar producción | Comprobaciones de disponibilidad, datos, sesiones y secreto de archivos registradas arriba. |
| Revocar bypass temporal de automatización | Realizado. |
| Limpiar historial remoto y coordinar clones | Pendiente de decisión y ejecución coordinada. |
| Publicar limpieza local en GitHub | Pendiente: lo realizará el usuario. |

La exposición histórica sigue pendiente de coordinación: retirar archivos de la versión actual y rotar claves no borra `8370dc7`, las ramas o las copias anteriores. No se reescribió el historial ni se hizo push desde esta intervención. Las verificaciones se documentaron sin secretos ni datos personales.
