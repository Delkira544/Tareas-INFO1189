"""
Authentication Routes - JWT Token Management
Endpoints para generar y gestionar tokens JWT
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional

from infrastructure.auth_service import jwt_service

router = APIRouter(prefix="/auth", tags=["authentication"])


# ============================================================================
# DTOs para autenticación
# ============================================================================

class TokenRequest(BaseModel):
    """DTO para solicitar token"""
    username: str = "admin"
    password: str = "admin123"


class TokenResponse(BaseModel):
    """DTO para respuesta de token"""
    access_token: str
    token_type: str = "Bearer"
    expires_in_hours: int
    expires_at: str


class TokenInfoResponse(BaseModel):
    """DTO para información del token"""
    valid: bool
    expired: bool
    issued_at: Optional[str]
    expires_at: Optional[str]
    time_remaining_seconds: float
    user_data: dict


# ============================================================================
# Endpoints de autenticación
# ============================================================================

@router.post("/token", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def generate_token(credentials: TokenRequest):
    """
    Generar token JWT con expiración de 1 hora
    
    Credenciales por defecto:
    - username: admin
    - password: admin123
    """
    # Validación simple de credenciales (en producción usar hash)
    if credentials.username != "admin" or credentials.password != "admin123":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    
    # Generar token
    user_data = {
        "username": credentials.username,
        "role": "admin"
    }
    
    token = jwt_service.generate_token(user_data)
    token_info = jwt_service.get_token_info(token)
    
    return TokenResponse(
        access_token=token,
        token_type="Bearer",
        expires_in_hours=1,
        expires_at=token_info["expires_at"] if token_info else ""
    )


@router.get("/token/info", response_model=TokenInfoResponse)
async def get_token_info(token: str):
    """
    Obtener información de un token
    
    Query parameter:
    - token: Token JWT a verificar
    """
    token_info = jwt_service.get_token_info(token)
    
    if not token_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido o malformado"
        )
    
    return TokenInfoResponse(**token_info)


@router.post("/token/validate")
async def validate_token(token: str):
    """
    Validar si un token es válido y no ha expirado
    
    Query parameter:
    - token: Token JWT a validar
    """
    payload = jwt_service.validate_token(token)
    
    if payload is None:
        token_info = jwt_service.get_token_info(token)
        if token_info and token_info.get("expired"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
    
    return {
        "message": "Token válido",
        "user_data": payload.get("data", {}),
        "expires_at": jwt_service.get_token_info(token)["expires_at"]
    }