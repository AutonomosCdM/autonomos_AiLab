import os
import sys
import traceback
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Load environment variables
load_dotenv()

# Initialize Slack client
print("Inicializando cliente de Slack...")
client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

# Test function to verify Slack API connection
def test_slack_connection():
    try:
        print("Verificando la identidad del bot...")
        # Get bot info to verify token is valid
        bot_info = client.auth_test()
        print(f"✓ Conexión exitosa como: {bot_info['user']} (ID: {bot_info['user_id']})")
        print(f"✓ Workspace: {bot_info['team']}")
        print(f"✓ Scopes disponibles: {bot_info.get('scope', 'No disponible')}")
        
        print("\nVerificando permisos del bot...")
        # Check if the bot has the necessary scopes
        scopes = bot_info.get("scope", "").split(",")
        if "app_mentions:read" in scopes:
            print("✓ El bot puede leer menciones")
        else:
            print("⚠️ El bot no tiene permiso para leer menciones (app_mentions:read)")
        
        # Try to get a list of conversations the bot can access
        print("\nObteniendo lista de canales accesibles...")
        conversations = client.conversations_list(types="public_channel,private_channel,im,mpim")
        channels = conversations.get("channels", [])
        if channels:
            print(f"✓ El bot puede ver {len(channels)} canales/conversaciones")
            for channel in channels[:5]:  # Show first 5 channels
                channel_name = channel.get("name", "DM" if channel.get("is_im", False) else "Unknown")
                channel_id = channel.get("id", "Unknown")
                print(f"  - {channel_name} (ID: {channel_id})")
            if len(channels) > 5:
                print(f"  - ... y {len(channels) - 5} más")
        else:
            print("⚠️ El bot no puede ver ningún canal")
        
        print("\nInformación importante:")
        print("1. Para hablar con el bot directamente:")
        print("   - Abre un mensaje directo con @Lucius")
        print("   - Escribe cualquier mensaje y el bot responderá")
        
        print("\n2. Para mencionar al bot en un canal:")
        print("   - Escribe @Lucius seguido de tu mensaje en cualquier canal")
        print("   - El bot responderá en el mismo canal")
        
        return True
    except SlackApiError as e:
        print(f"Error completo: {e.response}")
        error = e.response["error"]
        print(f"Error: {error}")
        
        # Provide more helpful error messages
        if error == "account_inactive":
            print("El token parece ser para una aplicación o usuario eliminado, o la aplicación no está instalada.")
        elif error == "invalid_auth":
            print("El token es inválido. Verifica que estés usando el token correcto.")
        elif error == "missing_scope":
            print("El token del bot no tiene los permisos necesarios. Verifica el mensaje de error para más detalles.")
        
        return False
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        print("Traceback completo:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("PRUEBA DE CONEXIÓN CON SLACK")
    print("=" * 50)
    print(f"Versión de Python: {sys.version}")
    print(f"Token del bot: {os.environ['SLACK_BOT_TOKEN'][:10]}...{os.environ['SLACK_BOT_TOKEN'][-5:]}")
    print(f"Token de la app: {os.environ['SLACK_APP_TOKEN'][:10]}...{os.environ['SLACK_APP_TOKEN'][-5:]}")
    print("-" * 50)
    
    if test_slack_connection():
        print("\n✅ Prueba exitosa! Tu bot puede conectarse a Slack.")
        print("\nPara ejecutar el bot:")
        print("1. Ejecuta: python app.py")
        print("2. O usa el script: ./run_bot.sh")
    else:
        print("\n❌ Prueba fallida. Por favor revisa los mensajes de error anteriores.")
