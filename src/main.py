"""
Main Application - Entry Point
Configuración principal de la aplicación FastAPI con Clean Architecture
Implementa OWASP Top 10 Security Standards
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Infrastructure Layer
from infrastructure.database import db_manager
from infrastructure.container import container

# Security Infrastructure
from infrastructure.security_config import security_config
from infrastructure.security_logger import security_logger
from infrastructure.integrity_checker import integrity_checker

# Presentation Layer - API Routes
from presentation.api.auth_routes import router as auth_router
from presentation.api.categories_routes import router as categories_router
from presentation.api.subcategories_routes import router as subcategories_router
from presentation.api.products_routes import router as products_router
from presentation.api.graphql_routes import router as graphql_router

# Security Middleware
from presentation.middlewares.auth import ConditionalAuthMiddleware
from presentation.middlewares.rolemiddleware import RoleBasedAuthMiddleware  
from presentation.middlewares.security_headers import SecurityHeadersMiddleware

# ============================================================================
# FastAPI Application Setup
# ============================================================================

app = FastAPI(
    title="Products API - Clean Architecture + OWASP Security",
    description="""
    API REST y GraphQL para gestión de productos con Clean Architecture
    
    ## 🔒 Características de Seguridad (OWASP Top 10):
    
    * **A01 - Access Control**: Role-based authentication con JWT
    * **A02 - Cryptographic Failures**: Hashing seguro y encriptación
    * **A03 - Injection**: Sanitización de inputs y validación
    * **A04 - Insecure Design**: Security-by-design patterns
    * **A05 - Security Misconfiguration**: Configuración centralizada
    * **A06 - Vulnerable Components**: Headers de seguridad
    * **A07 - Identity Failures**: JWT con expiración y validación
    * **A08 - Software Integrity**: Verificación de integridad
    * **A09 - Security Logging**: Logging completo de eventos
    * **A10 - SSRF**: Validación de requests
    
    ## 🏗️ Arquitectura:
    
    * **Clean Architecture**: Separación clara de responsabilidades
    * **JWT Authentication**: Tokens con expiración de 1 hora
    * **ACID Transactions**: Propiedades ACID en base de datos
    * **REST API**: Endpoints tradicionales para CRUD
    * **GraphQL**: Consultas flexibles y específicas
    * **Rate Limiting**: Protección contra DoS
    * **Input Validation**: Prevención de inyecciones
    
    ## 📊 Estructura de Datos:
    
    ```
    Categoría (ej: "Electrónicos")
    └── Subcategoría (ej: "Smartphones")
        └── Producto (ej: "iPhone 15 Pro")
    ```
    
    ## 🔐 Autenticación:
    
    1. Obtener token: `POST /auth/token`
    2. Usar token: `Authorization: Bearer {token}`
    3. El token expira en 1 hora
    4. Logs de seguridad automáticos
    
    ## 🛡️ Endpoints Protegidos:
    
    - POST, PUT, DELETE en `/products`
    - POST, DELETE en `/categories` (requiere admin)
    - POST, DELETE en `/subcategories` (requiere admin)
    - Mutaciones GraphQL
    
    ## 📋 Monitoring de Seguridad:
    
    - Logs en `security.log`
    - Verificación de integridad automática
    - Rate limiting por IP
    - Headers de seguridad automáticos
    """,
    version="2.0.0-secure",
    contact={
        "name": "Equipo de Desarrollo",
        "email": "dev@example.com"
    },
    license_info={
        "name": "MIT",
    }
)

# ============================================================================
# Security Middleware
# ============================================================================

# Security Headers (aplicar primero)
app.add_middleware(SecurityHeadersMiddleware)

# Rate Limiting y Role-based access control
app.add_middleware(RoleBasedAuthMiddleware)

# ============================================================================
# CORS Configuration
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=security_config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# ============================================================================
# Authentication Middleware
# ============================================================================

# Rutas protegidas que requieren JWT
protected_routes = [
    # Products
    ("/products", "POST"),
    ("/products", "PUT"),
    ("/products", "PATCH"),
    ("/products", "DELETE"),
    
    # Categories
    ("/categories", "POST"),
    ("/categories", "DELETE"),
    
    # Subcategories
    ("/subcategories", "POST"),
    ("/subcategories", "DELETE"),
    
    # GraphQL Mutations (todas las mutaciones)
    ("/graphql", "POST"),  # GraphQL usa POST para queries y mutations
]

app.add_middleware(ConditionalAuthMiddleware, protected_routes=protected_routes)

# ============================================================================
# API Routes Registration
# ============================================================================

# Authentication
app.include_router(auth_router)

# REST API Routes
app.include_router(categories_router)
app.include_router(subcategories_router)
app.include_router(products_router)

# GraphQL Route
app.include_router(graphql_router)

# ============================================================================
# Root and Health Check Endpoints
# ============================================================================

@app.get("/", tags=["root"])
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "message": "Products API - Clean Architecture + OWASP Security",
        "version": "2.0.0-secure",
        "description": "API para gestión de productos con categorías y subcategorías",
        "features": [
            "Clean Architecture",
            "JWT Authentication con expiración",
            "REST API",
            "GraphQL",
            "ACID Transactions",
            "Categorización jerárquica",
            "OWASP Top 10 Security",
            "Rate Limiting",
            "Input Validation",
            "Security Logging",
            "Integrity Checking"
        ],
        "endpoints": {
            "auth": "/auth/token",
            "categories": "/categories",
            "subcategories": "/subcategories", 
            "products": "/products",
            "graphql": "/graphql",
            "docs": "/docs",
            "health": "/health"
        },
        "security": {
            "owasp_compliance": "Top 10 2021",
            "authentication": "JWT Bearer Token",
            "authorization": "Role-based access control",
            "rate_limiting": "Enabled",
            "input_validation": "SQL Injection & XSS prevention",
            "security_headers": "Comprehensive",
            "logging": "Security events tracked"
        },
        "structure": "Categoría -> Subcategoría -> Producto"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint para monitoring"""
    try:
        # Verificar container de dependencias
        container_health = container.health_check()
        
        # Verificar base de datos
        db_conn = db_manager.get_connection()
        db_conn.execute("SELECT 1").fetchone()
        db_conn.close()
        
        # Verificar integridad de archivos
        integrity_report = integrity_checker.get_integrity_report()
        
        # Obtener resumen de seguridad
        security_summary = security_logger.get_security_summary()
        
        return {
            "status": "healthy",
            "version": "2.0.0-secure",
            "database": "connected",
            "container": container_health,
            "security": {
                "integrity_status": integrity_report["integrity_status"],
                "monitored_files": integrity_report["monitored_files"],
                "security_events": security_summary["total_events"],
                "failed_auths": security_summary["failed_auths"]
            },
            "features": {
                "jwt_expiration": "1 hour",
                "database": "SQLite with ACID",
                "architecture": "Clean Architecture",
                "owasp_compliance": "Top 10 2021",
                "rate_limiting": f"{security_config.RATE_LIMIT_REQUESTS}/min",
                "security_logging": "Enabled"
            }
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


# ============================================================================
# Global Exception Handler
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Manejador global de excepciones con logging de seguridad"""
    # Log del error con información de seguridad
    client_ip = request.client.host if request.client else "unknown"
    
    error_details = {
        "error": str(exc),
        "path": str(request.url),
        "method": request.method,
        "ip": client_ip,
        "user_agent": request.headers.get("user-agent", "unknown")
    }
    
    # Log como actividad sospechosa si parece un ataque
    if any(keyword in str(exc).lower() for keyword in ["sql", "script", "injection", "xss"]):
        security_logger.log_suspicious_activity(
            request, 
            "potential_attack", 
            {"error_type": type(exc).__name__, "error_message": str(exc)}
        )
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Error interno del servidor",
            "error_id": "Contact support with this ID if needed",
            "path": str(request.url.path),
            "method": request.method
        }
    )


# ============================================================================
# Startup and Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Eventos de inicio de la aplicación"""
    print("🚀 Products API iniciándose...")
    
    # Verificar integridad de archivos críticos
    print("� Verificando integridad de archivos...")
    integrity_ok, modified_files, new_files = integrity_checker.verify_integrity()
    
    if integrity_ok:
        print("✅ Integridad de archivos verificada")
    else:
        print("⚠️  Advertencia: Integridad de archivos comprometida")
        print(f"   - Archivos modificados: {len(modified_files)}")
        if modified_files:
            for file in modified_files[:3]:  # Mostrar solo los primeros 3
                print(f"     • {file}")
    
    print("�📊 Base de datos inicializada")
    print("🔐 JWT Authentication configurado (expira en 1 hora)")
    print("🛡️  Medidas de seguridad OWASP activadas")
    print("🔒 Headers de seguridad configurados")
    print("📝 Logging de seguridad habilitado")
    print("⚡ Rate limiting activado")
    print("🏗️  Clean Architecture cargada")
    print("✅ API lista para recibir peticiones")


@app.on_event("shutdown")
async def shutdown_event():
    """Eventos de cierre de la aplicación"""
    print("⏹️  Products API cerrándose...")
    
    # Generar reporte final de seguridad
    security_summary = security_logger.get_security_summary()
    print(f"📊 Resumen de seguridad:")
    print(f"   - Eventos totales: {security_summary['total_events']}")
    print(f"   - Intentos de auth: {security_summary['auth_attempts']}")
    print(f"   - Fallos de auth: {security_summary['failed_auths']}")
    print(f"   - Accesos denegados: {security_summary['access_denied']}")
    
    print("✅ Recursos liberados correctamente")


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
