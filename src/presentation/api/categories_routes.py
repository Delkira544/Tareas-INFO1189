"""
Categories API Routes - Presentation Layer
Endpoints REST para gestionar categorías con Clean Architecture
"""
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import List, Optional

from infrastructure.container import container
from application.use_cases import CategoryUseCases

router = APIRouter(prefix="/categories", tags=["categories"])


# ============================================================================
# DTOs (Data Transfer Objects)
# ============================================================================

class CategoryCreateRequest(BaseModel):
    """DTO para crear categoría"""
    name: str = Field(..., min_length=1, max_length=100, description="Nombre de la categoría")
    description: Optional[str] = Field(None, max_length=500, description="Descripción opcional")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Electrónicos",
                "description": "Productos electrónicos y tecnológicos"
            }
        }


class CategoryResponse(BaseModel):
    """DTO para responder categoría"""
    id: int
    name: str
    description: Optional[str]
    created_at: Optional[str]

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Electrónicos",
                "description": "Productos electrónicos y tecnológicos",
                "created_at": "2024-01-15T10:30:00"
            }
        }


# ============================================================================
# Dependency Injection
# ============================================================================

def get_category_use_cases() -> CategoryUseCases:
    """Inyección de dependencia para casos de uso de categorías"""
    return container.get_category_use_cases()


# ============================================================================
# Endpoints REST
# ============================================================================

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreateRequest,
    use_cases: CategoryUseCases = Depends(get_category_use_cases)
):
    """
    Crear nueva categoría
    
    Requiere autenticación JWT.
    """
    try:
        category = use_cases.create_category(
            name=category_data.name,
            description=category_data.description
        )
        
        return CategoryResponse(
            id=category.id,
            name=category.name,
            description=category.description,
            created_at=category.created_at.isoformat() if category.created_at else None
        )
    
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


@router.get("/", response_model=List[CategoryResponse])
async def get_all_categories(
    use_cases: CategoryUseCases = Depends(get_category_use_cases)
):
    """Obtener todas las categorías"""
    try:
        categories = use_cases.get_all_categories()
        
        return [
            CategoryResponse(
                id=category.id,
                name=category.name,
                description=category.description,
                created_at=category.created_at.isoformat() if category.created_at else None
            )
            for category in categories
        ]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category_by_id(
    category_id: int,
    use_cases: CategoryUseCases = Depends(get_category_use_cases)
):
    """Obtener categoría por ID"""
    try:
        category = use_cases.get_category_by_id(category_id)
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Categoría con ID {category_id} no encontrada"
            )
        
        return CategoryResponse(
            id=category.id,
            name=category.name,
            description=category.description,
            created_at=category.created_at.isoformat() if category.created_at else None
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


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    use_cases: CategoryUseCases = Depends(get_category_use_cases)
):
    """
    Eliminar categoría
    
    Requiere autenticación JWT.
    Eliminará también todas las subcategorías y productos asociados.
    """
    try:
        deleted = use_cases.delete_category(category_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Categoría con ID {category_id} no encontrada"
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
