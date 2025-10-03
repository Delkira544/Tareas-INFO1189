from typing import List, Optional
from .models import Product, ProductRequest, ProductUpdate
from .repository import ProductRepository

class ProductController:
    def __init__(self, repository: ProductRepository):
        self.repository = repository
    
    def create_product(self, product_request: ProductRequest) -> Product:
        # Aquí puedes agregar validaciones de negocio
        if product_request.price <= 0:
            raise ValueError("El precio debe ser mayor a 0")
        
        return self.repository.create(product_request)
    
    def get_product(self, product_id: int) -> Optional[Product]:
        return self.repository.get_by_id(product_id)
    
    def get_all_products(self) -> List[Product]:
        return self.repository.get_all()
    
    def update_product(self, product_id: int, product_update: ProductUpdate) -> Optional[Product]:
        # Validaciones de negocio
        if product_update.price is not None and product_update.price <= 0:
            raise ValueError("El precio debe ser mayor a 0")
        
        product_updated = self.repository.update(product_id, product_update)
        if not product_updated:
            raise ValueError("Producto no encontrado")
        
        return product_updated
    
    def delete_product(self, product_id: int) -> bool:
        return self.repository.delete(product_id)