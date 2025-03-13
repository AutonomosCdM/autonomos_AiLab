"""
Implementación del conector Slack utilizando Composio MCP.
"""
import logging
from typing import Dict, Any, Callable, Optional

from composio_core import ComposioToolSet
from composio_openai import App, Action

from slack_bot.config import settings
from slack_bot.connectors.base import SlackConnector, EventHandler

logger = logging.getLogger(__name__)


class ComposioMCPConnector(SlackConnector):
    """
    Implementación de SlackConnector utilizando Composio MCP Slack server.
    """
    
    def __init__(self, bot_token: Optional[str] = None, app_token: Optional[str] = None):
        """
        Inicializa el conector Composio MCP.
        
        Args:
            bot_token (Optional[str]): Token de bot de Slack. 
            app_token (Optional[str]): Token de app de Slack.
        """
        self.bot_token = bot_token or settings.SLACK_BOT_TOKEN
        self.app_token = app_token or settings.SLACK_APP_TOKEN
        
        if not self.bot_token or not self.app_token:
            raise ValueError("Se requieren los tokens de bot y app de Slack")
        
        # Inicializar el conjunto de herramientas de Composio
        self.toolset = ComposioToolSet()
        
        # Obtener todas las acciones de Slack
        self.slack_actions = self.toolset.get_tools(apps=[App.SLACK])
        
        logger.debug("ComposioMCPConnector inicializado")
    
    def connect(self) -> bool:
        """
        Establece la conexión con Slack usando Composio MCP.
        
        Returns:
            bool: True si la conexión fue exitosa, False en caso contrario.
        """
        try:
            # Composio MCP maneja la conexión internamente
            logger.info("Conexión establecida con Slack a través de Composio MCP")
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
            # Composio MCP maneja la desconexión internamente
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
            # Usar la acción de envío de mensaje de Composio
            result = self.toolset.execute_tool(
                tool_name="chat.postMessage", 
                params={
                    "channel": channel,
                    "text": text,
                    **kwargs
                }
            )
            logger.debug(f"Mensaje enviado a {channel}")
            return result
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
        # Composio MCP maneja los eventos de manera diferente
        # Aquí podrías configurar un webhook o usar la API de eventos de Composio
        logger.warning(f"Registro de manejador de eventos {event_type} no implementado directamente")
    
    def get_channel_info(self, channel_id: str) -> Dict[str, Any]:
        """
        Obtiene información sobre un canal.
        
        Args:
            channel_id (str): ID del canal.
            
        Returns:
            Dict[str, Any]: Información del canal.
        """
        try:
            result = self.toolset.execute_tool(
                tool_name="conversations.info", 
                params={"channel": channel_id}
            )
            return result
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
            result = self.toolset.execute_tool(
                tool_name="users.info", 
                params={"user": user_id}
            )
            return result
        except Exception as e:
            logger.error(f"Error al obtener información del usuario {user_id}: {e}", exc_info=True)
            return {"ok": False, "error": str(e)}
