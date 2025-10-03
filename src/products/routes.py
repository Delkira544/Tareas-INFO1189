from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPAuthorizationCredentials
from typing import List
from .models import Product, ProductRequest, ProductUpdate
from .controller import ProductController
from .repository import ProductRepository

router = APIRouter(prefix="/products", tags=["products"])

product_repository = ProductRepository()
product_controller = ProductController(product_repository)

@router.post("/", response_model=dict)
async def create_product(
    product_request: ProductRequest,
   # token: str = Depends(verificar_token_bearer)
):
    try:
        product = product_controller.create_product(product_request)
        return product.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", response_model=List[dict])
async def get_products():
    products = product_controller.get_all_products()
    return [product.to_dict() for product in products]

@router.get("/{product_id}", response_model=dict)
async def get_product(product_id: int):
    product = product_controller.get_product(product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return product.to_dict()

@router.put("/{product_id}", response_model=dict)
async def update_product(product_id: int, product_update: ProductUpdate):
    try:
        product = product_controller.update_product(product_id, product_update)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
        return product.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.patch("/{product_id}", response_model=dict)
async def partial_update_product(product_id: int, product_update: ProductUpdate):
    return await update_product(product_id, product_update)