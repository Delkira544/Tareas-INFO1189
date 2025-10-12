"""
Main Application - Clean Architecture Entry Point

Este archivo es el punto de entrada de la aplicación.
Configura FastAPI, middlewares, y registra todas las rutas.

Arquitectura:
- Presentation Layer: Rutas REST y GraphQL
- Application Layer: Use Cases (inyectados via Container)
- Domain Layer: Entidades y lógica de negocio
- Infrastructure Layer: Repositorios y base de datos
"""
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

# Presentation Layer - Rutas
from presentation.api.products_routes import router as products_router
from presentation.api.categories_routes import router as categories_router
from presentation.api.graphql_routes import schema as graphql_schema
from presentation.middlewares.auth import ConditionalAuthMiddleware

# Infrastructure Layer - Inicialización
from infrastructure.database import db_manager  # Inicializa BD al importar


# ============================================================================
# Configuración de la aplicación FastAPI
# ============================================================================

app = FastAPI(
    title="API de Productos - Tienda de Informática",
    description="""
    API REST y GraphQL para gestión de productos de informática.
    
    **Arquitectura:**
    - Clean Architecture (4 capas)
    - SOLID Principles
    - ACID Properties (transacciones)
    - Dependency Injection
    
    **Autenticación:**
    - JWT Bearer token: "secreto123"
    - Rutas protegidas: POST /products
    """,
    version="2.0.0"
)


# ============================================================================
# Middleware de autenticación
# ============================================================================

app.add_middleware(
    ConditionalAuthMiddleware,
    protected_routes=[
        ("/products", "POST"),  # Crear producto requiere JWT
        # Agregar más rutas protegidas según sea necesario
    ]
)


# ============================================================================
# Registro de rutas REST
# ============================================================================

app.include_router(products_router)
app.include_router(categories_router)


# ============================================================================
# Registro de GraphQL
# ============================================================================

graphql_app = GraphQLRouter(graphql_schema)
app.include_router(graphql_app, prefix="/graphql")


# ============================================================================
# Endpoints de información
# ============================================================================

@app.get("/")
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "message": "🚀 API de Tienda de Informática - Clean Architecture",
        "version": "2.0.0",
        "architecture": {
            "pattern": "Clean Architecture",
            "principles": ["SOLID", "DDD", "Dependency Injection"],
            "properties": ["ACID Transactions"]
        },
        "endpoints": {
            "REST API Productos": "/products",
            "REST API Categorías": "/categories",
            "GraphQL": "/graphql",
            "GraphQL Playground": "/graphql (navegador)",
            "Documentación OpenAPI": "/docs",
            "Redoc": "/redoc"
        },
        "authentication": {
            "type": "JWT Bearer",
            "token": "secreto123",
            "protected_routes": [
                "POST /products"
            ]
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected"
    }
