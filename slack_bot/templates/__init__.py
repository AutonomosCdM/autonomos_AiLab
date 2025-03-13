"""
Paquete de plantillas para el bot de Slack.

Este módulo gestiona plantillas de proyectos, configuraciones y otros recursos.
"""

# Importar módulos de plantillas
from . import bot_templates
from . import config_templates

# Lista de plantillas disponibles
AVAILABLE_TEMPLATES = {
    "bot_templates": list(bot_templates.bot_templates.__dict__.keys()),
    "config_templates": list(config_templates.config_templates.__dict__.keys())
}

# Versión del paquete de plantillas
__version__ = "0.1.0"

# Exportar funciones principales
__all__ = [
    # Módulos de plantillas
    'bot_templates',
    'config_templates'
]

# Información de uso
TEMPLATE_USAGE = """
Plantillas disponibles para {{ project_name_title }}:

1. Plantillas de Bot:
   {}

2. Plantillas de Configuración:
   {}
""".format(
    ", ".join(AVAILABLE_TEMPLATES["bot_templates"]),
    ", ".join(AVAILABLE_TEMPLATES["config_templates"])
)
