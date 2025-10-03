from typing import List, Optional
from config import db_manager
from .models import Product, ProductRequest, ProductUpdate

class ProductRepository:
    def create(self, product_request: ProductRequest) -> Product:
        with db_manager.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO products (name, price, in_stock, currency)
                VALUES (?, ?, ?, ?)
            """, (
                product_request.name,
                product_request.price,
                product_request.in_stock,
                product_request.currency
            ))
            
            product_id = cursor.lastrowid
            conn.commit()
            
            return Product(
                id=product_id,
                name=product_request.name,
                price=product_request.price,
                in_stock=product_request.in_stock,
                currency=product_request.currency
            )
    
    def get_by_id(self, product_id: int) -> Optional[Product]:
        with db_manager.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM products WHERE id = ?", (product_id,)
            ).fetchone()
            
            if row:
                return Product(
                    id=row['id'],
                    name=row['name'],
                    price=row['price'],
                    in_stock=bool(row['in_stock']),
                    currency=row['currency']
                )
            return None
    
    def get_all(self) -> List[Product]:
        with db_manager.get_connection() as conn:
            rows = conn.execute("SELECT * FROM products ORDER BY id").fetchall()
            
            return [
                Product(
                    id=row['id'],
                    name=row['name'],
                    price=row['price'],
                    in_stock=bool(row['in_stock']),
                    currency=row['currency']
                )
                for row in rows
            ]
    
    def update(self, product_id: int, product_update: ProductUpdate) -> Optional[Product]:
        # Primero obtener el producto actual
        current_product = self.get_by_id(product_id)
        if not current_product:
            return None
        
        # Usar valores actuales si no se proporciona actualización
        new_name = product_update.name or current_product.name
        new_price = product_update.price or current_product.price
        new_in_stock = product_update.in_stock if product_update.in_stock is not None else current_product.in_stock
        new_currency = product_update.currency or current_product.currency
        
        with db_manager.get_connection() as conn:
            conn.execute("""
                UPDATE products 
                SET name = ?, price = ?, in_stock = ?, currency = ?
                WHERE id = ?
            """, (new_name, new_price, new_in_stock, new_currency, product_id))
            
            conn.commit()
            
            return Product(
                id=product_id,
                name=new_name,
                price=new_price,
                in_stock=new_in_stock,
                currency=new_currency
            )
    
    def delete(self, product_id: int) -> bool:
        with db_manager.get_connection() as conn:
            cursor = conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
            conn.commit()
            return cursor.rowcount > 0