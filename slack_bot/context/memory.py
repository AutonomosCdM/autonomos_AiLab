"""
Implementación de almacenamiento en memoria modular y reutilizable.
"""
import logging
import time
import json
import abc
from typing import Dict, List, Any, Optional, Type, Callable

logger = logging.getLogger(__name__)

class MemoryStore(abc.ABC):
    """
    Clase base abstracta para almacenamiento de memoria
    Define la interfaz para diferentes estrategias de almacenamiento de memoria
    """
    @abc.abstractmethod
    def save(self, key: str, value: Any):
        """Guarda un valor con una clave específica"""
        pass

    @abc.abstractmethod
    def load(self, key: str) -> Any:
        """Carga un valor por su clave"""
        pass

    @abc.abstractmethod
    def exists(self, key: str) -> bool:
        """Verifica si una clave existe"""
        pass

    @abc.abstractmethod
    def get_all_keys(self) -> List[str]:
        """Obtiene todas las claves almacenadas"""
        pass

    @abc.abstractmethod
    def clear(self):
        """Limpia todos los datos almacenados"""
        pass

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
        memory_class: Optional[Type] = None, 
        config_handler: Optional[Callable] = None
    ):
        """
        Registra una nueva estrategia de memoria
        
        Args:
            name: Nombre único de la estrategia
            memory_class: Clase de memoria (opcional)
            config_handler: Función opcional para manejar configuraciones personalizadas
        """
        cls._strategies[name] = {
            'class': memory_class,
            'config_handler': config_handler or (lambda **kwargs: {})
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
MemoryStrategyRegistry.register_strategy('buffer')
MemoryStrategyRegistry.register_strategy('summary')
MemoryStrategyRegistry.register_strategy('summary_buffer')

class PersistentMemoryStore(MemoryStore):
    """
    Almacenamiento persistente para memoria
    """
    def __init__(self, file_path: str = 'memory_store.json'):
        """
        Inicializa el almacenamiento persistente
        
        Args:
            file_path: Ruta del archivo para almacenar la memoria
        """
        self.file_path = file_path
        self._data: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        """
        Carga los datos desde el archivo
        
        Returns:
            Diccionario de datos de memoria
        """
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save(self):
        """
        Guarda los datos en el archivo
        """
        with open(self.file_path, 'w') as f:
            json.dump(self._data, f, indent=2)

    def save(self, key: str, value: Any):
        """
        Guarda un valor con una clave específica
        
        Args:
            key: Clave para almacenar el valor
            value: Valor a almacenar
        """
        self._data[key] = value
        self._save()

    def load(self, key: str) -> Any:
        """
        Carga un valor por su clave
        
        Args:
            key: Clave para cargar el valor
        
        Returns:
            Valor almacenado
        """
        return self._data.get(key)

    def exists(self, key: str) -> bool:
        """
        Verifica si una clave existe
        
        Args:
            key: Clave a verificar
        
        Returns:
            True si la clave existe, False en caso contrario
        """
        return key in self._data

    def get_all_keys(self) -> List[str]:
        """
        Obtiene todas las claves almacenadas
        
        Returns:
            Lista de claves
        """
        return list(self._data.keys())

    def clear(self):
        """
        Limpia todos los datos almacenados
        """
        self._data.clear()
        self._save()

def messages_from_dict(message_dicts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convierte una lista de diccionarios de mensajes a un formato estándar
    
    Args:
        message_dicts: Lista de diccionarios de mensajes
    
    Returns:
        Lista de mensajes normalizados
    """
    return [
        {
            'type': msg.get('type', 'unknown'),
            'content': msg.get('content', ''),
            'timestamp': msg.get('timestamp', time.time())
        } for msg in message_dicts
    ]

class BaseMemoryManager:
    """
    Gestor de memoria base con funcionalidades genéricas
    Diseñado para ser extensible y reutilizable entre diferentes personalidades
    """
    
    def __init__(
        self, 
        memory_type: str = 'summary_buffer',
        max_token_limit: int = 1000,
        persistent_store: Optional[PersistentMemoryStore] = None,
        **strategy_kwargs
    ):
        """
        Inicializa el gestor de memoria con estrategia configurable
        
        Args:
            memory_type: Tipo de estrategia de memoria
            max_token_limit: Límite máximo de tokens
            persistent_store: Almacenamiento persistente opcional
            strategy_kwargs: Argumentos adicionales para la estrategia de memoria
        """
        self.memory_type = memory_type
        self.max_token_limit = max_token_limit
        
        # Usar almacenamiento persistente predeterminado si no se proporciona
        self.persistent_store = persistent_store or PersistentMemoryStore('memory_store.json')
        
        # Obtener estrategia de memoria
        strategy = MemoryStrategyRegistry.get_strategy(memory_type)
        
        # Configurar parámetros de memoria
        self.memory_config = strategy['config_handler'](
            max_token_limit=self.max_token_limit,
            **strategy_kwargs
        )
        
        # Inicializar almacenamiento de mensajes
        self._messages: List[Dict[str, Any]] = []

    def add_user_message(self, message: str):
        """
        Añade un mensaje de usuario a la memoria
        
        Args:
            message: Mensaje de usuario
        """
        try:
            message_entry = {
                "type": "human",
                "content": message,
                "timestamp": time.time()
            }
            self._messages.append(message_entry)
            
            # Almacenar en memoria persistente
            message_key = f"user_message_{int(time.time())}"
            self.persistent_store.save(message_key, message_entry)
        except Exception as e:
            logger.error(f"Error añadiendo mensaje de usuario: {e}", exc_info=True)

    def add_ai_message(self, message: str):
        """
        Añade un mensaje de IA a la memoria
        
        Args:
            message: Mensaje de IA
        """
        try:
            message_entry = {
                "type": "ai",
                "content": message,
                "timestamp": time.time()
            }
            self._messages.append(message_entry)
            
            # Almacenar en memoria persistente
            message_key = f"ai_message_{int(time.time())}"
            self.persistent_store.save(message_key, message_entry)
        except Exception as e:
            logger.error(f"Error añadiendo mensaje de IA: {e}", exc_info=True)

    def get_memory_context(self) -> List[Dict[str, Any]]:
        """
        Recupera el contexto actual de la memoria
        
        Returns:
            Lista de diccionarios de mensajes
        """
        try:
            return self._messages
        except Exception as e:
            logger.error(f"Error recuperando contexto de memoria: {e}", exc_info=True)
            return []

    def clear_memory(self):
        """
        Limpia toda la memoria
        """
        try:
            self._messages.clear()
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
            return {"history": "\n".join([f"{msg['type']}: {msg['content']}" for msg in self._messages])}
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
                if msg['type'] == 'human':
                    self.add_user_message(msg['content'])
                elif msg['type'] == 'ai':
                    self.add_ai_message(msg['content'])
            
            return True
        except Exception as e:
            logger.error(f"Error importando memoria: {e}", exc_info=True)
            return False

# Alias para mantener la compatibilidad con implementaciones anteriores
LuciusMemoryManager = BaseMemoryManager
