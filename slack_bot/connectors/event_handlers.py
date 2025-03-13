"""
Implementaciones de manejadores de eventos para Slack.
"""
import logging
from typing import Dict, Any, Optional, Callable

from slack_bot.connectors.base import EventHandler, SlackConnector

logger = logging.getLogger(__name__)


class MessageEventHandler(EventHandler):
    """
    Manejador de eventos de mensajes directos.
    """
    
    def __init__(self, connector: SlackConnector, message_processor: Callable):
        """
        Inicializa el manejador de eventos de mensajes.
        
        Args:
            connector (SlackConnector): Conector de Slack.
            message_processor (Callable): Función que procesa los mensajes y genera respuestas.
                Debe aceptar el texto del mensaje y devolver una respuesta.
        """
        self.connector = connector
        self.message_processor = message_processor
        logger.debug("MessageEventHandler inicializado")
    
    def handle_message(self, message: Dict[str, Any]) -> Optional[str]:
        """
        Maneja un evento de mensaje directo.
        
        Args:
            message (Dict[str, Any]): Datos del mensaje.
            
        Returns:
            Optional[str]: Respuesta al mensaje, si corresponde.
        """
        logger.info(f"Mensaje recibido: {message}")
        
        # Ignorar mensajes del propio bot
        if message.get("bot_id"):
            logger.info(f"Ignorando mensaje del bot: {message.get('bot_id')}")
            return None
        
        # Extraer texto del mensaje
        text = message.get("text", "")
        user_id = message.get("user")
        channel_id = message.get("channel")
        
        logger.info(f"Procesando mensaje: '{text}' de usuario {user_id} en canal {channel_id}")
        
        try:
            # Procesar el mensaje y obtener respuesta
            response = self.message_processor(text, user_id=user_id, channel_id=channel_id)
            
            # Enviar respuesta
            if response:
                self.connector.send_message(channel=channel_id, text=response)
                return response
            
            return None
        except Exception as e:
            logger.error(f"Error al procesar mensaje: {e}", exc_info=True)
            error_msg = "Lo siento, tuve un problema al procesar tu mensaje. Por favor intenta de nuevo."
            self.connector.send_message(channel=channel_id, text=error_msg)
            return error_msg
    
    def handle_mention(self, mention: Dict[str, Any]) -> Optional[str]:
        """
        No implementado para este manejador.
        """
        logger.warning("handle_mention llamado en MessageEventHandler, pero no está implementado")
        return None


class MentionEventHandler(EventHandler):
    """
    Manejador de eventos de menciones en canales.
    """
    
    def __init__(self, connector: SlackConnector, mention_processor: Callable):
        """
        Inicializa el manejador de eventos de menciones.
        
        Args:
            connector (SlackConnector): Conector de Slack.
            mention_processor (Callable): Función que procesa las menciones y genera respuestas.
                Debe aceptar el texto de la mención y devolver una respuesta.
        """
        self.connector = connector
        self.mention_processor = mention_processor
        logger.debug("MentionEventHandler inicializado")
    
    def handle_message(self, message: Dict[str, Any]) -> Optional[str]:
        """
        No implementado para este manejador.
        """
        logger.warning("handle_message llamado en MentionEventHandler, pero no está implementado")
        return None
    
    def handle_mention(self, mention: Dict[str, Any]) -> Optional[str]:
        """
        Maneja un evento de mención en canal.
        
        Args:
            mention (Dict[str, Any]): Datos de la mención.
            
        Returns:
            Optional[str]: Respuesta a la mención, si corresponde.
        """
        logger.info(f"Mención recibida: {mention}")
        
        # Extraer texto de la mención (eliminar la parte de la mención al bot)
        full_text = mention.get("text", "")
        text = full_text.split(">", 1)[1].strip() if ">" in full_text else full_text
        user_id = mention.get("user")
        channel_id = mention.get("channel")
        
        logger.info(f"Procesando mención: '{text}' de usuario {user_id} en canal {channel_id}")
        
        try:
            # Procesar la mención y obtener respuesta
            response = self.mention_processor(text, user_id=user_id, channel_id=channel_id)
            
            # Enviar respuesta
            if response:
                self.connector.send_message(channel=channel_id, text=response)
                return response
            
            return None
        except Exception as e:
            logger.error(f"Error al procesar mención: {e}", exc_info=True)
            error_msg = "Lo siento, tuve un problema al procesar tu mención. Por favor intenta de nuevo."
            self.connector.send_message(channel=channel_id, text=error_msg)
            return error_msg


class CombinedEventHandler(EventHandler):
    """
    Manejador que combina el manejo de mensajes directos y menciones.
    """
    
    def __init__(self, connector: SlackConnector, message_processor: Callable):
        """
        Inicializa el manejador combinado.
        
        Args:
            connector (SlackConnector): Conector de Slack.
            message_processor (Callable): Función que procesa los mensajes y menciones.
                Debe aceptar el texto del mensaje y devolver una respuesta.
        """
        self.connector = connector
        self.message_processor = message_processor
        logger.debug("CombinedEventHandler inicializado")
    
    def handle_message(self, message: Dict[str, Any]) -> Optional[str]:
        """
        Maneja un evento de mensaje directo.
        
        Args:
            message (Dict[str, Any]): Datos del mensaje.
            
        Returns:
            Optional[str]: Respuesta al mensaje, si corresponde.
        """
        logger.info(f"Mensaje recibido: {message}")
        
        # Ignorar mensajes del propio bot
        if message.get("bot_id"):
            logger.info(f"Ignorando mensaje del bot: {message.get('bot_id')}")
            return None
        
        # Extraer texto del mensaje
        text = message.get("text", "")
        user_id = message.get("user")
        channel_id = message.get("channel")
        
        logger.info(f"Procesando mensaje: '{text}' de usuario {user_id} en canal {channel_id}")
        
        try:
            # Procesar el mensaje y obtener respuesta
            response = self.message_processor(text, user_id=user_id, channel_id=channel_id, is_mention=False)
            
            # Enviar respuesta
            if response:
                self.connector.send_message(channel=channel_id, text=response)
                return response
            
            return None
        except Exception as e:
            logger.error(f"Error al procesar mensaje: {e}", exc_info=True)
            error_msg = "Lo siento, tuve un problema al procesar tu mensaje. Por favor intenta de nuevo."
            self.connector.send_message(channel=channel_id, text=error_msg)
            return error_msg
    
    def handle_mention(self, mention: Dict[str, Any]) -> Optional[str]:
        """
        Maneja un evento de mención en canal.
        
        Args:
            mention (Dict[str, Any]): Datos de la mención.
            
        Returns:
            Optional[str]: Respuesta a la mención, si corresponde.
        """
        logger.info(f"Mención recibida: {mention}")
        
        # Extraer texto de la mención (eliminar la parte de la mención al bot)
        full_text = mention.get("text", "")
        text = full_text.split(">", 1)[1].strip() if ">" in full_text else full_text
        user_id = mention.get("user")
        channel_id = mention.get("channel")
        
        logger.info(f"Procesando mención: '{text}' de usuario {user_id} en canal {channel_id}")
        
        try:
            # Procesar la mención y obtener respuesta
            response = self.message_processor(text, user_id=user_id, channel_id=channel_id, is_mention=True)
            
            # Enviar respuesta
            if response:
                self.connector.send_message(channel=channel_id, text=response)
                return response
            
            return None
        except Exception as e:
            logger.error(f"Error al procesar mención: {e}", exc_info=True)
            error_msg = "Lo siento, tuve un problema al procesar tu mención. Por favor intenta de nuevo."
            self.connector.send_message(channel=channel_id, text=error_msg)
            return error_msg
