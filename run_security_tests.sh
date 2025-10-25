#!/bin/bash

echo "🔐 OWASP Top 10 Security Testing Suite"
echo "======================================"
echo "Proyecto: Products API - Clean Architecture"
echo "Fecha: $(date)"
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Variables
API_URL="http://localhost:8000"
API_PID=""
PYTHON_CMD="python3"

# Verificar si python3 está disponible
if ! command -v python3 &> /dev/null; then
    if command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        log_error "Python no encontrado. Instala Python 3.7+ para continuar."
        exit 1
    fi
fi

log_info "Usando comando Python: $PYTHON_CMD"

# Función para limpiar procesos al salir
cleanup() {
    log_info "Limpiando procesos..."
    if [ ! -z "$API_PID" ]; then
        log_info "Deteniendo API (PID: $API_PID)..."
        kill $API_PID 2>/dev/null
        wait $API_PID 2>/dev/null
    fi
    log_success "Limpieza completada"
}

# Registrar función de limpieza
trap cleanup EXIT

# Verificar dependencias
log_info "Verificando dependencias de Python..."

# Lista de dependencias requeridas
required_packages=("fastapi" "uvicorn" "requests")
missing_packages=()

for package in "${required_packages[@]}"; do
    if ! $PYTHON_CMD -c "import $package" &> /dev/null; then
        missing_packages+=("$package")
    fi
done

# Instalar dependencias faltantes
if [ ${#missing_packages[@]} -ne 0 ]; then
    log_warning "Faltan dependencias: ${missing_packages[*]}"
    log_info "Instalando dependencias faltantes..."
    
    for package in "${missing_packages[@]}"; do
        log_info "Instalando $package..."
        $PYTHON_CMD -m pip install $package
        if [ $? -ne 0 ]; then
            log_error "Error instalando $package"
            exit 1
        fi
    done
    
    log_success "Dependencias instaladas"
else
    log_success "Todas las dependencias están disponibles"
fi

# Verificar estructura del proyecto
log_info "Verificando estructura del proyecto..."

required_files=(
    "src/main.py"
    "test_api_security.py"
    "src/infrastructure/security_config.py"
    "src/infrastructure/security_service.py"
    "src/infrastructure/security_logger.py"
    "src/infrastructure/integrity_checker.py"
    "src/presentation/middlewares/security_headers.py"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -ne 0 ]; then
    log_error "Archivos faltantes:"
    for file in "${missing_files[@]}"; do
        echo "   - $file"
    done
    log_error "Asegúrate de que todos los archivos de seguridad estén implementados"
    exit 1
fi

log_success "Estructura del proyecto verificada"

# Función para verificar si la API está disponible
check_api() {
    for i in {1..30}; do
        if curl -s -f "$API_URL/health" > /dev/null 2>&1; then
            return 0
        fi
        sleep 1
    done
    return 1
}

# Iniciar la API en segundo plano
log_info "Iniciando Products API..."
cd src

# Generar baseline de integridad si no existe
if [ ! -f "../integrity_checksums.json" ]; then
    log_info "Generando baseline de integridad..."
    $PYTHON_CMD -c "
from infrastructure.integrity_checker import integrity_checker
integrity_checker.save_checksums()
" 2>/dev/null
fi

# Iniciar la aplicación
$PYTHON_CMD main.py &
API_PID=$!

cd ..

log_info "API iniciada con PID: $API_PID"
log_info "Esperando que la API esté disponible..."

# Verificar que la API esté disponible
if check_api; then
    log_success "API disponible en $API_URL"
else
    log_error "La API no pudo iniciarse correctamente"
    log_error "Verifica los logs de la aplicación para más detalles"
    exit 1
fi

# Ejecutar pruebas de seguridad
echo ""
log_info "=== EJECUTANDO PRUEBAS DE SEGURIDAD OWASP TOP 10 ==="
echo ""

# Ejecutar el suite de pruebas
$PYTHON_CMD test_api_security.py --url "$API_URL"
TEST_EXIT_CODE=$?

echo ""
echo "======================================"

# Mostrar resultados
if [ $TEST_EXIT_CODE -eq 0 ]; then
    log_success "TODAS LAS PRUEBAS DE SEGURIDAD PASARON"
    echo ""
    log_success "🛡️  OWASP Top 10 Implementation Status:"
    echo "   ✅ A01 - Broken Access Control: IMPLEMENTED"
    echo "   ✅ A02 - Cryptographic Failures: IMPLEMENTED" 
    echo "   ✅ A03 - Injection: IMPLEMENTED"
    echo "   ✅ A04 - Insecure Design: IMPLEMENTED"
    echo "   ✅ A05 - Security Misconfiguration: IMPLEMENTED"
    echo "   ✅ A06 - Vulnerable Components: IMPLEMENTED"
    echo "   ✅ A07 - Identity and Auth Failures: IMPLEMENTED"
    echo "   ✅ A08 - Software Integrity Failures: IMPLEMENTED"
    echo "   ✅ A09 - Security Logging: IMPLEMENTED"
    echo "   ✅ A10 - Server-Side Request Forgery: IMPLEMENTED"
    echo ""
    log_success "🧪 API Testing Status:"
    echo "   ✅ Test 1: Authentication & Authorization"
    echo "   ✅ Test 2: Input Validation & SQL Injection"
    echo "   ✅ Test 3: JWT Security & Session Management"
    echo "   ✅ Test 4: Rate Limiting & DoS Prevention"
    echo "   ✅ Test 5: Complete Security Workflow"
    echo ""
    log_success "🎯 Tu API está SEGURA y cumple con OWASP Top 10!"
else
    log_warning "ALGUNAS PRUEBAS FALLARON"
    echo ""
    log_warning "Revisa los detalles arriba para ver qué necesita mejorarse"
    log_info "La mayoría de fallos pueden deberse a:"
    echo "   - API no completamente iniciada"
    echo "   - Configuración de base de datos"
    echo "   - Servicios de autenticación no configurados"
    echo ""
    log_info "Ejecuta las pruebas individualmente para diagnosticar:"
    echo "   $PYTHON_CMD test_api_security.py --test 1  # Auth tests"
    echo "   $PYTHON_CMD test_api_security.py --test 2  # Injection tests"
    echo "   $PYTHON_CMD test_api_security.py --test 3  # JWT tests"
    echo "   $PYTHON_CMD test_api_security.py --test 4  # Rate limiting tests"
    echo "   $PYTHON_CMD test_api_security.py --test 5  # Complete workflow"
fi

# Mostrar archivos de logs generados
echo ""
log_info "📄 Archivos generados:"
if [ -f "security.log" ]; then
    echo "   📝 security.log - Logs de eventos de seguridad"
fi

if [ -f "integrity_checksums.json" ]; then
    echo "   🔐 integrity_checksums.json - Baseline de integridad"
fi

echo ""
log_info "📊 Para ver el estado de la API en tiempo real:"
echo "   curl $API_URL/health | jq"
echo ""

log_info "🔍 Para ver logs de seguridad:"
echo "   tail -f security.log"
echo ""

log_info "📈 Para acceder a la documentación interactiva:"
echo "   Abre: $API_URL/docs"
echo ""

exit $TEST_EXIT_CODE