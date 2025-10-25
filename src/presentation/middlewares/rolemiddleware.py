"""
Role-Based Access Control Middleware
Implementa control de acceso basado en roles (OWASP A01)
"""
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException, status, Response
import json
import time
from typing import Dict, List, Optional
from infrastructure.auth_service import jwt_service
from infrastructure.security_config import security_config


class RoleBasedAuthMiddleware(BaseHTTPMiddleware):
    """Middleware para control de acceso basado en roles mejorado"""
    
    def __init__(self, app, admin_only_routes: Optional[List[tuple]] = None):
        super().__init__(app)
        self.admin_only_routes = admin_only_routes or security_config.ADMIN_ONLY_ROUTES
        
        # Rate limiting básico por IP
        self.rate_limit_data: Dict[str, List[float]] = {}
        self.rate_limit_requests = security_config.RATE_LIMIT_REQUESTS
        self.rate_limit_window = security_config.RATE_LIMIT_WINDOW
    
    def _check_rate_limit(self, client_ip: str) -> bool:
        """
        Verificar rate limiting por IP
        
        Args:
            client_ip: IP del cliente
            
        Returns:
            True si está dentro del límite
        """
        current_time = time.time()
        
        # Limpiar requests antiguos
        if client_ip in self.rate_limit_data:
            self.rate_limit_data[client_ip] = [
                req_time for req_time in self.rate_limit_data[client_ip]
                if current_time - req_time < self.rate_limit_window
            ]
        else:
            self.rate_limit_data[client_ip] = []
        
        # Verificar límite
        if len(self.rate_limit_data[client_ip]) >= self.rate_limit_requests:
            return False
        
        # Agregar request actual
        self.rate_limit_data[client_ip].append(current_time)
        return True
    
    def _is_protected_route(self, path: str, method: str) -> bool:
        """
        Verificar si la ruta está protegida
        
        Args:
            path: Ruta de la request
            method: Método HTTP
            
        Returns:
            True si la ruta está protegida
        """
        # Verificar rutas de admin
        for route_path, route_method in self.admin_only_routes:
            if route_path in path and route_method == method:
                return True
        
        # Verificar otras rutas protegidas (modificaciones)
        protected_operations = ["POST", "PUT", "PATCH", "DELETE"]
        if method in protected_operations:
            protected_paths = ["/products", "/categories", "/subcategories"]
            if any(protected_path in path for protected_path in protected_paths):
                return True
        
        return False
    
    def _extract_token_from_header(self, auth_header: Optional[str]) -> Optional[str]:
        """
        Extraer token del header Authorization
        
        Args:
            auth_header: Header de autorización
            
        Returns:
            Token extraído o None
        """
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header[7:].strip()
        if not token:
            return None
            
        return token
    
    async def dispatch(self, request: Request, call_next):
        """
        Procesar request con control de acceso y rate limiting
        
        Args:
            request: Request de FastAPI
            call_next: Siguiente middleware
            
        Returns:
            Response procesada
        """
        path = request.url.path
        method = request.method
        client_ip = request.client.host if request.client else "unknown"
        
        # Rate limiting
        if not self._check_rate_limit(client_ip):
            return Response(
                content=json.dumps({
                    "detail": "Demasiadas solicitudes",
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "retry_after": self.rate_limit_window
                }),
                status_code=429,
                headers={
                    "Content-Type": "application/json",
                    "Retry-After": str(self.rate_limit_window)
                }
            )
        
        # Verificar si la ruta requiere autenticación
        if self._is_protected_route(path, method):
            auth_header = request.headers.get("Authorization")
            token = self._extract_token_from_header(auth_header)
            
            if not token:
                return Response(
                    content=json.dumps({
                        "detail": "Token Bearer requerido para esta operación",
                        "error_code": "TOKEN_REQUIRED"
                    }),
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    headers={"Content-Type": "application/json"}
                )
            
            # Validar token
            payload = jwt_service.validate_token(token)
            
            if not payload:
                # Token inválido o expirado
                token_info = jwt_service.get_token_info(token)
                if token_info and token_info.get("expired"):
                    return Response(
                        content=json.dumps({
                            "detail": "Token expirado",
                            "error_code": "TOKEN_EXPIRED",
                            "message": "El token ha expirado, genera uno nuevo"
                        }),
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        headers={"Content-Type": "application/json"}
                    )
                else:
                    return Response(
                        content=json.dumps({
                            "detail": "Token inválido",
                            "error_code": "TOKEN_INVALID"
                        }),
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        headers={"Content-Type": "application/json"}
                    )
            
            # Verificar si requiere rol admin
            user_data = payload.get("data", {})
            user_role = user_data.get("role", "user")
            
            # Verificar rutas que requieren admin
            requires_admin = any(
                route_path in path and route_method == method
                for route_path, route_method in self.admin_only_routes
            )
            
            if requires_admin and user_role != "admin":
                return Response(
                    content=json.dumps({
                        "detail": "Acceso denegado: se requiere rol de administrador",
                        "error_code": "INSUFFICIENT_PRIVILEGES",
                        "required_role": "admin",
                        "current_role": user_role
                    }),
                    status_code=status.HTTP_403_FORBIDDEN,
                    headers={"Content-Type": "application/json"}
                )
            
            # Agregar información del usuario al request
            request.state.user = user_data
            request.state.token_payload = payload
        
        # Continuar con la solicitud
        return await call_next(request)