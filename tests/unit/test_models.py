import pytest
from datetime import datetime
from src.chatbot.db.models import Conversation, Message, Configuration, Feedback


class TestDatabaseModels:
    """Test database model functionality"""

    def test_conversation_creation(self, test_db):
        """Test creating a conversation"""
        # Arrange
        conversation = Conversation(title="Test Conversation")

        # Act
        test_db.add(conversation)
        test_db.commit()

        # Assert
        assert conversation.id is not None
        assert conversation.title == "Test Conversation"
        assert isinstance(conversation.created_at, datetime)
        assert isinstance(conversation.updated_at, datetime)

    def test_message_creation(self, test_db):
        """Test creating a message with conversation relationship"""
        # Arrange
        conversation = Conversation()
        test_db.add(conversation)
        test_db.commit()

        message = Message(
            conversation_id=conversation.id,
            role="user",
            content="Test message"
        )

        # Act
        test_db.add(message)
        test_db.commit()

        # Assert
        assert message.id is not None
        assert message.conversation_id == conversation.id
        assert message.role == "user"
        assert message.content == "Test message"

    def test_configuration_json_storage(self, test_db):
        """Test storing JSON configuration"""
        # Arrange
        config_data = {
            "name": "Test Config",
            "model": "test-model",
            "parameters": {"temperature": 0.7}
        }

        configuration = Configuration(
            name="Test Config",
            config_json=config_data,
            is_active=True
        )

        # Act
        test_db.add(configuration)
        test_db.commit()

        # Assert
        assert configuration.config_json == config_data
        assert configuration.is_active is True
        assert configuration.version == 1

    def test_feedback_relationship(self, test_db):
        """Test feedback linked to message"""
        # Arrange
        conversation = Conversation()
        test_db.add(conversation)
        test_db.commit()

        message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content="Bot response"
        )
        test_db.add(message)
        test_db.commit()

        feedback = Feedback(
            message_id=message.id,
            feedback_type="thumbs_up"
        )

        # Act
        test_db.add(feedback)
        test_db.commit()

        # Assert
        assert feedback.message_id == message.id
        assert feedback.feedback_type == "thumbs_up"
