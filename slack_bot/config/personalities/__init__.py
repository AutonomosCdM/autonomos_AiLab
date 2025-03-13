"""
Paquete de personalidades para el bot de Slack.

Este módulo gestiona diferentes configuraciones de personalidad para el bot.
"""

# Importar personalidades disponibles
from . import default
from . import custom

# Lista de personalidades disponibles
AVAILABLE_PERSONALITIES = [
    "default",
    "custom"
]

# Versión del paquete de personalidades
__version__ = "0.1.0"
