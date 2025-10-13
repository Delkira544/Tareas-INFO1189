"""
Dependency Injection Container - Infrastructure Layer
Configuración de inyección de dependencias siguiendo principios SOLID
"""
from functools import lru_cache

from domain.interfaces import IProductRepository, ICategoryRepository, ISubcategoryRepository
from infrastructure.repositories import (
    SQLiteProductRepository, 
    SQLiteCategoryRepository, 
    SQLiteSubcategoryRepository
)
from application.use_cases import ProductUseCases, CategoryUseCases, SubcategoryUseCases


class DIContainer:
    """
    Contenedor de Inyección de Dependencias
    
    Implementa:
    - Dependency Inversion Principle (SOLID)
    - Singleton pattern para repositorios
    - Factory pattern para casos de uso
    """
    
    def __init__(self):
        self._repositories = {}
        self._use_cases = {}
    
    # ========================================================================
    # Repository Layer (Singletons)
    # ========================================================================
    
    @lru_cache(maxsize=1)
    def get_category_repository(self) -> ICategoryRepository:
        """Obtener instancia singleton del repositorio de categorías"""
        if 'category' not in self._repositories:
            self._repositories['category'] = SQLiteCategoryRepository()
        return self._repositories['category']
    
    @lru_cache(maxsize=1)
    def get_subcategory_repository(self) -> ISubcategoryRepository:
        """Obtener instancia singleton del repositorio de subcategorías"""
        if 'subcategory' not in self._repositories:
            self._repositories['subcategory'] = SQLiteSubcategoryRepository()
        return self._repositories['subcategory']
    
    @lru_cache(maxsize=1)
    def get_product_repository(self) -> IProductRepository:
        """Obtener instancia singleton del repositorio de productos"""
        if 'product' not in self._repositories:
            self._repositories['product'] = SQLiteProductRepository()
        return self._repositories['product']
    
    # ========================================================================
    # Use Cases Layer (Factory Pattern)
    # ========================================================================
    
    def get_category_use_cases(self) -> CategoryUseCases:
        """Factory method para casos de uso de categorías"""
        return CategoryUseCases(
            category_repository=self.get_category_repository()
        )
    
    def get_subcategory_use_cases(self) -> SubcategoryUseCases:
        """Factory method para casos de uso de subcategorías"""
        return SubcategoryUseCases(
            subcategory_repository=self.get_subcategory_repository(),
            category_repository=self.get_category_repository()
        )
    
    def get_product_use_cases(self) -> ProductUseCases:
        """Factory method para casos de uso de productos"""
        return ProductUseCases(
            product_repository=self.get_product_repository(),
            subcategory_repository=self.get_subcategory_repository()
        )
    
    # ========================================================================
    # Health Check Methods
    # ========================================================================
    
    def health_check(self) -> dict:
        """Verificar el estado de las dependencias"""
        try:
            # Verificar repositorios
            category_repo = self.get_category_repository()
            subcategory_repo = self.get_subcategory_repository()
            product_repo = self.get_product_repository()
            
            # Verificar casos de uso
            category_uc = self.get_category_use_cases()
            subcategory_uc = self.get_subcategory_use_cases()
            product_uc = self.get_product_use_cases()
            
            return {
                "status": "healthy",
                "repositories": {
                    "category": str(type(category_repo).__name__),
                    "subcategory": str(type(subcategory_repo).__name__),
                    "product": str(type(product_repo).__name__)
                },
                "use_cases": {
                    "category": str(type(category_uc).__name__),
                    "subcategory": str(type(subcategory_uc).__name__),
                    "product": str(type(product_uc).__name__)
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }


# Instancia global del contenedor
container = DIContainer()
