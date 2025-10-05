from typing import List, Optional
from config import db_manager
from .models import Product, ProductRequest, ProductUpdate, Category, CategoryRequest

class CategoryRepository:
    def get_all(self) -> List[Category]:
        with db_manager.get_connection() as conn:
            rows = conn.execute("SELECT * FROM categories ORDER BY name").fetchall()
            return [
                Category(
                    id=row['id'],
                    name=row['name'],
                    description=row['description']
                )
                for row in rows
            ]
    
    def get_by_id(self, category_id: int) -> Optional[Category]:
        with db_manager.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM categories WHERE id = ?", (category_id,)
            ).fetchone()
            
            if row:
                return Category(
                    id=row['id'],
                    name=row['name'],
                    description=row['description']
                )
            return None
    
    def create(self, category_request: CategoryRequest) -> Category:
        with db_manager.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO categories (name, description)
                VALUES (?, ?)
            """, (category_request.name, category_request.description))
            
            category_id = cursor.lastrowid
            conn.commit()
            
            return Category(
                id=category_id,
                name=category_request.name,
                description=category_request.description
            )
    
    def delete(self, category_id: int) -> bool:
        with db_manager.get_connection() as conn:
            cursor = conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            conn.commit()
            return cursor.rowcount > 0

class ProductRepository:
    def create(self, product_request: ProductRequest) -> Product:
        with db_manager.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO products (name, price, in_stock, currency, category_id)
                VALUES (?, ?, ?, ?, ?)
            """, (
                product_request.name,
                product_request.price,
                product_request.in_stock,
                product_request.currency,
                product_request.category_id
            ))
            
            product_id = cursor.lastrowid
            conn.commit()
            
            # Obtener nombre de categoría si existe
            category_name = None
            if product_request.category_id:
                cat_row = conn.execute(
                    "SELECT name FROM categories WHERE id = ?", 
                    (product_request.category_id,)
                ).fetchone()
                category_name = cat_row['name'] if cat_row else None
            
            return Product(
                id=product_id,
                name=product_request.name,
                price=product_request.price,
                in_stock=product_request.in_stock,
                currency=product_request.currency,
                category_id=product_request.category_id,
                category_name=category_name
            )
    
    def get_by_id(self, product_id: int) -> Optional[Product]:
        with db_manager.get_connection() as conn:
            row = conn.execute("""
                SELECT p.*, c.name as category_name 
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE p.id = ?
            """, (product_id,)).fetchone()
            
            if row:
                return Product(
                    id=row['id'],
                    name=row['name'],
                    price=row['price'],
                    in_stock=bool(row['in_stock']),
                    currency=row['currency'],
                    category_id=row['category_id'],
                    category_name=row['category_name']
                )
            return None
    
    def get_all(self) -> List[Product]:
        with db_manager.get_connection() as conn:
            rows = conn.execute("""
                SELECT p.*, c.name as category_name 
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                ORDER BY p.id
            """).fetchall()
            
            return [
                Product(
                    id=row['id'],
                    name=row['name'],
                    price=row['price'],
                    in_stock=bool(row['in_stock']),
                    currency=row['currency'],
                    category_id=row['category_id'],
                    category_name=row['category_name']
                )
                for row in rows
            ]
    
    def get_by_category(self, category_id: int) -> List[Product]:
        with db_manager.get_connection() as conn:
            rows = conn.execute("""
                SELECT p.*, c.name as category_name 
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE p.category_id = ?
                ORDER BY p.id
            """, (category_id,)).fetchall()
            
            return [
                Product(
                    id=row['id'],
                    name=row['name'],
                    price=row['price'],
                    in_stock=bool(row['in_stock']),
                    currency=row['currency'],
                    category_id=row['category_id'],
                    category_name=row['category_name']
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
        new_category_id = product_update.category_id if product_update.category_id is not None else current_product.category_id
        
        with db_manager.get_connection() as conn:
            conn.execute("""
                UPDATE products 
                SET name = ?, price = ?, in_stock = ?, currency = ?, category_id = ?
                WHERE id = ?
            """, (new_name, new_price, new_in_stock, new_currency, new_category_id, product_id))
            
            conn.commit()
            
            # Obtener nombre de categoría
            category_name = None
            if new_category_id:
                cat_row = conn.execute(
                    "SELECT name FROM categories WHERE id = ?", 
                    (new_category_id,)
                ).fetchone()
                category_name = cat_row['name'] if cat_row else None
            
            return Product(
                id=product_id,
                name=new_name,
                price=new_price,
                in_stock=new_in_stock,
                currency=new_currency,
                category_id=new_category_id,
                category_name=category_name
            )
    
    def delete(self, product_id: int) -> bool:
        with db_manager.get_connection() as conn:
            cursor = conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
            conn.commit()
            return cursor.rowcount > 0