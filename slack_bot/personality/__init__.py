"""
Paquete de gestión de personalidad para el bot de Slack.

Este módulo gestiona la personalización del comportamiento del bot.
"""

# Importar clases de gestión de personalidad
from .manager import PersonalityManager
from .formatters import (
    ResponseFormatter, 
    DefaultFormatter, 
    MarkdownFormatter, 
    FormatterFactory
)
from .templates import (
    PromptTemplate, 
    TemplateManager, 
    template_manager
)

# Lista de componentes de personalidad disponibles
AVAILABLE_PERSONALITY_COMPONENTS = [
    "personality_manager",
    "response_formatters",
    "template_manager"
]

# Versión del paquete de personalidad
__version__ = "0.1.0"

# Exportar clases principales
__all__ = [
    'PersonalityManager',
    'ResponseFormatter',
    'DefaultFormatter',
    'MarkdownFormatter',
    'FormatterFactory',
    'PromptTemplate',
    'TemplateManager',
    'template_manager'
]
