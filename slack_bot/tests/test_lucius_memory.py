import pytest
import os
from slack_bot.context.memory import BaseMemoryManager, MemoryStrategyRegistry
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
    from langchain.memory import ConversationBufferMemory

    # Register a custom strategy
    MemoryStrategyRegistry.register_strategy(
        'custom', 
        ConversationBufferMemory,
        lambda llm, custom_param=None, **kwargs: {
            'return_messages': True,
            'extra_config': custom_param
        }
    )

    # Create memory manager with custom strategy
    memory_manager = BaseMemoryManager(
        llm=ChatOpenAI(temperature=0),
        memory_type='custom',
        custom_param='test_value'
    )

    assert memory_manager.memory_type == 'custom'

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
    
    # Clear memory and import
    memory_manager.clear_memory()
    assert memory_manager.import_memory(export_file)
    
    # Check imported memory
    context = memory_manager.get_memory_context()
    assert len(context) == 2
    
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
    memory_manager = BaseMemoryManager()
    
    # Add a message
    memory_manager.add_user_message("Persistent memory test")
    
    # Check persistent store
    assert memory_manager.persistent_store.exists(
        memory_manager.persistent_store.get_all_keys()[0]
    )

def test_invalid_memory_strategy():
    """Test handling of invalid memory strategy"""
    with pytest.raises(ValueError):
        BaseMemoryManager(memory_type='non_existent_strategy')
