"""
Paquete de plantillas de configuración para {{ project_name_title }}.

Este módulo gestiona diferentes plantillas de configuración.
"""

# Importar plantillas de configuración disponibles
# Usar importaciones lazy para evitar importaciones circulares
config_templates = {}

# Versión del paquete de plantillas de configuración
__version__ = "0.1.0"

# Función para cargar módulos de configuración
def _load_config_modules():
    """
    Carga los módulos de configuración de manera diferida
    para evitar importaciones circulares
    """
    global config_templates
    try:
        from . import logging_config
        from . import project_settings
        from . import pytest_config
        from . import ci_config

        config_templates = {
            "logging_config": logging_config,
            "project_settings": project_settings,
            "pytest_config": pytest_config,
            "ci_config": ci_config
        }
    except ImportError as e:
        print(f"Error cargando módulos de configuración: {e}")

# Exportar plantillas
__all__ = [
    'logging_config',
    'project_settings',
    'pytest_config',
    'ci_config'
]

# Cargar módulos de configuración al importar
_load_config_modules()
