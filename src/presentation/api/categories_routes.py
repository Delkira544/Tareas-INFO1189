"""
Categories REST API - Implementación con Clean Architecture
Usa Use Cases en lugar de acceder directamente a repositorios
"""
from fastapi import APIRouter, HTTPException, status
from typing import List
from pydantic import BaseModel

from infrastructure.container import get_container

router = APIRouter(prefix="/categories", tags=["categories"])


# ============================================================================
# DTOs (Data Transfer Objects)
# ============================================================================

class CategoryRequest(BaseModel):
    """DTO para crear categorías"""
    name: str
    description: str | None = None


class CategoryResponse(BaseModel):
    """DTO para respuestas de categorías"""
    id: int
    name: str
    description: str | None


# ============================================================================
# Endpoints REST
# ============================================================================

@router.get("/", response_model=List[CategoryResponse])
async def get_categories():
    """Obtener todas las categorías"""
    container = get_container()
    use_case = container.get_categories_use_case()
    
    categories = use_case.execute()
    
    return [
        CategoryResponse(
            id=c.id,
            name=c.name,
            description=c.description
        )
        for c in categories
    ]


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int):
    """Obtener una categoría por ID"""
    container = get_container()
    use_case = container.get_category_by_id_use_case()
    
    category = use_case.execute(category_id)
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría con ID {category_id} no encontrada"
        )
    
    return CategoryResponse(
        id=category.id,
        name=category.name,
        description=category.description
    )


@router.get("/{category_id}/products", response_model=List[dict])
async def get_products_by_category(category_id: int):
    """Obtener todos los productos de una categoría"""
    container = get_container()
    
    # Verificar que la categoría existe
    category_use_case = container.get_category_by_id_use_case()
    category = category_use_case.execute(category_id)
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría con ID {category_id} no encontrada"
        )
    
    # Obtener productos de la categoría
    products_use_case = container.get_products_use_case()
    products = products_use_case.execute(category_id=category_id)
    
    return [
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "in_stock": p.in_stock,
            "currency": p.currency,
            "category_id": p.category_id
        }
        for p in products
    ]


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(category_request: CategoryRequest):
    """Crear una nueva categoría"""
    container = get_container()
    use_case = container.create_category_use_case()
    
    try:
        category = use_case.execute(
            name=category_request.name,
            description=category_request.description
        )
        
        return CategoryResponse(
            id=category.id,
            name=category.name,
            description=category.description
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{category_id}", response_model=dict)
async def delete_category(category_id: int):
    """Eliminar una categoría"""
    container = get_container()
    use_case = container.get_category_by_id_use_case()
    
    # Verificar que existe antes de eliminar
    category = use_case.execute(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría con ID {category_id} no encontrada"
        )
    
    # Verificar que no tenga productos asociados
    products_use_case = container.get_products_use_case()
    products = products_use_case.execute(category_id=category_id)
    
    if products:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede eliminar la categoría porque tiene {len(products)} producto(s) asociado(s)"
        )
    
    # Eliminar categoría
    from infrastructure.repositories import SQLiteCategoryRepository
    repo = SQLiteCategoryRepository()
    
    try:
        success = repo.delete(category_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar la categoría"
            )
        
        return {
            "message": "Categoría eliminada exitosamente",
            "id": category_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar categoría: {str(e)}"
        )
