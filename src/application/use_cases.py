"""
Application Layer - Use Cases (Clean Architecture)
Contiene la lógica de aplicación, orquesta las entidades del dominio

SOLID Principles aplicados:
- Single Responsibility: Cada use case tiene una única responsabilidad
- Open/Closed: Extensible sin modificar código existente
- Dependency Inversion: Depende de interfaces, no de implementaciones
"""
from typing import List, Optional
from domain.entities import Product, Category
from domain.interfaces import IProductRepository, ICategoryRepository


class CreateProductUseCase:
    """
    Use Case: Crear Producto (SOLID: Single Responsibility)
    Responsabilidad única: Orquestar la creación de un producto
    """
    
    def __init__(
        self, 
        product_repo: IProductRepository,
        category_repo: ICategoryRepository
    ):
        self.product_repo = product_repo
        self.category_repo = category_repo
    
    def execute(self, product_data: dict) -> Product:
        """
        Ejecutar caso de uso con validaciones de negocio
        ACID: Garantiza atomicidad en la creación
        """
        # Validación de negocio: verificar que la categoría existe
        if product_data.get('category_id'):
            category = self.category_repo.get_by_id(product_data['category_id'])
            if not category:
                raise ValueError(f"Categoría {product_data['category_id']} no encontrada")
        
        # Crear entidad de dominio (con validaciones propias)
        product = Product(
            name=product_data['name'],
            price=product_data['price'],
            in_stock=product_data.get('in_stock', True),
            currency=product_data.get('currency', 'CLP'),
            category_id=product_data.get('category_id')
        )
        
        # Persistir (ACID: operación atómica)
        return self.product_repo.create(product)


class GetProductsUseCase:
    """Use Case: Obtener Productos"""
    
    def __init__(self, product_repo: IProductRepository):
        self.product_repo = product_repo
    
    def execute(self, category_id: Optional[int] = None) -> List[Product]:
        """Obtener productos, opcionalmente filtrados por categoría"""
        if category_id:
            return self.product_repo.get_by_category(category_id)
        return self.product_repo.get_all()


class GetProductByIdUseCase:
    """Use Case: Obtener Producto por ID"""
    
    def __init__(self, product_repo: IProductRepository):
        self.product_repo = product_repo
    
    def execute(self, product_id: int) -> Optional[Product]:
        """Obtener un producto específico"""
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise ValueError(f"Producto {product_id} no encontrado")
        return product


class UpdateProductUseCase:
    """
    Use Case: Actualizar Producto
    ACID: Garantiza consistencia en la actualización
    """
    
    def __init__(
        self,
        product_repo: IProductRepository,
        category_repo: ICategoryRepository
    ):
        self.product_repo = product_repo
        self.category_repo = category_repo
    
    def execute(self, product_id: int, update_data: dict) -> Product:
        """
        Actualizar producto con validaciones
        ACID: Isolation - la actualización es aislada de otras operaciones
        """
        # Obtener producto existente
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise ValueError(f"Producto {product_id} no encontrado")
        
        # Validar categoría si se está actualizando
        if 'category_id' in update_data and update_data['category_id']:
            category = self.category_repo.get_by_id(update_data['category_id'])
            if not category:
                raise ValueError(f"Categoría {update_data['category_id']} no encontrada")
        
        # Actualizar campos
        if 'name' in update_data:
            product.name = update_data['name']
        if 'price' in update_data:
            product.price = update_data['price']
        if 'in_stock' in update_data:
            product.in_stock = update_data['in_stock']
        if 'currency' in update_data:
            product.currency = update_data['currency']
        if 'category_id' in update_data:
            product.category_id = update_data['category_id']
        
        # Validaciones de dominio se ejecutan automáticamente
        product.__post_init__()
        
        # Persistir cambios (ACID: Durability)
        return self.product_repo.update(product)


class DeleteProductUseCase:
    """
    Use Case: Eliminar Producto
    ACID: Operación durable y atómica
    """
    
    def __init__(self, product_repo: IProductRepository):
        self.product_repo = product_repo
    
    def execute(self, product_id: int) -> bool:
        """Eliminar producto"""
        # Verificar que existe
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise ValueError(f"Producto {product_id} no encontrado")
        
        # Eliminar (ACID: operación atómica y durable)
        return self.product_repo.delete(product_id)


class CreateCategoryUseCase:
    """Use Case: Crear Categoría"""
    
    def __init__(self, category_repo: ICategoryRepository):
        self.category_repo = category_repo
    
    def execute(self, category_data: dict) -> Category:
        """Crear nueva categoría con validaciones"""
        category = Category(
            name=category_data['name'],
            description=category_data.get('description')
        )
        return self.category_repo.create(category)


class GetCategoriesUseCase:
    """Use Case: Obtener Categorías"""
    
    def __init__(self, category_repo: ICategoryRepository):
        self.category_repo = category_repo
    
    def execute(self) -> List[Category]:
        """Obtener todas las categorías"""
        return self.category_repo.get_all()


class GetCategoryByIdUseCase:
    """Use Case: Obtener Categoría por ID"""
    
    def __init__(self, category_repo: ICategoryRepository):
        self.category_repo = category_repo
    
    def execute(self, category_id: int) -> Optional[Category]:
        """Obtener categoría específica"""
        category = self.category_repo.get_by_id(category_id)
        if not category:
            raise ValueError(f"Categoría {category_id} no encontrada")
        return category
