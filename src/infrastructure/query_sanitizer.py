"""
Query Sanitization - SQL Injection Prevention (OWASP A03)
Sanitizador de consultas para prevenir inyección SQL y XSS
"""
import re
import html
from typing import Any, Dict, List, Union
from infrastructure.security_config import security_config


class QuerySanitizer:
    """Sanitizador de consultas para prevenir inyección SQL y XSS"""
    
    def __init__(self):
        """Inicializar sanitizador"""
        # Patrones peligrosos de SQL injection
        self.SQL_INJECTION_PATTERNS = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE|UNION|SCRIPT)\b)",
            r"(--|#|/\*|\*/)",
            r"(\b(OR|AND)\s+[\w\d]+\s*=\s*[\w\d]+)",
            r"(;|\||&|\$)",
            r"(\b(INFORMATION_SCHEMA|SYS|MASTER)\b)",
            r"(\bCONCAT\s*\()",
            r"(\bCHAR\s*\()",
            r"(\bASCII\s*\()"
        ]
        
        # Patrones XSS
        self.XSS_PATTERNS = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"vbscript:",
            r"onload\s*=",
            r"onerror\s*=",
            r"onclick\s*=",
            r"onmouseover\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
            r"<form[^>]*>",
            r"<input[^>]*>"
        ]
        
        # Caracteres HTML peligrosos
        self.HTML_ESCAPE_MAP = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#x27;",
            "/": "&#x2F;"
        }
    
    def detect_sql_injection(self, value: str) -> bool:
        """
        Detectar patrones de SQL injection
        
        Args:
            value: Valor a verificar
            
        Returns:
            True si se detecta un patrón peligroso
        """
        if not isinstance(value, str):
            return False
        
        value_upper = value.upper()
        
        for pattern in self.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value_upper, re.IGNORECASE):
                return True
        
        return False
    
    def detect_xss(self, value: str) -> bool:
        """
        Detectar patrones XSS
        
        Args:
            value: Valor a verificar
            
        Returns:
            True si se detecta XSS
        """
        if not isinstance(value, str):
            return False
        
        for pattern in self.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        
        return False
    
    def sanitize_string(self, value: str) -> str:
        """
        Sanitizar string para prevenir inyecciones
        
        Args:
            value: String a sanitizar
            
        Returns:
            String sanitizado
        """
        if not isinstance(value, str):
            return str(value)
        
        # Detectar patrones peligrosos
        if self.detect_sql_injection(value):
            raise ValueError(f"Entrada no válida: contenido SQL potencialmente peligroso detectado")
        
        if self.detect_xss(value):
            raise ValueError(f"Entrada no válida: contenido XSS potencialmente peligroso detectado")
        
        # Escapar HTML
        sanitized = html.escape(value)
        
        # Escapar comillas para SQL
        sanitized = sanitized.replace("'", "''")
        
        # Validar longitud
        max_length = security_config.MAX_STRING_LENGTH
        if len(sanitized) > max_length:
            raise ValueError(f"Entrada muy larga: máximo {max_length} caracteres")
        
        return sanitized
    
    def sanitize_input(self, value: Any) -> Any:
        """
        Sanitizar entrada del usuario
        
        Args:
            value: Valor a sanitizar
            
        Returns:
            Valor sanitizado
        """
        if value is None:
            return None
        
        if isinstance(value, str):
            return self.sanitize_string(value)
        
        if isinstance(value, (int, float, bool)):
            return value
        
        if isinstance(value, dict):
            return {k: self.sanitize_input(v) for k, v in value.items()}
        
        if isinstance(value, list):
            return [self.sanitize_input(item) for item in value]
        
        # Para otros tipos, convertir a string y sanitizar
        return self.sanitize_string(str(value))
    
    def validate_numeric_id(self, id_value: Any) -> int:
        """
        Validar que el ID sea numérico válido
        
        Args:
            id_value: Valor del ID
            
        Returns:
            ID como entero
            
        Raises:
            ValueError: Si el ID no es válido
        """
        try:
            numeric_id = int(id_value)
            if numeric_id <= 0:
                raise ValueError("ID debe ser un número positivo")
            if numeric_id > 2147483647:  # Max INT
                raise ValueError("ID demasiado grande")
            return numeric_id
        except (ValueError, TypeError) as e:
            raise ValueError(f"ID debe ser un número entero válido: {str(e)}")
    
    def validate_price(self, price_value: Any) -> float:
        """
        Validar precio
        
        Args:
            price_value: Valor del precio
            
        Returns:
            Precio como float
        """
        try:
            price = float(price_value)
            if price < 0:
                raise ValueError("El precio no puede ser negativo")
            if price > 999999999.99:
                raise ValueError("Precio demasiado alto")
            return round(price, 2)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Precio debe ser un número válido: {str(e)}")
    
    def sanitize_json_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitizar payload JSON completo
        
        Args:
            payload: Payload a sanitizar
            
        Returns:
            Payload sanitizado
        """
        if not isinstance(payload, dict):
            raise ValueError("Payload debe ser un objeto JSON válido")
        
        sanitized = {}
        
        for key, value in payload.items():
            # Sanitizar clave
            clean_key = self.sanitize_string(str(key))
            
            # Sanitizar valor
            clean_value = self.sanitize_input(value)
            
            sanitized[clean_key] = clean_value
        
        return sanitized
    
    def validate_search_query(self, query: str) -> str:
        """
        Validar consulta de búsqueda
        
        Args:
            query: Consulta de búsqueda
            
        Returns:
            Consulta sanitizada
        """
        if not query or not isinstance(query, str):
            return ""
        
        # Remover caracteres especiales peligrosos pero permitir espacios y caracteres básicos
        clean_query = re.sub(r'[^\w\s\-áéíóúñüÁÉÍÓÚÑÜ]', '', query)
        
        # Limitar longitud
        if len(clean_query) > 100:
            clean_query = clean_query[:100]
        
        return clean_query.strip()
    
    def escape_like_query(self, query: str) -> str:
        """
        Escapar consulta LIKE para SQL
        
        Args:
            query: Consulta para LIKE
            
        Returns:
            Consulta escapada
        """
        if not query:
            return ""
        
        # Escapar caracteres especiales de LIKE
        escaped = query.replace("\\", "\\\\")
        escaped = escaped.replace("%", "\\%")
        escaped = escaped.replace("_", "\\_")
        
        return escaped


# Instancia global del sanitizador
query_sanitizer = QuerySanitizer()


def get_query_sanitizer() -> QuerySanitizer:
    """Obtener instancia del sanitizador"""
    return query_sanitizer