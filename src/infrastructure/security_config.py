"""
Security Configuration - Secure Design Patterns (OWASP A04/A05)
Configuración centralizada de seguridad para la aplicación
"""
import os
from typing import Dict, List


class SecurityConfig:
    """Configuración de seguridad centralizada"""
    
    def __init__(self):
        """Inicializar configuración de seguridad"""
        # JWT Configuration
        self.JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change_this_in_production_2024!")
        self.JWT_EXPIRATION_HOURS: int = 1
        self.JWT_ALGORITHM: str = "HS256"
        
        # Rate Limiting
        self.RATE_LIMIT_REQUESTS: int = 100
        self.RATE_LIMIT_WINDOW: int = 60  # segundos
        
        # CORS Configuration
        self.ALLOWED_ORIGINS: List[str] = [
            "http://localhost:3000", 
            "http://localhost:8080",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8080"
        ]
        
        # Database Security
        self.DB_ENABLE_FOREIGN_KEYS: bool = True
        self.DB_ENABLE_WAL_MODE: bool = True
        
        # Security Headers
        self.SECURITY_HEADERS: Dict[str, str] = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
        
        # Input Validation
        self.MAX_STRING_LENGTH: int = 1000
        self.MAX_DESCRIPTION_LENGTH: int = 5000
        self.MAX_PAYLOAD_SIZE: int = 1048576  # 1MB
        
        # Admin Routes (requieren rol admin)
        self.ADMIN_ONLY_ROUTES: List[tuple] = [
            ("/categories", "DELETE"),
            ("/subcategories", "DELETE"),
            ("/products/bulk", "POST"),
            ("/products/bulk", "DELETE")
        ]
        
        # Sensitive Data Patterns (para logging)
        self.SENSITIVE_PATTERNS: List[str] = [
            "password",
            "token",
            "secret",
            "key",
            "auth"
        ]


# Instancia global de configuración
security_config = SecurityConfig()


def get_security_config() -> SecurityConfig:
    """Obtener instancia de configuración de seguridad"""
    return security_config