"""
Punto de entrada principal para el bot de Slack.
"""
import os
import logging
import dotenv

# Cargar variables de entorno
dotenv.load_dotenv()

# Configuración de logging
import slack_bot.utils.logging as log_config
log_config.configure_logging()

# Importaciones de módulos internos
from slack_bot.config import settings
from slack_bot.connectors import ComposioMCPConnector, DefaultEventHandler
from slack_bot.personality.manager import PersonalityManager
from slack_bot.context.manager import ContextManager

logger = logging.getLogger(__name__)

def main():
    """
    Función principal para iniciar el bot de Slack.
    """
    try:
        # Inicializar manejadores de contexto y personalidad
        context_manager = ContextManager()
        personality_manager = PersonalityManager()

        # Inicializar conector Composio MCP
        connector = ComposioMCPConnector()
        
        # Configurar manejador de eventos
        event_handler = DefaultEventHandler(
            connector=connector,
            personality_manager=personality_manager,
            context_manager=context_manager
        )

        # Registrar manejadores de eventos
        connector.register_event_handler("message", event_handler.handle_message)
        connector.register_event_handler("app_mention", event_handler.handle_mention)

        # Establecer conexión
        if connector.connect():
            logger.info("Bot de Slack iniciado exitosamente con Composio MCP")
            # Mantener el bot en ejecución
            while True:
                pass
        else:
            logger.error("No se pudo iniciar el bot de Slack")

    except Exception as e:
        logger.error(f"Error crítico al iniciar el bot: {e}", exc_info=True)

if __name__ == "__main__":
    main()
