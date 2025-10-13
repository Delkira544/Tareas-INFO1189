"""
Subcategories API Routes - Presentation Layer
Endpoints REST para gestionar subcategorías con Clean Architecture
"""
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import List, Optional

from infrastructure.container import container
from application.use_cases import SubcategoryUseCases

router = APIRouter(prefix="/subcategories", tags=["subcategories"])


# ============================================================================
# DTOs (Data Transfer Objects)
# ============================================================================

class SubcategoryCreateRequest(BaseModel):
    """DTO para crear subcategoría"""
    name: str = Field(..., min_length=1, max_length=100, description="Nombre de la subcategoría")
    category_id: int = Field(..., gt=0, description="ID de la categoría padre")
    description: Optional[str] = Field(None, max_length=500, description="Descripción opcional")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Smartphones",
                "category_id": 1,
                "description": "Teléfonos inteligentes y móviles"
            }
        }


class CategoryInSubcategoryResponse(BaseModel):
    """DTO para categoría dentro de subcategoría"""
    id: int
    name: str
    description: Optional[str]


class SubcategoryResponse(BaseModel):
    """DTO para responder subcategoría con información de categoría"""
    id: int
    name: str
    description: Optional[str]
    category_id: int
    created_at: Optional[str]
    category: Optional[CategoryInSubcategoryResponse]

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Smartphones",
                "description": "Teléfonos inteligentes y móviles",
                "category_id": 1,
                "created_at": "2024-01-15T10:30:00",
                "category": {
                    "id": 1,
                    "name": "Electrónicos",
                    "description": "Productos electrónicos y tecnológicos"
                }
            }
        }


# ============================================================================
# Dependency Injection
# ============================================================================

def get_subcategory_use_cases() -> SubcategoryUseCases:
    """Inyección de dependencia para casos de uso de subcategorías"""
    return container.get_subcategory_use_cases()


# ============================================================================
# Endpoints REST
# ============================================================================

@router.post("/", response_model=SubcategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_subcategory(
    subcategory_data: SubcategoryCreateRequest,
    use_cases: SubcategoryUseCases = Depends(get_subcategory_use_cases)
):
    """
    Crear nueva subcategoría
    
    Requiere autenticación JWT.
    """
    try:
        subcategory = use_cases.create_subcategory(
            name=subcategory_data.name,
            category_id=subcategory_data.category_id,
            description=subcategory_data.description
        )
        
        return SubcategoryResponse(
            id=subcategory.id,
            name=subcategory.name,
            description=subcategory.description,
            category_id=subcategory.category_id,
            created_at=subcategory.created_at.isoformat() if subcategory.created_at else None,
            category=CategoryInSubcategoryResponse(
                id=subcategory.category.id,
                name=subcategory.category.name,
                description=subcategory.category.description
            ) if subcategory.category else None
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


@router.get("/", response_model=List[SubcategoryResponse])
async def get_all_subcategories(
    use_cases: SubcategoryUseCases = Depends(get_subcategory_use_cases)
):
    """Obtener todas las subcategorías con información de categoría"""
    try:
        subcategories = use_cases.get_all_subcategories()
        
        return [
            SubcategoryResponse(
                id=subcategory.id,
                name=subcategory.name,
                description=subcategory.description,
                category_id=subcategory.category_id,
                created_at=subcategory.created_at.isoformat() if subcategory.created_at else None,
                category=CategoryInSubcategoryResponse(
                    id=subcategory.category.id,
                    name=subcategory.category.name,
                    description=subcategory.category.description
                ) if subcategory.category else None
            )
            for subcategory in subcategories
        ]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get("/{subcategory_id}", response_model=SubcategoryResponse)
async def get_subcategory_by_id(
    subcategory_id: int,
    use_cases: SubcategoryUseCases = Depends(get_subcategory_use_cases)
):
    """Obtener subcategoría por ID con información de categoría"""
    try:
        subcategory = use_cases.get_subcategory_by_id(subcategory_id)
        
        if not subcategory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subcategoría con ID {subcategory_id} no encontrada"
            )
        
        return SubcategoryResponse(
            id=subcategory.id,
            name=subcategory.name,
            description=subcategory.description,
            category_id=subcategory.category_id,
            created_at=subcategory.created_at.isoformat() if subcategory.created_at else None,
            category=CategoryInSubcategoryResponse(
                id=subcategory.category.id,
                name=subcategory.category.name,
                description=subcategory.category.description
            ) if subcategory.category else None
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


@router.get("/category/{category_id}", response_model=List[SubcategoryResponse])
async def get_subcategories_by_category(
    category_id: int,
    use_cases: SubcategoryUseCases = Depends(get_subcategory_use_cases)
):
    """Obtener todas las subcategorías de una categoría específica"""
    try:
        subcategories = use_cases.get_subcategories_by_category(category_id)
        
        return [
            SubcategoryResponse(
                id=subcategory.id,
                name=subcategory.name,
                description=subcategory.description,
                category_id=subcategory.category_id,
                created_at=subcategory.created_at.isoformat() if subcategory.created_at else None,
                category=CategoryInSubcategoryResponse(
                    id=subcategory.category.id,
                    name=subcategory.category.name,
                    description=subcategory.category.description
                ) if subcategory.category else None
            )
            for subcategory in subcategories
        ]
    
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


@router.delete("/{subcategory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subcategory(
    subcategory_id: int,
    use_cases: SubcategoryUseCases = Depends(get_subcategory_use_cases)
):
    """
    Eliminar subcategoría
    
    Requiere autenticación JWT.
    Eliminará también todos los productos asociados.
    """
    try:
        deleted = use_cases.delete_subcategory(subcategory_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subcategoría con ID {subcategory_id} no encontrada"
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