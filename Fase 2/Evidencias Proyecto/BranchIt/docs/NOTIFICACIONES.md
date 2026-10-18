# Notificaciones de postulaciones

La campana aparece para cuentas autenticadas, con contador de avisos sin leer y un desplegable con las últimas 50 notificaciones. Abrir el panel no las marca automáticamente: abrir un aviso marca ese aviso; también se pueden marcar todas como leídas. El contador incluye todos los avisos pendientes, aunque haya más de 50.

Eventos implementados:

- Empresa: nueva postulación recibida, con enlace a las postulaciones de esa oferta.
- Egresado: convocatoria cerrada o reabierta, con enlace a sus postulaciones. No se comunica quién fue seleccionado.

Los eventos y el cambio que los origina se guardan en la misma transacción. Repetir un cierre sin cambiar el estado no genera avisos duplicados. No se generan avisos retroactivos. Cada cuenta solo consulta o marca sus propias notificaciones.

El frontend consulta al entrar, cada 30 segundos mientras la pestaña está visible, al recuperar el foco y al abrir el panel. No utiliza WebSockets ni notificaciones push del sistema.

## Actualización

Antes de desplegar el backend nuevo, aplicar la migración `0007_notificaciones` sobre la base correspondiente. Desde la carpeta `backend`, con `DATABASE_URL` configurada de forma privada para la base destino:

```powershell
.\.venv\Scripts\python.exe -m alembic current
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic current
```

La última salida debe indicar `0007_notificaciones (head)`. La migración añade una tabla y un índice; conserva empresas, ofertas, postulaciones y egresados. Después publicar los cambios de frontend y backend. No ejecutar con el `.env` local si se pretende actualizar Neon y ese archivo apunta a localhost.

Verificación local: 36 pruebas de backend, incluyendo permisos de lectura, marcado, cierre repetido, reapertura, privacidad y eliminación de cuenta; lint y build de frontend correctos. La prueba de migraciones verifica actualización y reversión con datos existentes y generación SQL para PostgreSQL. La migración de producción no se ha ejecutado como parte de este cambio.
