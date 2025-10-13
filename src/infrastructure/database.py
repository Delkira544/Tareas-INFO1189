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
    - Poblar datos iniciales (categorías y subcategorías)
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
            
            # Tabla de categorías principales
            conn.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de subcategorías
            conn.execute("""
                CREATE TABLE IF NOT EXISTS subcategories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    category_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
                    UNIQUE(name, category_id)
                )
            """)
            
            # Tabla de productos con subcategoría
            conn.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price REAL NOT NULL CHECK(price >= 0),
                    in_stock BOOLEAN NOT NULL DEFAULT 1,
                    currency TEXT NOT NULL DEFAULT 'CLP' CHECK(currency IN ('CLP', 'USD', 'EUR')),
                    subcategory_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (subcategory_id) REFERENCES subcategories(id) ON DELETE CASCADE
                )
            """)
            
            # Insertar categorías predefinidas si no existen
            categories = [
                ("Audio y Video", "Equipos de audio, video y streaming"),
                ("Hardware PC", "Componentes de computadora"),
                ("Almacenamiento", "Dispositivos de almacenamiento"),
                ("Periféricos", "Mouse, teclados y accesorios"),
                ("Monitores", "Pantallas y displays"),
                ("Redes", "Equipos de red y conectividad")
            ]
            
            cursor = conn.cursor()
            for name, description in categories:
                cursor.execute(
                    "INSERT OR IGNORE INTO categories (name, description) VALUES (?, ?)",
                    (name, description)
                )
            
            # Insertar subcategorías predefinidas
            subcategories = [
                # Audio y Video (ID: 1)
                ("Micrófonos", "Micrófonos para streaming y grabación", 1),
                ("Cámaras Web", "Webcams y cámaras de streaming", 1),
                ("Auriculares", "Audífonos y headsets", 1),
                
                # Hardware PC (ID: 2)
                ("Tarjetas de Video", "GPUs y tarjetas gráficas", 2),
                ("Procesadores", "CPUs Intel y AMD", 2),
                ("Memorias RAM", "Módulos de memoria RAM", 2),
                ("Placas Madres", "Motherboards y placas base", 2),
                ("Fuentes de Poder", "PSUs y fuentes de alimentación", 2),
                
                # Almacenamiento (ID: 3)
                ("SSD", "Discos sólidos SSD", 3),
                ("HDD", "Discos duros tradicionales", 3),
                ("Almacenamiento Externo", "USB, externos y portables", 3),
                
                # Periféricos (ID: 4)
                ("Teclados", "Teclados mecánicos y de membrana", 4),
                ("Mouse", "Ratones gaming y oficina", 4),
                ("Mousepads", "Alfombrillas para mouse", 4),
                
                # Monitores (ID: 5)
                ("Gaming", "Monitores para gaming", 5),
                ("Profesional", "Monitores para trabajo", 5),
                
                # Redes (ID: 6)
                ("Routers", "Routers y access points", 6),
                ("Switches", "Switches de red", 6)
            ]
            
            for name, description, category_id in subcategories:
                cursor.execute(
                    "INSERT OR IGNORE INTO subcategories (name, description, category_id) VALUES (?, ?, ?)",
                    (name, description, category_id)
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
