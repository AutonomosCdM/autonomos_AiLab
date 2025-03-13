"""
Implementación de historial de conversación.
"""
import logging
import time
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class ConversationHistory:
    """
    Clase para gestionar el historial de una conversación.
    """
    
    def __init__(self, conversation_id: str):
        """
        Inicializa el historial de conversación.
        
        Args:
            conversation_id (str): ID único de la conversación.
        """
        self.conversation_id = conversation_id
        self.messages = []
        self.created_at = time.time()
        self.last_updated = time.time()
        
        logger.debug(f"ConversationHistory inicializado para conversación {conversation_id}")
    
    def add_message(self, role: str, content: str) -> None:
        """
        Añade un mensaje al historial.
        
        Args:
            role (str): Rol del mensaje ('user' o 'assistant').
            content (str): Contenido del mensaje.
        """
        if role not in ['user', 'assistant', 'system']:
            logger.warning(f"Rol de mensaje no válido: {role}, se usará 'user'")
            role = 'user'
        
        message = {
            "role": role,
            "content": content,
            "timestamp": time.time()
        }
        
        self.messages.append(message)
        self.last_updated = time.time()
        
        logger.debug(f"Mensaje añadido a conversación {self.conversation_id}, "
                    f"total: {len(self.messages)}")
    
    def get_messages(self, max_messages: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Obtiene los mensajes del historial.
        
        Args:
            max_messages (Optional[int]): Número máximo de mensajes a devolver.
                Si es None, devuelve todos los mensajes.
                
        Returns:
            List[Dict[str, Any]]: Lista de mensajes.
        """
        if max_messages is None:
            return self.messages
        
        return self.messages[-max_messages:]
    
    def get_formatted_messages(self, include_timestamps: bool = False) -> List[Dict[str, str]]:
        """
        Obtiene los mensajes formateados para enviar a la API de IA.
        
        Args:
            include_timestamps (bool): Si se deben incluir los timestamps.
            
        Returns:
            List[Dict[str, str]]: Lista de mensajes formateados.
        """
        if include_timestamps:
            return self.messages
        
        # Formatear para API (solo role y content)
        return [{"role": msg["role"], "content": msg["content"]} for msg in self.messages]
    
    def get_last_message(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene el último mensaje del historial.
        
        Returns:
            Optional[Dict[str, Any]]: Último mensaje, o None si no hay mensajes.
        """
        if not self.messages:
            return None
        
        return self.messages[-1]
    
    def clear(self) -> None:
        """
        Limpia el historial de mensajes.
        """
        self.messages = []
        self.last_updated = time.time()
        logger.debug(f"Historial de conversación {self.conversation_id} limpiado")
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Obtiene un resumen del historial.
        
        Returns:
            Dict[str, Any]: Resumen del historial.
        """
        return {
            "conversation_id": self.conversation_id,
            "message_count": len(self.messages),
            "created_at": self.created_at,
            "last_updated": self.last_updated,
            "duration": self.last_updated - self.created_at,
            "user_messages": sum(1 for msg in self.messages if msg["role"] == "user"),
            "assistant_messages": sum(1 for msg in self.messages if msg["role"] == "assistant"),
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el historial a un diccionario para serialización.
        
        Returns:
            Dict[str, Any]: Diccionario con los datos del historial.
        """
        return {
            "conversation_id": self.conversation_id,
            "messages": self.messages,
            "created_at": self.created_at,
            "last_updated": self.last_updated,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationHistory':
        """
        Crea un historial a partir de un diccionario.
        
        Args:
            data (Dict[str, Any]): Diccionario con los datos del historial.
            
        Returns:
            ConversationHistory: Historial creado.
        """
        history = cls(data["conversation_id"])
        history.messages = data["messages"]
        history.created_at = data["created_at"]
        history.last_updated = data["last_updated"]
        
        return history


class ConversationHistoryManager:
    """
    Gestor de historiales de conversación.
    """
    
    def __init__(self, max_conversations: int = 100):
        """
        Inicializa el gestor de historiales.
        
        Args:
            max_conversations (int): Número máximo de conversaciones a mantener.
        """
        self.max_conversations = max_conversations
        self.histories = {}  # Diccionario de historiales por ID de conversación
        
        logger.debug(f"ConversationHistoryManager inicializado con max_conversations={max_conversations}")
    
    def get_history(self, conversation_id: str) -> ConversationHistory:
        """
        Obtiene el historial de una conversación.
        
        Args:
            conversation_id (str): ID de la conversación.
            
        Returns:
            ConversationHistory: Historial de la conversación.
        """
        if conversation_id not in self.histories:
            self.histories[conversation_id] = ConversationHistory(conversation_id)
            
            # Limitar número de conversaciones
            if len(self.histories) > self.max_conversations:
                self._cleanup_oldest()
        
        return self.histories[conversation_id]
    
    def add_message(self, conversation_id: str, role: str, content: str) -> None:
        """
        Añade un mensaje al historial de una conversación.
        
        Args:
            conversation_id (str): ID de la conversación.
            role (str): Rol del mensaje ('user' o 'assistant').
            content (str): Contenido del mensaje.
        """
        history = self.get_history(conversation_id)
        history.add_message(role, content)
    
    def clear_history(self, conversation_id: str) -> None:
        """
        Limpia el historial de una conversación.
        
        Args:
            conversation_id (str): ID de la conversación.
        """
        if conversation_id in self.histories:
            self.histories[conversation_id].clear()
            logger.debug(f"Historial de conversación {conversation_id} limpiado")
    
    def delete_history(self, conversation_id: str) -> None:
        """
        Elimina el historial de una conversación.
        
        Args:
            conversation_id (str): ID de la conversación.
        """
        if conversation_id in self.histories:
            del self.histories[conversation_id]
            logger.debug(f"Historial de conversación {conversation_id} eliminado")
    
    def _cleanup_oldest(self) -> None:
        """
        Elimina la conversación más antigua.
        """
        if not self.histories:
            return
        
        # Encontrar la conversación más antigua
        oldest_id = min(
            self.histories.keys(),
            key=lambda k: self.histories[k].last_updated
        )
        
        # Eliminar la conversación más antigua
        del self.histories[oldest_id]
        logger.debug(f"Historial de conversación más antiguo ({oldest_id}) eliminado")
    
    def get_all_conversation_ids(self) -> List[str]:
        """
        Obtiene todos los IDs de conversación.
        
        Returns:
            List[str]: Lista de IDs de conversación.
        """
        return list(self.histories.keys())
    
    def get_conversation_summaries(self) -> List[Dict[str, Any]]:
        """
        Obtiene resúmenes de todas las conversaciones.
        
        Returns:
            List[Dict[str, Any]]: Lista de resúmenes.
        """
        return [
            history.get_summary()
            for history in self.histories.values()
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el gestor a un diccionario para serialización.
        
        Returns:
            Dict[str, Any]: Diccionario con los datos del gestor.
        """
        return {
            "max_conversations": self.max_conversations,
            "histories": {
                conv_id: history.to_dict()
                for conv_id, history in self.histories.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationHistoryManager':
        """
        Crea un gestor a partir de un diccionario.
        
        Args:
            data (Dict[str, Any]): Diccionario con los datos del gestor.
            
        Returns:
            ConversationHistoryManager: Gestor creado.
        """
        manager = cls(data["max_conversations"])
        
        for conv_id, history_data in data["histories"].items():
            manager.histories[conv_id] = ConversationHistory.from_dict(history_data)
        
        return manager
