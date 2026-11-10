$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path -LiteralPath 'C:\Users\Roberto\Documents\GitHub\Capstone').Path
$expectedRoot = 'C:\Users\Roberto\Documents\GitHub\Capstone'
if ($repoRoot -ne $expectedRoot) { throw 'La raíz del repositorio no coincide.' }
$appRelative = 'Fase 2\Evidencias Proyecto\BranchIt'
$appRoot = Join-Path $repoRoot $appRelative
$backupRoot = Join-Path $appRoot '.vercel\respaldo-organizacion-2026-10-19'
New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
$script:actions = @()
function Safe-Path([string]$relative) {
    $full = [IO.Path]::GetFullPath((Join-Path $repoRoot $relative))
    if (-not $full.StartsWith($repoRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw "Ruta fuera del repositorio: $full" }
    return $full
}
function Ensure-Directory([string]$relative) {
    $full = Safe-Path $relative
    if (-not (Test-Path -LiteralPath $full)) { New-Item -ItemType Directory -Path $full -Force | Out-Null }
    return $full
}
function Move-Evidence([string]$from, [string]$to) {
    $source = Safe-Path $from
    $target = Safe-Path $to
    if ($from -ceq $to) { return }
    if ($from.Equals($to,[StringComparison]::OrdinalIgnoreCase)) {
        $intermediate = Safe-Path ($from + '.renombrado-temporal')
        if (Test-Path -LiteralPath $intermediate) { throw 'Ya existe la ruta temporal de renombrado.' }
        Move-Item -LiteralPath $source -Destination $intermediate
        Move-Item -LiteralPath $intermediate -Destination $target
        $script:actions += [pscustomobject]@{tipo='normalizacion_nombre';origen=$from;destino=$to}
        return
    }
    if ((-not (Test-Path -LiteralPath $source)) -and (Test-Path -LiteralPath $target)) {
        $script:actions += [pscustomobject]@{tipo='movimiento_completado_previamente';origen=$from;destino=$to}
        return
    }
    if (-not (Test-Path -LiteralPath $source)) { throw "No existe el origen: $from" }
    if (Test-Path -LiteralPath $target) { throw "El destino ya existe: $to" }
    Ensure-Directory ([IO.Path]::GetDirectoryName($to)) | Out-Null
    Move-Item -LiteralPath $source -Destination $target
    $script:actions += [pscustomobject]@{tipo='movimiento';origen=$from;destino=$to}
}
function Copy-Attachment([string]$filename, [string]$to) {
    $source = Join-Path 'C:\Users\Roberto\Downloads' $filename
    $target = Safe-Path $to
    if (Test-Path -LiteralPath $target) {
        if ((Get-FileHash -LiteralPath $source).Hash -ne (Get-FileHash -LiteralPath $target).Hash) { throw "El destino ya existe con contenido diferente: $to" }
        $script:actions += [pscustomobject]@{tipo='adjunto_copiado_previamente';origen=$source;destino=$to}
        return
    }
    Ensure-Directory ([IO.Path]::GetDirectoryName($to)) | Out-Null
    Copy-Item -LiteralPath $source -Destination $target
    if ((Get-FileHash -LiteralPath $source).Hash -ne (Get-FileHash -LiteralPath $target).Hash) { throw "Copia no íntegra: $filename" }
    $script:actions += [pscustomobject]@{tipo='adjunto';origen=$source;destino=$to}
}
function Write-Guide([string]$relative,[string]$text) {
    $target = Safe-Path $relative
    Ensure-Directory ([IO.Path]::GetDirectoryName($relative)) | Out-Null
    if (Test-Path -LiteralPath $target -PathType Leaf) {
        $backupName = $relative.Replace('\','__')
        Copy-Item -LiteralPath $target -Destination (Join-Path $backupRoot $backupName)
    }
    [IO.File]::WriteAllText($target, $text + "`n", [Text.UTF8Encoding]::new($false))
    $script:actions += [pscustomobject]@{tipo='indice';destino=$relative}
}
# Solo se trasladan evidencias generadas; frontend, backend, migraciones y configuración conservan sus rutas.
Move-Evidence "$appRelative\docs\presentacion\BranchIT_Avances_Proyecto.pptx" 'Fase 2\Evidencias Proyecto\Presentacion Proyecto.pptx'
Move-Evidence "$appRelative\docs\diagrama" 'Fase 2\Evidencias Proyecto\Base de datos\Diagrama'
Move-Evidence "$appRelative\docs\mapa-tecnologico" 'Fase 2\Evidencias Proyecto\Evidencias de documentacion\Mapa tecnologico'
Copy-Attachment 'Resumen evidencias (1).xlsx' 'Pauta de evidencias.xlsx'
Copy-Attachment 'BranchIT_Informe_Contexto_para_Codex.docx' 'Fase 2\Evidencias Proyecto\Evidencias de documentacion\Contexto\BranchIT_Informe_Contexto_para_Codex.docx'
Copy-Attachment 'Presentacion proyecto (1).pptx' 'Fase 2\Evidencias Proyecto\Evidencias de documentacion\Referencias\Presentacion original.pptx'
Copy-Attachment '1.5_GuiaEstudiante_Fase 1_Definicion Proyecto APT (2).docx' 'Fase 1\Evidencias Grupales\Versiones de referencia\1.5_Definicion Proyecto APT - adjunto.docx'
Move-Evidence 'Fase 1\Evidencias Individuales\Orrego_roberto_1.3_APT122_AutoevaluacionFase1.docx' 'Fase 1\Evidencias Individuales\Orrego_Roberto_1.3_APT122_AutoevaluacionFase1.docx'
# Los marcadores originales se conservan fuera de las carpetas de entrega principales.
Move-Evidence 'Fase 2\Evidencias Grupales\notas.txt' 'Fase 2\Evidencias Proyecto\Evidencias de documentacion\Referencias\Marcadores originales\notas.txt'
Move-Evidence 'Fase 2\Evidencias Proyecto\notas 2.txt' 'Fase 2\Evidencias Proyecto\Evidencias de documentacion\Referencias\Marcadores originales\notas 2.txt'
Ensure-Directory 'Fase 2\Evidencias Individuales' | Out-Null
Write-Guide 'README.md' @'
# BranchIT · Proyecto de título

Repositorio del proyecto Capstone de Duoc UC. La entrega se organiza por fase y tipo de evidencia, de acuerdo con [la pauta proporcionada](Pauta%20de%20evidencias.xlsx).

## Accesos principales

- [Fase 1: definición](Fase%201/README.md).
- [Fase 2: desarrollo y avance](Fase%202/README.md).
- [Fase 3: cierre](Fase%203/README.md).
- [Presentación de avance actualizada](Fase%202/Evidencias%20Proyecto/Presentacion%20Proyecto.pptx).
- [Aplicación BranchIT](Fase%202/Evidencias%20Proyecto/BranchIt/README.md).
- [Documentación del proyecto](Fase%202/Evidencias%20Proyecto/Evidencias%20de%20documentacion/README.md).
- [Base de datos y diagrama](Fase%202/Evidencias%20Proyecto/Base%20de%20datos/README.md).
- [Estado de las evidencias](ESTADO_EVIDENCIAS.md).

## Organización

```text
Fase 1/
  Evidencias Individuales/
  Evidencias Grupales/
Fase 2/
  Evidencias Individuales/
  Evidencias Grupales/
  Evidencias Proyecto/
    Presentacion Proyecto.pptx
    Evidencias de documentacion/
    Base de datos/
    BranchIt/                     # aplicación y documentación técnica
Fase 3/
  Evidencias Individuales/
  Evidencias Grupales/
```

Las guías y planillas que todavía no han sido incorporadas se enumeran en el estado de evidencias. No se crean entregables vacíos que aparenten estar completos. Los documentos en inglés son optativos según la pauta.

La carpeta local `Fase 2 Version Cristobal` conserva una copia de comparación; no representa la aplicación principal ni forma parte de esta clasificación de entregables.

El código conserva su ubicación para mantener la configuración de Vercel. Las migraciones permanecen junto a la API. Las credenciales, dependencias y archivos temporales siguen excluidos por las reglas existentes de Git. Los cambios están preparados localmente; el equipo gestiona su publicación en GitHub.
'@
Write-Guide 'Fase 1\README.md' @'
# Fase 1 · Definición del proyecto

## Evidencias individuales

En [Evidencias Individuales](Evidencias%20Individuales/) se conservan las tres entregas de cada integrante: autoevaluación de competencias 1.1, diario de reflexión 1.2 y autoevaluación 1.3.

Integrantes: Cristobal Lara, Roberto Orrego y Matías Werner. Los archivos se mantienen en una sola carpeta con el prefijo `Apellido_Nombre`, como indica la pauta.

## Evidencias grupales

En [Evidencias Grupales](Evidencias%20Grupales/) están la presentación inicial, el documento 1.4, la definición 1.5 en español y la planilla de evaluación de Fase 1.

La guía 1.5 adjuntada en este chat se conserva en `Evidencias Grupales/Versiones de referencia/`. Su contenido difiere de la guía que ya estaba en el repositorio; no reemplaza automáticamente la versión de entrega existente.

La versión en inglés de la definición es optativa y no se encontró entre los archivos revisados.
'@
Write-Guide 'Fase 2\README.md' @'
# Fase 2 · Desarrollo del proyecto

| Carpeta | Contenido |
| --- | --- |
| [Evidencias Individuales](Evidencias%20Individuales/) | Diarios de reflexión de Fase 2 por integrante. Pendientes de incorporar. |
| [Evidencias Grupales](Evidencias%20Grupales/) | Guía de desarrollo 2.4, informe final 2.6 y planillas de evaluación. Pendientes de incorporar. |
| [Evidencias Proyecto](Evidencias%20Proyecto/README.md) | Presentación de avance, documentación, aplicación y base de datos. |

La carpeta de la aplicación y sus configuraciones de despliegue conservan las rutas existentes.
'@
Write-Guide 'Fase 2\Evidencias Individuales\README.md' @'
# Evidencias individuales · Fase 2

Aquí corresponde incorporar el diario de reflexión de Fase 2 de cada integrante, con el patrón de la pauta:

`Apellido_Nombre_2.1_APT122_DiarioReflexionFase2.docx`

No se encontraron estos documentos en el repositorio ni entre los adjuntos autorizados. Este índice no reemplaza las evidencias individuales.
'@
Write-Guide 'Fase 2\Evidencias Grupales\README.md' @'
# Evidencias grupales · Fase 2

Pendientes de incorporar, según la pauta:

- `2.4_GuiaEstudiante_Fase 2_DesarrolloProyecto APT (Español).docx`.
- `PLANILLA DE EVALUACION AVANCE FASE 2.xlsx`.
- `2.6_GuiaEstudiante_Fase 2_Informe Final Proyecto APT (Español).docx`.
- `PLANILLA DE EVALUACION FINAL FASE 2.xlsx`.

Las versiones en inglés de las guías 2.4 y 2.6 son optativas. No se generaron documentos sustitutos ni se rellenaron formularios académicos.
'@
Write-Guide 'Fase 2\Evidencias Proyecto\README.md' @'
# Evidencias del proyecto · Fase 2

- [Presentación de avance](Presentacion%20Proyecto.pptx): versión actualizada con arquitectura, avances y sprints condensados.
- [Evidencias de documentación](Evidencias%20de%20documentacion/README.md): contexto, mapa tecnológico y accesos a la documentación técnica y a los sprints.
- [Aplicación BranchIT](BranchIt/README.md): frontend, API, pruebas y configuración de despliegue.
- [Base de datos](Base%20de%20datos/README.md): diagrama y referencias al esquema y a las migraciones.

La presentación original se conserva como referencia dentro de la documentación. La presentación inicial de Fase 1 permanece en su propia fase.
'@
Write-Guide 'Fase 2\Evidencias Proyecto\Evidencias de documentacion\README.md' @'
# Evidencias de documentación

- [Informe de contexto](Contexto/BranchIT_Informe_Contexto_para_Codex.docx): antecedente aportado por Roberto; puede describir un estado anterior de la aplicación.
- [Mapa tecnológico](Mapa%20tecnologico/README.md): imagen y vector del stack del proyecto.
- [Documentación técnica](../BranchIt/docs/): accesibilidad, integración, despliegue, formularios, notificaciones, afinidad y orientación con IA.
- [Sprints y capturas](../BranchIt/sprints/): registros de implementación y evidencias visuales. Los registros históricos describen su fecha de elaboración.
- [Base de datos](../Base%20de%20datos/README.md): diagrama del esquema y migraciones.
- [Presentación original](Referencias/Presentacion%20original.pptx): fuente de la actualización de avance.

La documentación técnica se mantiene junto al código para conservar sus referencias relativas y facilitar su mantenimiento. Este índice permite localizarla desde la estructura académica de entrega.
'@
Write-Guide 'Fase 2\Evidencias Proyecto\Base de datos\README.md' @'
# Evidencias de base de datos

- [Diagrama e inventario del esquema](Diagrama/README.md): ocho tablas de aplicación y diez claves foráneas, según los modelos hasta `0008_entrevista_diaria`.
- [Diagrama PNG](Diagrama/branchit.png), [SVG](Diagrama/branchit.svg) y [visor local](Diagrama/branchit.html).
- [DDL de referencia](Diagrama/branchit.sql): describe el esquema; no debe ejecutarse sobre una base existente.
- [Modelos SQLAlchemy](../BranchIt/backend/app/models.py).
- [Migraciones Alembic](../BranchIt/backend/migrations/versions/).
- [Instrucciones de despliegue y migración](../BranchIt/docs/DESPLIEGUE_VERCEL.md).

PostgreSQL se aloja en Neon. Este conjunto documenta la estructura y no contiene un respaldo de datos de producción ni credenciales. Los archivos multimedia se almacenan en Vercel Blob. Las migraciones permanecen dentro de la API para conservar su funcionamiento.
'@
Write-Guide 'Fase 3\README.md' @'
# Fase 3 · Cierre del proyecto

- [Evidencias Individuales](Evidencias%20Individuales/README.md): diarios de reflexión de Fase 3.
- [Evidencias Grupales](Evidencias%20Grupales/README.md): evaluación y presentación final.

Las carpetas están preparadas. No se encontraron entregables de esta fase entre los archivos revisados.
'@
Write-Guide 'Fase 3\Evidencias Individuales\README.md' @'
# Evidencias individuales · Fase 3

Pendiente el diario de reflexión de cada integrante:

`Apellido_Nombre_3.1_APT122_DiarioReflexionFase3.docx`
'@
Write-Guide 'Fase 3\Evidencias Grupales\README.md' @'
# Evidencias grupales · Fase 3

Pendientes de incorporar:

- `PLANILLA DE EVALUACIÓN FASE 3.xlsx`.
- `Presentación Final del proyecto (Español).pptx`.
- `Presentación Final del proyecto (Inglés).pptx`, optativa.

La presentación de avance de Fase 2 no se duplica aquí como si fuera la entrega final.
'@
Write-Guide 'ESTADO_EVIDENCIAS.md' @'
# Estado de las evidencias

Inventario de archivos disponibles al 19 de octubre de 2026. La presencia de un archivo no valida su contenido académico. Fuente: [Pauta de evidencias](Pauta%20de%20evidencias.xlsx), hoja «Resumen de evidencias por fase».

| Fase | Evidencia | Estado |
| --- | --- | --- |
| 1 | 1.1, 1.2 y 1.3 de cada integrante | Nueve documentos presentes. |
| 1 | Presentación del proyecto | Presente en Evidencias Grupales. |
| 1 | Formativa 1.4 | Presente. |
| 1 | Definición 1.5, español | Presente; un adjunto distinto conservado como referencia. |
| 1 | Planilla de evaluación | Presente. |
| 1 | Definición 1.5, inglés | No encontrada; optativa. |
| 2 | Diario de reflexión 2.1 | No encontrado; incorporar las entregas individuales. |
| 2 | Guía de desarrollo 2.4, español | No encontrada. |
| 2 | Evaluación de avance | No encontrada. |
| 2 | Informe final 2.6, español | No encontrado. |
| 2 | Evaluación final | No encontrada. |
| 2 | Guías 2.4 y 2.6, inglés | No encontradas; optativas. |
| 2 | Presentación del proyecto | Avance actualizado presente. |
| 2 | Documentación | Contexto, mapa, documentación técnica y registros de sprints presentes. |
| 2 | Aplicación | Código, pruebas y configuración presentes en BranchIt. |
| 2 | Base de datos | Diagrama, DDL de referencia, modelos y migraciones presentes. Sin volcado de datos de producción. |
| 3 | Diario de reflexión 3.1 | No encontrado. |
| 3 | Planilla de evaluación | No encontrada. |
| 3 | Presentación final, español | No encontrada. |
| 3 | Presentación final, inglés | No encontrada; optativa. |

Las cantidades globales de la pauta no se usan para inferir documentos adicionales cuyo nombre no esté especificado. Confirmar con el docente si se exigen varias entradas de diario durante la Fase 2.

La guía de definición adjuntada tiene contenido diferente a la existente. Revisar ambas antes de elegir una nueva versión oficial. La versión existente no se sobrescribió.
'@
# Corregir una carpeta vacía llamada README.md y crear una guía real de la aplicación.
$readmePath = Safe-Path "$appRelative\README.md"
if (Test-Path -LiteralPath $readmePath -PathType Container) {
    if (@(Get-ChildItem -LiteralPath $readmePath -Force).Count -ne 0) { throw 'La carpeta README.md contiene archivos; no se elimina.' }
    Remove-Item -LiteralPath $readmePath
}
Write-Guide "$appRelative\README.md" @'
# BranchIT · Aplicación

- `frontend/`: interfaz React y funciones de archivos de Vercel.
- `backend/`: API FastAPI, modelos, migraciones, scripts y pruebas.
- [Documentación técnica](docs/DESPLIEGUE_VERCEL.md): ejecución, variables y despliegue.
- [Sprints y evidencias](sprints/README.md).
- [Documentación académica](../Evidencias%20de%20documentacion/README.md).
- [Base de datos y diagrama](../Base%20de%20datos/README.md).
- [Presentación de avance](../Presentacion%20Proyecto.pptx).

Para Vercel, las raíces siguen siendo `Fase 2/Evidencias Proyecto/BranchIt/frontend` y `Fase 2/Evidencias Proyecto/BranchIt/backend`. Las migraciones se mantienen en `backend/migrations`.

Las dependencias, variables privadas y temporales no son entregables académicos y siguen fuera de Git según las reglas existentes.
'@
Write-Guide "$appRelative\database\README.md" @'
# Base de datos de BranchIT

El esquema se mantiene en [los modelos](../backend/app/models.py) y [las migraciones Alembic](../backend/migrations/versions/).

El diagrama y las evidencias académicas se encuentran en [Base de datos](../../Base%20de%20datos/README.md). No hay una segunda base de datos en esta carpeta.
'@
# Eliminar únicamente el contenedor vacío que quedó al trasladar la presentación.
$oldPresentation = Safe-Path "$appRelative\docs\presentacion"
if ((Test-Path -LiteralPath $oldPresentation -PathType Container) -and @(Get-ChildItem -LiteralPath $oldPresentation -Force).Count -eq 0) { Remove-Item -LiteralPath $oldPresentation }
$script:actions | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $backupRoot 'operaciones.json') -Encoding utf8
Write-Output "Organización completada: $($script:actions.Count) operaciones."
