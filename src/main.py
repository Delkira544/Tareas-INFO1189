from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from products.routes import router as products_router
from categories.routes import router as categories_router
from shared.middlewares import ConditionalAuthMiddleware
from strawberry.fastapi import GraphQLRouter
from graphql_api.schema import schema

app = FastAPI(
    title="API de Productos - Tienda de Informática",
    description="API REST y GraphQL para gestión de productos de informática",
    version="1.0.0"
)

# Middleware de autenticación condicional
app.add_middleware(
    ConditionalAuthMiddleware,
    protected_routes=[("/products", "POST")]
)

# Incluir rutas REST
app.include_router(products_router)
app.include_router(categories_router)

# Crear y montar el router de GraphQL
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
async def root():
    return {
        "message": "Servidor en línea - Tienda de Informática",
        "endpoints": {
            "REST API Productos": "/products",
            "REST API Categorías": "/categories",
            "GraphQL": "/graphql",
            "GraphQL Playground": "/graphql (navegador)",
            "Documentación": "/docs"
        }
    }
