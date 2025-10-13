"""
Domain Layer - Interfaces (Dependency Inversion Principle)
Define contratos que la infraestructura debe implementar
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import Product, Category, Subcategory


class ICategoryRepository(ABC):
    """Interface para el repositorio de categorías"""
    
    @abstractmethod
    def create(self, category: Category) -> Category:
        pass
    
    @abstractmethod
    def get_by_id(self, category_id: int) -> Optional[Category]:
        pass
    
    @abstractmethod
    def get_all(self) -> List[Category]:
        pass
    
    @abstractmethod
    def delete(self, category_id: int) -> bool:
        pass


class ISubcategoryRepository(ABC):
    """Interface para el repositorio de subcategorías"""
    
    @abstractmethod
    def create(self, subcategory: Subcategory) -> Subcategory:
        pass
    
    @abstractmethod
    def get_by_id(self, subcategory_id: int) -> Optional[Subcategory]:
        pass
    
    @abstractmethod
    def get_all(self) -> List[Subcategory]:
        pass
    
    @abstractmethod
    def get_by_category(self, category_id: int) -> List[Subcategory]:
        pass
    
    @abstractmethod
    def delete(self, subcategory_id: int) -> bool:
        pass


class IProductRepository(ABC):
    """Interface para el repositorio de productos"""
    
    @abstractmethod
    def create(self, product: Product) -> Product:
        """Crear un nuevo producto (ACID: Atomic operation)"""
        pass
    
    @abstractmethod
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Obtener producto por ID con subcategoría y categoría"""
        pass
    
    @abstractmethod
    def get_all(self) -> List[Product]:
        """Obtener todos los productos con subcategoría y categoría"""
        pass
    
    @abstractmethod
    def get_by_subcategory(self, subcategory_id: int) -> List[Product]:
        """Obtener productos por subcategoría"""
        pass
    
    @abstractmethod
    def get_by_category(self, category_id: int) -> List[Product]:
        """Obtener productos por categoría (todos los de sus subcategorías)"""
        pass
    
    @abstractmethod
    def update(self, product: Product) -> Optional[Product]:
        """Actualizar producto (ACID: Consistency)"""
        pass
    
    @abstractmethod
    def delete(self, product_id: int) -> bool:
        """Eliminar producto (ACID: Durability)"""
        pass


class IUnitOfWork(ABC):
    """
    Unit of Work Pattern (ACID: Atomicity + Isolation)
    Gestiona transacciones para mantener consistencia
    """
    
    @abstractmethod
    def begin_transaction(self):
        """Iniciar transacción"""
        pass
    
    @abstractmethod
    def commit(self):
        """Confirmar transacción"""
        pass
    
    @abstractmethod
    def rollback(self):
        """Revertir transacción"""
        pass
