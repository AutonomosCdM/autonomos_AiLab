"""
Paquete de esquemas de validación para el bot de Slack.

Este módulo gestiona la validación de mensajes, respuestas y otros datos estructurados.
"""

# Importar esquemas de validación
from .messages import (
    ValidationError,
    Field,
    StringField,
    NumberField,
    BooleanField,
    Schema,
    user_message_schema,
    bot_response_schema
)
from .responses import (
    ResponseSchema,
    text_response_schema,
    blocks_response_schema,
    attachments_response_schema,
    create_text_response,
    create_blocks_response,
    create_attachments_response,
    create_header_block,
    create_section_block,
    create_divider_block,
    create_button_block
)

# Lista de esquemas disponibles
AVAILABLE_SCHEMAS = [
    "user_message",
    "bot_response",
    "text_response",
    "blocks_response",
    "attachments_response"
]

# Versión del paquete de esquemas
__version__ = "0.1.0"

# Exportar clases y funciones principales
__all__ = [
    # Clases de validación
    'ValidationError',
    'Field',
    'StringField',
    'NumberField',
    'BooleanField',
    'Schema',
    'ResponseSchema',
    
    # Esquemas predefinidos
    'user_message_schema',
    'bot_response_schema',
    'text_response_schema',
    'blocks_response_schema',
    'attachments_response_schema',
    
    # Funciones de creación de respuestas
    'create_text_response',
    'create_blocks_response',
    'create_attachments_response',
    
    # Funciones de creación de bloques
    'create_header_block',
    'create_section_block',
    'create_divider_block',
    'create_button_block'
]
