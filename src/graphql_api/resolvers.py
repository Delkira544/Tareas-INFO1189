"""
Resolvers GraphQL
Contienen la lógica de negocio para las queries y mutations
"""
from typing import List
import strawberry
from products.repository import ProductRepository
from products.models import ProductRequest, ProductUpdate
from .types import ProductType, ProductInput, ProductUpdateInput


# Instancia del repositorio
product_repository = ProductRepository()


@strawberry.type
class Query:
    """Queries GraphQL - Operaciones de lectura"""
    
    @strawberry.field
    def products(self) -> List[ProductType]:
        """
        Obtener todos los productos
        Query: { products { id name price in_stock currency } }
        """
        products = product_repository.get_all()
        return [
            ProductType(
                id=p.id,
                name=p.name,
                price=p.price,
                in_stock=p.in_stock,
                currency=p.currency
            )
            for p in products
        ]
    
    @strawberry.field
    def product(self, product_id: int) -> ProductType:
        """
        Obtener un producto por ID
        Query: { product(productId: 1) { id name price in_stock currency } }
        """
        product = product_repository.get_by_id(product_id)
        if not product:
            raise Exception(f"Producto con ID {product_id} no encontrado")
        
        return ProductType(
            id=product.id,
            name=product.name,
            price=product.price,
            in_stock=product.in_stock,
            currency=product.currency
        )


@strawberry.type
class Mutation:
    """Mutations GraphQL - Operaciones de escritura"""
    
    @strawberry.mutation
    def create_product(self, input: ProductInput) -> ProductType:
        """
        Crear un nuevo producto
        Mutation: 
        mutation {
          createProduct(input: {
            name: "Laptop"
            price: 999.99
            inStock: true
            currency: "USD"
          }) {
            id name price inStock currency
          }
        }
        """
        # Validación
        if input.price <= 0:
            raise Exception("El precio debe ser mayor a 0")
        
        # Crear producto usando el repositorio
        product_request = ProductRequest(
            name=input.name,
            price=input.price,
            in_stock=input.in_stock,
            currency=input.currency
        )
        
        product = product_repository.create(product_request)
        
        return ProductType(
            id=product.id,
            name=product.name,
            price=product.price,
            in_stock=product.in_stock,
            currency=product.currency
        )
    
    @strawberry.mutation
    def update_product(self, product_id: int, input: ProductUpdateInput) -> ProductType:
        """
        Actualizar un producto existente (actualización parcial)
        Mutation:
        mutation {
          updateProduct(productId: 1, input: {
            price: 899.99
          }) {
            id name price inStock currency
          }
        }
        """
        # Validación
        if input.price is not None and input.price <= 0:
            raise Exception("El precio debe ser mayor a 0")
        
        # Actualizar usando el repositorio
        product_update = ProductUpdate(
            name=input.name,
            price=input.price,
            in_stock=input.in_stock,
            currency=input.currency
        )
        
        product = product_repository.update(product_id, product_update)
        if not product:
            raise Exception(f"Producto con ID {product_id} no encontrado")
        
        return ProductType(
            id=product.id,
            name=product.name,
            price=product.price,
            in_stock=product.in_stock,
            currency=product.currency
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
