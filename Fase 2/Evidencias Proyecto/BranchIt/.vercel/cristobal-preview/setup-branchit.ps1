<#
    setup-branchit.ps1
    ----------------------------------------------------------------
    Instala (si falta) todo lo necesario para correr BranchIt en
    local: Node.js, Python y PostgreSQL, y deja listas las
    dependencias de frontend y backend.

    COMO USARLO:
    1) Copia este archivo DENTRO de la carpeta BranchIt (la que
       contiene las carpetas "frontend" y "backend").
    2) Abre PowerShell en esa carpeta (botón derecho > "Abrir en
       Terminal" o "Abrir ventana de PowerShell aquí").
    3) Ejecuta:
         powershell -ExecutionPolicy Bypass -File .\setup-branchit.ps1
       (Windows bloquea por defecto los scripts descargados; el
       -ExecutionPolicy Bypass es solo para esta ejecución, no cambia
       nada permanente en tu equipo)
    ----------------------------------------------------------------
#>

$ErrorActionPreference = "Stop"

function Write-Step($msg) {
    Write-Host ""
    Write-Host "== $msg ==" -ForegroundColor Cyan
}

function Test-CommandExists($name) {
    return [bool](Get-Command $name -ErrorAction SilentlyContinue)
}

# ---------------------------------------------------------------
# 0) Verificar que estamos parados en la carpeta correcta
# ---------------------------------------------------------------
if (-not (Test-Path ".\frontend") -or -not (Test-Path ".\backend")) {
    Write-Host "No encuentro las carpetas 'frontend' y 'backend' en esta ubicación." -ForegroundColor Red
    Write-Host "Mueve este .ps1 dentro de la carpeta BranchIt y vuelve a intentar." -ForegroundColor Red
    exit 1
}

# ---------------------------------------------------------------
# 1) winget (gestor de paquetes de Windows)
# ---------------------------------------------------------------
if (-not (Test-CommandExists "winget")) {
    Write-Host "No tienes 'winget' disponible (viene con Windows 10/11 actualizado)." -ForegroundColor Red
    Write-Host "Actualiza la app 'Instalador de aplicaciones' desde la Microsoft Store e intenta de nuevo." -ForegroundColor Red
    exit 1
}

# ---------------------------------------------------------------
# 2) Node.js
# ---------------------------------------------------------------
Write-Step "Node.js"
if (Test-CommandExists "node") {
    Write-Host "Ya instalado: $(node --version)" -ForegroundColor Green
} else {
    Write-Host "Instalando Node.js LTS..."
    winget install -e --id OpenJS.NodeJS.LTS --accept-source-agreements --accept-package-agreements
    Write-Host "Instalado. Puede que necesites abrir una terminal nueva para usarlo." -ForegroundColor Yellow
}

# ---------------------------------------------------------------
# 3) Python
# ---------------------------------------------------------------
Write-Step "Python"
$pythonOk = $false
try {
    python --version *> $null
    if ($LASTEXITCODE -eq 0) { $pythonOk = $true }
} catch { $pythonOk = $false }

if ($pythonOk) {
    Write-Host "Ya instalado: $(python --version)" -ForegroundColor Green
} else {
    Write-Host "Instalando Python 3.12..."
    winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements
    Write-Host "Instalado. IMPORTANTE: cierra esta terminal y abre una nueva antes de seguir," -ForegroundColor Yellow
    Write-Host "para que Windows reconozca el comando 'python'. Luego vuelve a correr este script." -ForegroundColor Yellow
    exit 0
}

# ---------------------------------------------------------------
# 4) PostgreSQL
#    (No es obligatorio todavía para lo que hay hoy en el backend,
#    pero lo dejamos listo para cuando se conecte a la base de datos)
# ---------------------------------------------------------------
Write-Step "PostgreSQL"
if (Test-CommandExists "psql") {
    Write-Host "Ya instalado." -ForegroundColor Green
} else {
    Write-Host "Instalando PostgreSQL 16..."
    winget install -e --id PostgreSQL.PostgreSQL.16 --accept-source-agreements --accept-package-agreements
    Write-Host "Instalado. Durante la instalación se pide una contraseña para el usuario 'postgres':" -ForegroundColor Yellow
    Write-Host "anótala, la vas a necesitar más adelante para conectar el backend a la base de datos." -ForegroundColor Yellow
}

# ---------------------------------------------------------------
# 5) Backend: entorno virtual + dependencias Python
# ---------------------------------------------------------------
Write-Step "Backend (entorno virtual + dependencias)"
Push-Location backend
if (-not (Test-Path ".venv")) {
    python -m venv .venv
}
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
deactivate
Pop-Location

# ---------------------------------------------------------------
# 6) Frontend: dependencias npm
# ---------------------------------------------------------------
Write-Step "Frontend (dependencias npm)"
Push-Location frontend
npm install
Pop-Location

# ---------------------------------------------------------------
# Listo
# ---------------------------------------------------------------
Write-Step "Todo listo"
Write-Host "Para levantar el backend (deja esta terminal corriendo):" -ForegroundColor Green
Write-Host "  cd backend"
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host "  uvicorn app.main:app --reload"
Write-Host ""
Write-Host "Para levantar el frontend (ábrelo en OTRA terminal):" -ForegroundColor Green
Write-Host "  cd frontend"
Write-Host "  npm run dev"
Write-Host ""
Write-Host "El frontend queda en http://localhost:5173" -ForegroundColor Green
