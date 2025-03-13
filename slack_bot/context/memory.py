"""
Implementación de almacenamiento en memoria modular y reutilizable.
"""
import logging
import time
import json
from typing import Dict, List, Any, Optional, Type, Callable

from langchain.memory import (
    ConversationBufferMemory, 
    ConversationSummaryMemory, 
    ConversationSummaryBufferMemory,
    EntityMemory
)
from langchain.chat_models import ChatOpenAI
from langchain.memory.chat_memory import BaseChatMemory
from langchain.schema import messages_from_dict, messages_to_dict

logger = logging.getLogger(__name__)

class MemoryStrategyRegistry:
    """
    Registro centralizado de estrategias de memoria
    Permite registrar, recuperar y gestionar diferentes estrategias de memoria
    """
    _strategies: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def register_strategy(
        cls, 
        name: str, 
        memory_class: Type[BaseChatMemory], 
        config_handler: Optional[Callable] = None
    ):
        """
        Registra una nueva estrategia de memoria
        
        Args:
            name: Nombre único de la estrategia
            memory_class: Clase de memoria de LangChain
            config_handler: Función opcional para manejar configuraciones personalizadas
        """
        cls._strategies[name] = {
            'class': memory_class,
            'config_handler': config_handler or (lambda llm, **kwargs: {})
        }

    @classmethod
    def get_strategy(cls, name: str) -> Dict[str, Any]:
        """
        Obtiene una estrategia de memoria registrada
        
        Args:
            name: Nombre de la estrategia
        
        Returns:
            Diccionario con la clase de memoria y manejador de configuración
        """
        if name not in cls._strategies:
            raise ValueError(f"Estrategia de memoria no registrada: {name}")
        return cls._strategies[name]

# Registrar estrategias de memoria predeterminadas
MemoryStrategyRegistry.register_strategy(
    'buffer', 
    ConversationBufferMemory,
    lambda llm, max_token_limit=1000, **kwargs: {
        'return_messages': True,
        'max_token_limit': max_token_limit
    }
)

MemoryStrategyRegistry.register_strategy(
    'summary', 
    ConversationSummaryMemory,
    lambda llm, max_token_limit=1000, **kwargs: {
        'llm': llm,
        'return_messages': True,
        'max_token_limit': max_token_limit
    }
)

MemoryStrategyRegistry.register_strategy(
    'summary_buffer', 
    ConversationSummaryBufferMemory,
    lambda llm, max_token_limit=1000, **kwargs: {
        'llm': llm,
        'max_token_limit': max_token_limit,
        'return_messages': True
    }
)

MemoryStrategyRegistry.register_strategy(
    'entity', 
    EntityMemory,
    lambda llm, **kwargs: {
        'llm': llm,
        'return_messages': True
    }
)

class BaseMemoryManager:
    """
    Gestor de memoria base con funcionalidades genéricas
    Diseñado para ser extensible y reutilizable entre diferentes personalidades
    """
    
    def __init__(
        self, 
        llm: Optional[ChatOpenAI] = None, 
        memory_type: str = 'summary_buffer',
        max_token_limit: int = 1000,
        persistent_store: Optional['PersistentMemoryStore'] = None,
        **strategy_kwargs
    ):
        """
        Inicializa el gestor de memoria con estrategia configurable
        
        Args:
            llm: Modelo de lenguaje para generación de resúmenes
            memory_type: Tipo de estrategia de memoria
            max_token_limit: Límite máximo de tokens
            persistent_store: Almacenamiento persistente opcional
            strategy_kwargs: Argumentos adicionales para la estrategia de memoria
        """
        self.llm = llm or ChatOpenAI(temperature=0)
        self.memory_type = memory_type
        self.max_token_limit = max_token_limit
        
        # Usar almacenamiento persistente predeterminado si no se proporciona
        from .memory import PersistentMemoryStore  # Importación local para evitar circularidad
        self.persistent_store = persistent_store or PersistentMemoryStore('memory_store.json')
        
        # Obtener estrategia de memoria
        strategy = MemoryStrategyRegistry.get_strategy(memory_type)
        
        # Configurar parámetros de memoria
        memory_config = strategy['config_handler'](
            self.llm, 
            max_token_limit=self.max_token_limit,
            **strategy_kwargs
        )
        
        # Crear instancia de memoria
        self.memory = strategy['class'](**memory_config)

    def add_user_message(self, message: str):
        """
        Añade un mensaje de usuario a la memoria
        
        Args:
            message: Mensaje de usuario
        """
        try:
            self.memory.chat_memory.add_user_message(message)
            
            # Almacenar en memoria persistente
            message_key = f"user_message_{int(time.time())}"
            self.persistent_store.save(message_key, {
                "type": "user",
                "content": message,
                "timestamp": time.time()
            })
        except Exception as e:
            logger.error(f"Error añadiendo mensaje de usuario: {e}", exc_info=True)

    def add_ai_message(self, message: str):
        """
        Añade un mensaje de IA a la memoria
        
        Args:
            message: Mensaje de IA
        """
        try:
            self.memory.chat_memory.add_ai_message(message)
            
            # Almacenar en memoria persistente
            message_key = f"ai_message_{int(time.time())}"
            self.persistent_store.save(message_key, {
                "type": "ai",
                "content": message,
                "timestamp": time.time()
            })
        except Exception as e:
            logger.error(f"Error añadiendo mensaje de IA: {e}", exc_info=True)

    def get_memory_context(self) -> List[Dict[str, Any]]:
        """
        Recupera el contexto actual de la memoria
        
        Returns:
            Lista de diccionarios de mensajes
        """
        try:
            return messages_to_dict(self.memory.chat_memory.messages)
        except Exception as e:
            logger.error(f"Error recuperando contexto de memoria: {e}", exc_info=True)
            return []

    def clear_memory(self):
        """
        Limpia toda la memoria
        """
        try:
            self.memory.chat_memory.clear()
            self.persistent_store.clear()
        except Exception as e:
            logger.error(f"Error limpiando memoria: {e}", exc_info=True)

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Carga variables de memoria para una entrada dada
        
        Args:
            inputs: Diccionario de entrada
        
        Returns:
            Variables de memoria
        """
        try:
            return self.memory.load_memory_variables(inputs)
        except Exception as e:
            logger.error(f"Error cargando variables de memoria: {e}", exc_info=True)
            return {}

    def export_memory(self, file_path: str) -> bool:
        """
        Exporta el contexto completo de la memoria a un archivo
        
        Args:
            file_path: Ruta para exportar la memoria
        
        Returns:
            True si la exportación fue exitosa, False en caso contrario
        """
        try:
            memory_context = self.get_memory_context()
            with open(file_path, 'w') as f:
                json.dump(memory_context, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error exportando memoria: {e}", exc_info=True)
            return False

    def import_memory(self, file_path: str) -> bool:
        """
        Importa el contexto de memoria desde un archivo
        
        Args:
            file_path: Ruta para importar la memoria
        
        Returns:
            True si la importación fue exitosa, False en caso contrario
        """
        try:
            with open(file_path, 'r') as f:
                memory_data = json.load(f)
            
            # Limpiar memoria existente
            self.clear_memory()
            
            # Reconstruir mensajes
            messages = messages_from_dict(memory_data)
            
            # Añadir mensajes de vuelta a la memoria
            for msg in messages:
                if msg.type == 'human':
                    self.add_user_message(msg.content)
                elif msg.type == 'ai':
                    self.add_ai_message(msg.content)
            
            return True
        except Exception as e:
            logger.error(f"Error importando memoria: {e}", exc_info=True)
            return False

# Alias para mantener la compatibilidad con implementaciones anteriores
LuciusMemoryManager = BaseMemoryManager
