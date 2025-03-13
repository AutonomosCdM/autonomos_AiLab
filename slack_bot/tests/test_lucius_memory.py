import pytest
import os
import json
from slack_bot.context.memory import (
    BaseMemoryManager, 
    MemoryStrategyRegistry, 
    PersistentMemoryStore
)
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI

def test_memory_strategy_registration():
    """Test memory strategy registration"""
    # Verify existing strategies
    strategies = ['buffer', 'summary', 'summary_buffer', 'entity']
    for strategy in strategies:
        assert strategy in MemoryStrategyRegistry._strategies

def test_memory_manager_creation():
    """Test creation of memory manager with different strategies"""
    strategies = ['buffer', 'summary', 'summary_buffer', 'entity']
    
    for strategy in strategies:
        memory_manager = BaseMemoryManager(
            llm=ChatOpenAI(temperature=0),
            memory_type=strategy,
            max_token_limit=500
        )
        
        assert memory_manager is not None
        assert memory_manager.memory_type == strategy

def test_custom_memory_strategy():
    """Test registering and using a custom memory strategy"""
    # Register a custom strategy
    MemoryStrategyRegistry.register_strategy(
        'custom_test', 
        ConversationBufferMemory,
        lambda llm, custom_param=None, **kwargs: {
            'return_messages': True,
            'extra_config': custom_param
        }
    )

    # Create memory manager with custom strategy
    memory_manager = BaseMemoryManager(
        llm=ChatOpenAI(temperature=0),
        memory_type='custom_test',
        custom_param='test_value'
    )

    assert memory_manager.memory_type == 'custom_test'

def test_memory_message_handling():
    """Test adding and retrieving messages"""
    memory_manager = BaseMemoryManager()
    
    # Add messages
    memory_manager.add_user_message("Hello, how are you?")
    memory_manager.add_ai_message("I'm doing great, how can I help you?")
    
    # Check memory context
    context = memory_manager.get_memory_context()
    assert len(context) == 2
    assert context[0]['type'] == 'human'
    assert context[1]['type'] == 'ai'

def test_memory_export_import():
    """Test memory export and import functionality"""
    memory_manager = BaseMemoryManager()
    
    # Add some messages
    memory_manager.add_user_message("Test user message")
    memory_manager.add_ai_message("Test AI response")
    
    # Export memory
    export_file = 'test_memory_export.json'
    assert memory_manager.export_memory(export_file)
    
    # Verify export file contents
    with open(export_file, 'r') as f:
        exported_data = json.load(f)
    
    assert len(exported_data) == 2
    assert exported_data[0]['type'] == 'human'
    assert exported_data[1]['type'] == 'ai'
    
    # Clear memory and import
    memory_manager.clear_memory()
    assert memory_manager.import_memory(export_file)
    
    # Check imported memory
    context = memory_manager.get_memory_context()
    assert len(context) == 2
    assert context[0]['type'] == 'human'
    assert context[1]['type'] == 'ai'
    
    # Clean up export file
    os.remove(export_file)

def test_memory_clearing():
    """Test memory clearing functionality"""
    memory_manager = BaseMemoryManager()
    
    memory_manager.add_user_message("Test message")
    memory_manager.clear_memory()
    
    context = memory_manager.get_memory_context()
    assert len(context) == 0

def test_memory_persistence():
    """Test that persistent store is working"""
    # Use a unique file for this test to avoid conflicts
    persistent_store = PersistentMemoryStore('test_memory_persistence.json')
    memory_manager = BaseMemoryManager(persistent_store=persistent_store)
    
    # Add a message
    memory_manager.add_user_message("Persistent memory test")
    
    # Check persistent store
    keys = persistent_store.get_all_keys()
    assert len(keys) > 0
    assert persistent_store.exists(keys[0])
    
    # Verify stored message
    stored_data = persistent_store.load(keys[0])
    assert stored_data['type'] == 'user'
    assert stored_data['content'] == "Persistent memory test"

def test_invalid_memory_strategy():
    """Test handling of invalid memory strategy"""
    with pytest.raises(ValueError, match="Estrategia de memoria no registrada"):
        BaseMemoryManager(memory_type='non_existent_strategy')

def test_memory_strategy_config_handling():
    """Test memory strategy configuration handling"""
    # Create memory manager with specific configuration
    memory_manager = BaseMemoryManager(
        llm=ChatOpenAI(temperature=0),
        memory_type='buffer',
        max_token_limit=250  # Custom token limit
    )
    
    # Verify configuration was applied
    assert memory_manager.max_token_limit == 250

def test_memory_load_variables():
    """Test loading memory variables"""
    memory_manager = BaseMemoryManager()
    
    # Add some messages
    memory_manager.add_user_message("What's the weather like?")
    memory_manager.add_ai_message("I'm sorry, I don't have real-time weather information.")
    
    # Load memory variables
    memory_vars = memory_manager.load_memory_variables({})
    
    # Verify memory variables are returned
    assert isinstance(memory_vars, dict)
