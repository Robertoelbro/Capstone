# Sprint 6 — Postulaciones y protección de datos

## Empresa

Cada oferta admite hasta diez preguntas de texto corto, párrafo, número o
selección, opcionales u obligatorias. Las preguntas tienen identificadores
estables y el formulario incrementa su versión cuando cambia. La empresa
puede consultar únicamente las postulaciones de sus propias ofertas.

## Egresado

El formulario muestra qué empresa recibirá los datos. Permite compartir
teléfono, enlace de CV/portafolio y mensaje opcionales, además de responder las
preguntas requeridas. Solicita consentimiento explícito antes de enviar.
Muestra confirmación e historial del contenido enviado.

Se rechazan duplicados, ofertas cerradas, respuestas desconocidas, respuestas
obligatorias vacías, selecciones inválidas y formularios desactualizados.
Una restricción única de base de datos respalda la prevención de duplicados.
La operación toma un bloqueo sobre la oferta en PostgreSQL para coordinarse
con cambios de formulario o cierre.

## Seguridad implementada

- Contraseñas con hash bcrypt; no se cifran reversiblemente.
- Cifrado autenticado Fernet del conjunto de antecedentes de cada postulación:
  nombre, correo, carrera, presentación, contacto, mensaje y respuestas.
- Clave `DATA_ENCRYPTION_KEY` separada de la clave JWT y guardada fuera de Git.
  Su ausencia o corrupción bloquea la operación; nunca se guarda texto plano
  como alternativa. Respaldar la clave: perderla impide recuperar los datos.
- Comprobación de rol y propietario en backend antes de descifrar datos.
- Logout revoca todos los tokens previos de la cuenta mediante `token_version`.
- Límite de 20 solicitudes de autenticación por IP y minuto, con HTTP 429.
- Validaciones que no devuelven los valores de contraseña o contacto recibidos.
- Cabeceras `no-store`, `nosniff`, `DENY` y `no-referrer` en la API.
- URLs de perfil y CV limitadas a HTTP/HTTPS sin credenciales incrustadas.
- Copia de las preguntas y presentación dentro de la postulación para que
  cambios posteriores no alteren lo que se envió.

## Configuración

Generar una clave Fernet una sola vez y colocarla en `backend/.env`:

```powershell
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
alembic upgrade head
```

No reemplazar la clave después de guardar postulaciones sin un proceso de
rotación y recifrado. La migración es `0002_postulaciones` y conserva los datos
existentes de cuentas y ofertas; los tokens anteriores requieren nuevo login.

## Límites técnicos explícitos

El cifrado cubre los datos guardados en `postulaciones.datos_cifrados`. Los
campos originales del perfil y el correo de acceso siguen en sus tablas
operativas; esto no equivale a cifrado de toda la base. HTTPS y cifrado de
disco/copias de seguridad dependen del despliegue. Los enlaces de CV no son
archivos subidos ni alojados por BranchIT.

El limitador actual vive en memoria y es apropiado para un proceso local;
con varios workers debe sustituirse por un almacén compartido o gateway.
La clave debe administrarse mediante secretos del servidor en producción.
No se afirma una auditoría de seguridad completa ni una validación contra
PostgreSQL real, que permanece pendiente de disponibilidad.

## Evidencia

- `evidencias/formulario-postulacion.png`
- `evidencias/postulacion-recibida.png`
- Pruebas de cifrado, permisos, validación, duplicados, revocación y rate limit
  en `backend/tests/test_sprints.py`.
- Migración y SQL PostgreSQL en `backend/tests/test_migrations.py`.
