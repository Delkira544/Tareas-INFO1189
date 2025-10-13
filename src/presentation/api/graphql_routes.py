"""
GraphQL Routes - Presentation Layer (Updated)
API GraphQL para consultas complejas con subcategorías y categorías
"""
from fastapi import APIRouter, Depends
import strawberry
from strawberry.fastapi import GraphQLRouter
from typing import List, Optional

from infrastructure.container import container
from application.use_cases import ProductUseCases, CategoryUseCases, SubcategoryUseCases


# ============================================================================
# GraphQL Types (Strawberry)
# ============================================================================

@strawberry.type
class CategoryType:
    """Tipo GraphQL para Category"""
    id: int
    name: str
    description: Optional[str]
    created_at: Optional[str]


@strawberry.type
class SubcategoryType:
    """Tipo GraphQL para Subcategory con información de categoría"""
    id: int
    name: str
    description: Optional[str]
    category_id: int
    created_at: Optional[str]
    category: Optional[CategoryType]


@strawberry.type
class ProductType:
    """Tipo GraphQL para Product con subcategoría y categoría anidadas"""
    id: int
    name: str
    price: float
    in_stock: bool
    currency: str
    subcategory_id: int
    created_at: Optional[str]
    subcategory: Optional[SubcategoryType]


@strawberry.input
class ProductCreateInput:
    """Input para crear producto via GraphQL"""
    name: str
    price: float
    subcategory_id: int
    in_stock: bool = True
    currency: str = "CLP"


@strawberry.input
class CategoryCreateInput:
    """Input para crear categoría via GraphQL"""
    name: str
    description: Optional[str] = None


@strawberry.input
class SubcategoryCreateInput:
    """Input para crear subcategoría via GraphQL"""
    name: str
    category_id: int
    description: Optional[str] = None


# ============================================================================
# Helper Functions
# ============================================================================

def map_category_to_graphql(category) -> CategoryType:
    """Convertir entidad Category a CategoryType"""
    return CategoryType(
        id=category.id,
        name=category.name,
        description=category.description,
        created_at=category.created_at.isoformat() if category.created_at else None
    )


def map_subcategory_to_graphql(subcategory) -> SubcategoryType:
    """Convertir entidad Subcategory a SubcategoryType"""
    return SubcategoryType(
        id=subcategory.id,
        name=subcategory.name,
        description=subcategory.description,
        category_id=subcategory.category_id,
        created_at=subcategory.created_at.isoformat() if subcategory.created_at else None,
        category=map_category_to_graphql(subcategory.category) if subcategory.category else None
    )


def map_product_to_graphql(product) -> ProductType:
    """Convertir entidad Product a ProductType"""
    return ProductType(
        id=product.id,
        name=product.name,
        price=product.price,
        in_stock=product.in_stock,
        currency=product.currency,
        subcategory_id=product.subcategory_id,
        created_at=product.created_at.isoformat() if product.created_at else None,
        subcategory=map_subcategory_to_graphql(product.subcategory) if product.subcategory else None
    )


# ============================================================================
# Dependency Injection para GraphQL
# ============================================================================

def get_product_use_cases() -> ProductUseCases:
    return container.get_product_use_cases()


def get_category_use_cases() -> CategoryUseCases:
    return container.get_category_use_cases()


def get_subcategory_use_cases() -> SubcategoryUseCases:
    return container.get_subcategory_use_cases()


# ============================================================================
# GraphQL Query Class
# ============================================================================

@strawberry.type
class Query:
    """
    GraphQL Queries
    
    Permite consultas flexibles y específicas siguiendo el principio
    de "pedir solo lo que necesitas" de GraphQL
    """
    
    @strawberry.field
    def products(self) -> List[ProductType]:
        """Obtener todos los productos con subcategoría y categoría"""
        use_cases = get_product_use_cases()
        products = use_cases.get_all_products()
        return [map_product_to_graphql(product) for product in products]
    
    @strawberry.field
    def product(self, id: int) -> Optional[ProductType]:
        """Obtener producto por ID"""
        use_cases = get_product_use_cases()
        product = use_cases.get_product_by_id(id)
        return map_product_to_graphql(product) if product else None
    
    @strawberry.field
    def products_by_subcategory(self, subcategory_id: int) -> List[ProductType]:
        """Obtener productos por subcategoría"""
        use_cases = get_product_use_cases()
        products = use_cases.get_products_by_subcategory(subcategory_id)
        return [map_product_to_graphql(product) for product in products]
    
    @strawberry.field
    def products_by_category(self, category_id: int) -> List[ProductType]:
        """Obtener productos por categoría (todas sus subcategorías)"""
        use_cases = get_product_use_cases()
        products = use_cases.get_products_by_category(category_id)
        return [map_product_to_graphql(product) for product in products]
    
    @strawberry.field
    def available_products(self) -> List[ProductType]:
        """Obtener solo productos disponibles"""
        use_cases = get_product_use_cases()
        products = use_cases.get_available_products()
        return [map_product_to_graphql(product) for product in products]
    
    @strawberry.field
    def categories(self) -> List[CategoryType]:
        """Obtener todas las categorías"""
        use_cases = get_category_use_cases()
        categories = use_cases.get_all_categories()
        return [map_category_to_graphql(category) for category in categories]
    
    @strawberry.field
    def category(self, id: int) -> Optional[CategoryType]:
        """Obtener categoría por ID"""
        use_cases = get_category_use_cases()
        category = use_cases.get_category_by_id(id)
        return map_category_to_graphql(category) if category else None
    
    @strawberry.field
    def subcategories(self) -> List[SubcategoryType]:
        """Obtener todas las subcategorías con información de categoría"""
        use_cases = get_subcategory_use_cases()
        subcategories = use_cases.get_all_subcategories()
        return [map_subcategory_to_graphql(subcategory) for subcategory in subcategories]
    
    @strawberry.field
    def subcategory(self, id: int) -> Optional[SubcategoryType]:
        """Obtener subcategoría por ID"""
        use_cases = get_subcategory_use_cases()
        subcategory = use_cases.get_subcategory_by_id(id)
        return map_subcategory_to_graphql(subcategory) if subcategory else None
    
    @strawberry.field
    def subcategories_by_category(self, category_id: int) -> List[SubcategoryType]:
        """Obtener subcategorías por categoría"""
        use_cases = get_subcategory_use_cases()
        subcategories = use_cases.get_subcategories_by_category(category_id)
        return [map_subcategory_to_graphql(subcategory) for subcategory in subcategories]


# ============================================================================
# GraphQL Mutation Class
# ============================================================================

@strawberry.type
class Mutation:
    """
    GraphQL Mutations
    
    Operaciones de escritura (CREATE, UPDATE, DELETE)
    Requieren autenticación JWT mediante middleware
    """
    
    @strawberry.mutation
    def create_product(self, input: ProductCreateInput) -> ProductType:
        """Crear nuevo producto"""
        try:
            use_cases = get_product_use_cases()
            product = use_cases.create_product(
                name=input.name,
                price=input.price,
                subcategory_id=input.subcategory_id,
                in_stock=input.in_stock,
                currency=input.currency
            )
            return map_product_to_graphql(product)
        except ValueError as e:
            raise Exception(f"Error de validación: {str(e)}")
        except Exception as e:
            raise Exception(f"Error interno: {str(e)}")
    
    @strawberry.mutation
    def create_category(self, input: CategoryCreateInput) -> CategoryType:
        """Crear nueva categoría"""
        try:
            use_cases = get_category_use_cases()
            category = use_cases.create_category(
                name=input.name,
                description=input.description
            )
            return map_category_to_graphql(category)
        except ValueError as e:
            raise Exception(f"Error de validación: {str(e)}")
        except Exception as e:
            raise Exception(f"Error interno: {str(e)}")
    
    @strawberry.mutation
    def create_subcategory(self, input: SubcategoryCreateInput) -> SubcategoryType:
        """Crear nueva subcategoría"""
        try:
            use_cases = get_subcategory_use_cases()
            subcategory = use_cases.create_subcategory(
                name=input.name,
                category_id=input.category_id,
                description=input.description
            )
            return map_subcategory_to_graphql(subcategory)
        except ValueError as e:
            raise Exception(f"Error de validación: {str(e)}")
        except Exception as e:
            raise Exception(f"Error interno: {str(e)}")
    
    @strawberry.mutation
    def delete_product(self, id: int) -> bool:
        """Eliminar producto"""
        try:
            use_cases = get_product_use_cases()
            return use_cases.delete_product(id)
        except ValueError as e:
            raise Exception(f"Error de validación: {str(e)}")
        except Exception as e:
            raise Exception(f"Error interno: {str(e)}")
    
    @strawberry.mutation
    def delete_category(self, id: int) -> bool:
        """Eliminar categoría"""
        try:
            use_cases = get_category_use_cases()
            return use_cases.delete_category(id)
        except ValueError as e:
            raise Exception(f"Error de validación: {str(e)}")
        except Exception as e:
            raise Exception(f"Error interno: {str(e)}")
    
    @strawberry.mutation
    def delete_subcategory(self, id: int) -> bool:
        """Eliminar subcategoría"""
        try:
            use_cases = get_subcategory_use_cases()
            return use_cases.delete_subcategory(id)
        except ValueError as e:
            raise Exception(f"Error de validación: {str(e)}")
        except Exception as e:
            raise Exception(f"Error interno: {str(e)}")
    
    @strawberry.mutation
    def apply_discount_to_category(self, category_id: int, discount_percentage: float) -> str:
        """Aplicar descuento a todos los productos de una categoría"""
        try:
            use_cases = get_product_use_cases()
            updated_products = use_cases.apply_discount_to_category(category_id, discount_percentage)
            return f"Descuento del {discount_percentage}% aplicado a {len(updated_products)} productos"
        except ValueError as e:
            raise Exception(f"Error de validación: {str(e)}")
        except Exception as e:
            raise Exception(f"Error interno: {str(e)}")


# ============================================================================
# GraphQL Schema
# ============================================================================

schema = strawberry.Schema(query=Query, mutation=Mutation)

# Router GraphQL
router = APIRouter()
graphql_app = GraphQLRouter(schema)

router.include_router(graphql_app, prefix="/graphql")
