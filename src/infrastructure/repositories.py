"""
Infrastructure Layer - Repository Implementations
Implementaciones concretas de repositorios usando SQLite con propiedades ACID
"""
from typing import List, Optional
import sqlite3
from contextlib import contextmanager

from domain.entities import Product, Category
from domain.interfaces import IProductRepository, ICategoryRepository, IUnitOfWork
from infrastructure.database import db_manager


# ============================================================================
# Unit of Work - Gestión de transacciones ACID
# ============================================================================

class SQLiteUnitOfWork(IUnitOfWork):
    """
    Unit of Work para gestionar transacciones ACID en SQLite
    
    Propiedades ACID implementadas:
    - Atomicity: Todo o nada con commit/rollback
    - Consistency: Foreign keys y constraints
    - Isolation: Nivel de aislamiento de SQLite
    - Durability: Los commits son permanentes
    """
    
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
# Product Repository - Implementación SQLite
# ============================================================================

class SQLiteProductRepository(IProductRepository):
    """
    Implementación concreta del repositorio de productos
    
    Implementa IProductRepository (SOLID: Dependency Inversion)
    Usa DatabaseManager global para conexiones
    """
    
    def __init__(self):
        """Inicializar repositorio usando DatabaseManager global"""
        self.uow = SQLiteUnitOfWork()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Obtener conexión desde el DatabaseManager"""
        return db_manager.get_connection()
    
    def create(self, product: Product) -> Product:
        """
        Crear producto (ACID: Atomicity + Durability)
        La operación es atómica y los cambios son permanentes
        """
        with self.uow.transaction() as conn:
            cursor = conn.execute("""
                INSERT INTO products (name, price, in_stock, currency, category_id)
                VALUES (?, ?, ?, ?, ?)
            """, (
                product.name,
                product.price,
                product.in_stock,
                product.currency,
                product.category_id
            ))
            
            product.id = cursor.lastrowid
        
        return self.get_by_id(product.id)
    
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """
        Obtener producto por ID
        Incluye información de categoría mediante JOIN
        """
        conn = self._get_connection()
        try:
            row = conn.execute("""
                SELECT 
                    p.id,
                    p.name,
                    p.price,
                    p.in_stock,
                    p.currency,
                    p.category_id,
                    c.name as category_name
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
                    category_id=row['category_id']
                )
            return None
        finally:
            conn.close()
    
    def get_all(self, category_id: Optional[int] = None) -> List[Product]:
        """
        Obtener todos los productos, opcionalmente filtrados por categoría
        
        Args:
            category_id: ID de categoría para filtrar (opcional)
        """
        conn = self._get_connection()
        try:
            if category_id is not None:
                query = """
                    SELECT 
                        p.id,
                        p.name,
                        p.price,
                        p.in_stock,
                        p.currency,
                        p.category_id,
                        c.name as category_name
                    FROM products p
                    LEFT JOIN categories c ON p.category_id = c.id
                    WHERE p.category_id = ?
                    ORDER BY p.name
                """
                rows = conn.execute(query, (category_id,)).fetchall()
            else:
                query = """
                    SELECT 
                        p.id,
                        p.name,
                        p.price,
                        p.in_stock,
                        p.currency,
                        p.category_id,
                        c.name as category_name
                    FROM products p
                    LEFT JOIN categories c ON p.category_id = c.id
                    ORDER BY p.name
                """
                rows = conn.execute(query).fetchall()
            
            return [
                Product(
                    id=row['id'],
                    name=row['name'],
                    price=row['price'],
                    in_stock=bool(row['in_stock']),
                    currency=row['currency'],
                    category_id=row['category_id']
                )
                for row in rows
            ]
        finally:
            conn.close()
    
    def get_by_category(self, category_id: int) -> List[Product]:
        """
        Obtener productos por categoría
        Método requerido por la interfaz IProductRepository
        """
        return self.get_all(category_id=category_id)
    
    def update(self, product: Product) -> Optional[Product]:
        """
        Actualizar producto (ACID: Atomicity + Consistency)
        La actualización es atómica y mantiene integridad referencial
        """
        with self.uow.transaction() as conn:
            conn.execute("""
                UPDATE products
                SET name = ?, price = ?, in_stock = ?, currency = ?, category_id = ?
                WHERE id = ?
            """, (
                product.name,
                product.price,
                product.in_stock,
                product.currency,
                product.category_id,
                product.id
            ))
        
        return self.get_by_id(product.id)
    
    def delete(self, product_id: int) -> bool:
        """
        Eliminar producto (ACID: Atomicity + Durability)
        La eliminación es permanente y atómica
        """
        with self.uow.transaction() as conn:
            cursor = conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
            return cursor.rowcount > 0


# ============================================================================
# Category Repository - Implementación SQLite
# ============================================================================

class SQLiteCategoryRepository(ICategoryRepository):
    """
    Implementación concreta del repositorio de categorías
    
    Implementa ICategoryRepository (SOLID: Dependency Inversion)
    """
    
    def __init__(self):
        """Inicializar repositorio usando DatabaseManager global"""
        self.uow = SQLiteUnitOfWork()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Obtener conexión desde el DatabaseManager"""
        return db_manager.get_connection()
    
    def create(self, category: Category) -> Category:
        """
        Crear categoría (ACID)
        Operación atómica con commit automático
        """
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
                SELECT id, name, description
                FROM categories
                WHERE id = ?
            """, (category_id,)).fetchone()
            
            if row:
                return Category(
                    id=row['id'],
                    name=row['name'],
                    description=row['description']
                )
            return None
        finally:
            conn.close()
    
    def get_all(self) -> List[Category]:
        """Obtener todas las categorías ordenadas por nombre"""
        conn = self._get_connection()
        try:
            rows = conn.execute("""
                SELECT id, name, description
                FROM categories
                ORDER BY name
            """).fetchall()
            
            return [
                Category(
                    id=row['id'],
                    name=row['name'],
                    description=row['description']
                )
                for row in rows
            ]
        finally:
            conn.close()
    
    def delete(self, category_id: int) -> bool:
        """
        Eliminar categoría (ACID)
        
        NOTA: Si hay productos asociados, SQLite devolverá error
        por la foreign key constraint (garantiza CONSISTENCY)
        """
        with self.uow.transaction() as conn:
            cursor = conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            return cursor.rowcount > 0
