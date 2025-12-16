# Script de inicio rapido para el proyecto
# Quick start script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Sistema de Gestion de Tickets E-SEUS  " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si existe el entorno virtual
if (!(Test-Path "venv")) {
    Write-Host "[!] No se encontro el entorno virtual. Creandolo..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "[OK] Entorno virtual creado" -ForegroundColor Green
}

# Activar entorno virtual
Write-Host "[*] Activando entorno virtual..." -ForegroundColor Blue
& ".\venv\Scripts\Activate.ps1"

# Verificar si existe el archivo .env
if (!(Test-Path ".env")) {
    Write-Host "[!] No se encontro el archivo .env" -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Write-Host "[*] Copiando .env.example a .env..." -ForegroundColor Blue
        Copy-Item ".env.example" ".env"
        Write-Host "[OK] Archivo .env creado. Por favor, configura tus variables de entorno." -ForegroundColor Green
    }
}

# Instalar dependencias si no estan instaladas
Write-Host "[*] Instalando dependencias..." -ForegroundColor Blue
pip install -r requirements.txt --quiet

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Error al instalar dependencias" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Dependencias instaladas" -ForegroundColor Green

# Limpiar migraciones antiguas
Write-Host ""
Write-Host "[*] Limpiando migraciones antiguas..." -ForegroundColor Blue
if (Test-Path "apps\tickets\migrations") {
    Get-ChildItem "apps\tickets\migrations\*.py" | Where-Object { $_.Name -ne "__init__.py" } | Remove-Item -Force
    Write-Host "[OK] Migraciones antiguas eliminadas" -ForegroundColor Green
}

# Crear nuevas migraciones
Write-Host "[*] Creando migraciones..." -ForegroundColor Blue
python manage.py makemigrations

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Error al crear migraciones" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Migraciones creadas" -ForegroundColor Green

# Aplicar migraciones
Write-Host ""
Write-Host "[*] Aplicando migraciones..." -ForegroundColor Blue
python manage.py migrate --noinput

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Error al aplicar migraciones" -ForegroundColor Red
    Write-Host "[TIP] Verifica tu configuracion de base de datos en .env" -ForegroundColor Yellow
    exit 1
}

Write-Host "[OK] Migraciones aplicadas" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Sistema listo para usar" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Iniciando servidor de desarrollo..." -ForegroundColor Cyan
Write-Host ""
Write-Host "El servidor estara disponible en:" -ForegroundColor White
Write-Host "   http://127.0.0.1:8000/ (redirige a documentacion)" -ForegroundColor White
Write-Host "   http://127.0.0.1:8000/api/docs/ (documentacion API)" -ForegroundColor White
Write-Host "   http://127.0.0.1:8000/admin/ (panel de administracion)" -ForegroundColor White
Write-Host ""
Write-Host "Para detener el servidor presiona: CTRL+C" -ForegroundColor Yellow
Write-Host ""

# Iniciar servidor
python manage.py runserver
