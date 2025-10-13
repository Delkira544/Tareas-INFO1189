"""
Application Layer - Use Cases (Clean Architecture)
Casos de uso que orquestan la lógica de negocio
"""
from typing import List, Optional
from domain.entities import Product, Category, Subcategory
from domain.interfaces import IProductRepository, ICategoryRepository, ISubcategoryRepository


# ============================================================================
# Category Use Cases
# ============================================================================

class CategoryUseCases:
    """
    Casos de uso para gestionar categorías
    
    Principios SOLID:
    - Single Responsibility: Solo gestiona lógica de categorías
    - Dependency Inversion: Depende de abstracciones (interfaces)
    """
    
    def __init__(self, category_repository: ICategoryRepository):
        self._category_repository = category_repository
    
    def create_category(self, name: str, description: str = None) -> Category:
        """Crear nueva categoría con validaciones de negocio"""
        if not name or len(name.strip()) == 0:
            raise ValueError("El nombre de la categoría es requerido")
        
        category = Category(name=name.strip(), description=description)
        return self._category_repository.create(category)
    
    def get_category_by_id(self, category_id: int) -> Optional[Category]:
        """Obtener categoría por ID"""
        if category_id <= 0:
            raise ValueError("ID de categoría inválido")
        
        return self._category_repository.get_by_id(category_id)
    
    def get_all_categories(self) -> List[Category]:
        """Obtener todas las categorías"""
        return self._category_repository.get_all()
    
    def delete_category(self, category_id: int) -> bool:
        """Eliminar categoría (validar que no tenga subcategorías)"""
        if category_id <= 0:
            raise ValueError("ID de categoría inválido")
        
        # Aquí podrías agregar validación de negocio
        # Por ejemplo, verificar que no tenga subcategorías
        return self._category_repository.delete(category_id)


# ============================================================================
# Subcategory Use Cases
# ============================================================================

class SubcategoryUseCases:
    """Casos de uso para gestionar subcategorías"""
    
    def __init__(self, 
                 subcategory_repository: ISubcategoryRepository,
                 category_repository: ICategoryRepository):
        self._subcategory_repository = subcategory_repository
        self._category_repository = category_repository
    
    def create_subcategory(self, name: str, category_id: int, description: str = None) -> Subcategory:
        """Crear subcategoría con validaciones de negocio"""
        if not name or len(name.strip()) == 0:
            raise ValueError("El nombre de la subcategoría es requerido")
        
        if category_id <= 0:
            raise ValueError("ID de categoría inválido")
        
        # Validar que la categoría existe
        category = self._category_repository.get_by_id(category_id)
        if not category:
            raise ValueError(f"La categoría con ID {category_id} no existe")
        
        subcategory = Subcategory(
            name=name.strip(),
            description=description,
            category_id=category_id
        )
        
        return self._subcategory_repository.create(subcategory)
    
    def get_subcategory_by_id(self, subcategory_id: int) -> Optional[Subcategory]:
        """Obtener subcategoría por ID con información de categoría"""
        if subcategory_id <= 0:
            raise ValueError("ID de subcategoría inválido")
        
        return self._subcategory_repository.get_by_id(subcategory_id)
    
    def get_all_subcategories(self) -> List[Subcategory]:
        """Obtener todas las subcategorías con información de categoría"""
        return self._subcategory_repository.get_all()
    
    def get_subcategories_by_category(self, category_id: int) -> List[Subcategory]:
        """Obtener subcategorías de una categoría específica"""
        if category_id <= 0:
            raise ValueError("ID de categoría inválido")
        
        return self._subcategory_repository.get_by_category(category_id)
    
    def delete_subcategory(self, subcategory_id: int) -> bool:
        """Eliminar subcategoría"""
        if subcategory_id <= 0:
            raise ValueError("ID de subcategoría inválido")
        
        return self._subcategory_repository.delete(subcategory_id)


# ============================================================================
# Product Use Cases (Actualizados)
# ============================================================================

class ProductUseCases:
    """Casos de uso para gestionar productos con subcategorías"""
    
    def __init__(self, 
                 product_repository: IProductRepository,
                 subcategory_repository: ISubcategoryRepository):
        self._product_repository = product_repository
        self._subcategory_repository = subcategory_repository
    
    def create_product(self, name: str, price: float, subcategory_id: int, 
                      in_stock: bool = True, currency: str = "CLP") -> Product:
        """
        Crear producto con validaciones de negocio
        
        Business Rules:
        - Nombre requerido y mínimo 3 caracteres
        - Precio no negativo
        - Subcategoría debe existir
        - Moneda válida
        """
        if not name or len(name.strip()) < 3:
            raise ValueError("El nombre del producto debe tener al menos 3 caracteres")
        
        if price < 0:
            raise ValueError("El precio no puede ser negativo")
        
        if subcategory_id <= 0:
            raise ValueError("ID de subcategoría inválido")
        
        if currency not in ["CLP", "USD", "EUR"]:
            raise ValueError("Moneda no válida. Usar: CLP, USD, EUR")
        
        # Validar que la subcategoría existe
        subcategory = self._subcategory_repository.get_by_id(subcategory_id)
        if not subcategory:
            raise ValueError(f"La subcategoría con ID {subcategory_id} no existe")
        
        product = Product(
            name=name.strip(),
            price=price,
            in_stock=in_stock,
            currency=currency,
            subcategory_id=subcategory_id
        )
        
        return self._product_repository.create(product)
    
    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """Obtener producto por ID con subcategoría y categoría"""
        if product_id <= 0:
            raise ValueError("ID de producto inválido")
        
        return self._product_repository.get_by_id(product_id)
    
    def get_all_products(self) -> List[Product]:
        """Obtener todos los productos con subcategoría y categoría"""
        return self._product_repository.get_all()
    
    def get_products_by_subcategory(self, subcategory_id: int) -> List[Product]:
        """Obtener productos por subcategoría"""
        if subcategory_id <= 0:
            raise ValueError("ID de subcategoría inválido")
        
        return self._product_repository.get_by_subcategory(subcategory_id)
    
    def get_products_by_category(self, category_id: int) -> List[Product]:
        """Obtener todos los productos de una categoría (todas sus subcategorías)"""
        if category_id <= 0:
            raise ValueError("ID de categoría inválido")
        
        return self._product_repository.get_by_category(category_id)
    
    def update_product(self, product_id: int, name: str = None, price: float = None,
                      in_stock: bool = None, currency: str = None, 
                      subcategory_id: int = None) -> Optional[Product]:
        """
        Actualizar producto con validaciones
        
        Args:
            product_id: ID del producto a actualizar
            Los demás parámetros son opcionales (solo se actualizan si se proporcionan)
        """
        if product_id <= 0:
            raise ValueError("ID de producto inválido")
        
        # Obtener producto actual
        current_product = self._product_repository.get_by_id(product_id)
        if not current_product:
            raise ValueError(f"Producto con ID {product_id} no encontrado")
        
        # Actualizar solo los campos proporcionados
        if name is not None:
            if len(name.strip()) < 3:
                raise ValueError("El nombre debe tener al menos 3 caracteres")
            current_product.name = name.strip()
        
        if price is not None:
            if price < 0:
                raise ValueError("El precio no puede ser negativo")
            current_product.price = price
        
        if in_stock is not None:
            current_product.in_stock = in_stock
        
        if currency is not None:
            if currency not in ["CLP", "USD", "EUR"]:
                raise ValueError("Moneda no válida")
            current_product.currency = currency
        
        if subcategory_id is not None:
            if subcategory_id <= 0:
                raise ValueError("ID de subcategoría inválido")
            
            # Validar que la subcategoría existe
            subcategory = self._subcategory_repository.get_by_id(subcategory_id)
            if not subcategory:
                raise ValueError(f"La subcategoría con ID {subcategory_id} no existe")
            
            current_product.subcategory_id = subcategory_id
        
        return self._product_repository.update(current_product)
    
    def delete_product(self, product_id: int) -> bool:
        """Eliminar producto"""
        if product_id <= 0:
            raise ValueError("ID de producto inválido")
        
        return self._product_repository.delete(product_id)
    
    def get_available_products(self) -> List[Product]:
        """Obtener solo productos disponibles (regla de negocio)"""
        all_products = self.get_all_products()
        return [product for product in all_products if product.is_available()]
    
    def apply_discount_to_category(self, category_id: int, discount_percentage: float) -> List[Product]:
        """
        Aplicar descuento a todos los productos de una categoría
        
        Business Rule: Descuento válido entre 0-100%
        """
        if discount_percentage < 0 or discount_percentage > 100:
            raise ValueError("El descuento debe estar entre 0% y 100%")
        
        products = self.get_products_by_category(category_id)
        updated_products = []
        
        for product in products:
            discounted_price = product.calculate_discount(discount_percentage)
            updated_product = self.update_product(product.id, price=discounted_price)
            if updated_product:
                updated_products.append(updated_product)
        
        return updated_products
