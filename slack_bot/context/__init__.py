"""
Paquete de gestión de contexto para el bot de Slack.

Este módulo gestiona el historial de conversaciones, memoria y estado del contexto.
"""

# Importar clases de gestión de contexto
from .manager import ContextManager
from .memory import MemoryStore, PersistentMemoryStore, BaseMemoryManager
from .history import ConversationHistory, ConversationHistoryManager

# Lista de componentes de contexto disponibles
AVAILABLE_CONTEXT_COMPONENTS = [
    "context_manager",
    "memory_store",
    "conversation_history"
]

# Versión del paquete de contexto
__version__ = "0.1.0"

# Exportar clases principales
__all__ = [
    'ContextManager',
    'MemoryStore',
    'PersistentMemoryStore',
    'BaseMemoryManager',
    'ConversationHistory',
    'ConversationHistoryManager'
]
