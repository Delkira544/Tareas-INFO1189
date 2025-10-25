"""
Security Headers Middleware (OWASP A06/A07)
Middleware para agregar headers de seguridad a todas las respuestas
"""
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
from infrastructure.security_config import security_config


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware para agregar headers de seguridad"""
    
    def __init__(self, app):
        super().__init__(app)
        self.security_headers = security_config.SECURITY_HEADERS
    
    async def dispatch(self, request: Request, call_next):
        """
        Agregar headers de seguridad a todas las respuestas
        
        Args:
            request: Request de FastAPI
            call_next: Siguiente middleware
            
        Returns:
            Response con headers de seguridad
        """
        # Procesar request
        response = await call_next(request)
        
        # Agregar headers de seguridad
        for header, value in self.security_headers.items():
            response.headers[header] = value
        
        # Remover headers que revelan información del servidor
        headers_to_remove = ["Server", "X-Powered-By", "X-AspNet-Version"]
        for header in headers_to_remove:
            if header in response.headers:
                del response.headers[header]
        
        # Header específico para JSON responses
        if response.headers.get("content-type", "").startswith("application/json"):
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        
        # Headers adicionales para endpoints de autenticación
        if "/auth/" in request.url.path:
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        
        return response