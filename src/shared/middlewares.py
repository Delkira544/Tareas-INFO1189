from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response

class ConditionalAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, protected_routes=None):
        super().__init__(app)
        self.valid_token = "secreto123"
        # Definir rutas protegidas con sus métodos HTTP
        self.protected_routes = protected_routes or [("/products", "POST")]
    
    async def dispatch(self, request: Request, call_next):
        # Verificar si la ruta y el método están protegidos
        for route, method in self.protected_routes:
            if request.url.path.startswith(route) and request.method == method:
                # Verificar el header Authorization
                auth_header = request.headers.get("Authorization")
                if not auth_header or not auth_header.startswith("Bearer "):
                    return Response(
                        content='{"detail": "Token Bearer requerido"}',
                        status_code=401,
                        headers={"Content-Type": "application/json"}
                    )
                
                # Validar el token
                token = auth_header.split(" ")[1]
                if token != self.valid_token:
                    return Response(
                        content='{"detail": "Token Bearer inválido"}',
                        status_code=401,
                        headers={"Content-Type": "application/json"}
                    )
        
        # Continuar con la solicitud si no está protegida
        return await call_next(request)