"""
Pruebas de conexión y configuración para el bot de Slack.
"""
import os
import sys
import logging
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

def test_environment_variables():
    """
    Verifica la presencia de variables de entorno necesarias.
    
    Raises:
        AssertionError: Si falta alguna variable de entorno.
    """
    required_vars = [
        'SLACK_BOT_TOKEN',
        'SLACK_APP_TOKEN',
        'GROQ_API_KEY'
    ]
    
    for var in required_vars:
        assert os.environ.get(var), f"Variable de entorno {var} no configurada"
    
    logger.info("✅ Todas las variables de entorno necesarias están configuradas")


def test_slack_connection():
    """
    Prueba de conexión básica con Slack.
    
    Raises:
        ImportError: Si no se pueden importar las dependencias.
        Exception: Si la conexión falla.
    """
    try:
        from slack_bolt import App
        from slack_bolt.adapter.socket_mode import SocketModeHandler
    except ImportError as e:
        logger.error(f"Error al importar dependencias de Slack: {e}")
        raise
    
    try:
        # Inicializar app de Slack
        app = App(token=os.environ['SLACK_BOT_TOKEN'])
        
        # Probar conexión básica
        response = app.client.auth_test()
        
        logger.info(f"✅ Conexión con Slack exitosa")
        logger.info(f"Bot conectado como: {response['user']}")
        logger.info(f"Equipo: {response['team']}")
        
        return response
    except Exception as e:
        logger.error(f"Error al conectar con Slack: {e}")
        raise


def test_groq_connection():
    """
    Prueba de conexión básica con Groq API.
    
    Raises:
        ImportError: Si no se pueden importar las dependencias.
        Exception: Si la conexión falla.
    """
    try:
        import groq
    except ImportError as e:
        logger.error(f"Error al importar librería Groq: {e}")
        raise
    
    try:
        # Inicializar cliente de Groq
        client = groq.Client(api_key=os.environ['GROQ_API_KEY'])
        
        # Realizar una prueba de generación de texto
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Eres un asistente de prueba."},
                {"role": "user", "content": "Hola, ¿estás funcionando?"}
            ],
            model=os.environ.get('GROQ_MODEL', 'llama3-70b-8192'),
            max_tokens=50
        )
        
        logger.info("✅ Conexión con Groq API exitosa")
        logger.info(f"Respuesta de prueba: {response.choices[0].message.content}")
        
        return response
    except Exception as e:
        logger.error(f"Error al conectar con Groq API: {e}")
        raise


def main():
    """
    Ejecuta todas las pruebas de conexión.
    """
    try:
        print("=" * 50)
        print("🤖 Pruebas de Conexión del Bot de Slack")
        print("=" * 50)
        
        test_environment_variables()
        test_slack_connection()
        test_groq_connection()
        
        print("\n✅ Todas las pruebas de conexión fueron exitosas!")
        print("El bot está listo para ser ejecutado.")
        sys.exit(0)
    
    except AssertionError as e:
        logger.error(f"Error de configuración: {e}")
        print(f"\n❌ Error de configuración: {e}")
        print("Por favor, revisa tu archivo .env y configura todas las variables necesarias.")
        sys.exit(1)
    
    except Exception as e:
        logger.error(f"Error durante las pruebas: {e}")
        print(f"\n❌ Error durante las pruebas de conexión: {e}")
        print("Revisa la configuración y las credenciales.")
        sys.exit(1)


if __name__ == "__main__":
    main()
