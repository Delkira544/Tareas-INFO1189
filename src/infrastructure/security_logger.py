"""
Security Logging System (OWASP A09)
Sistema de logging de eventos de seguridad
"""
import logging
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import Request
from infrastructure.security_config import security_config


class SecurityLogger:
    """Logger de eventos de seguridad"""
    
    def __init__(self, log_file: str = "security.log"):
        """
        Inicializar logger de seguridad
        
        Args:
            log_file: Archivo de logs
        """
        self.log_file = log_file
        self.sensitive_patterns = security_config.SENSITIVE_PATTERNS
        
        # Configurar logger
        self.logger = logging.getLogger("security")
        self.logger.setLevel(logging.INFO)
        
        # Evitar duplicar handlers
        if not self.logger.handlers:
            # Handler para archivo de logs de seguridad
            file_handler = logging.FileHandler(log_file)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
            
            # Handler para consola (solo errores críticos)
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.ERROR)
            console_formatter = logging.Formatter(
                '🚨 SECURITY: %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)
    
    def _sanitize_log_data(self, data: Any) -> Any:
        """
        Sanitizar datos sensibles para logging
        
        Args:
            data: Datos a sanitizar
            
        Returns:
            Datos sanitizados
        """
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                # Enmascarar datos sensibles
                if any(pattern in str(key).lower() for pattern in self.sensitive_patterns):
                    sanitized[key] = "***MASKED***"
                elif isinstance(value, (dict, list)):
                    sanitized[key] = self._sanitize_log_data(value)
                else:
                    sanitized[key] = value
            return sanitized
        
        elif isinstance(data, list):
            return [self._sanitize_log_data(item) for item in data]
        
        elif isinstance(data, str):
            # Enmascarar patrones sensibles en strings
            sanitized = data
            for pattern in self.sensitive_patterns:
                if pattern in data.lower():
                    sanitized = "***MASKED***"
                    break
            return sanitized
        
        return data
    
    def _create_log_entry(self, event_type: str, **kwargs) -> Dict[str, Any]:
        """
        Crear entrada de log estándar
        
        Args:
            event_type: Tipo de evento
            **kwargs: Datos adicionales
            
        Returns:
            Entrada de log estructurada
        """
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "application": "products-api",
            "version": "2.0.0",
            **self._sanitize_log_data(kwargs)
        }
    
    def log_auth_attempt(self, request: Request, success: bool, username: Optional[str] = None, 
                        error_reason: Optional[str] = None):
        """
        Log de intentos de autenticación
        
        Args:
            request: Request de FastAPI
            success: Si fue exitoso
            username: Usuario que intenta autenticarse
            error_reason: Razón del error si falló
        """
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        event = self._create_log_entry(
            event_type="authentication_attempt",
            success=success,
            username=username,
            ip_address=client_ip,
            user_agent=user_agent,
            endpoint=str(request.url.path),
            method=request.method,
            error_reason=error_reason
        )
        
        level = logging.INFO if success else logging.WARNING
        self.logger.log(level, json.dumps(event))
        
        # Log crítico para múltiples fallos
        if not success:
            self._check_multiple_failures(client_ip)
    
    def log_access_denied(self, request: Request, reason: str, user_role: Optional[str] = None):
        """
        Log de accesos denegados
        
        Args:
            request: Request de FastAPI
            reason: Razón del acceso denegado
            user_role: Rol del usuario si está disponible
        """
        client_ip = request.client.host if request.client else "unknown"
        
        event = self._create_log_entry(
            event_type="access_denied",
            reason=reason,
            user_role=user_role,
            path=request.url.path,
            method=request.method,
            ip_address=client_ip,
            query_params=dict(request.query_params)
        )
        
        self.logger.warning(json.dumps(event))
    
    def log_suspicious_activity(self, request: Request, activity_type: str, 
                              details: Optional[Dict] = None):
        """
        Log de actividad sospechosa
        
        Args:
            request: Request de FastAPI
            activity_type: Tipo de actividad sospechosa
            details: Detalles adicionales
        """
        client_ip = request.client.host if request.client else "unknown"
        
        event = self._create_log_entry(
            event_type="suspicious_activity",
            activity_type=activity_type,
            ip_address=client_ip,
            path=request.url.path,
            method=request.method,
            user_agent=request.headers.get("user-agent", "unknown"),
            details=details or {}
        )
        
        self.logger.error(json.dumps(event))
        
        # Alertar en consola para actividades críticas
        critical_activities = ["sql_injection", "xss_attempt", "path_traversal"]
        if activity_type in critical_activities:
            print(f"🚨 CRITICAL SECURITY ALERT: {activity_type} from {client_ip}")
    
    def log_rate_limit_exceeded(self, request: Request, limit_type: str = "general"):
        """
        Log de límite de rate excedido
        
        Args:
            request: Request de FastAPI
            limit_type: Tipo de límite excedido
        """
        client_ip = request.client.host if request.client else "unknown"
        
        event = self._create_log_entry(
            event_type="rate_limit_exceeded",
            limit_type=limit_type,
            ip_address=client_ip,
            path=request.url.path,
            method=request.method,
            user_agent=request.headers.get("user-agent", "unknown")
        )
        
        self.logger.warning(json.dumps(event))
    
    def log_input_validation_error(self, request: Request, field: str, 
                                  error_type: str, value: Any):
        """
        Log de errores de validación de entrada
        
        Args:
            request: Request de FastAPI
            field: Campo que falló la validación
            error_type: Tipo de error
            value: Valor que causó el error
        """
        client_ip = request.client.host if request.client else "unknown"
        
        event = self._create_log_entry(
            event_type="input_validation_error",
            field=field,
            error_type=error_type,
            invalid_value=str(value)[:100],  # Truncar valores largos
            ip_address=client_ip,
            path=request.url.path,
            method=request.method
        )
        
        self.logger.warning(json.dumps(event))
    
    def log_token_event(self, event_type: str, token_info: Dict, 
                       client_ip: Optional[str] = None):
        """
        Log de eventos relacionados con tokens
        
        Args:
            event_type: Tipo de evento (generated, validated, expired, etc.)
            token_info: Información del token
            client_ip: IP del cliente
        """
        event = self._create_log_entry(
            event_type=f"token_{event_type}",
            token_id=token_info.get("jti", "unknown"),
            user=token_info.get("data", {}).get("username", "unknown"),
            ip_address=client_ip or "unknown",
            expires_at=token_info.get("exp"),
            issued_at=token_info.get("iat")
        )
        
        level = logging.INFO if event_type in ["generated", "validated"] else logging.WARNING
        self.logger.log(level, json.dumps(event))
    
    def _check_multiple_failures(self, client_ip: str):
        """
        Verificar múltiples fallos desde la misma IP
        
        Args:
            client_ip: IP del cliente
        """
        # Esto es una implementación simple. En producción usar Redis o similar
        failure_count = self._count_recent_failures(client_ip)
        
        if failure_count >= 5:
            self.logger.error(json.dumps(self._create_log_entry(
                event_type="multiple_auth_failures",
                ip_address=client_ip,
                failure_count=failure_count,
                action="IP should be blocked temporarily"
            )))
    
    def _count_recent_failures(self, client_ip: str) -> int:
        """
        Contar fallos recientes desde una IP
        
        Args:
            client_ip: IP del cliente
            
        Returns:
            Número de fallos en la última hora
        """
        # Implementación simplificada - contar líneas en el log
        if not os.path.exists(self.log_file):
            return 0
        
        current_time = datetime.utcnow()
        count = 0
        
        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    if client_ip in line and "authentication_attempt" in line and '"success": false' in line:
                        count += 1
        except Exception:
            pass
        
        return count
    
    def get_security_summary(self) -> Dict[str, Any]:
        """
        Obtener resumen de eventos de seguridad
        
        Returns:
            Resumen de eventos de seguridad
        """
        summary = {
            "total_events": 0,
            "auth_attempts": 0,
            "failed_auths": 0,
            "access_denied": 0,
            "suspicious_activities": 0,
            "rate_limits": 0,
            "last_updated": datetime.utcnow().isoformat()
        }
        
        if not os.path.exists(self.log_file):
            return summary
        
        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    summary["total_events"] += 1
                    
                    if "authentication_attempt" in line:
                        summary["auth_attempts"] += 1
                        if '"success": false' in line:
                            summary["failed_auths"] += 1
                    
                    elif "access_denied" in line:
                        summary["access_denied"] += 1
                    
                    elif "suspicious_activity" in line:
                        summary["suspicious_activities"] += 1
                    
                    elif "rate_limit_exceeded" in line:
                        summary["rate_limits"] += 1
        
        except Exception:
            pass
        
        return summary


# Instancia global del logger de seguridad
security_logger = SecurityLogger()


def get_security_logger() -> SecurityLogger:
    """Obtener instancia del logger de seguridad"""
    return security_logger