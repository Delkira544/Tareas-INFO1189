"""
Tipos GraphQL para el schema
Define los tipos de datos que se expondrán en la API GraphQL
"""
import strawberry
from typing import Optional


@strawberry.type
class CategoryType:
    """Tipo GraphQL para representar una categoría"""
    id: int
    name: str
    description: Optional[str] = None


@strawberry.type
class ProductType:
    """Tipo GraphQL para representar un producto"""
    id: int
    name: str
    price: float
    in_stock: bool
    currency: str
    category_id: Optional[int] = None
    category_name: Optional[str] = None


@strawberry.input
class CategoryInput:
    """Input GraphQL para crear una categoría"""
    name: str
    description: Optional[str] = None


@strawberry.input
class ProductInput:
    """Input GraphQL para crear un producto"""
    name: str
    price: float
    in_stock: bool
    currency: str = "CLP"
    category_id: Optional[int] = None


@strawberry.input
class ProductUpdateInput:
    """Input GraphQL para actualizar un producto (parcial)"""
    name: Optional[str] = None
    price: Optional[float] = None
    in_stock: Optional[bool] = None
    currency: Optional[str] = None
    category_id: Optional[int] = None
