"""
Resolvers GraphQL
Contienen la lógica de negocio para las queries y mutations
"""
from typing import List, Optional
import strawberry
from products.repository import ProductRepository, CategoryRepository
from products.models import ProductRequest, ProductUpdate, CategoryRequest
from .types import ProductType, ProductInput, ProductUpdateInput, CategoryType, CategoryInput


# Instancias de repositorios
product_repository = ProductRepository()
category_repository = CategoryRepository()


@strawberry.type
class Query:
    """Queries GraphQL - Operaciones de lectura"""
    
    @strawberry.field
    def categories(self) -> List[CategoryType]:
        """
        Obtener todas las categorías
        Query: { categories { id name description } }
        """
        categories = category_repository.get_all()
        return [
            CategoryType(
                id=c.id,
                name=c.name,
                description=c.description
            )
            for c in categories
        ]
    
    @strawberry.field
    def category(self, category_id: int) -> CategoryType:
        """
        Obtener una categoría por ID
        Query: { category(categoryId: 1) { id name description } }
        """
        category = category_repository.get_by_id(category_id)
        if not category:
            raise Exception(f"Categoría con ID {category_id} no encontrada")
        
        return CategoryType(
            id=category.id,
            name=category.name,
            description=category.description
        )
    
    @strawberry.field
    def products(self, category_id: Optional[int] = None) -> List[ProductType]:
        """
        Obtener todos los productos, opcionalmente filtrados por categoría
        Query: { products { id name price inStock currency categoryName } }
        Query con filtro: { products(categoryId: 1) { id name price categoryName } }
        """
        if category_id:
            products = product_repository.get_by_category(category_id)
        else:
            products = product_repository.get_all()
        
        return [
            ProductType(
                id=p.id,
                name=p.name,
                price=p.price,
                in_stock=p.in_stock,
                currency=p.currency,
                category_id=p.category_id,
                category_name=p.category_name
            )
            for p in products
        ]
    
    @strawberry.field
    def product(self, product_id: int) -> ProductType:
        """
        Obtener un producto por ID
        Query: { product(productId: 1) { id name price inStock currency categoryName } }
        """
        product = product_repository.get_by_id(product_id)
        if not product:
            raise Exception(f"Producto con ID {product_id} no encontrado")
        
        return ProductType(
            id=product.id,
            name=product.name,
            price=product.price,
            in_stock=product.in_stock,
            currency=product.currency,
            category_id=product.category_id,
            category_name=product.category_name
        )


@strawberry.type
class Mutation:
    """Mutations GraphQL - Operaciones de escritura"""
    
    @strawberry.mutation
    def create_category(self, input: CategoryInput) -> CategoryType:
        """
        Crear una nueva categoría
        Mutation: 
        mutation {
          createCategory(input: {
            name: "Procesadores"
            description: "CPUs Intel y AMD"
          }) {
            id name description
          }
        }
        """
        category_request = CategoryRequest(
            name=input.name,
            description=input.description
        )
        
        category = category_repository.create(category_request)
        
        return CategoryType(
            id=category.id,
            name=category.name,
            description=category.description
        )
    
    @strawberry.mutation
    def create_product(self, input: ProductInput) -> ProductType:
        """
        Crear un nuevo producto
        Mutation: 
        mutation {
          createProduct(input: {
            name: "RTX 4090"
            price: 1999.99
            inStock: true
            currency: "USD"
            categoryId: 2
          }) {
            id name price inStock currency categoryName
          }
        }
        """
        # Validación
        if input.price <= 0:
            raise Exception("El precio debe ser mayor a 0")
        
        # Verificar que la categoría existe si se proporciona
        if input.category_id:
            category = category_repository.get_by_id(input.category_id)
            if not category:
                raise Exception(f"Categoría con ID {input.category_id} no encontrada")
        
        # Crear producto usando el repositorio
        product_request = ProductRequest(
            name=input.name,
            price=input.price,
            in_stock=input.in_stock,
            currency=input.currency,
            category_id=input.category_id
        )
        
        product = product_repository.create(product_request)
        
        return ProductType(
            id=product.id,
            name=product.name,
            price=product.price,
            in_stock=product.in_stock,
            currency=product.currency,
            category_id=product.category_id,
            category_name=product.category_name
        )
    
    @strawberry.mutation
    def update_product(self, product_id: int, input: ProductUpdateInput) -> ProductType:
        """
        Actualizar un producto existente (actualización parcial)
        Mutation:
        mutation {
          updateProduct(productId: 1, input: {
            price: 899.99
            categoryId: 3
          }) {
            id name price inStock currency categoryName
          }
        }
        """
        # Validación
        if input.price is not None and input.price <= 0:
            raise Exception("El precio debe ser mayor a 0")
        
        # Verificar que la categoría existe si se proporciona
        if input.category_id:
            category = category_repository.get_by_id(input.category_id)
            if not category:
                raise Exception(f"Categoría con ID {input.category_id} no encontrada")
        
        # Actualizar usando el repositorio
        product_update = ProductUpdate(
            name=input.name,
            price=input.price,
            in_stock=input.in_stock,
            currency=input.currency,
            category_id=input.category_id
        )
        
        product = product_repository.update(product_id, product_update)
        if not product:
            raise Exception(f"Producto con ID {product_id} no encontrado")
        
        return ProductType(
            id=product.id,
            name=product.name,
            price=product.price,
            in_stock=product.in_stock,
            currency=product.currency,
            category_id=product.category_id,
            category_name=product.category_name
        )
    
    @strawberry.mutation
    def delete_product(self, product_id: int) -> bool:
        """
        Eliminar un producto
        Mutation:
        mutation {
          deleteProduct(productId: 1)
        }
        """
        success = product_repository.delete(product_id)
        if not success:
            raise Exception(f"Producto con ID {product_id} no encontrado")
        return success
    
    @strawberry.mutation
    def delete_category(self, category_id: int) -> bool:
        """
        Eliminar una categoría
        Mutation:
        mutation {
          deleteCategory(categoryId: 1)
        }
        """
        success = category_repository.delete(category_id)
        if not success:
            raise Exception(f"Categoría con ID {category_id} no encontrada")
        return success
