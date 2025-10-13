"""
GraphQL API - Implementación con Clean Architecture
Usa Use Cases en lugar de acceder directamente a repositorios
"""
from typing import List, Optional
import strawberry

from infrastructure.container import get_container


# ============================================================================
# GraphQL Types
# ============================================================================

@strawberry.type
class CategoryType:
    """Tipo GraphQL para Category"""
    id: int
    name: str
    description: Optional[str] = None
    
    @strawberry.field
    def products(self) -> List["ProductType"]:
        """Obtener todos los productos de esta categoría"""
        container = get_container()
        use_case = container.get_products_use_case()
        products = use_case.execute(category_id=self.id)
        
        return [
            ProductType(
                id=p.id,
                name=p.name,
                price=p.price,
                in_stock=p.in_stock,
                currency=p.currency,
                category_id=p.category_id
            )
            for p in products
        ]


@strawberry.type
class ProductType:
    """Tipo GraphQL para Product"""
    id: int
    name: str
    price: float
    in_stock: bool
    currency: str
    category_id: Optional[int] = None
    
    @strawberry.field
    def category(self) -> Optional[CategoryType]:
        """Obtener la categoría de este producto"""
        if not self.category_id:
            return None
        
        container = get_container()
        use_case = container.get_category_by_id_use_case()
        category = use_case.execute(self.category_id)
        
        if not category:
            return None
        
        return CategoryType(
            id=category.id,
            name=category.name,
            description=category.description
        )


# ============================================================================
# Input Types
# ============================================================================

@strawberry.input
class ProductInput:
    """Input para crear productos en GraphQL"""
    name: str
    price: float
    in_stock: bool
    currency: str = "CLP"
    category_id: Optional[int] = None


@strawberry.input
class ProductUpdateInput:
    """Input para actualizar productos en GraphQL"""
    name: Optional[str] = None
    price: Optional[float] = None
    in_stock: Optional[bool] = None
    currency: Optional[str] = None
    category_id: Optional[int] = None


@strawberry.input
class CategoryInput:
    """Input para crear categorías en GraphQL"""
    name: str
    description: Optional[str] = None


# ============================================================================
# Queries
# ============================================================================

@strawberry.type
class Query:
    """Queries GraphQL - Operaciones de lectura"""
    
    @strawberry.field
    def categories(self) -> List[CategoryType]:
        """Obtener todas las categorías"""
        container = get_container()
        use_case = container.get_categories_use_case()
        categories = use_case.execute()
        
        return [
            CategoryType(
                id=c.id,
                name=c.name,
                description=c.description
            )
            for c in categories
        ]
    
    @strawberry.field
    def category(self, category_id: int) -> Optional[CategoryType]:
        """Obtener una categoría por ID"""
        container = get_container()
        use_case = container.get_category_by_id_use_case()
        category = use_case.execute(category_id)
        
        if not category:
            return None
        
        return CategoryType(
            id=category.id,
            name=category.name,
            description=category.description
        )
    
    @strawberry.field
    def products(self, category_id: Optional[int] = None) -> List[ProductType]:
        """Obtener todos los productos, opcionalmente filtrados por categoría"""
        container = get_container()
        use_case = container.get_products_use_case()
        products = use_case.execute(category_id=category_id)
        
        return [
            ProductType(
                id=p.id,
                name=p.name,
                price=p.price,
                in_stock=p.in_stock,
                currency=p.currency,
                category_id=p.category_id
            )
            for p in products
        ]
    
    @strawberry.field
    def product(self, product_id: int) -> Optional[ProductType]:
        """Obtener un producto por ID"""
        container = get_container()
        use_case = container.get_product_by_id_use_case()
        product = use_case.execute(product_id)
        
        if not product:
            return None
        
        return ProductType(
            id=product.id,
            name=product.name,
            price=product.price,
            in_stock=product.in_stock,
            currency=product.currency,
            category_id=product.category_id
        )


# ============================================================================
# Mutations
# ============================================================================

@strawberry.type
class Mutation:
    """Mutations GraphQL - Operaciones de escritura"""
    
    @strawberry.mutation
    def create_product(self, product_input: ProductInput) -> ProductType:
        """Crear un nuevo producto"""
        container = get_container()
        use_case = container.create_product_use_case()
        
        try:
            product = use_case.execute({
                'name': product_input.name,
                'price': product_input.price,
                'in_stock': product_input.in_stock,
                'currency': product_input.currency,
                'category_id': product_input.category_id
            })
            
            return ProductType(
                id=product.id,
                name=product.name,
                price=product.price,
                in_stock=product.in_stock,
                currency=product.currency,
                category_id=product.category_id
            )
        except (ValueError, Exception) as e:
            raise Exception(f"Error al crear producto: {str(e)}")
    
    @strawberry.mutation
    def update_product(
        self, 
        product_id: int, 
        product_input: ProductUpdateInput
    ) -> Optional[ProductType]:
        """Actualizar un producto"""
        container = get_container()
        use_case = container.update_product_use_case()
        
        try:
            update_data = {}
            if product_input.name is not None:
                update_data['name'] = product_input.name
            if product_input.price is not None:
                update_data['price'] = product_input.price
            if product_input.in_stock is not None:
                update_data['in_stock'] = product_input.in_stock
            if product_input.currency is not None:
                update_data['currency'] = product_input.currency
            if product_input.category_id is not None:
                update_data['category_id'] = product_input.category_id
            
            product = use_case.execute(product_id, update_data)
            
            if not product:
                return None
            
            return ProductType(
                id=product.id,
                name=product.name,
                price=product.price,
                in_stock=product.in_stock,
                currency=product.currency,
                category_id=product.category_id
            )
        except (ValueError, Exception) as e:
            raise Exception(f"Error al actualizar producto: {str(e)}")
    
    @strawberry.mutation
    def delete_product(self, product_id: int) -> bool:
        """Eliminar un producto"""
        container = get_container()
        use_case = container.delete_product_use_case()
        
        try:
            return use_case.execute(product_id)
        except ValueError as e:
            raise Exception(str(e))
    
    @strawberry.mutation
    def create_category(self, category_input: CategoryInput) -> CategoryType:
        """Crear una nueva categoría"""
        container = get_container()
        use_case = container.create_category_use_case()
        
        category = use_case.execute({
            'name': category_input.name,
            'description': category_input.description
        })
        
        return CategoryType(
            id=category.id,
            name=category.name,
            description=category.description
        )
    
    @strawberry.mutation
    def delete_category(self, category_id: int) -> bool:
        """Eliminar una categoría"""
        container = get_container()
        
        # Verificar que existe antes de eliminar
        get_category_use_case = container.get_category_by_id_use_case()
        category = get_category_use_case.execute(category_id)
        if not category:
            raise Exception(f"Categoría con ID {category_id} no encontrada")
        
        # Verificar que no tenga productos asociados
        products_use_case = container.get_products_use_case()
        products = products_use_case.execute(category_id=category_id)
        
        if products:
            raise Exception(f"No se puede eliminar la categoría porque tiene {len(products)} producto(s) asociado(s)")
        
        # Eliminar categoría
        from infrastructure.repositories import SQLiteCategoryRepository
        repo = SQLiteCategoryRepository()
        
        try:
            success = repo.delete(category_id)
            return success
        except Exception as e:
            raise Exception(f"Error al eliminar categoría: {str(e)}")


# ============================================================================
# Schema
# ============================================================================

schema = strawberry.Schema(query=Query, mutation=Mutation)
