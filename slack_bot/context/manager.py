"""
Gestor de contexto para mantener historial de conversaciones.
"""
import logging
import time
from typing import Dict, List, Any, Optional, Tuple

from slack_bot.config import settings

logger = logging.getLogger(__name__)


class ContextManager:
    """
    Gestor de contexto que mantiene el historial de conversaciones.
    """
    
    def __init__(self, max_messages: int = None, expiry_minutes: int = None):
        """
        Inicializa el gestor de contexto.
        
        Args:
            max_messages (int, optional): Número máximo de mensajes a mantener por conversación.
                Si es None, se usa el configurado en settings.
            expiry_minutes (int, optional): Tiempo en minutos tras el cual expira una conversación.
                Si es None, se usa el configurado en settings.
        """
        self.max_messages = max_messages or settings.MAX_CONTEXT_MESSAGES
        self.expiry_minutes = expiry_minutes or settings.CONTEXT_EXPIRY_MINUTES
        self.conversations = {}  # Diccionario de conversaciones por ID de conversación
        
        logger.debug(f"ContextManager inicializado con max_messages={self.max_messages}, "
                    f"expiry_minutes={self.expiry_minutes}")
    
    def _get_conversation_id(self, user_id: str, channel_id: str) -> str:
        """
        Genera un ID único para una conversación.
        
        Args:
            user_id (str): ID del usuario.
            channel_id (str): ID del canal.
            
        Returns:
            str: ID único de la conversación.
        """
        return f"{channel_id}:{user_id}"
    
    def add_message(self, user_id: str, channel_id: str, text: str, is_bot: bool = False) -> None:
        """
        Añade un mensaje al contexto de una conversación.
        
        Args:
            user_id (str): ID del usuario.
            channel_id (str): ID del canal.
            text (str): Texto del mensaje.
            is_bot (bool, optional): Si el mensaje es del bot. Por defecto, False.
        """
        conversation_id = self._get_conversation_id(user_id, channel_id)
        
        # Inicializar conversación si no existe
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = {
                "messages": [],
                "last_updated": time.time()
            }
        
        # Añadir mensaje
        self.conversations[conversation_id]["messages"].append({
            "role": "assistant" if is_bot else "user",
            "content": text,
            "timestamp": time.time()
        })
        
        # Actualizar timestamp
        self.conversations[conversation_id]["last_updated"] = time.time()
        
        # Limitar número de mensajes
        if len(self.conversations[conversation_id]["messages"]) > self.max_messages:
            self.conversations[conversation_id]["messages"].pop(0)
        
        logger.debug(f"Mensaje añadido a conversación {conversation_id}, "
                    f"total: {len(self.conversations[conversation_id]['messages'])}")
    
    def get_conversation_history(self, user_id: str, channel_id: str) -> List[Dict[str, Any]]:
        """
        Obtiene el historial de una conversación.
        
        Args:
            user_id (str): ID del usuario.
            channel_id (str): ID del canal.
            
        Returns:
            List[Dict[str, Any]]: Lista de mensajes de la conversación.
        """
        conversation_id = self._get_conversation_id(user_id, channel_id)
        
        # Verificar si la conversación existe
        if conversation_id not in self.conversations:
            logger.debug(f"Conversación {conversation_id} no encontrada")
            return []
        
        # Verificar si la conversación ha expirado
        if self._has_expired(conversation_id):
            logger.debug(f"Conversación {conversation_id} ha expirado")
            self._cleanup_conversation(conversation_id)
            return []
        
        # Actualizar timestamp
        self.conversations[conversation_id]["last_updated"] = time.time()
        
        return self.conversations[conversation_id]["messages"]
    
    def get_formatted_history(self, user_id: str, channel_id: str) -> Tuple[List[Dict[str, str]], str]:
        """
        Obtiene el historial formateado para enviar a la API de IA.
        
        Args:
            user_id (str): ID del usuario.
            channel_id (str): ID del canal.
            
        Returns:
            Tuple[List[Dict[str, str]], str]: Tupla con la lista de mensajes formateados
                para la API y un string con el historial formateado para debugging.
        """
        history = self.get_conversation_history(user_id, channel_id)
        
        # Formatear para API (solo role y content)
        api_messages = [{"role": msg["role"], "content": msg["content"]} for msg in history]
        
        # Formatear para debugging
        debug_history = "\n".join([
            f"[{msg['role']}]: {msg['content']}"
            for msg in history
        ])
        
        return api_messages, debug_history
    
    def clear_conversation(self, user_id: str, channel_id: str) -> None:
        """
        Limpia el historial de una conversación.
        
        Args:
            user_id (str): ID del usuario.
            channel_id (str): ID del canal.
        """
        conversation_id = self._get_conversation_id(user_id, channel_id)
        self._cleanup_conversation(conversation_id)
        logger.debug(f"Conversación {conversation_id} limpiada")
    
    def _cleanup_conversation(self, conversation_id: str) -> None:
        """
        Elimina una conversación del contexto.
        
        Args:
            conversation_id (str): ID de la conversación.
        """
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
    
    def _has_expired(self, conversation_id: str) -> bool:
        """
        Verifica si una conversación ha expirado.
        
        Args:
            conversation_id (str): ID de la conversación.
            
        Returns:
            bool: True si la conversación ha expirado, False en caso contrario.
        """
        if conversation_id not in self.conversations:
            return True
        
        last_updated = self.conversations[conversation_id]["last_updated"]
        expiry_time = last_updated + (self.expiry_minutes * 60)
        
        return time.time() > expiry_time
    
    def cleanup_expired(self) -> int:
        """
        Limpia todas las conversaciones expiradas.
        
        Returns:
            int: Número de conversaciones limpiadas.
        """
        expired_ids = [
            conv_id for conv_id in self.conversations
            if self._has_expired(conv_id)
        ]
        
        for conv_id in expired_ids:
            self._cleanup_conversation(conv_id)
        
        logger.debug(f"Limpiadas {len(expired_ids)} conversaciones expiradas")
        return len(expired_ids)
