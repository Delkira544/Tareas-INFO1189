"""
Shared Utilities - Date/Time Helpers
Utilidades compartidas para manejo de fechas y timestamps
"""
from datetime import datetime
from typing import Optional, Union
import sqlite3


def parse_sqlite_datetime(date_string: Optional[str]) -> Optional[datetime]:
    """
    Convierte string de fecha de SQLite a objeto datetime
    
    Args:
        date_string: String de fecha en formato SQLite o None
        
    Returns:
        Objeto datetime o None si la entrada es None/vacía
        
    Ejemplos:
        >>> parse_sqlite_datetime("2024-01-15 10:30:00")
        datetime(2024, 1, 15, 10, 30)
        >>> parse_sqlite_datetime(None)
        None
    """
    if not date_string:
        return None
    
    try:
        # SQLite devuelve fechas en formato: "YYYY-MM-DD HH:MM:SS"
        return datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            # Formato alternativo sin tiempo: "YYYY-MM-DD"
            return datetime.strptime(date_string, "%Y-%m-%d")
        except ValueError:
            try:
                # Formato ISO con T: "YYYY-MM-DDTHH:MM:SS"
                return datetime.fromisoformat(date_string.replace('T', ' '))
            except ValueError:
                # Si no se puede parsear, retornar None
                return None


def format_datetime_for_response(dt: Optional[Union[datetime, str]]) -> Optional[str]:
    """
    Convierte datetime a string ISO para respuestas API
    
    Args:
        dt: Objeto datetime, string, o None
        
    Returns:
        String en formato ISO o None
        
    Ejemplos:
        >>> format_datetime_for_response(datetime(2024, 1, 15, 10, 30))
        "2024-01-15T10:30:00"
        >>> format_datetime_for_response("2024-01-15 10:30:00")
        "2024-01-15T10:30:00"
        >>> format_datetime_for_response(None)
        None
    """
    if dt is None:
        return None
    
    # Si ya es string, intentar parsearlo primero
    if isinstance(dt, str):
        parsed_dt = parse_sqlite_datetime(dt)
        return parsed_dt.isoformat() if parsed_dt else dt
    
    # Si es datetime, convertir directamente
    if isinstance(dt, datetime):
        return dt.isoformat()
    
    # Cualquier otro tipo, retornar None
    return None


def safe_datetime_to_iso(dt: Optional[Union[datetime, str]]) -> Optional[str]:
    """
    Función segura para convertir datetime a ISO string
    Maneja tanto objetos datetime como strings de SQLite
    
    Args:
        dt: datetime, string, o None
        
    Returns:
        String ISO o None (nunca falla)
    """
    try:
        return format_datetime_for_response(dt)
    except Exception:
        # En caso de cualquier error, retornar None
        return None


class DateTimeConverter:
    """
    Clase helper para conversiones de fecha/hora en repositorios
    """
    
    @staticmethod
    def from_sqlite_row(row: sqlite3.Row, field_name: str = 'created_at') -> Optional[datetime]:
        """
        Extrae y convierte campo datetime de una fila SQLite
        
        Args:
            row: Fila de SQLite
            field_name: Nombre del campo de fecha (default: 'created_at')
            
        Returns:
            Objeto datetime o None
        """
        try:
            date_value = row[field_name] if field_name in row.keys() else None
            return parse_sqlite_datetime(date_value)
        except (KeyError, TypeError):
            return None
    
    @staticmethod
    def to_response_format(dt: Optional[Union[datetime, str]]) -> Optional[str]:
        """
        Convierte datetime para respuesta de API (alias de safe_datetime_to_iso)
        """
        return safe_datetime_to_iso(dt)


# Alias para facilidad de uso
datetime_to_iso = safe_datetime_to_iso
parse_db_datetime = parse_sqlite_datetime