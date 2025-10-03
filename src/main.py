from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models import Product, ProductRequest, ProductUpdate

app = FastAPI()

security = HTTPBearer()

VALID_TOKEN = "secreto123"

def verificar_token_bearer(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if token != VALID_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token Bearer inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token

products = []

@app.get("/")
async def root():
    return {"message": "Servidor en línea"}

@app.post("/products")
async def create_product(productRequest: ProductRequest,
                         token: str = Depends(verificar_token_bearer)):
    print(f"Token verificado: {token}")
    print(f"Creando Producto: {productRequest}")
    product_id = len(products) + 1
    product = Product(id=product_id, **productRequest.to_dict()) # type: ignore
    products.append(product)
    return product.to_dict()

@app.put("/products/{item_id}")
async def update_product(item_id: int, product: ProductUpdate):
    print(f"Actualizacion de producto ID: {item_id} to {product}")
    for idx, existing_product in enumerate(products):
        if existing_product.id == item_id:
            updated_product = Product(
                id=item_id,  # Mantener el ID original
                name=product.name,  # type: ignore
                price=product.price, # type: ignore
                in_stock=product.in_stock # type: ignore
            )

            products[idx] = product
            return product.to_dict()
    return {"error": "Product not found"}

@app.patch("/products/{item_id}")
async def partial_update_product(item_id: int, product: ProductUpdate):
    print(f"Actualizacion parcial ID: {item_id} to {product}")
    for idx, existing_product in enumerate(products):
        if existing_product.id == item_id:
            updated_product = existing_product
            if product.name is not None:
                updated_product.name = product.name
            if product.price is not None:
                updated_product.price = product.price
            if product.in_stock is not None:
                updated_product.in_stock = product.in_stock
            products[idx] = updated_product
            return updated_product.to_dict()
    return {"error": "Product not found"}

@app.get("/products")
async def get_products():
    print("Consultando todos los productos")
    return [product.to_dict() for product in products]

@app.get("/products/{item_id}")
async def read_item(item_id: int):
    print(f"Consultando producto con ID: {item_id}")
    for product in products:
        print(product.id, item_id)
        if product.id == item_id:
            return product.to_dict()
    return {"error": "Product not found"}