"""
Interfaces base para la capa de conectores.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, List, Optional


class SlackConnector(ABC):
    """
    Interfaz abstracta para conectores de Slack.
    Define los métodos que cualquier implementación de conector debe proporcionar.
    """
    
    @abstractmethod
    def connect(self) -> bool:
        """
        Establece la conexión con Slack.
        
        Returns:
            bool: True si la conexión fue exitosa, False en caso contrario.
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """
        Cierra la conexión con Slack.
        
        Returns:
            bool: True si la desconexión fue exitosa, False en caso contrario.
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def register_event_handler(self, event_type: str, handler: Callable) -> None:
        """
        Registra un manejador para un tipo de evento específico.
        
        Args:
            event_type (str): Tipo de evento a manejar.
            handler (Callable): Función que maneja el evento.
        """
        pass
    
    @abstractmethod
    def get_channel_info(self, channel_id: str) -> Dict[str, Any]:
        """
        Obtiene información sobre un canal.
        
        Args:
            channel_id (str): ID del canal.
            
        Returns:
            Dict[str, Any]: Información del canal.
        """
        pass
    
    @abstractmethod
    def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """
        Obtiene información sobre un usuario.
        
        Args:
            user_id (str): ID del usuario.
            
        Returns:
            Dict[str, Any]: Información del usuario.
        """
        pass


class EventHandler(ABC):
    """
    Interfaz abstracta para manejadores de eventos.
    Define los métodos que cualquier implementación de manejador debe proporcionar.
    """
    
    @abstractmethod
    def handle_message(self, message: Dict[str, Any]) -> Optional[str]:
        """
        Maneja un evento de mensaje.
        
        Args:
            message (Dict[str, Any]): Datos del mensaje.
            
        Returns:
            Optional[str]: Respuesta al mensaje, si corresponde.
        """
        pass
    
    @abstractmethod
    def handle_mention(self, mention: Dict[str, Any]) -> Optional[str]:
        """
        Maneja un evento de mención.
        
        Args:
            mention (Dict[str, Any]): Datos de la mención.
            
        Returns:
            Optional[str]: Respuesta a la mención, si corresponde.
        """
        pass


class MessageFormatter(ABC):
    """
    Interfaz abstracta para formateadores de mensajes.
    Define los métodos que cualquier implementación de formateador debe proporcionar.
    """
    
    @abstractmethod
    def format_message(self, text: str, **kwargs) -> Dict[str, Any]:
        """
        Formatea un mensaje para envío a Slack.
        
        Args:
            text (str): Texto del mensaje.
            **kwargs: Opciones de formato adicionales.
            
        Returns:
            Dict[str, Any]: Mensaje formateado.
        """
        pass
    
    @abstractmethod
    def parse_message(self, message: Dict[str, Any]) -> str:
        """
        Extrae el texto de un mensaje de Slack.
        
        Args:
            message (Dict[str, Any]): Mensaje de Slack.
            
        Returns:
            str: Texto extraído del mensaje.
        """
        pass
