"""
Domain Layer - Interfaces (Dependency Inversion Principle)
Define contratos que la infraestructura debe implementar
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import Product, Category


class IProductRepository(ABC):
    """
    Interface para el repositorio de productos (SOLID: Dependency Inversion)
    La capa de dominio no depende de la implementación, solo del contrato
    """
    
    @abstractmethod
    def create(self, product: Product) -> Product:
        """Crear un nuevo producto (ACID: Atomic operation)"""
        pass
    
    @abstractmethod
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Obtener producto por ID"""
        pass
    
    @abstractmethod
    def get_all(self) -> List[Product]:
        """Obtener todos los productos"""
        pass
    
    @abstractmethod
    def get_by_category(self, category_id: int) -> List[Product]:
        """Obtener productos por categoría"""
        pass
    
    @abstractmethod
    def update(self, product: Product) -> Optional[Product]:
        """Actualizar producto (ACID: Consistency)"""
        pass
    
    @abstractmethod
    def delete(self, product_id: int) -> bool:
        """Eliminar producto (ACID: Durability)"""
        pass


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
