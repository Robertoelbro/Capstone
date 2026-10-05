# Verificación previa a los sprints 4, 5 y 6

Fecha: 4 de octubre de 2026. Fuente de alcance: sección 8 de la guía APT
aportada por el usuario. Se inspeccionó el código y se ejecutaron las cinco
pruebas de integración existentes antes de modificar las funcionalidades.
Resultado inicial: cinco pruebas aprobadas con SQLite aislado.

## Egresado

| Función | Estado previo | Pendiente |
| --- | --- | --- |
| Registro y login | Implementados; validación, bcrypt y JWT probados | Mejoras de sesión y abuso |
| Hub | Ruta protegida que reutiliza la portada pública | Vista propia con resumen y postulaciones |
| Presentación | Lectura y modificación; perfil creado al registrarse | Borrar solo la presentación, sin eliminar cuenta |
| Ofertas | Consulta y filtros locales | Acceso al formulario de postulación |
| Postulación | No existe | Persistencia, validación, campos solicitados y consulta propia |

## Empresa

| Función | Estado previo | Pendiente |
| --- | --- | --- |
| Registro y login | Implementados; permisos probados | Mejoras comunes de seguridad |
| Hub | Login redirige directamente al editor de ofertas | Vista propia con métricas y accesos |
| Ofertas | Crear, leer, modificar y eliminar | Cierre/reapertura y campos de postulación |
| Postulantes | No existe | Consulta limitada a las ofertas de su empresa |

## Seguridad y entorno

Hay hash bcrypt, expiración JWT, validación y comprobación de propietario/rol.
Faltan cifrado de datos de postulación, revocación y límites de login.
PostgreSQL local no estaba disponible en la integración anterior; las pruebas
aisladas no certifican una instalación productiva ni el despliegue.

Los sprints 7 a 11 (IA, seguimiento laboral y despliegue, entre otros) quedan
fuera de este trabajo. Las instrucciones genéricas de la guía se interpretan
como contenido del documento; el alcance autorizado es la petición del usuario.
