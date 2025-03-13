"""
Configuraciones globales para {{ project_name_title }}.
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuraciones de Slack
SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN', '')
SLACK_APP_TOKEN = os.getenv('SLACK_APP_TOKEN', '')
SLACK_CHANNEL = os.getenv('SLACK_CHANNEL', '')

# Configuraciones de Groq
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama3-70b-8192')
GROQ_MAX_TOKENS = int(os.getenv('GROQ_MAX_TOKENS', 500))

# Configuraciones de logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'slack_bot.log')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Configuraciones de personalidad
DEFAULT_PERSONALITY = os.getenv('DEFAULT_PERSONALITY', 'default')

# Configuraciones de contexto
MAX_CONTEXT_MESSAGES = int(os.getenv('MAX_CONTEXT_MESSAGES', 10))
CONTEXT_EXPIRY_MINUTES = int(os.getenv('CONTEXT_EXPIRY_MINUTES', 60))

# Configuraciones de seguridad
TOKEN_VALIDATION = os.getenv('TOKEN_VALIDATION', 'true').lower() == 'true'
RATE_LIMITING_ENABLED = os.getenv('RATE_LIMITING_ENABLED', 'true').lower() == 'true'
MAX_REQUESTS_PER_MINUTE = int(os.getenv('MAX_REQUESTS_PER_MINUTE', 30))

# Configuraciones de despliegue
DEPLOYMENT_PLATFORM = os.getenv('DEPLOYMENT_PLATFORM', 'google_compute_engine')
DEPLOYMENT_MACHINE_TYPE = os.getenv('DEPLOYMENT_MACHINE_TYPE', 'e2-micro')
DEPLOYMENT_REGION = os.getenv('DEPLOYMENT_REGION', 'us-central1')

# Características experimentales
MULTIMODAL_SUPPORT = os.getenv('MULTIMODAL_SUPPORT', 'false').lower() == 'true'
MULTILINGUAL_SUPPORT = os.getenv('MULTILINGUAL_SUPPORT', 'false').lower() == 'true'

# Validaciones de configuración
def validate_config():
    """
    Valida las configuraciones críticas.
    
    Raises:
        ValueError: Si falta alguna configuración crítica.
    """
    if not SLACK_BOT_TOKEN:
        raise ValueError("SLACK_BOT_TOKEN no está configurado")
    
    if not SLACK_APP_TOKEN:
        raise ValueError("SLACK_APP_TOKEN no está configurado")
    
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY no está configurado")

# Ejecutar validaciones al importar
validate_config()
