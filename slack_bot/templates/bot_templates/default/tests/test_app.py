"""
Pruebas para la aplicación principal del bot de Slack.
"""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Añadir directorio raíz al path para importar módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from slack_bot.config import settings
from slack_bot.connectors.slack_bolt import BoltConnector, DefaultEventHandler
from slack_bot.personality.manager import PersonalityManager
from slack_bot.context.manager import ContextManager


def test_bot_connector_initialization():
    """
    Prueba la inicialización del conector de Slack.
    """
    connector = BoltConnector()
    
    assert connector is not None, "El conector de Slack no debe ser None"
    assert connector.bot_token is not None, "El token de bot debe estar configurado"
    assert connector.app is not None, "La aplicación de Slack Bolt debe estar inicializada"


def test_personality_manager_initialization():
    """
    Prueba la inicialización del gestor de personalidad.
    """
    personality_manager = PersonalityManager()
    
    assert personality_manager is not None, "El gestor de personalidad no debe ser None"
    assert personality_manager.active_personality is not None, "Debe haber una personalidad activa"
    
    # Verificar que se puedan obtener configuraciones
    system_prompt = personality_manager.get_system_prompt()
    assert system_prompt, "El prompt del sistema no debe estar vacío"
    
    response_config = personality_manager.get_response_config()
    assert response_config, "La configuración de respuesta no debe estar vacía"


def test_context_manager_initialization():
    """
    Prueba la inicialización del gestor de contexto.
    """
    context_manager = ContextManager()
    
    assert context_manager is not None, "El gestor de contexto no debe ser None"
    
    # Probar añadir un mensaje
    context_manager.add_message('test_user', 'test_channel', 'Mensaje de prueba')
    
    # Obtener historial
    history = context_manager.get_conversation_history('test_user', 'test_channel')
    assert len(history) > 0, "El historial de conversación debe contener el mensaje añadido"


@patch('slack_bolt.App')
@patch('slack_bolt.adapter.socket_mode.SocketModeHandler')
def test_bot_connection(mock_socket_handler, mock_app):
    """
    Prueba la conexión del bot simulando la inicialización.
    """
    # Configurar mocks
    mock_app_instance = MagicMock()
    mock_app.return_value = mock_app_instance
    
    mock_handler_instance = MagicMock()
    mock_socket_handler.return_value = mock_handler_instance
    
    # Crear componentes del bot
    connector = BoltConnector()
    personality_manager = PersonalityManager()
    context_manager = ContextManager()
    
    # Crear manejador de eventos
    event_handler = DefaultEventHandler(
        connector=connector, 
        personality_manager=personality_manager, 
        context_manager=context_manager
    )
    
    # Registrar manejadores de eventos
    connector.register_event_handler("message", event_handler.handle_message)
    connector.register_event_handler("app_mention", event_handler.handle_mention)
    
    # Simular conexión
    connection_result = connector.connect()
    
    assert connection_result is True, "La conexión del bot debe ser exitosa"
    mock_socket_handler.assert_called_once()
    mock_handler_instance.start.assert_called_once()


def test_environment_variables():
    """
    Prueba la configuración de variables de entorno.
    """
    required_vars = [
        'SLACK_BOT_TOKEN',
        'SLACK_APP_TOKEN',
        'GROQ_API_KEY'
    ]
    
    for var in required_vars:
        assert os.environ.get(var) is not None, f"La variable de entorno {var} debe estar configurada"


def test_settings_configuration():
    """
    Prueba la configuración de settings.
    """
    assert hasattr(settings, 'SLACK_BOT_TOKEN'), "Settings debe tener SLACK_BOT_TOKEN"
    assert hasattr(settings, 'SLACK_APP_TOKEN'), "Settings debe tener SLACK_APP_TOKEN"
    assert hasattr(settings, 'LOG_LEVEL'), "Settings debe tener LOG_LEVEL"
    
    # Verificar que los valores no estén vacíos
    assert settings.LOG_LEVEL, "LOG_LEVEL no debe estar vacío"
    assert settings.DEFAULT_PERSONALITY, "DEFAULT_PERSONALITY no debe estar vacío"


def test_message_processing():
    """
    Prueba básica del procesamiento de mensajes.
    """
    connector = BoltConnector()
    personality_manager = PersonalityManager()
    context_manager = ContextManager()
    
    event_handler = DefaultEventHandler(
        connector=connector, 
        personality_manager=personality_manager, 
        context_manager=context_manager
    )
    
    # Simular un mensaje
    test_message = {
        "text": "Hola, ¿cómo estás?",
        "user": "test_user",
        "channel": "test_channel"
    }
    
    # Simular manejo de mensaje
    response = event_handler.handle_message(test_message)
    
    assert response is not None, "La respuesta no debe ser None"
    assert isinstance(response, str), "La respuesta debe ser un string"
    assert len(response) > 0, "La respuesta no debe estar vacía"
