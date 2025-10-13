"""
Authentication Middleware - Clean Architecture
Middleware JWT para proteger rutas específicas con expiración de tokens
"""
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
import json

from infrastructure.auth_service import jwt_service


class ConditionalAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware de autenticación condicional con JWT y expiración
    
    Protege rutas específicas con JWT Bearer token.
    Implementa el principio de Single Responsibility (SOLID).
    """
    
    def __init__(self, app, protected_routes=None):
        super().__init__(app)
        # Definir rutas protegidas con sus métodos HTTP
        self.protected_routes = protected_routes or [
            ("/products", "POST"),
            ("/products", "PUT"),
            ("/products", "PATCH"),
            ("/products", "DELETE"),
            ("/categories", "POST"),
            ("/categories", "DELETE"),
            ("/subcategories", "POST"),
            ("/subcategories", "DELETE"),
        ]
    
    async def dispatch(self, request: Request, call_next):
        """
        Intercepta todas las peticiones y valida JWT en rutas protegidas
        """
        # Verificar si la ruta y el método están protegidos
        path = request.url.path
        method = request.method
        
        is_protected = False
        for route_path, route_method in self.protected_routes:
            if path.startswith(route_path) and method == route_method:
                is_protected = True
                break
        
        if is_protected:
            # Verificar el header Authorization
            auth_header = request.headers.get("Authorization")
            
            if not auth_header or not auth_header.startswith("Bearer "):
                return Response(
                    content=json.dumps({"detail": "Token Bearer requerido"}),
                    status_code=401,
                    headers={"Content-Type": "application/json"}
                )
            
            # Validar el token con expiración
            token = auth_header.split(" ")[1]
            payload = jwt_service.validate_token(token)
            
            if payload is None:
                # Token inválido o expirado
                token_info = jwt_service.get_token_info(token)
                if token_info and token_info.get("expired"):
                    return Response(
                        content=json.dumps({
                            "detail": "Token expirado",
                            "error_code": "TOKEN_EXPIRED",
                            "message": "El token ha expirado, genera uno nuevo"
                        }),
                        status_code=401,
                        headers={"Content-Type": "application/json"}
                    )
                else:
                    return Response(
                        content=json.dumps({
                            "detail": "Token inválido",
                            "error_code": "TOKEN_INVALID"
                        }),
                        status_code=401,
                        headers={"Content-Type": "application/json"}
                    )
            
            # Agregar información del usuario al request
            request.state.user = payload.get("data", {})
        
        # Continuar con la solicitud si no está protegida o si pasó la validación
        return await call_next(request)
