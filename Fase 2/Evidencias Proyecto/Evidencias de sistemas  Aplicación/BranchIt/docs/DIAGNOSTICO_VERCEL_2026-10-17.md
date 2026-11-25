# Diagnóstico de despliegues Vercel — 17 de octubre de 2026

Los últimos despliegues fallidos pertenecen a la rama `Cristobal`, commit
`b855856420b7a2c879ff868dff1652a88b3d67ca`, mensaje «Version Actual Branchlt».
Son vistas previas (`target: null`), no los despliegues de producción.

| Proyecto | Despliegue fallido | Error |
| --- | --- | --- |
| branchit | dpl_Fsvg8C2EygxzgxU3w4S6P17ZsDqD | NOW_SANDBOX_WORKER_ROOTDIR_NOT_EXIST |
| branchit-api | dpl_AStZPVFyVoqVXkZaLT1XQXsgH4U3 | NOW_SANDBOX_WORKER_ROOTDIR_NOT_EXIST |

La configuración espera `Fase 2/Evidencias Proyecto/BranchIt/frontend` y
`Fase 2/Evidencias Proyecto/BranchIt/backend`. El árbol del commit fallido solo
tiene los proyectos en `Fase 2 Version Cristobal/BranchIt/frontend` y
`Fase 2 Version Cristobal/BranchIt/backend`. Por eso el build falla antes de
instalar o compilar; este error no se origina en Neon ni en una consulta de API.

La rama productiva sigue siendo `Roberto-branch`. Ambos despliegues de producción
del commit `b597a8587e2b376ed5432dd03cf750714bf219eb` están READY. Comprobaciones
HTTP: frontend público 200; API `/api/employment/jobs` 200, con 101 ofertas.

No fue necesario restaurar producción ni cambiar las raíces globales. Para
integrar el trabajo del compañero hay que incorporar sus cambios a las carpetas
canónicas conservadas por la rama productiva, o crear proyectos Vercel separados
para su estructura. No apuntar los proyectos actuales a la carpeta de su rama,
porque eso rompería los siguientes despliegues de `Roberto-branch`.

No se aplicaron cambios a GitHub, Vercel, CORS ni Neon durante este diagnóstico.
