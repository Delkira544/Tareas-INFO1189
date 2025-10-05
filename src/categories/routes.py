from fastapi import APIRouter, HTTPException, status
from typing import List
from products.models import Category, CategoryRequest
from products.repository import CategoryRepository, ProductRepository

router = APIRouter(prefix="/categories", tags=["categories"])

category_repository = CategoryRepository()
product_repository = ProductRepository()

@router.get("/", response_model=List[dict])
async def get_categories():
    """Obtener todas las categorías"""
    categories = category_repository.get_all()
    return [category.to_dict() for category in categories]

@router.get("/{category_id}", response_model=dict)
async def get_category(category_id: int):
    """Obtener una categoría por ID"""
    category = category_repository.get_by_id(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Categoría no encontrada"
        )
    return category.to_dict()

@router.get("/{category_id}/products", response_model=List[dict])
async def get_products_by_category(category_id: int):
    """Obtener todos los productos de una categoría"""
    category = category_repository.get_by_id(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Categoría no encontrada"
        )
    
    products = product_repository.get_by_category(category_id)
    return [product.to_dict() for product in products]

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_category(category_request: CategoryRequest):
    """Crear una nueva categoría"""
    try:
        category = category_repository.create(category_request)
        return category.to_dict()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Error al crear categoría: {str(e)}"
        )

@router.delete("/{category_id}", response_model=dict)
async def delete_category(category_id: int):
    """Eliminar una categoría"""
    success = category_repository.delete(category_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Categoría no encontrada"
        )
    return {"message": "Categoría eliminada exitosamente", "id": category_id}
