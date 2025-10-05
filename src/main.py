from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from products.routes import router as products_router
from shared.middlewares import ConditionalAuthMiddleware
from strawberry.fastapi import GraphQLRouter
from graphql_api.schema import schema

app = FastAPI(
    title="API de Productos",
    description="API REST y GraphQL para gestión de productos",
    version="1.0.0"
)

# Middleware de autenticación condicional
app.add_middleware(
    ConditionalAuthMiddleware,
    protected_routes=[("/products", "POST")]
)

# Incluir rutas REST
app.include_router(products_router)

# Crear y montar el router de GraphQL
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
async def root():
    return {
        "message": "Servidor en línea",
        "endpoints": {
            "REST API": "/products",
            "GraphQL": "/graphql",
            "GraphQL Playground": "/graphql (navegador)"
        }
    }
