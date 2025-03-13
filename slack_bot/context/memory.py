"""
Implementación de almacenamiento en memoria para el contexto con soporte de LangChain.
"""
import logging
import time
import json
from typing import Dict, List, Any, Optional, Tuple

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

# Existing MemoryStore and PersistentMemoryStore classes remain unchanged

class LuciusMemoryManager:
    """
    Advanced memory management for Lucius personality
    Supports multiple memory strategies with flexible configuration
    Integrates with existing MemoryStore for enhanced persistence and tracking
    """
    
    def __init__(
        self, 
        llm: Optional[ChatOpenAI] = None, 
        max_token_limit: int = 1000,
        memory_type: str = 'summary_buffer',
        persistent_store: Optional[PersistentMemoryStore] = None
    ):
        """
        Initialize memory manager with configurable memory strategy
        
        Args:
            llm: Language model for summary generation
            max_token_limit: Maximum tokens to retain in memory
            memory_type: Type of memory strategy
            persistent_store: Optional persistent memory store for additional tracking
        """
        self.llm = llm or ChatOpenAI(temperature=0)
        self.max_token_limit = max_token_limit
        self.memory_type = memory_type
        self.persistent_store = persistent_store or PersistentMemoryStore('memory_store.json')
        self.memory = self._create_memory()

    def _create_memory(self) -> BaseChatMemory:
        """
        Create memory based on configured strategy
        
        Returns:
            Configured memory instance
        """
        try:
            if self.memory_type == 'buffer':
                return ConversationBufferMemory(
                    return_messages=True,
                    max_token_limit=self.max_token_limit
                )
            
            elif self.memory_type == 'summary':
                return ConversationSummaryMemory(
                    llm=self.llm,
                    return_messages=True,
                    max_token_limit=self.max_token_limit
                )
            
            elif self.memory_type == 'summary_buffer':
                return ConversationSummaryBufferMemory(
                    llm=self.llm,
                    max_token_limit=self.max_token_limit,
                    return_messages=True
                )
            
            elif self.memory_type == 'entity':
                return EntityMemory(
                    llm=self.llm,
                    return_messages=True
                )
            
            else:
                raise ValueError(f"Unsupported memory type: {self.memory_type}")
        except Exception as e:
            logger.error(f"Error creating memory: {e}", exc_info=True)
            raise

    def add_user_message(self, message: str):
        """
        Add a user message to memory and persistent store
        
        Args:
            message: User message to add
        """
        try:
            # Add to LangChain memory
            self.memory.chat_memory.add_user_message(message)
            
            # Add to persistent store with timestamp
            message_key = f"user_message_{int(time.time())}"
            self.persistent_store.save(message_key, {
                "type": "user",
                "content": message,
                "timestamp": time.time()
            })
        except Exception as e:
            logger.error(f"Error adding user message: {e}", exc_info=True)

    def add_ai_message(self, message: str):
        """
        Add an AI message to memory and persistent store
        
        Args:
            message: AI message to add
        """
        try:
            # Add to LangChain memory
            self.memory.chat_memory.add_ai_message(message)
            
            # Add to persistent store with timestamp
            message_key = f"ai_message_{int(time.time())}"
            self.persistent_store.save(message_key, {
                "type": "ai",
                "content": message,
                "timestamp": time.time()
            })
        except Exception as e:
            logger.error(f"Error adding AI message: {e}", exc_info=True)

    def get_memory_context(self) -> List[Dict[str, Any]]:
        """
        Retrieve current memory context
        
        Returns:
            List of message dictionaries
        """
        try:
            # Convert LangChain messages to dictionary format
            return messages_to_dict(self.memory.chat_memory.messages)
        except Exception as e:
            logger.error(f"Error retrieving memory context: {e}", exc_info=True)
            return []

    def clear_memory(self):
        """
        Clear all memory in LangChain and persistent store
        """
        try:
            # Clear LangChain memory
            self.memory.chat_memory.clear()
            
            # Clear persistent store
            self.persistent_store.clear()
        except Exception as e:
            logger.error(f"Error clearing memory: {e}", exc_info=True)

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Load memory variables for a given input
        
        Args:
            inputs: Input dictionary
        
        Returns:
            Memory variables
        """
        try:
            return self.memory.load_memory_variables(inputs)
        except Exception as e:
            logger.error(f"Error loading memory variables: {e}", exc_info=True)
            return {}

    def export_memory(self, file_path: str) -> bool:
        """
        Export entire memory context to a file
        
        Args:
            file_path: Path to export memory
        
        Returns:
            True if export successful, False otherwise
        """
        try:
            memory_context = self.get_memory_context()
            with open(file_path, 'w') as f:
                json.dump(memory_context, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error exporting memory: {e}", exc_info=True)
            return False

    def import_memory(self, file_path: str) -> bool:
        """
        Import memory context from a file
        
        Args:
            file_path: Path to import memory from
        
        Returns:
            True if import successful, False otherwise
        """
        try:
            with open(file_path, 'r') as f:
                memory_data = json.load(f)
            
            # Clear existing memory
            self.clear_memory()
            
            # Reconstruct messages
            messages = messages_from_dict(memory_data)
            
            # Add messages back to memory
            for msg in messages:
                if msg.type == 'human':
                    self.add_user_message(msg.content)
                elif msg.type == 'ai':
                    self.add_ai_message(msg.content)
            
            return True
        except Exception as e:
            logger.error(f"Error importing memory: {e}", exc_info=True)
            return False
