import pytest
import os
from slack_bot.config.personalities.lucius import create_lucius_memory_manager, PERSONALITY_CONFIG

def test_lucius_memory_manager_creation():
    """Test creation of Lucius memory manager"""
    memory_manager = create_lucius_memory_manager()
    
    assert memory_manager is not None
    assert memory_manager.memory_type == PERSONALITY_CONFIG['memory_config']['type']
    assert memory_manager.max_token_limit == PERSONALITY_CONFIG['memory_config']['max_token_limit']

def test_memory_message_handling():
    """Test adding and retrieving messages"""
    memory_manager = create_lucius_memory_manager()
    
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
    memory_manager = create_lucius_memory_manager()
    
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
    memory_manager = create_lucius_memory_manager()
    
    memory_manager.add_user_message("Test message")
    memory_manager.clear_memory()
    
    context = memory_manager.get_memory_context()
    assert len(context) == 0

def test_memory_persistence():
    """Test that persistent store is working"""
    memory_manager = create_lucius_memory_manager()
    
    # Add a message
    memory_manager.add_user_message("Persistent memory test")
    
    # Check persistent store
    assert memory_manager.persistent_store.exists(
        memory_manager.persistent_store.get_all_keys()[0]
    )
