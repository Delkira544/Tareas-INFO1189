"""
Database Configuration - Infrastructure Layer
Gestión de conexiones y inicialización de la base de datos
"""
import sqlite3
import os
from typing import Optional


class DatabaseManager:
    """
    Gestiona la conexión y inicialización de SQLite
    
    Responsabilidades (Single Responsibility):
    - Crear directorios y archivos de BD
    - Inicializar esquema de tablas
    - Proveer conexiones a repositorios
    - Poblar datos iniciales (categorías)
    """
    
    def __init__(self, db_name: str = "products.db"):
        # Ruta relativa desde src/infrastructure/
        self.db_path = os.path.join(
            os.path.dirname(__file__), 
            "..", 
            "data", 
            db_name
        )
        self._create_directories()
        self._init_database()
    
    def _create_directories(self):
        """Crear directorio data si no existe"""
        data_dir = os.path.dirname(self.db_path)
        os.makedirs(data_dir, exist_ok=True)
    
    def _init_database(self):
        """
        Inicializar base de datos y crear tablas
        
        Implementa propiedades ACID:
        - Atomicity: Transacciones automáticas con context manager
        - Consistency: Foreign keys garantizan integridad referencial
        - Isolation: Modo de aislamiento por defecto de SQLite
        - Durability: Commits persistentes en disco
        """
        with sqlite3.connect(self.db_path) as conn:
            # Habilitar foreign keys (importante para ACID)
            conn.execute("PRAGMA foreign_keys = ON")
            
            # Tabla de categorías
            conn.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de productos con categoría
            conn.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    in_stock BOOLEAN NOT NULL DEFAULT 1,
                    currency TEXT NOT NULL DEFAULT 'USD',
                    category_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories(id)
                )
            """)
            
            # Insertar categorías predefinidas si no existen
            categories = [
                ("Micrófonos", "Micrófonos para streaming y grabación"),
                ("Tarjetas de Video", "GPUs y tarjetas gráficas"),
                ("Memorias RAM", "Módulos de memoria RAM"),
                ("Placas Madres", "Motherboards y placas base"),
                ("Discos Duros", "HDDs, SSDs y almacenamiento"),
                ("Fuentes de Poder", "PSUs y fuentes de alimentación")
            ]
            
            cursor = conn.cursor()
            for name, description in categories:
                cursor.execute(
                    "INSERT OR IGNORE INTO categories (name, description) VALUES (?, ?)",
                    (name, description)
                )
            
            conn.commit()
    
    def get_connection(self):
        """
        Obtener conexión a la base de datos
        
        Returns:
            sqlite3.Connection con row_factory configurado
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Para acceder por nombre de columna
        conn.execute("PRAGMA foreign_keys = ON")  # Habilitar foreign keys
        return conn


# Instancia global del DatabaseManager
db_manager = DatabaseManager()
