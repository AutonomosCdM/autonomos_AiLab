"""
Paquete de utilidades para el bot de Slack.

Este módulo proporciona herramientas de soporte, logging y manejo de errores.
"""

# Importar módulos de utilidades
from .logging import (
    setup_logging, 
    LoggerAdapter, 
    get_logger
)
from .error_handling import (
    BotError,
    ConnectionError,
    APIError,
    ConfigurationError,
    ValidationError,
    handle_exceptions,
    safe_execute,
    ErrorRegistry,
    error_registry
)

# Lista de utilidades disponibles
AVAILABLE_UTILITIES = [
    "logging",
    "error_handling"
]

# Versión del paquete de utilidades
__version__ = "0.1.0"

# Exportar funciones y clases principales
__all__ = [
    # Funciones de logging
    'setup_logging',
    'LoggerAdapter',
    'get_logger',
    
    # Clases de manejo de errores
    'BotError',
    'ConnectionError',
    'APIError',
    'ConfigurationError',
    'ValidationError',
    'ErrorRegistry',
    
    # Decoradores y funciones de manejo de errores
    'handle_exceptions',
    'safe_execute',
    
    # Instancias globales
    'error_registry'
]
