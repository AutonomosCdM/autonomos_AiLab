"""
Paquete de herramientas CLI para el bot de Slack.

Este módulo proporciona comandos de línea de comandos para generar, desplegar y gestionar el bot.
"""

# Importar módulos CLI
from . import generate
from . import deploy

# Lista de herramientas CLI disponibles
AVAILABLE_CLI_TOOLS = [
    "generate",
    "deploy"
]

# Versión del paquete CLI
__version__ = "0.1.0"

# Exportar funciones principales
__all__ = [
    # Módulos CLI
    'generate',
    'deploy'
]

# Información de uso
CLI_USAGE = """
Herramientas CLI para {{ project_name_title }}:

1. Generar proyecto:
   python -m slack_bot.cli.generate <nombre-proyecto>

2. Desplegar bot:
   python -m slack_bot.cli.deploy -i <nombre-instancia>
"""
