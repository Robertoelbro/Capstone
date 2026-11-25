# Publicación en Vercel del 16 de noviembre de 2026

Se publicó la versión de trabajo verificada en las direcciones principales, conservando las variables privadas de producción. La publicación no utilizó las conexiones, claves ni cuentas del entorno aislado de QA.

| Componente | Resultado |
| --- | --- |
| Página principal | https://branchit-blue.vercel.app/ · HTTP 200 |
| API principal | https://branchit-api.vercel.app · `/health` y `/health/ready` con HTTP 200 |
| Frontend | `dpl_MueCc28qTNFXuRzQaNKh9LzfPDtT` · READY · Production |
| Backend | `dpl_3REhayDCeD7pTqMX6z1WyjAGxkmo` · READY · Production |
| Neon principal | `neondb`, migración `0013_pagos_webpay` |
| Ofertas públicas comprobadas | 100 |
| Acceso y suscripción | Inicio de sesión ficticio correcto; `/billing/me` con HTTP 200 |

La migración añadió únicamente la tabla de órdenes Webpay. Se ejecutó en una transacción, con límites de espera, respaldo de la revisión y conteos agregados en `branchit_backup_20261116_webpay`. Los conteos de usuarios, ofertas, postulaciones, entrevistas, seguimientos, suscripciones y archivos permanecieron iguales. No se crearon pagos ni suscripciones de producción durante la publicación.

Se comprobó que el archivo JavaScript publicado incluye la interfaz nueva de suscripción y apunta a la API principal, sin usar el dominio de QA. La API principal no emite el marcador del ensayo aislado y acepta el origen de la web pública.

## Pagos y validación pendiente

Webpay está implementado y fue validado con una tarjeta ficticia en el entorno de integración de QA, incluida la protección contra retornos simultáneos. Las credenciales de prueba se mantienen en el entorno autorizado de Preview. **El checkout de la página principal permanece deshabilitado**; esta publicación no habilita cobros reales ni copia la configuración de pagos de QA a producción.

La revisión funcional cuenta con una suite completa de 110 pruebas backend correctas, nueve pruebas Node y lint y compilación del frontend correctos. La prueba de carga sigue teniendo una incidencia abierta de `ReadTimeout`; no se declara aprobada ni se promete una capacidad de usuarios a partir de esos ensayos. Ver [incidencia de rendimiento](INCIDENCIA_RENDIMIENTO_QA_2026-11-16.md).

Esta publicación se hizo con la herramienta de Vercel desde una copia que excluye archivos privados y temporales. Los cambios del código fuente continúan disponibles en el PC para que el usuario los publique en GitHub conforme a su flujo de trabajo.
