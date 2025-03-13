"""
Configuración de logging para el bot de Slack.
"""
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional

from slack_bot.config import settings


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    log_format: Optional[str] = None
) -> logging.Logger:
    """
    Configura el sistema de logging.
    
    Args:
        log_level (Optional[str]): Nivel de logging. Si es None, se usa el configurado en settings.
        log_file (Optional[str]): Ruta del archivo de log. Si es None, solo se usa stdout.
        log_format (Optional[str]): Formato de los mensajes de log. Si es None, se usa el configurado en settings.
        
    Returns:
        logging.Logger: Logger configurado.
    """
    # Obtener configuración
    level = log_level or settings.LOG_LEVEL
    format_str = log_format or settings.LOG_FORMAT
    
    # Convertir nivel de string a constante de logging
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Nivel de log inválido: {level}")
    
    # Configurar logger raíz
    logger = logging.getLogger()
    logger.setLevel(numeric_level)
    
    # Eliminar handlers existentes
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Crear formatter
    formatter = logging.Formatter(format_str)
    
    # Configurar handler para stdout
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Configurar handler para archivo si se especificó
    if log_file:
        # Crear directorio si no existe
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Configurar rotating file handler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Configurar loggers específicos
    configure_specific_loggers(numeric_level)
    
    logger.debug("Sistema de logging configurado")
    return logger


def configure_specific_loggers(level: int) -> None:
    """
    Configura loggers específicos para bibliotecas externas.
    
    Args:
        level (int): Nivel de logging.
    """
    # Configurar loggers de bibliotecas externas para reducir verbosidad
    logging.getLogger('slack_bolt').setLevel(max(level, logging.INFO))
    logging.getLogger('slack_sdk').setLevel(max(level, logging.INFO))
    logging.getLogger('urllib3').setLevel(max(level, logging.WARNING))
    logging.getLogger('requests').setLevel(max(level, logging.WARNING))


class LoggerAdapter(logging.LoggerAdapter):
    """
    Adaptador de logger que añade contexto a los mensajes.
    """
    
    def __init__(self, logger, extra=None):
        """
        Inicializa el adaptador.
        
        Args:
            logger: Logger base.
            extra: Información extra para añadir a los mensajes.
        """
        super().__init__(logger, extra or {})
    
    def process(self, msg, kwargs):
        """
        Procesa el mensaje añadiendo contexto.
        
        Args:
            msg: Mensaje original.
            kwargs: Argumentos adicionales.
            
        Returns:
            Tupla (mensaje procesado, kwargs).
        """
        # Añadir contexto al mensaje
        context_str = ' '.join(f'{k}={v}' for k, v in self.extra.items())
        if context_str:
            msg = f"{msg} [{context_str}]"
        
        return msg, kwargs


def get_logger(name: str, **extra) -> logging.LoggerAdapter:
    """
    Obtiene un logger con contexto.
    
    Args:
        name (str): Nombre del logger.
        **extra: Información extra para añadir a los mensajes.
        
    Returns:
        logging.LoggerAdapter: Logger con contexto.
    """
    logger = logging.getLogger(name)
    return LoggerAdapter(logger, extra)
