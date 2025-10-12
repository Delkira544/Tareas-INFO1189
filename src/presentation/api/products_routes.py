"""
Products REST API - Implementación con Clean Architecture
Usa Use Cases en lugar de acceder directamente a repositorios
"""
from fastapi import APIRouter, HTTPException, status
from typing import List
from pydantic import BaseModel

from infrastructure.container import get_container

router = APIRouter(prefix="/products", tags=["products"])


# ============================================================================
# DTOs (Data Transfer Objects) - Modelos de entrada/salida
# ============================================================================

class ProductRequest(BaseModel):
    """DTO para crear productos"""
    name: str
    price: float
    in_stock: bool
    currency: str = "CLP"
    category_id: int | None = None


class ProductUpdate(BaseModel):
    """DTO para actualizar productos"""
    name: str | None = None
    price: float | None = None
    in_stock: bool | None = None
    currency: str | None = None
    category_id: int | None = None


class ProductResponse(BaseModel):
    """DTO para respuestas de productos"""
    id: int
    name: str
    price: float
    in_stock: bool
    currency: str
    category_id: int | None
    category_name: str | None = None


# ============================================================================
# Endpoints REST
# ============================================================================

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product_request: ProductRequest):
    """
    Crear un nuevo producto
    
    Requiere: JWT Bearer token (protegido por middleware)
    """
    container = get_container()
    use_case = container.create_product_use_case()
    
    try:
        product = use_case.execute(
            name=product_request.name,
            price=product_request.price,
            in_stock=product_request.in_stock,
            currency=product_request.currency,
            category_id=product_request.category_id
        )
        
        return ProductResponse(
            id=product.id,
            name=product.name,
            price=product.price,
            in_stock=product.in_stock,
            currency=product.currency,
            category_id=product.category_id,
            category_name=None  # Se puede agregar si se necesita
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[ProductResponse])
async def get_products(category_id: int | None = None):
    """
    Obtener todos los productos
    
    Query params:
    - category_id: Filtrar por categoría (opcional)
    """
    container = get_container()
    use_case = container.get_products_use_case()
    
    products = use_case.execute(category_id=category_id)
    
    return [
        ProductResponse(
            id=p.id,
            name=p.name,
            price=p.price,
            in_stock=p.in_stock,
            currency=p.currency,
            category_id=p.category_id,
            category_name=None
        )
        for p in products
    ]


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    """Obtener un producto por ID"""
    container = get_container()
    use_case = container.get_product_by_id_use_case()
    
    product = use_case.execute(product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con ID {product_id} no encontrado"
        )
    
    return ProductResponse(
        id=product.id,
        name=product.name,
        price=product.price,
        in_stock=product.in_stock,
        currency=product.currency,
        category_id=product.category_id,
        category_name=None
    )


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, product_update: ProductUpdate):
    """Actualizar un producto completamente"""
    container = get_container()
    use_case = container.update_product_use_case()
    
    try:
        product = use_case.execute(
            product_id=product_id,
            name=product_update.name,
            price=product_update.price,
            in_stock=product_update.in_stock,
            currency=product_update.currency,
            category_id=product_update.category_id
        )
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con ID {product_id} no encontrado"
            )
        
        return ProductResponse(
            id=product.id,
            name=product.name,
            price=product.price,
            in_stock=product.in_stock,
            currency=product.currency,
            category_id=product.category_id,
            category_name=None
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/{product_id}", response_model=ProductResponse)
async def partial_update_product(product_id: int, product_update: ProductUpdate):
    """Actualizar parcialmente un producto"""
    return await update_product(product_id, product_update)


@router.delete("/{product_id}", response_model=dict)
async def delete_product(product_id: int):
    """Eliminar un producto"""
    container = get_container()
    use_case = container.delete_product_use_case()
    
    success = use_case.execute(product_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con ID {product_id} no encontrado"
        )
    
    return {
        "message": "Producto eliminado exitosamente",
        "id": product_id
    }
