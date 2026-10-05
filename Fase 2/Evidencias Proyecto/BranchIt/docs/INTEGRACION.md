# Integración de BranchIT

La aplicación integrada está en `Fase 2/Evidencias Proyecto/BranchIt`. La carpeta
`Fase 2 Version Cristobal/BranchIt` se conserva como referencia y no fue modificada.

Se incorporaron sus modelos, migración inicial, registro, perfil del egresado y
CRUD de ofertas. Se añadieron login JWT, comprobación de sesión y autorización
por propietario y tipo de cuenta. Se conservaron los contratos existentes
(`/auth`, `/egresados`, `/empresas`) para evitar romper la integración. La
separación futura en los cuatro dominios del informe queda pendiente.

El frontend conserva React 18, Vite 4, Tailwind, Poppins y el azul del template.
La portada y los formularios están en español y utilizan la API real. Los
componentes originales no utilizados permanecen como referencia visual.

## Preparación local

Desde `backend`, activar el entorno e instalar dependencias:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Crear `.env` a partir de `.env.example` únicamente si todavía no existe.
Configurar `DATABASE_URL` con una base PostgreSQL existente y `SECRET_KEY` con
un valor aleatorio de al menos 32 caracteres. Para generar una clave local:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

No publicar `.env`. La API y Alembic cargan el mismo archivo. La base debe estar
vacía para aplicar la migración inicial; si ya contiene tablas, revisar su
historial antes de migrar. No utilizar `stamp` para ocultar diferencias.

Con PostgreSQL disponible:

```powershell
alembic upgrade head
uvicorn app.main:app --reload
```

En otra terminal, desde `frontend`:

```powershell
npm install
npm run dev -- --port 5173
```

La API se espera en `http://localhost:8000`. Puede cambiarse mediante
`VITE_API_URL` en `frontend/.env`. Si se cambia el origen del frontend, actualizar
`CORS_ORIGINS` en `backend/.env`. Swagger está en `/docs`.

## Recorrido

1. Abrir `/registro` y seleccionar egresado o empresa.
2. Crear la cuenta; se muestra una confirmación y se solicita iniciar sesión.
3. Iniciar sesión en `/iniciar-sesion`.
4. El egresado accede a `/hub-egresado`; la empresa, a `/hub-empresa`.
   Desde allí navegan a presentación, ofertas y postulaciones.
5. Las ofertas publicadas aparecen en la portada y pueden filtrarse por cargo,
   empresa, ubicación y modalidad.

El token dura dos horas y se almacena en `sessionStorage` de la pestaña. La API
comprueba que la cuenta siga activa y que el propietario y rol coincidan con el
recurso. Cerrar sesión revoca en el servidor todos los tokens anteriores de
la cuenta y elimina el token de la pestaña. La recuperación de contraseña
sigue pendiente.
Contraseñas: mínimo ocho caracteres y máximo 72 bytes UTF-8, con bcrypt.

## Verificación

```powershell
# backend
pip install -r requirements-dev.txt
python -m unittest discover -s tests -v

# frontend
npm run lint
npm run build
```

Las pruebas usan SQLite aislado y no modifican PostgreSQL. Cubren registro,
duplicados, validación, login, expiración, cuentas desactivadas, perfiles,
CRUD de ofertas y protección contra acceso a cuentas ajenas.

## Límites actuales

- PostgreSQL local rechazó la conexión durante la integración; no se aplicaron
  migraciones a la base del usuario. El funcionamiento contra PostgreSQL queda
  pendiente hasta que el servicio y la base estén disponibles.
- Los sprints 4, 5 y 6 añadieron hubs, presentación, preguntas de ofertas,
  postulaciones e historial. Ver [evidencias de los sprints](../sprints/README.md).
- IA, recuperación de contraseña y seguimiento laboral siguen pendientes.
- Antes de producción: HTTPS, limitador compartido para múltiples workers,
  revisión de dependencias, gestión de claves y configuración de despliegue.
- La instalación detectó avisos de seguridad en el árbol de dependencias del
  frontend; no se aplicaron actualizaciones mayores automáticas del template.


## Actualización de sprints 4 a 6

Aplicar `alembic upgrade head` para incorporar `0002_postulaciones`.
Configurar también `DATA_ENCRYPTION_KEY` como clave Fernet válida en `.env` y
conservarla de forma segura; no regenerarla después de guardar postulaciones.
En este entorno se añadió una clave local sin mostrarla ni versionarla.
El cifrado protege los antecedentes de postulación; los datos operativos de
cuenta y perfil no están cifrados en sus tablas originales.

La guía completa, los límites y la vista temporal reproducible están en
[sprints/README.md](../sprints/README.md). La validación actual incluye 16 pruebas
API/migraciones, compilación, lint y recorridos de navegador con datos ficticios.
