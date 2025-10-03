from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from products.routes import router as products_router
from shared.middlewares import ConditionalAuthMiddleware

app = FastAPI()

app.add_middleware(
    ConditionalAuthMiddleware,
    protected_routes=[("/products", "POST")]
)

app.include_router(products_router)

@app.get("/")
async def root():
    return {"message": "Servidor en línea"}
