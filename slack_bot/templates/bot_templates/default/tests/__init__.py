"""
Paquete de pruebas para {{ project_name_title }}.

Este módulo contiene pruebas unitarias y de integración para el bot de Slack.
"""

# Importaciones necesarias para configuración de pruebas
import os
import sys

# Añadir directorio raíz al path para importar módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Configuraciones globales para pruebas
TEST_CONFIG = {
    "project_name": "{{ project_name }}",
    "test_environment": "development"
}
