"""
Dependency Injection Container - Infrastructure Layer
Gestiona la creación e inyección de dependencias (SOLID: Dependency Inversion)
"""
from functools import lru_cache

from application.use_cases import (
    CreateProductUseCase,
    GetProductsUseCase,
    GetProductByIdUseCase,
    UpdateProductUseCase,
    DeleteProductUseCase,
    CreateCategoryUseCase,
    GetCategoriesUseCase,
    GetCategoryByIdUseCase
)
from infrastructure.repositories import (
    SQLiteProductRepository,
    SQLiteCategoryRepository
)


class DependencyContainer:
    """
    Contenedor de Inyección de Dependencias
    
    Implementa el patrón Dependency Injection para:
    - Desacoplar capas (SOLID: Dependency Inversion)
    - Facilitar testing (mock de repositorios)
    - Centralizar configuración
    - Gestionar ciclo de vida de objetos
    """
    
    def __init__(self):
        """Inicializar contenedor (usa DatabaseManager global de infrastructure)"""
        # Repositorios (Singleton - una instancia por contenedor)
        self._product_repository = None
        self._category_repository = None
    
    # ========================================================================
    # Factories de Repositorios
    # ========================================================================
    
    def product_repository(self) -> SQLiteProductRepository:
        """Obtener instancia del repositorio de productos (Singleton)"""
        if self._product_repository is None:
            self._product_repository = SQLiteProductRepository()
        return self._product_repository
    
    def category_repository(self) -> SQLiteCategoryRepository:
        """Obtener instancia del repositorio de categorías (Singleton)"""
        if self._category_repository is None:
            self._category_repository = SQLiteCategoryRepository()
        return self._category_repository
    
    # ========================================================================
    # Factories de Use Cases - Products
    # ========================================================================
    
    def create_product_use_case(self) -> CreateProductUseCase:
        """
        Crear Use Case para crear productos
        Inyecta repositorio de productos y categorías
        """
        return CreateProductUseCase(
            product_repository=self.product_repository(),
            category_repository=self.category_repository()
        )
    
    def get_products_use_case(self) -> GetProductsUseCase:
        """Crear Use Case para obtener productos"""
        return GetProductsUseCase(
            product_repository=self.product_repository()
        )
    
    def get_product_by_id_use_case(self) -> GetProductByIdUseCase:
        """Crear Use Case para obtener producto por ID"""
        return GetProductByIdUseCase(
            product_repository=self.product_repository()
        )
    
    def update_product_use_case(self) -> UpdateProductUseCase:
        """Crear Use Case para actualizar productos"""
        return UpdateProductUseCase(
            product_repository=self.product_repository(),
            category_repository=self.category_repository()
        )
    
    def delete_product_use_case(self) -> DeleteProductUseCase:
        """Crear Use Case para eliminar productos"""
        return DeleteProductUseCase(
            product_repository=self.product_repository()
        )
    
    # ========================================================================
    # Factories de Use Cases - Categories
    # ========================================================================
    
    def create_category_use_case(self) -> CreateCategoryUseCase:
        """Crear Use Case para crear categorías"""
        return CreateCategoryUseCase(
            category_repository=self.category_repository()
        )
    
    def get_categories_use_case(self) -> GetCategoriesUseCase:
        """Crear Use Case para obtener categorías"""
        return GetCategoriesUseCase(
            category_repository=self.category_repository()
        )
    
    def get_category_by_id_use_case(self) -> GetCategoryByIdUseCase:
        """Crear Use Case para obtener categoría por ID"""
        return GetCategoryByIdUseCase(
            category_repository=self.category_repository()
        )


# ============================================================================
# Instancia global del contenedor (Singleton)
# ============================================================================

@lru_cache
def get_container() -> DependencyContainer:
    """
    Obtener instancia global del contenedor (Singleton)
    
    Uses lru_cache para garantizar una única instancia.
    Esta función es la que se debe importar en las capas superiores.
    """
    return DependencyContainer()
