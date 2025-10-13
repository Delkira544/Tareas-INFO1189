"""
Products API Routes - Presentation Layer (Updated)
Endpoints REST para gestionar productos con subcategorías y categorías
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Optional

from infrastructure.container import container
from application.use_cases import ProductUseCases
from shared.datetime_utils import safe_datetime_to_iso  # ← Import del shared

router = APIRouter(prefix="/products", tags=["products"])


# ============================================================================
# DTOs (Data Transfer Objects)
# ============================================================================

class ProductCreateRequest(BaseModel):
    """DTO para crear producto"""
    name: str = Field(..., min_length=3, max_length=200, description="Nombre del producto")
    price: float = Field(..., ge=0, description="Precio del producto")
    subcategory_id: int = Field(..., gt=0, description="ID de la subcategoría")
    in_stock: bool = Field(True, description="Disponibilidad en stock")
    currency: str = Field("CLP", description="Moneda (CLP, USD, EUR)")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "iPhone 15 Pro Max",
                "price": 1299000,
                "subcategory_id": 3,
                "in_stock": True,
                "currency": "CLP"
            }
        }


class ProductUpdateRequest(BaseModel):
    """DTO para actualizar producto (campos opcionales)"""
    name: Optional[str] = Field(None, min_length=3, max_length=200)
    price: Optional[float] = Field(None, ge=0)
    subcategory_id: Optional[int] = Field(None, gt=0)
    in_stock: Optional[bool] = None
    currency: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "iPhone 15 Pro Max 256GB",
                "price": 1399000,
                "in_stock": False
            }
        }


class CategoryInProductResponse(BaseModel):
    """DTO para categoría en respuesta de producto"""
    id: int
    name: str
    description: Optional[str]


class SubcategoryInProductResponse(BaseModel):
    """DTO para subcategoría en respuesta de producto"""
    id: int
    name: str
    description: Optional[str]
    category_id: int
    category: CategoryInProductResponse


class ProductResponse(BaseModel):
    """DTO para respuesta de producto con estructura anidada"""
    id: int
    name: str
    price: float
    in_stock: bool
    currency: str
    subcategory_id: int
    created_at: Optional[str]
    subcategory: SubcategoryInProductResponse

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "iPhone 15 Pro Max",
                "price": 1299000,
                "in_stock": True,
                "currency": "CLP",
                "subcategory_id": 3,
                "created_at": "2024-01-15T10:30:00",
                "subcategory": {
                    "id": 3,
                    "name": "Smartphones",
                    "description": "Teléfonos inteligentes",
                    "category_id": 1,
                    "category": {
                        "id": 1,
                        "name": "Electrónicos",
                        "description": "Productos electrónicos y tecnológicos"
                    }
                }
            }
        }


# ============================================================================
# Dependency Injection
# ============================================================================

def get_product_use_cases() -> ProductUseCases:
    """Inyección de dependencia para casos de uso de productos"""
    return container.get_product_use_cases()


# ============================================================================
# Helper Functions (ACTUALIZADA)
# ============================================================================

def map_to_product_response(product) -> ProductResponse:
    """
    Convertir entidad Product a ProductResponse
    Usa safe_datetime_to_iso para manejar fechas de forma segura
    """
    return ProductResponse(
        id=product.id,
        name=product.name,
        price=product.price,
        in_stock=product.in_stock,
        currency=product.currency,
        subcategory_id=product.subcategory_id,
        created_at=safe_datetime_to_iso(product.created_at),  # ← USO DEL SHARED
        subcategory=SubcategoryInProductResponse(
            id=product.subcategory.id,
            name=product.subcategory.name,
            description=product.subcategory.description,
            category_id=product.subcategory.category_id,
            category=CategoryInProductResponse(
                id=product.subcategory.category.id,
                name=product.subcategory.category.name,
                description=product.subcategory.category.description
            )
        )
    )


# ============================================================================
# Endpoints REST - Sin cambios en la lógica
# ============================================================================

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreateRequest,
    use_cases: ProductUseCases = Depends(get_product_use_cases)
):
    """
    Crear nuevo producto
    
    Requiere autenticación JWT.
    """
    try:
        product = use_cases.create_product(
            name=product_data.name,
            price=product_data.price,
            subcategory_id=product_data.subcategory_id,
            in_stock=product_data.in_stock,
            currency=product_data.currency
        )
        
        return map_to_product_response(product)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get("/", response_model=List[ProductResponse])
async def get_all_products(
    available_only: bool = Query(False, description="Solo productos disponibles"),
    use_cases: ProductUseCases = Depends(get_product_use_cases)
):
    """Obtener todos los productos con subcategoría y categoría"""
    try:
        if available_only:
            products = use_cases.get_available_products()
        else:
            products = use_cases.get_all_products()
        
        return [map_to_product_response(product) for product in products]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product_by_id(
    product_id: int,
    use_cases: ProductUseCases = Depends(get_product_use_cases)
):
    """Obtener producto por ID con subcategoría y categoría"""
    try:
        product = use_cases.get_product_by_id(product_id)
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con ID {product_id} no encontrado"
            )
        
        return map_to_product_response(product)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get("/subcategory/{subcategory_id}", response_model=List[ProductResponse])
async def get_products_by_subcategory(
    subcategory_id: int,
    use_cases: ProductUseCases = Depends(get_product_use_cases)
):
    """Obtener productos por subcategoría"""
    try:
        products = use_cases.get_products_by_subcategory(subcategory_id)
        return [map_to_product_response(product) for product in products]
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get("/category/{category_id}", response_model=List[ProductResponse])
async def get_products_by_category(
    category_id: int,
    use_cases: ProductUseCases = Depends(get_product_use_cases)
):
    """Obtener todos los productos de una categoría (todas sus subcategorías)"""
    try:
        products = use_cases.get_products_by_category(category_id)
        return [map_to_product_response(product) for product in products]
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdateRequest,
    use_cases: ProductUseCases = Depends(get_product_use_cases)
):
    """
    Actualizar producto
    
    Requiere autenticación JWT.
    Solo actualiza los campos proporcionados.
    """
    try:
        product = use_cases.update_product(
            product_id=product_id,
            name=product_data.name,
            price=product_data.price,
            in_stock=product_data.in_stock,
            currency=product_data.currency,
            subcategory_id=product_data.subcategory_id
        )
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con ID {product_id} no encontrado"
            )
        
        return map_to_product_response(product)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    use_cases: ProductUseCases = Depends(get_product_use_cases)
):
    """
    Eliminar producto
    
    Requiere autenticación JWT.
    """
    try:
        deleted = use_cases.delete_product(product_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con ID {product_id} no encontrado"
            )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.post("/category/{category_id}/apply-discount")
async def apply_discount_to_category(
    category_id: int,
    discount_percentage: float = Query(..., ge=0, le=100, description="Porcentaje de descuento"),
    use_cases: ProductUseCases = Depends(get_product_use_cases)
):
    """
    Aplicar descuento a todos los productos de una categoría
    
    Requiere autenticación JWT.
    """
    try:
        updated_products = use_cases.apply_discount_to_category(category_id, discount_percentage)
        
        return {
            "message": f"Descuento del {discount_percentage}% aplicado a {len(updated_products)} productos",
            "products_updated": len(updated_products),
            "category_id": category_id,
            "discount_percentage": discount_percentage
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )
