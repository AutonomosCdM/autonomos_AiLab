"""
Implementación del conector de Slack utilizando Slack Bolt.
"""
import logging
from typing import Dict, Any, Callable, Optional

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from slack_bot.config import settings
from slack_bot.connectors.base import SlackConnector, EventHandler

logger = logging.getLogger(__name__)


class BoltConnector(SlackConnector):
    """
    Implementación de SlackConnector utilizando Slack Bolt.
    """
    
    def __init__(self, bot_token: Optional[str] = None, app_token: Optional[str] = None):
        """
        Inicializa el conector de Bolt.
        
        Args:
            bot_token (Optional[str]): Token de bot de Slack. Si es None, se usa el de settings.
            app_token (Optional[str]): Token de app de Slack. Si es None, se usa el de settings.
        """
        self.bot_token = bot_token or settings.SLACK_BOT_TOKEN
        self.app_token = app_token or settings.SLACK_APP_TOKEN
        
        if not self.bot_token or not self.app_token:
            raise ValueError("Se requieren los tokens de bot y app de Slack")
        
        # Inicializar la app de Bolt
        self.app = App(token=self.bot_token)
        self.handler = None
        self.event_handlers = {}
        
        logger.debug("BoltConnector inicializado")
    
    def connect(self) -> bool:
        """
        Establece la conexión con Slack usando Socket Mode.
        
        Returns:
            bool: True si la conexión fue exitosa, False en caso contrario.
        """
        try:
            self.handler = SocketModeHandler(self.app, self.app_token)
            self.handler.start()
            logger.info("Conexión establecida con Slack")
            return True
        except Exception as e:
            logger.error(f"Error al conectar con Slack: {e}", exc_info=True)
            return False
    
    def disconnect(self) -> bool:
        """
        Cierra la conexión con Slack.
        
        Returns:
            bool: True si la desconexión fue exitosa, False en caso contrario.
        """
        try:
            if self.handler:
                self.handler.close()
                logger.info("Conexión cerrada con Slack")
            return True
        except Exception as e:
            logger.error(f"Error al desconectar de Slack: {e}", exc_info=True)
            return False
    
    def send_message(self, channel: str, text: str, **kwargs) -> Dict[str, Any]:
        """
        Envía un mensaje a un canal o usuario específico.
        
        Args:
            channel (str): ID del canal o usuario.
            text (str): Texto del mensaje.
            **kwargs: Argumentos adicionales para el mensaje.
            
        Returns:
            Dict[str, Any]: Respuesta de la API de Slack.
        """
        try:
            response = self.app.client.chat_postMessage(
                channel=channel,
                text=text,
                **kwargs
            )
            logger.debug(f"Mensaje enviado a {channel}")
            return response
        except Exception as e:
            logger.error(f"Error al enviar mensaje a {channel}: {e}", exc_info=True)
            return {"ok": False, "error": str(e)}
    
    def register_event_handler(self, event_type: str, handler: Callable) -> None:
        """
        Registra un manejador para un tipo de evento específico.
        
        Args:
            event_type (str): Tipo de evento a manejar.
            handler (Callable): Función que maneja el evento.
        """
        if event_type == "message":
            self.app.message("")(handler)
            logger.debug("Manejador de mensajes registrado")
        elif event_type == "app_mention":
            self.app.event("app_mention")(handler)
            logger.debug("Manejador de menciones registrado")
        else:
            self.app.event(event_type)(handler)
            logger.debug(f"Manejador para evento {event_type} registrado")
        
        # Guardar referencia al manejador
        self.event_handlers[event_type] = handler
    
    def get_channel_info(self, channel_id: str) -> Dict[str, Any]:
        """
        Obtiene información sobre un canal.
        
        Args:
            channel_id (str): ID del canal.
            
        Returns:
            Dict[str, Any]: Información del canal.
        """
        try:
            response = self.app.client.conversations_info(channel=channel_id)
            return response
        except Exception as e:
            logger.error(f"Error al obtener información del canal {channel_id}: {e}", exc_info=True)
            return {"ok": False, "error": str(e)}
    
    def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """
        Obtiene información sobre un usuario.
        
        Args:
            user_id (str): ID del usuario.
            
        Returns:
            Dict[str, Any]: Información del usuario.
        """
        try:
            response = self.app.client.users_info(user=user_id)
            return response
        except Exception as e:
            logger.error(f"Error al obtener información del usuario {user_id}: {e}", exc_info=True)
            return {"ok": False, "error": str(e)}


class DefaultEventHandler(EventHandler):
    """
    Implementación por defecto del manejador de eventos.
    """
    
    def __init__(self, connector: SlackConnector, personality_manager=None, context_manager=None):
        """
        Inicializa el manejador de eventos.
        
        Args:
            connector (SlackConnector): Conector de Slack.
            personality_manager: Gestor de personalidad.
            context_manager: Gestor de contexto.
        """
        self.connector = connector
        self.personality_manager = personality_manager
        self.context_manager = context_manager
        logger.debug("DefaultEventHandler inicializado")
    
    def handle_message(self, message: Dict[str, Any]) -> Optional[str]:
        """
        Maneja un evento de mensaje.
        
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
        
        # Aquí se procesaría el mensaje con las capas de personalidad y contexto
        # Por ahora, devolvemos un mensaje simple
        return f"Recibí tu mensaje: '{text}'"
    
    def handle_mention(self, mention: Dict[str, Any]) -> Optional[str]:
        """
        Maneja un evento de mención.
        
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
        
        # Aquí se procesaría la mención con las capas de personalidad y contexto
        # Por ahora, devolvemos un mensaje simple
        return f"Gracias por mencionarme. Recibí tu mensaje: '{text}'"
