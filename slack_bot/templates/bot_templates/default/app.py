"""
Bot de Slack para {{ project_name_title }}.
"""
import os
import logging
from dotenv import load_dotenv

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from slack_bot.config import settings
from slack_bot.connectors.slack_bolt import BoltConnector, DefaultEventHandler
from slack_bot.personality.manager import PersonalityManager
from slack_bot.context.manager import ContextManager
from slack_bot.utils.logging import setup_logging

# Configurar logging
logger = setup_logging()

# Cargar variables de entorno
load_dotenv()

def create_bot():
    """
    Crea y configura el bot de Slack.
    
    Returns:
        Tuple: Conector de Slack, manejador de eventos, gestor de personalidad, gestor de contexto
    """
    # Inicializar gestores
    personality_manager = PersonalityManager()
    context_manager = ContextManager()
    
    # Inicializar conector de Slack
    slack_connector = BoltConnector()
    
    # Definir función de procesamiento de mensajes
    def process_message(text, user_id=None, channel_id=None, is_mention=False):
        """
        Procesa un mensaje utilizando las capas de personalidad y contexto.
        
        Args:
            text (str): Texto del mensaje.
            user_id (str, optional): ID del usuario.
            channel_id (str, optional): ID del canal.
            is_mention (bool, optional): Si es una mención.
            
        Returns:
            str: Respuesta generada.
        """
        try:
            # Obtener historial de conversación
            conversation_history, debug_history = context_manager.get_formatted_history(
                user_id or 'default', 
                channel_id or settings.SLACK_CHANNEL
            )
            
            # Obtener configuración de personalidad
            system_prompt = personality_manager.get_system_prompt()
            response_config = personality_manager.get_response_config()
            
            # TODO: Implementar llamada a Groq API para generar respuesta
            # Por ahora, una respuesta de ejemplo
            response = f"Recibí tu mensaje: '{text}'"
            
            # Añadir mensaje al contexto
            context_manager.add_message(
                user_id or 'default', 
                channel_id or settings.SLACK_CHANNEL, 
                text
            )
            context_manager.add_message(
                user_id or 'default', 
                channel_id or settings.SLACK_CHANNEL, 
                response, 
                is_bot=True
            )
            
            return response
        except Exception as e:
            logger.error(f"Error al procesar mensaje: {e}", exc_info=True)
            return "Lo siento, tuve un problema al procesar tu mensaje."
    
    # Crear manejador de eventos
    event_handler = DefaultEventHandler(
        connector=slack_connector, 
        personality_manager=personality_manager, 
        context_manager=context_manager
    )
    
    # Registrar manejadores de eventos
    slack_connector.register_event_handler("message", event_handler.handle_message)
    slack_connector.register_event_handler("app_mention", event_handler.handle_mention)
    
    return slack_connector, event_handler, personality_manager, context_manager


def main():
    """
    Función principal para iniciar el bot.
    """
    try:
        # Crear bot
        slack_connector, event_handler, personality_manager, context_manager = create_bot()
        
        # Conectar
        if not slack_connector.connect():
            logger.error("No se pudo conectar con Slack")
            return
        
        print("=" * 50)
        print("⚡️ Bot de Slack iniciado!")
        print("El bot responderá a:")
        print("1. Mensajes directos")
        print("2. Menciones en canales")
        print("=" * 50)
    
    except Exception as e:
        logger.error(f"Error al iniciar el bot: {e}", exc_info=True)


if __name__ == "__main__":
    main()
