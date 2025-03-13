"""
Utilidades para manejo de errores.
"""
import functools
import logging
import sys
import traceback
from typing import Callable, Any, Optional, Type, Dict, List, Union

logger = logging.getLogger(__name__)


class BotError(Exception):
    """
    Excepción base para errores del bot.
    """
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        """
        Inicializa la excepción.
        
        Args:
            message (str): Mensaje de error.
            original_error (Optional[Exception]): Excepción original que causó el error.
        """
        super().__init__(message)
        self.original_error = original_error
        self.traceback = traceback.format_exc() if original_error else None


class ConnectionError(BotError):
    """
    Error de conexión con servicios externos.
    """
    pass


class APIError(BotError):
    """
    Error en llamadas a APIs externas.
    """
    pass


class ConfigurationError(BotError):
    """
    Error de configuración.
    """
    pass


class ValidationError(BotError):
    """
    Error de validación de datos.
    """
    pass


def handle_exceptions(
    error_types: Optional[Union[Type[Exception], List[Type[Exception]]]] = None,
    default_message: str = "Se produjo un error inesperado",
    log_level: int = logging.ERROR,
    reraise: bool = False
) -> Callable:
    """
    Decorador para manejar excepciones en funciones.
    
    Args:
        error_types (Optional[Union[Type[Exception], List[Type[Exception]]]]): Tipos de excepciones a manejar.
            Si es None, maneja todas las excepciones.
        default_message (str): Mensaje por defecto para errores no especificados.
        log_level (int): Nivel de logging para los errores.
        reraise (bool): Si se debe relanzar la excepción después de manejarla.
        
    Returns:
        Callable: Decorador configurado.
    """
    if error_types and not isinstance(error_types, list):
        error_types = [error_types]
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Verificar si el tipo de excepción debe ser manejado
                if error_types and not any(isinstance(e, t) for t in error_types):
                    raise
                
                # Obtener información de la excepción
                exc_type, exc_value, exc_traceback = sys.exc_info()
                tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
                
                # Determinar mensaje de error
                error_message = str(e) or default_message
                
                # Loggear el error
                log_message = f"Error en {func.__name__}: {error_message}\n{tb_str}"
                logger.log(log_level, log_message)
                
                # Relanzar la excepción si es necesario
                if reraise:
                    raise
                
                # Devolver None si no se relanza
                return None
        
        return wrapper
    
    return decorator


def safe_execute(
    func: Callable,
    *args,
    error_handler: Optional[Callable[[Exception], Any]] = None,
    default_return: Any = None,
    **kwargs
) -> Any:
    """
    Ejecuta una función de forma segura, manejando excepciones.
    
    Args:
        func (Callable): Función a ejecutar.
        *args: Argumentos posicionales para la función.
        error_handler (Optional[Callable[[Exception], Any]]): Función para manejar errores.
            Si es None, se loggea el error y se devuelve default_return.
        default_return (Any): Valor a devolver en caso de error si no hay error_handler.
        **kwargs: Argumentos de palabra clave para la función.
        
    Returns:
        Any: Resultado de la función o valor por defecto en caso de error.
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        # Obtener información de la excepción
        exc_type, exc_value, exc_traceback = sys.exc_info()
        tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        
        # Loggear el error
        logger.error(f"Error en {func.__name__}: {str(e)}\n{tb_str}")
        
        # Manejar el error si hay un manejador
        if error_handler:
            return error_handler(e)
        
        # Devolver valor por defecto
        return default_return


class ErrorRegistry:
    """
    Registro de errores para seguimiento y análisis.
    """
    
    def __init__(self, max_errors: int = 100):
        """
        Inicializa el registro de errores.
        
        Args:
            max_errors (int): Número máximo de errores a mantener en el registro.
        """
        self.max_errors = max_errors
        self.errors = []
        logger.debug(f"ErrorRegistry inicializado con max_errors={max_errors}")
    
    def register(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Registra un error.
        
        Args:
            error (Exception): Excepción a registrar.
            context (Optional[Dict[str, Any]]): Contexto adicional del error.
        """
        # Crear entrada de error
        error_entry = {
            "type": type(error).__name__,
            "message": str(error),
            "traceback": traceback.format_exc(),
            "timestamp": traceback.time.time(),
            "context": context or {}
        }
        
        # Añadir al registro
        self.errors.append(error_entry)
        
        # Limitar tamaño del registro
        if len(self.errors) > self.max_errors:
            self.errors.pop(0)
        
        logger.debug(f"Error registrado: {error_entry['type']}: {error_entry['message']}")
    
    def get_errors(self, error_type: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Obtiene errores del registro.
        
        Args:
            error_type (Optional[str]): Tipo de error a filtrar.
            limit (Optional[int]): Número máximo de errores a devolver.
            
        Returns:
            List[Dict[str, Any]]: Lista de errores.
        """
        # Filtrar por tipo si es necesario
        filtered_errors = self.errors
        if error_type:
            filtered_errors = [e for e in self.errors if e["type"] == error_type]
        
        # Limitar cantidad si es necesario
        if limit is not None:
            filtered_errors = filtered_errors[-limit:]
        
        return filtered_errors
    
    def clear(self) -> None:
        """
        Limpia el registro de errores.
        """
        self.errors = []
        logger.debug("Registro de errores limpiado")
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Obtiene un resumen de los errores registrados.
        
        Returns:
            Dict[str, Any]: Resumen de errores.
        """
        # Contar errores por tipo
        error_counts = {}
        for error in self.errors:
            error_type = error["type"]
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
        
        return {
            "total_errors": len(self.errors),
            "error_types": error_counts,
            "latest_error": self.errors[-1] if self.errors else None
        }


# Instancia global del registro de errores
error_registry = ErrorRegistry()
