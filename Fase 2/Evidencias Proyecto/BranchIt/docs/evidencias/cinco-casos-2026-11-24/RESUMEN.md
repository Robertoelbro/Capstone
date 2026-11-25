# BranchIT: cinco casos de prueba

Fecha: 24 de noviembre de 2026, America/Santiago.

Resultado: **5 casos aprobados, 0 fallidos**. Se ejecutó la API real mediante FastAPI TestClient, con datos ficticios y una base SQLite en memoria independiente para cada caso. No se modificó Neon ni producción.

| Caso | Procedimiento | Resultado observado | Estado |
| --- | --- | --- | --- |
| CP-01 Registro y sesión | Registrar egresado, ingresar, editar y eliminar su perfil. | Registro 201 y login 200; contraseña almacenada distinta del texto original; edición 200; eliminación 204; sesión invalidada con 401. | Aprobado |
| CP-02 Credenciales inválidas | Repetir correo con mayúsculas; ingresar con contraseña incorrecta y usuario inexistente. | Duplicado 409; ambos accesos inválidos 401 y mensaje genérico idéntico. | Aprobado |
| CP-03 Roles y ofertas | Crear como empresa, intentar acceso como egresado y empresa ajena; cerrar y eliminar. | Sin sesión 401; egresado 403; creación 201; acceso ajeno rechazado; oferta cerrada desaparece del listado público; eliminación 204. | Aprobado |
| CP-04 Privacidad del portafolio | Consultar privado, publicar sin contacto, autorizar correo y despublicar. | Privado 404; correo y teléfono ocultos al publicar; solo se muestra correo tras autorización; despublicado 404. | Aprobado |
| CP-05 Contratación | Elegir finalista entre dos candidatos, intentar nueva postulación y liberar con respaldo ficticio. | Contratación 200; nuevas postulaciones 409; segundo candidato conserva acceso sin conocer al seleccionado; fecha original conservada; liberación antes de un año habilita búsqueda. | Aprobado |

## Evidencia y reproducción

- `informe.html`: informe navegable con pasos, expectativas y respuestas HTTP por caso.
- `resultados.json`: estado, duración, trazas HTTP y huellas SHA-256 de los archivos de aplicación y pruebas.
- `ejecucion.txt`: salida original de unittest con los cinco resultados `OK`.
- `junit.xml`: resultados en formato para herramientas de integración continua.
- Ejecución desde `backend`: `.\.venv\Scripts\python.exe scripts/evidence_five_cases.py`.

Se reutilizaron cinco pruebas funcionales existentes y se añadió un ejecutor que registra evidencia sin cuerpos de solicitudes, contraseñas, tokens ni cabeceras. Los estados de rechazo esperados (401, 403, 404 y 409) son resultados correctos de los controles de acceso, no fallos del ensayo.

Límites: no se verificó interfaz visual, navegador, carga, despliegue Vercel, conexión Neon, subida real de PDF ni servicios externos de Gemini o Transbank. El caso de finiquito utiliza un registro ficticio de archivo verificado; no valida su contenido ni realiza una carga a Blob. El entorno emitió una advertencia de deprecación de Starlette sobre httpx; no impidió la ejecución ni produjo fallos.

## Tecnologías verificadas en el proyecto

| Área | Tecnologías y uso |
| --- | --- |
| Interfaz | JavaScript, React 18, HTML y CSS; Tailwind CSS y React Icons para presentación; React Router para navegación. |
| Construcción | Vite, npm, PostCSS y Autoprefixer. |
| API | Python, FastAPI, Pydantic para validación y Uvicorn para ejecución local. |
| Datos | PostgreSQL alojado en Neon; SQLAlchemy para acceso, psycopg2 como controlador y Alembic para migraciones. |
| Archivos | Vercel Blob para fotos, videos y documentos. |
| Seguridad | bcrypt para contraseñas, JWT mediante python-jose para sesiones y Cryptography/Fernet para cifrado de datos seleccionados. |
| IA | API de Google Gemini para orientación del egresado y práctica de entrevistas. |
| Pagos | API Webpay Plus de Transbank implementada para integración; estos cinco casos no ejercitan pagos ni acreditan su estado productivo actual. |
| Despliegue y métricas | Vercel y Vercel Web Analytics. |
| Calidad | unittest, FastAPI TestClient y httpx para pruebas de API; SQLite en memoria para aislamiento; pruebas nativas Node y ESLint en frontend. |
| Versiones | Git y GitHub. |

Fuentes revisadas: `frontend/package.json`, `backend/requirements.txt`, `backend/requirements-dev.txt`, módulos de seguridad, cifrado, IA y Webpay, y entrada React con Analytics. La lista describe el proyecto; no implica que cada tecnología se haya ejercitado en estos cinco casos.
