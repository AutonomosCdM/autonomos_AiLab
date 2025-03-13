"""
Paquete principal del bot de Slack.

Un bot de Slack inteligente impulsado por IA, diseñado para proporcionar 
asistencia contextual y conversacional.
"""

# Importar submódulos principales
from . import config
from . import connectors
from . import context
from . import personality
from . import schemas
from . import utils
from . import cli
from . import templates

# Información del paquete
__version__ = "0.1.0"
__author__ = "{{ project_name_title }} Team"
__email__ = "contacto@{{ project_name }}.com"
__license__ = "MIT"

# Componentes principales disponibles
COMPONENTS = {
    "config": config,
    "connectors": connectors,
    "context": context,
    "personality": personality,
    "schemas": schemas,
    "utils": utils,
    "cli": cli,
    "templates": templates
}

# Exportar submódulos principales
__all__ = [
    'config',
    'connectors',
    'context', 
    'personality',
    'schemas',
    'utils',
    'cli',
    'templates'
]

# Información de inicialización
def initialize():
    """
    Inicializa el paquete del bot de Slack.
    
    Realiza configuraciones y validaciones iniciales.
    """
    # Validar configuraciones críticas
    config.settings.validate_config()
    
    # Configurar logging
    utils.setup_logging()
    
    # Registrar información del paquete
    logger = utils.get_logger(__name__)
    logger.info(f"Inicializando Slack Bot v{__version__}")
    logger.info(f"Autor: {__author__}")

# Inicializar al importar
initialize()
