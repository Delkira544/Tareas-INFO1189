"""
Main Application - Entry Point
Configuración principal de la aplicación FastAPI con Clean Architecture
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Infrastructure Layer
from infrastructure.database import db_manager
from infrastructure.container import container

# Presentation Layer - API Routes
from presentation.api.auth_routes import router as auth_router
from presentation.api.categories_routes import router as categories_router
from presentation.api.subcategories_routes import router as subcategories_router
from presentation.api.products_routes import router as products_router
from presentation.api.graphql_routes import router as graphql_router

# Middleware
from presentation.middlewares.auth import ConditionalAuthMiddleware

# ============================================================================
# FastAPI Application Setup
# ============================================================================

app = FastAPI(
    title="Products API - Clean Architecture",
    description="""
    API REST y GraphQL para gestión de productos con Clean Architecture
    
    ## Características:
    
    * **Clean Architecture**: Separación clara de responsabilidades
    * **JWT Authentication**: Tokens con expiración de 1 hora
    * **ACID Transactions**: Propiedades ACID en base de datos
    * **REST API**: Endpoints tradicionales para CRUD
    * **GraphQL**: Consultas flexibles y específicas
    * **Categorización**: Productos organizados en categorías y subcategorías
    
    ## Estructura de Datos:
    
    ```
    Categoría (ej: "Electrónicos")
    └── Subcategoría (ej: "Smartphones")
        └── Producto (ej: "iPhone 15 Pro")
    ```
    
    ## Autenticación:
    
    1. Obtener token: `POST /auth/token`
    2. Usar token: `Authorization: Bearer {token}`
    3. El token expira en 1 hora
    
    ## Endpoints Protegidos:
    
    - POST, PUT, DELETE en `/products`
    - POST, DELETE en `/categories`
    - POST, DELETE en `/subcategories`
    - Mutaciones GraphQL
    """,
    version="2.0.0",
    contact={
        "name": "Equipo de Desarrollo",
        "email": "dev@example.com"
    },
    license_info={
        "name": "MIT",
    }
)

# ============================================================================
# CORS Configuration
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar orígenes específicos
    allow_credentials=True,
    allow_methods=["*"],
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
        "message": "Products API - Clean Architecture",
        "version": "2.0.0",
        "description": "API para gestión de productos con categorías y subcategorías",
        "features": [
            "Clean Architecture",
            "JWT Authentication con expiración",
            "REST API",
            "GraphQL",
            "ACID Transactions",
            "Categorización jerárquica"
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
        
        return {
            "status": "healthy",
            "version": "2.0.0",
            "database": "connected",
            "container": container_health,
            "features": {
                "jwt_expiration": "1 hour",
                "database": "SQLite with ACID",
                "architecture": "Clean Architecture"
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
    """Manejador global de excepciones"""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Error interno del servidor",
            "error": str(exc),
            "path": str(request.url),
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
    print("📊 Base de datos inicializada")
    print("🔐 JWT Authentication configurado (expira en 1 hora)")
    print("🏗️  Clean Architecture cargada")
    print("✅ API lista para recibir peticiones")


@app.on_event("shutdown")
async def shutdown_event():
    """Eventos de cierre de la aplicación"""
    print("⏹️  Products API cerrándose...")
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
