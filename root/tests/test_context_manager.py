# tests/test_context_manager.py
import pytest
from core.context_manager import ContextManager

@pytest.fixture
def context():
    return ContextManager()

@pytest.fixture
def system_messages():
    return [
        {"role": "system", "content": "System message 1"},
        {"role": "system", "content": "System message 2"}
    ]

def test_init(context):
    """Test initial state of ContextManager"""
    assert len(context) == 0
    assert context.get_messages() == []

def test_set_system_messages(context, system_messages):
    """Test setting system messages"""
    context.set_system_messages(system_messages)
    messages = context.get_messages()
    assert len(messages) == 2
    assert all(msg["role"] == "system" for msg in messages)
    assert messages == system_messages

def test_add_exchange(context):
    """Test adding a message exchange"""
    context.add_exchange("User message", "LLM response")
    messages = context.get_messages()
    assert len(context) == 1
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "User message"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["content"] == "LLM response"

def test_add_user_message(context):
    """Test adding only user message"""
    context.add_user_message("User message")
    messages = context.get_messages()
    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "User message"

def test_clear_context(context, system_messages):
    """Test clearing conversation context but keeping system messages"""
    context.set_system_messages(system_messages)
    context.add_exchange("User message", "LLM response")
    
    context.clear_context()
    messages = context.get_messages()
    
    assert len(context) == 0
    assert len(messages) == 2  # Only system messages remain
    assert all(msg["role"] == "system" for msg in messages)

def test_clear_all(context, system_messages):
    """Test clearing all messages including system messages"""
    context.set_system_messages(system_messages)
    context.add_exchange("User message", "LLM response")
    
    context.clear_all()
    messages = context.get_messages()
    
    assert len(context) == 0
    assert len(messages) == 0  # No messages remain

def test_get_last_n_exchanges(context, system_messages):
    """Test retrieving last n exchanges"""
    context.set_system_messages(system_messages)
    context.add_exchange("Message 1", "Response 1")
    context.add_exchange("Message 2", "Response 2")
    context.add_exchange("Message 3", "Response 3")
    
    # Get last 2 exchanges with system messages
    messages = context.get_last_n_exchanges(2, include_system=True)
    assert len(messages) == 6  # 2 system + 4 exchange messages
    assert messages[0]["content"] == "System message 1"
    assert messages[-2]["content"] == "Message 3"
    assert messages[-1]["content"] == "Response 3"
    
    # Get last exchange without system messages
    messages = context.get_last_n_exchanges(1, include_system=False)
    assert len(messages) == 2
    assert messages[0]["content"] == "Message 3"
    assert messages[1]["content"] == "Response 3"

def test_invalid_system_message_format():
    """Test validation of system message format"""
    context = ContextManager()
    invalid_messages = [
        {"role": "invalid", "content": "message"},  # Invalid role
        {"content": "message"},  # Missing role
        {"role": "system"}  # Missing content
    ]
    
    with pytest.raises(ValueError):
        context.set_system_messages(invalid_messages)

def test_get_messages_without_system(context, system_messages):
    """Test getting messages without system messages"""
    context.set_system_messages(system_messages)
    context.add_exchange("User message", "LLM response")
    
    messages = context.get_messages(include_system=False)
    assert len(messages) == 2
    assert all(msg["role"] != "system" for msg in messages)
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"
