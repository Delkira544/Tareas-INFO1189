"""
Tipos GraphQL para el schema
Define los tipos de datos que se expondrán en la API GraphQL
"""
import strawberry
from typing import Optional


@strawberry.type
class ProductType:
    """Tipo GraphQL para representar un producto"""
    id: int
    name: str
    price: float
    in_stock: bool
    currency: str


@strawberry.input
class ProductInput:
    """Input GraphQL para crear un producto"""
    name: str
    price: float
    in_stock: bool
    currency: str = "CLP"


@strawberry.input
class ProductUpdateInput:
    """Input GraphQL para actualizar un producto (parcial)"""
    name: Optional[str] = None
    price: Optional[float] = None
    in_stock: Optional[bool] = None
    currency: Optional[str] = None
