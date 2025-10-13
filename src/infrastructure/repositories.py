"""
Infrastructure Layer - Repository Implementations
Implementaciones concretas de repositorios usando SQLite con propiedades ACID
"""
from typing import List, Optional
import sqlite3
from contextlib import contextmanager

from domain.entities import Product, Category, Subcategory
from domain.interfaces import IProductRepository, ICategoryRepository, ISubcategoryRepository, IUnitOfWork
from infrastructure.database import db_manager
from shared.datetime_utils import DateTimeConverter  # ← Import del shared


# ============================================================================
# Unit of Work - Gestión de transacciones ACID
# ============================================================================

class SQLiteUnitOfWork(IUnitOfWork):
    """Unit of Work para gestionar transacciones ACID en SQLite"""
    
    def __init__(self):
        self.connection = None
    
    def begin_transaction(self):
        """Iniciar una transacción"""
        if self.connection is None:
            self.connection = db_manager.get_connection()
            self.connection.execute("BEGIN TRANSACTION")
    
    def commit(self):
        """Confirmar cambios (DURABILITY)"""
        if self.connection:
            self.connection.commit()
            self.connection.close()
            self.connection = None
    
    def rollback(self):
        """Deshacer cambios (ATOMICITY)"""
        if self.connection:
            self.connection.rollback()
            self.connection.close()
            self.connection = None
    
    @contextmanager
    def transaction(self):
        """Context manager para manejo automático de transacciones"""
        self.begin_transaction()
        try:
            yield self.connection
            self.commit()
        except Exception as e:
            self.rollback()
            raise e


# ============================================================================
# Category Repository - Implementación SQLite
# ============================================================================

class SQLiteCategoryRepository(ICategoryRepository):
    """Implementación concreta del repositorio de categorías"""
    
    def __init__(self):
        self.uow = SQLiteUnitOfWork()
    
    def _get_connection(self) -> sqlite3.Connection:
        return db_manager.get_connection()
    
    def create(self, category: Category) -> Category:
        """Crear categoría (ACID)"""
        with self.uow.transaction() as conn:
            cursor = conn.execute("""
                INSERT INTO categories (name, description)
                VALUES (?, ?)
            """, (category.name, category.description))
            
            category.id = cursor.lastrowid
        
        return self.get_by_id(category.id)
    
    def get_by_id(self, category_id: int) -> Optional[Category]:
        """Obtener categoría por ID"""
        conn = self._get_connection()
        try:
            row = conn.execute("""
                SELECT id, name, description, created_at
                FROM categories
                WHERE id = ?
            """, (category_id,)).fetchone()
            
            if row:
                return Category(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'],
                    created_at=DateTimeConverter.from_sqlite_row(row)  # ← USO DEL SHARED
                )
            return None
        finally:
            conn.close()
    
    def get_all(self) -> List[Category]:
        """Obtener todas las categorías ordenadas por nombre"""
        conn = self._get_connection()
        try:
            rows = conn.execute("""
                SELECT id, name, description, created_at
                FROM categories
                ORDER BY name
            """).fetchall()
            
            return [
                Category(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'],
                    created_at=DateTimeConverter.from_sqlite_row(row)  # ← USO DEL SHARED
                )
                for row in rows
            ]
        finally:
            conn.close()
    
    def delete(self, category_id: int) -> bool:
        """Eliminar categoría (CASCADE eliminará subcategorías)"""
        with self.uow.transaction() as conn:
            cursor = conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            return cursor.rowcount > 0


# ============================================================================
# Subcategory Repository - Implementación SQLite
# ============================================================================

class SQLiteSubcategoryRepository(ISubcategoryRepository):
    """Implementación concreta del repositorio de subcategorías"""
    
    def __init__(self):
        self.uow = SQLiteUnitOfWork()
    
    def _get_connection(self) -> sqlite3.Connection:
        return db_manager.get_connection()
    
    def create(self, subcategory: Subcategory) -> Subcategory:
        """Crear subcategoría (ACID)"""
        with self.uow.transaction() as conn:
            cursor = conn.execute("""
                INSERT INTO subcategories (name, description, category_id)
                VALUES (?, ?, ?)
            """, (subcategory.name, subcategory.description, subcategory.category_id))
            
            subcategory.id = cursor.lastrowid
        
        return self.get_by_id(subcategory.id)
    
    def get_by_id(self, subcategory_id: int) -> Optional[Subcategory]:
        """Obtener subcategoría por ID con información de categoría"""
        conn = self._get_connection()
        try:
            row = conn.execute("""
                SELECT 
                    s.id, s.name, s.description, s.category_id, s.created_at,
                    c.name as category_name, c.description as category_description
                FROM subcategories s
                JOIN categories c ON s.category_id = c.id
                WHERE s.id = ?
            """, (subcategory_id,)).fetchone()
            
            if row:
                category = Category(
                    id=row['category_id'],
                    name=row['category_name'],
                    description=row['category_description']
                )
                
                return Subcategory(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'],
                    category_id=row['category_id'],
                    created_at=DateTimeConverter.from_sqlite_row(row),  # ← USO DEL SHARED
                    category=category
                )
            return None
        finally:
            conn.close()
    
    def get_all(self) -> List[Subcategory]:
        """Obtener todas las subcategorías con información de categoría"""
        conn = self._get_connection()
        try:
            rows = conn.execute("""
                SELECT 
                    s.id, s.name, s.description, s.category_id, s.created_at,
                    c.name as category_name, c.description as category_description
                FROM subcategories s
                JOIN categories c ON s.category_id = c.id
                ORDER BY c.name, s.name
            """).fetchall()
            
            return [
                Subcategory(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'],
                    category_id=row['category_id'],
                    created_at=DateTimeConverter.from_sqlite_row(row),  # ← USO DEL SHARED
                    category=Category(
                        id=row['category_id'],
                        name=row['category_name'],
                        description=row['category_description']
                    )
                )
                for row in rows
            ]
        finally:
            conn.close()
    
    def get_by_category(self, category_id: int) -> List[Subcategory]:
        """Obtener subcategorías por categoría"""
        conn = self._get_connection()
        try:
            rows = conn.execute("""
                SELECT 
                    s.id, s.name, s.description, s.category_id, s.created_at,
                    c.name as category_name, c.description as category_description
                FROM subcategories s
                JOIN categories c ON s.category_id = c.id
                WHERE s.category_id = ?
                ORDER BY s.name
            """, (category_id,)).fetchall()
            
            return [
                Subcategory(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'],
                    category_id=row['category_id'],
                    created_at=DateTimeConverter.from_sqlite_row(row),  # ← USO DEL SHARED
                    category=Category(
                        id=row['category_id'],
                        name=row['category_name'],
                        description=row['category_description']
                    )
                )
                for row in rows
            ]
        finally:
            conn.close()
    
    def delete(self, subcategory_id: int) -> bool:
        """Eliminar subcategoría (CASCADE eliminará productos)"""
        with self.uow.transaction() as conn:
            cursor = conn.execute("DELETE FROM subcategories WHERE id = ?", (subcategory_id,))
            return cursor.rowcount > 0


# ============================================================================
# Product Repository - Implementación SQLite
# ============================================================================

class SQLiteProductRepository(IProductRepository):
    """Implementación concreta del repositorio de productos con subcategorías"""
    
    def __init__(self):
        self.uow = SQLiteUnitOfWork()
    
    def _get_connection(self) -> sqlite3.Connection:
        return db_manager.get_connection()
    
    def create(self, product: Product) -> Product:
        """Crear producto (ACID: Atomicity + Durability)"""
        with self.uow.transaction() as conn:
            cursor = conn.execute("""
                INSERT INTO products (name, price, in_stock, currency, subcategory_id)
                VALUES (?, ?, ?, ?, ?)
            """, (
                product.name,
                product.price,
                product.in_stock,
                product.currency,
                product.subcategory_id
            ))
            
            product.id = cursor.lastrowid
        
        return self.get_by_id(product.id)
    
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Obtener producto por ID con subcategoría y categoría completa"""
        conn = self._get_connection()
        try:
            row = conn.execute("""
                SELECT 
                    p.id, p.name, p.price, p.in_stock, p.currency, p.subcategory_id, p.created_at,
                    s.name as subcategory_name, s.description as subcategory_description,
                    c.id as category_id, c.name as category_name, c.description as category_description
                FROM products p
                JOIN subcategories s ON p.subcategory_id = s.id
                JOIN categories c ON s.category_id = c.id
                WHERE p.id = ?
            """, (product_id,)).fetchone()
            
            if row:
                category = Category(
                    id=row['category_id'],
                    name=row['category_name'],
                    description=row['category_description']
                )
                
                subcategory = Subcategory(
                    id=row['subcategory_id'],
                    name=row['subcategory_name'],
                    description=row['subcategory_description'],
                    category_id=row['category_id'],
                    category=category
                )
                
                return Product(
                    id=row['id'],
                    name=row['name'],
                    price=row['price'],
                    in_stock=bool(row['in_stock']),
                    currency=row['currency'],
                    subcategory_id=row['subcategory_id'],
                    created_at=DateTimeConverter.from_sqlite_row(row),  # ← USO DEL SHARED
                    subcategory=subcategory
                )
            return None
        finally:
            conn.close()
    
    def get_all(self) -> List[Product]:
        """Obtener todos los productos con subcategoría y categoría"""
        conn = self._get_connection()
        try:
            rows = conn.execute("""
                SELECT 
                    p.id, p.name, p.price, p.in_stock, p.currency, p.subcategory_id, p.created_at,
                    s.name as subcategory_name, s.description as subcategory_description,
                    c.id as category_id, c.name as category_name, c.description as category_description
                FROM products p
                JOIN subcategories s ON p.subcategory_id = s.id
                JOIN categories c ON s.category_id = c.id
                ORDER BY p.name
            """).fetchall()
            
            return [
                Product(
                    id=row['id'],
                    name=row['name'],
                    price=row['price'],
                    in_stock=bool(row['in_stock']),
                    currency=row['currency'],
                    subcategory_id=row['subcategory_id'],
                    created_at=DateTimeConverter.from_sqlite_row(row),  # ← USO DEL SHARED
                    subcategory=Subcategory(
                        id=row['subcategory_id'],
                        name=row['subcategory_name'],
                        description=row['subcategory_description'],
                        category_id=row['category_id'],
                        category=Category(
                            id=row['category_id'],
                            name=row['category_name'],
                            description=row['category_description']
                        )
                    )
                )
                for row in rows
            ]
        finally:
            conn.close()
    
    def get_by_subcategory(self, subcategory_id: int) -> List[Product]:
        """Obtener productos por subcategoría"""
        conn = self._get_connection()
        try:
            rows = conn.execute("""
                SELECT 
                    p.id, p.name, p.price, p.in_stock, p.currency, p.subcategory_id, p.created_at,
                    s.name as subcategory_name, s.description as subcategory_description,
                    c.id as category_id, c.name as category_name, c.description as category_description
                FROM products p
                JOIN subcategories s ON p.subcategory_id = s.id
                JOIN categories c ON s.category_id = c.id
                WHERE p.subcategory_id = ?
                ORDER BY p.name
            """, (subcategory_id,)).fetchall()
            
            return [
                Product(
                    id=row['id'],
                    name=row['name'],
                    price=row['price'],
                    in_stock=bool(row['in_stock']),
                    currency=row['currency'],
                    subcategory_id=row['subcategory_id'],
                    created_at=DateTimeConverter.from_sqlite_row(row),  # ← USO DEL SHARED
                    subcategory=Subcategory(
                        id=row['subcategory_id'],
                        name=row['subcategory_name'],
                        description=row['subcategory_description'],
                        category_id=row['category_id'],
                        category=Category(
                            id=row['category_id'],
                            name=row['category_name'],
                            description=row['category_description']
                        )
                    )
                )
                for row in rows
            ]
        finally:
            conn.close()
    
    def get_by_category(self, category_id: int) -> List[Product]:
        """Obtener todos los productos de una categoría (todas sus subcategorías)"""
        conn = self._get_connection()
        try:
            rows = conn.execute("""
                SELECT 
                    p.id, p.name, p.price, p.in_stock, p.currency, p.subcategory_id, p.created_at,
                    s.name as subcategory_name, s.description as subcategory_description,
                    c.id as category_id, c.name as category_name, c.description as category_description
                FROM products p
                JOIN subcategories s ON p.subcategory_id = s.id
                JOIN categories c ON s.category_id = c.id
                WHERE c.id = ?
                ORDER BY p.name
            """, (category_id,)).fetchall()
            
            return [
                Product(
                    id=row['id'],
                    name=row['name'],
                    price=row['price'],
                    in_stock=bool(row['in_stock']),
                    currency=row['currency'],
                    subcategory_id=row['subcategory_id'],
                    created_at=DateTimeConverter.from_sqlite_row(row),  # ← USO DEL SHARED
                    subcategory=Subcategory(
                        id=row['subcategory_id'],
                        name=row['subcategory_name'],
                        description=row['subcategory_description'],
                        category_id=row['category_id'],
                        category=Category(
                            id=row['category_id'],
                            name=row['category_name'],
                            description=row['category_description']
                        )
                    )
                )
                for row in rows
            ]
        finally:
            conn.close()
    
    def update(self, product: Product) -> Optional[Product]:
        """Actualizar producto (ACID: Atomicity + Consistency)"""
        with self.uow.transaction() as conn:
            conn.execute("""
                UPDATE products
                SET name = ?, price = ?, in_stock = ?, currency = ?, subcategory_id = ?
                WHERE id = ?
            """, (
                product.name,
                product.price,
                product.in_stock,
                product.currency,
                product.subcategory_id,
                product.id
            ))
        
        return self.get_by_id(product.id)
    
    def delete(self, product_id: int) -> bool:
        """Eliminar producto (ACID: Atomicity + Durability)"""
        with self.uow.transaction() as conn:
            cursor = conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
            return cursor.rowcount > 0
