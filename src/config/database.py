import sqlite3
import os
from typing import Optional

class DatabaseManager:
    def __init__(self, db_name: str = "products.db"):
        self.db_path = os.path.join("data", db_name)
        self._create_directories()
        self._init_database()
    
    def _create_directories(self):
        """Crear directorio data si no existe"""
        os.makedirs("data", exist_ok=True)
    
    def _init_database(self):
        """Inicializar base de datos y crear tablas"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    in_stock BOOLEAN NOT NULL DEFAULT 1,
                    currency TEXT NOT NULL DEFAULT 'USD',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def get_connection(self):
        """Obtener conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Para acceder por nombre de columna
        return conn

# Instancia global
db_manager = DatabaseManager()