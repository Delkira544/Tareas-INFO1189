"""
Security Service - Cryptographic implementations (OWASP A02)
Servicio de seguridad criptográfica para hashing y validaciones
"""
import hashlib
import secrets
import re
from typing import Dict, Any, Optional


class SecurityService:
    """Servicio de seguridad criptográfica"""
    
    def __init__(self):
        """Inicializar servicio de seguridad"""
        # Patrones para validación de entrada
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        self.username_pattern = re.compile(r'^[a-zA-Z0-9_]{3,20}$')
        
    def hash_password(self, password: str) -> str:
        """
        Hash seguro de contraseñas usando SHA-256 con salt
        
        Args:
            password: Contraseña en texto plano
            
        Returns:
            Hash seguro de la contraseña
        """
        # Generar salt aleatorio
        salt = secrets.token_hex(16)
        
        # Combinar contraseña con salt
        password_salt = f"{password}{salt}"
        
        # Hash SHA-256
        password_hash = hashlib.sha256(password_salt.encode('utf-8')).hexdigest()
        
        # Retornar hash con salt
        return f"{salt}${password_hash}"
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """
        Verificar contraseña contra hash
        
        Args:
            password: Contraseña en texto plano
            hashed: Hash almacenado
            
        Returns:
            True si la contraseña es correcta
        """
        try:
            # Separar salt y hash
            salt, stored_hash = hashed.split('$')
            
            # Recrear hash con la contraseña y salt
            password_salt = f"{password}{salt}"
            password_hash = hashlib.sha256(password_salt.encode('utf-8')).hexdigest()
            
            # Comparar hashes
            return password_hash == stored_hash
            
        except (ValueError, AttributeError):
            return False
    
    def generate_secure_token(self, length: int = 32) -> str:
        """
        Generar token criptográficamente seguro
        
        Args:
            length: Longitud del token
            
        Returns:
            Token seguro en formato URL-safe
        """
        return secrets.token_urlsafe(length)
    
    def hash_sensitive_data(self, data: str) -> str:
        """
        Hash SHA-256 para datos sensibles
        
        Args:
            data: Datos a hashear
            
        Returns:
            Hash SHA-256 hexadecimal
        """
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def validate_email(self, email: str) -> bool:
        """
        Validar formato de email
        
        Args:
            email: Email a validar
            
        Returns:
            True si el email es válido
        """
        if not email or len(email) > 254:
            return False
        return bool(self.email_pattern.match(email))
    
    def validate_username(self, username: str) -> bool:
        """
        Validar formato de username
        
        Args:
            username: Username a validar
            
        Returns:
            True si el username es válido
        """
        if not username:
            return False
        return bool(self.username_pattern.match(username))
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitizar nombre de archivo
        
        Args:
            filename: Nombre de archivo
            
        Returns:
            Nombre de archivo sanitizado
        """
        # Remover caracteres peligrosos
        sanitized = re.sub(r'[^\w\-_\.]', '', filename)
        
        # Limitar longitud
        if len(sanitized) > 255:
            name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
            sanitized = f"{name[:250]}.{ext}" if ext else sanitized[:255]
        
        return sanitized
    
    def mask_sensitive_data(self, data: str, pattern: str = "password") -> str:
        """
        Enmascarar datos sensibles para logging
        
        Args:
            data: Datos a enmascarar
            pattern: Patrón de datos sensibles
            
        Returns:
            Datos enmascarados
        """
        if pattern.lower() in data.lower():
            return "***MASKED***"
        return data
    
    def generate_csrf_token(self) -> str:
        """
        Generar token CSRF
        
        Returns:
            Token CSRF seguro
        """
        return self.generate_secure_token(16)
    
    def constant_time_compare(self, a: str, b: str) -> bool:
        """
        Comparación de strings en tiempo constante (previene timing attacks)
        
        Args:
            a: Primer string
            b: Segundo string
            
        Returns:
            True si los strings son iguales
        """
        if len(a) != len(b):
            return False
        
        result = 0
        for x, y in zip(a, b):
            result |= ord(x) ^ ord(y)
        
        return result == 0


# Instancia global del servicio de seguridad
security_service = SecurityService()


def get_security_service() -> SecurityService:
    """Obtener instancia del servicio de seguridad"""
    return security_service