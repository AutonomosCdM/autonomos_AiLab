"""
Esquemas para validación de respuestas de IA.
"""
from typing import Dict, Any, List, Optional, Union, Callable

from slack_bot.schemas.messages import Schema, Field, StringField, NumberField, BooleanField, ValidationError


class ResponseSchema:
    """
    Esquema para validación de respuestas de IA.
    """
    
    def __init__(self, schema: Schema):
        """
        Inicializa el esquema de respuesta.
        
        Args:
            schema (Schema): Esquema para validación.
        """
        self.schema = schema
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida una respuesta según el esquema.
        
        Args:
            data (Dict[str, Any]): Datos a validar.
            
        Returns:
            Dict[str, Any]: Datos validados.
            
        Raises:
            ValidationError: Si la validación falla.
        """
        return self.schema.validate(data)
    
    def format_for_slack(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formatea una respuesta para envío a Slack.
        
        Args:
            data (Dict[str, Any]): Datos de respuesta.
            
        Returns:
            Dict[str, Any]: Datos formateados para Slack.
        """
        # Validar datos
        validated_data = self.validate(data)
        
        # Formatear para Slack
        slack_data = {
            "channel": validated_data["channel_id"],
            "text": validated_data["text"]
        }
        
        # Añadir campos opcionales
        if "thread_ts" in validated_data and validated_data["thread_ts"]:
            slack_data["thread_ts"] = validated_data["thread_ts"]
        
        if "blocks" in validated_data and validated_data["blocks"]:
            slack_data["blocks"] = validated_data["blocks"]
        
        if "attachments" in validated_data and validated_data["attachments"]:
            slack_data["attachments"] = validated_data["attachments"]
        
        return slack_data


# Esquema para respuestas de texto simple
text_response_schema = ResponseSchema(Schema({
    "text": StringField(
        required=True,
        min_length=1,
        max_length=4000,
        error_message="El texto de la respuesta es requerido y debe tener entre 1 y 4000 caracteres"
    ),
    "channel_id": StringField(
        required=True,
        error_message="El ID de canal es requerido"
    ),
    "thread_ts": StringField(
        required=False
    )
}))

# Esquema para respuestas con bloques
blocks_response_schema = ResponseSchema(Schema({
    "text": StringField(
        required=True,
        min_length=1,
        max_length=4000,
        error_message="El texto de la respuesta es requerido y debe tener entre 1 y 4000 caracteres"
    ),
    "channel_id": StringField(
        required=True,
        error_message="El ID de canal es requerido"
    ),
    "thread_ts": StringField(
        required=False
    ),
    "blocks": Field(
        required=True,
        error_message="Los bloques son requeridos"
    )
}))

# Esquema para respuestas con adjuntos
attachments_response_schema = ResponseSchema(Schema({
    "text": StringField(
        required=True,
        min_length=1,
        max_length=4000,
        error_message="El texto de la respuesta es requerido y debe tener entre 1 y 4000 caracteres"
    ),
    "channel_id": StringField(
        required=True,
        error_message="El ID de canal es requerido"
    ),
    "thread_ts": StringField(
        required=False
    ),
    "attachments": Field(
        required=True,
        error_message="Los adjuntos son requeridos"
    )
}))


# Funciones de ayuda para crear respuestas

def create_text_response(text: str, channel_id: str, thread_ts: Optional[str] = None) -> Dict[str, Any]:
    """
    Crea una respuesta de texto simple.
    
    Args:
        text (str): Texto de la respuesta.
        channel_id (str): ID del canal.
        thread_ts (Optional[str]): Timestamp del hilo.
        
    Returns:
        Dict[str, Any]: Respuesta formateada.
    """
    response = {
        "text": text,
        "channel_id": channel_id
    }
    
    if thread_ts:
        response["thread_ts"] = thread_ts
    
    return text_response_schema.format_for_slack(response)


def create_blocks_response(
    text: str,
    blocks: List[Dict[str, Any]],
    channel_id: str,
    thread_ts: Optional[str] = None
) -> Dict[str, Any]:
    """
    Crea una respuesta con bloques.
    
    Args:
        text (str): Texto de la respuesta.
        blocks (List[Dict[str, Any]]): Bloques de la respuesta.
        channel_id (str): ID del canal.
        thread_ts (Optional[str]): Timestamp del hilo.
        
    Returns:
        Dict[str, Any]: Respuesta formateada.
    """
    response = {
        "text": text,
        "blocks": blocks,
        "channel_id": channel_id
    }
    
    if thread_ts:
        response["thread_ts"] = thread_ts
    
    return blocks_response_schema.format_for_slack(response)


def create_attachments_response(
    text: str,
    attachments: List[Dict[str, Any]],
    channel_id: str,
    thread_ts: Optional[str] = None
) -> Dict[str, Any]:
    """
    Crea una respuesta con adjuntos.
    
    Args:
        text (str): Texto de la respuesta.
        attachments (List[Dict[str, Any]]): Adjuntos de la respuesta.
        channel_id (str): ID del canal.
        thread_ts (Optional[str]): Timestamp del hilo.
        
    Returns:
        Dict[str, Any]: Respuesta formateada.
    """
    response = {
        "text": text,
        "attachments": attachments,
        "channel_id": channel_id
    }
    
    if thread_ts:
        response["thread_ts"] = thread_ts
    
    return attachments_response_schema.format_for_slack(response)


# Bloques predefinidos para respuestas comunes

def create_header_block(text: str) -> Dict[str, Any]:
    """
    Crea un bloque de encabezado.
    
    Args:
        text (str): Texto del encabezado.
        
    Returns:
        Dict[str, Any]: Bloque de encabezado.
    """
    return {
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": text,
            "emoji": True
        }
    }


def create_section_block(text: str) -> Dict[str, Any]:
    """
    Crea un bloque de sección.
    
    Args:
        text (str): Texto de la sección.
        
    Returns:
        Dict[str, Any]: Bloque de sección.
    """
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": text
        }
    }


def create_divider_block() -> Dict[str, Any]:
    """
    Crea un bloque divisor.
    
    Returns:
        Dict[str, Any]: Bloque divisor.
    """
    return {
        "type": "divider"
    }


def create_button_block(text: str, action_id: str, value: str) -> Dict[str, Any]:
    """
    Crea un bloque de botón.
    
    Args:
        text (str): Texto del botón.
        action_id (str): ID de la acción.
        value (str): Valor del botón.
        
    Returns:
        Dict[str, Any]: Bloque de botón.
    """
    return {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": text,
                    "emoji": True
                },
                "action_id": action_id,
                "value": value
            }
        ]
    }
