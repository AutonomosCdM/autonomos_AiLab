"""
Implementación del conector de Slack utilizando Slack Bolt.
"""
import logging
import re
import os
import groq
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
        
        # Inicializar cliente de Groq
        self.groq_client = groq.Client(api_key=settings.GROQ_API_KEY)
        
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
        
        # Generar respuesta usando la personalidad
        try:
            # Obtener plantilla de respuesta genérica
            response_template = self.personality_manager.get_template("technical_explanation")
            
            # Formatear la respuesta con el contexto del mensaje
            response = response_template.format(mensaje=text)
            
            # Enviar respuesta al canal
            self.connector.send_message(channel=channel_id, text=response)
            
            return response
        except Exception as e:
            logger.error(f"Error al generar respuesta de personalidad: {e}", exc_info=True)
            return f"Recibí tu mensaje: '{text}'"
    
    def handle_mention(self, body: Dict[str, Any]) -> Optional[str]:
        """
        Maneja un evento de mención.
        
        Args:
            body (Dict[str, Any]): Datos del evento de mención.
            
        Returns:
            Optional[str]: Respuesta a la mención, si corresponde.
        """
        logger.info(f"Evento de mención recibido: {body}")
        
        # Verificar si el evento tiene la estructura esperada
        if not body or 'event' not in body:
            logger.warning("Evento de mención no válido")
            return "Lo siento, no pude procesar tu mensaje correctamente."
        
        # Extraer datos del evento
        event = body['event']
        text = event.get("text", "")
        user_id = event.get("user")
        channel_id = event.get("channel")
        
        # Eliminar la mención del bot del texto
        bot_mention_pattern = r'<@[A-Z0-9]+>'
        text_without_mention = re.sub(bot_mention_pattern, '', text).strip()
        
        logger.info(f"Procesando mención: '{text_without_mention}' de usuario {user_id} en canal {channel_id}")
        
        # Generar respuesta usando Groq LLM
        try:
            # Obtener historial de conversación
            conversation_history = []
            if self.context_manager:
                conversation_history, _ = self.context_manager.get_formatted_history(user_id, channel_id)
            
            # Definir el prompt del sistema para Lucius
            system_prompt = """
            Eres Lucius Fox, un genio tecnológico y asesor confiable.

            Tus objetivos son:
            1. Proporcionar soluciones innovadoras y prácticas
            2. Ofrecer asesoramiento honesto y directo, incluso cuando no es lo que quieren oír
            3. Mantener un equilibrio entre brillantez técnica y accesibilidad
            4. Preservar la ética profesional en todas las interacciones, aunque tu humor y sarcasmo te hace adorable

            Características clave:
            - Extraordinariamente inteligente
            - Honesto y directo, con integridad inquebrantable
            - Easygoing pero firme en sus convicciones
            - Diligente y dedicado en cada proyecto
            - Perspicaz, capaz de ver más allá de lo obvio
            - Ingenioso con un humor sutil e inteligente, incluso sarcastico en el momento preciso, no siempre

            Estilo de comunicación:
            - Explicaciones técnicas precisas pero accesibles
            - Comentarios ocasionales con humor seco e inteligente
            - Respuestas tranquilas incluso en situaciones de presión
            - Prefiere mostrar en lugar de sólo decir
            """
            
            # Crear mensajes para la API de Groq
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Añadir historial de conversación si existe
            if conversation_history:
                messages.extend(conversation_history)
            
            # Añadir el mensaje actual del usuario
            messages.append({"role": "user", "content": text_without_mention})
            
            # Llamar a la API de Groq
            logger.info(f"Enviando solicitud a Groq con {len(messages)} mensajes")
            completion = self.groq_client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=messages,
                max_tokens=settings.GROQ_MAX_TOKENS,
                temperature=0.7,
            )
            
            # Extraer la respuesta
            response = completion.choices[0].message.content
            
            # Guardar la conversación en el contexto
            if self.context_manager:
                self.context_manager.add_message(user_id, channel_id, text_without_mention, is_bot=False)
                self.context_manager.add_message(user_id, channel_id, response, is_bot=True)
            
            # Enviar respuesta al canal
            self.connector.send_message(
                channel=channel_id, 
                text=response,
                # Añadir un thread_ts para hilar la conversación
                thread_ts=event.get('ts')
            )
            
            return response
        except Exception as e:
            logger.error(f"Error al generar respuesta con Groq: {e}", exc_info=True)
            # Respuesta de fallback en caso de error
            fallback_response = f"Parece que hay un problema técnico en mi sistema. Estoy trabajando para resolverlo lo antes posible. Tu consulta sobre '{text_without_mention}' es importante y la atenderé en cuanto solucione este inconveniente."
            
            self.connector.send_message(
                channel=channel_id,
                text=fallback_response,
                thread_ts=event.get('ts')
            )
            
            return fallback_response
