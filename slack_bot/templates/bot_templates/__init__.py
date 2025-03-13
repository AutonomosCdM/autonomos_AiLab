"""
Paquete de plantillas de bot para {{ project_name_title }}.

Este módulo gestiona diferentes plantillas de proyectos de bot.
"""

# Importar plantillas de bot disponibles
from . import default

# Lista de plantillas de bot disponibles
bot_templates = {
    "default": default
}

# Versión del paquete de plantillas de bot
__version__ = "0.1.0"

# Exportar plantillas
__all__ = [
    'default'
]
