"""
JWT Authentication Service - Infrastructure Layer
Servicio JWT simple con expiración de 1 hora
"""
import json
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict


class JWTService:
    """
    Servicio JWT simple con expiración
    
    Implementa:
    - Generación de tokens con expiración de 1 hora
    - Validación de tokens con verificación de expiración
    - Información detallada del token para debugging
    """
    
    def __init__(self, secret_key: str = "secreto_productos_api_2024", expires_hours: int = 1):
        self.secret_key = secret_key
        self.expires_hours = expires_hours
    
    def generate_token(self, user_data: Dict = None) -> str:
        """
        Generar token JWT simple con expiración de 1 hora
        
        Args:
            user_data: Datos adicionales del usuario (opcional)
        
        Returns:
            Token JWT como string con prefijo 'jwt_'
        """
        if user_data is None:
            user_data = {"user": "admin", "role": "admin"}
        
        # Crear payload con expiración
        now = datetime.utcnow()
        expires_at = now + timedelta(hours=self.expires_hours)
        
        payload = {
            "data": user_data,
            "iat": now.timestamp(),  # issued at (emitido en)
            "exp": expires_at.timestamp(),  # expires (expira en)
            "secret": self.secret_key,
            "version": "2.0"
        }
        
        # Codificar payload en base64 (JWT simplificado)
        payload_json = json.dumps(payload, separators=(',', ':'))
        token = base64.b64encode(payload_json.encode()).decode()
        
        return f"jwt_{token}"
    
    def validate_token(self, token: str) -> Optional[Dict]:
        """
        Validar token JWT y verificar expiración
        
        Args:
            token: Token a validar
        
        Returns:
            Payload del token si es válido, None si no es válido o expiró
        """
        try:
            # Verificar formato
            if not token.startswith("jwt_"):
                return None
            
            # Decodificar token
            token_data = token[4:]  # Remover prefijo "jwt_"
            payload_json = base64.b64decode(token_data.encode()).decode()
            payload = json.loads(payload_json)
            
            # Verificar secret
            if payload.get("secret") != self.secret_key:
                return None
            
            # Verificar expiración
            now = datetime.utcnow().timestamp()
            exp = payload.get("exp", 0)
            
            if now > exp:
                return None  # Token expirado
            
            return payload
            
        except (json.JSONDecodeError, ValueError, KeyError, Exception):
            return None
    
    def is_token_expired(self, token: str) -> bool:
        """Verificar si un token está expirado"""
        payload = self.validate_token(token)
        return payload is None
    
    def get_token_info(self, token: str) -> Optional[Dict]:
        """
        Obtener información detallada del token (para debugging)
        
        Returns:
            Información del token incluyendo tiempo restante
        """
        try:
            if not token.startswith("jwt_"):
                return None
            
            token_data = token[4:]
            payload_json = base64.b64decode(token_data.encode()).decode()
            payload = json.loads(payload_json)
            
            now = datetime.utcnow().timestamp()
            exp = payload.get("exp", 0)
            iat = payload.get("iat", 0)
            
            time_remaining = max(0, exp - now)
            
            return {
                "valid": payload.get("secret") == self.secret_key,
                "expired": now > exp,
                "issued_at": datetime.fromtimestamp(iat).isoformat() if iat else None,
                "expires_at": datetime.fromtimestamp(exp).isoformat() if exp else None,
                "time_remaining_seconds": time_remaining,
                "time_remaining_minutes": round(time_remaining / 60, 2),
                "user_data": payload.get("data", {}),
                "version": payload.get("version", "1.0")
            }
        except:
            return None
    
    def refresh_token(self, token: str) -> Optional[str]:
        """
        Renovar token si está próximo a expirar (últimos 10 minutos)
        
        Args:
            token: Token actual
        
        Returns:
            Nuevo token si se puede renovar, None si no
        """
        token_info = self.get_token_info(token)
        
        if not token_info or token_info["expired"]:
            return None
        
        # Renovar si quedan menos de 10 minutos
        if token_info["time_remaining_minutes"] < 10:
            user_data = token_info["user_data"]
            return self.generate_token(user_data)
        
        return None


# Instancia global del servicio JWT
jwt_service = JWTService(
    secret_key="productos_api_jwt_secret_2024", 
    expires_hours=1
)