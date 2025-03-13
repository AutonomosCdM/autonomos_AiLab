"""
Paquete de plantillas de configuración para {{ project_name_title }}.

Este módulo gestiona diferentes plantillas de configuración.
"""

# Importar plantillas de configuración disponibles
from . import logging_config
from . import project_settings
from . import pytest_config
from . import ci_config

# Lista de plantillas de configuración disponibles
config_templates = {
    "logging_config": logging_config,
    "project_settings": project_settings,
    "pytest_config": pytest_config,
    "ci_config": ci_config
}

# Versión del paquete de plantillas de configuración
__version__ = "0.1.0"

# Exportar plantillas
__all__ = [
    'logging_config',
    'project_settings',
    'pytest_config',
    'ci_config'
]
