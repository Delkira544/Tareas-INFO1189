"""
Domain Layer - Entidades del Negocio (Clean Architecture)
Estas son las entidades puras del dominio, sin dependencias externas
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Category:
    """Entidad de dominio: Categoría principal"""
    id: Optional[int] = None
    name: str = ""
    description: Optional[str] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Validaciones de dominio"""
        if self.name and len(self.name.strip()) == 0:
            raise ValueError("El nombre de la categoría no puede estar vacío")
        if self.name and len(self.name) > 100:
            raise ValueError("El nombre de la categoría no puede exceder 100 caracteres")


@dataclass
class Subcategory:
    """Entidad de dominio: Subcategoría"""
    id: Optional[int] = None
    name: str = ""
    description: Optional[str] = None
    category_id: int = 0
    created_at: Optional[datetime] = None
    
    # Información relacionada (no parte del dominio puro)
    category: Optional[Category] = None

    def __post_init__(self):
        """Validaciones de dominio"""
        if self.name and len(self.name.strip()) == 0:
            raise ValueError("El nombre de la subcategoría no puede estar vacío")
        if self.name and len(self.name) > 100:
            raise ValueError("El nombre de la subcategoría no puede exceder 100 caracteres")
        if self.category_id <= 0:
            raise ValueError("La subcategoría debe pertenecer a una categoría válida")


@dataclass
class Product:
    """Entidad de dominio: Producto"""
    id: Optional[int] = None
    name: str = ""
    price: float = 0.0
    in_stock: bool = True
    currency: str = "CLP"
    subcategory_id: int = 0
    created_at: Optional[datetime] = None
    
    # Información relacionada (no parte del dominio puro)
    subcategory: Optional[Subcategory] = None

    def __post_init__(self):
        """Validaciones de dominio (Business Rules)"""
        if self.name and len(self.name.strip()) == 0:
            raise ValueError("El nombre del producto no puede estar vacío")
        if self.name and len(self.name) < 3:
            raise ValueError("El nombre del producto debe tener al menos 3 caracteres")
        if self.price < 0:
            raise ValueError("El precio no puede ser negativo")
        if self.currency not in ["CLP", "USD", "EUR"]:
            raise ValueError("Moneda no válida")
        if self.subcategory_id <= 0:
            raise ValueError("El producto debe pertenecer a una subcategoría válida")
    
    def is_available(self) -> bool:
        """Regla de negocio: Un producto está disponible si está en stock"""
        return self.in_stock
    
    def calculate_discount(self, percentage: float) -> float:
        """Regla de negocio: Calcular precio con descuento"""
        if percentage < 0 or percentage > 100:
            raise ValueError("Porcentaje de descuento inválido")
        return self.price * (1 - percentage / 100)
