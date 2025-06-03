import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from src.chatbot.config_manager import ConfigurationManager
from src.chatbot.config_schemas import ChatbotConfiguration


class TestConfigurationManager:
    """Test configuration management functionality"""

    @patch('src.chatbot.config_manager.db.get_session')
    def test_create_configuration(self, mock_get_session):
        """Test creating a new configuration"""
        # Arrange
        mock_session = Mock()
        mock_get_session.return_value = iter([mock_session])

        mock_config = Mock()
        mock_config.id = 1
        mock_config.name = "Test Config"
        mock_config.version = 1
        mock_config.is_active = False
        mock_config.created_at = datetime.now()

        mock_session.query.return_value.filter_by.return_value.first.return_value = None
        mock_session.add = Mock()
        mock_session.commit = Mock(side_effect=lambda: setattr(mock_config, 'id', 1))

        config_manager = ConfigurationManager()
        config_data = ChatbotConfiguration(
            name="Test Config",
            description="Test description",
            model="test-model"
        )

        # Patch the Configuration class
        with patch('src.chatbot.config_manager.Configuration', return_value=mock_config):
            # Act
            result = config_manager.create_configuration(config_data)

        # Assert
        assert mock_session.add.called
        assert mock_session.commit.called
        assert result["name"] == "Test Config"
        assert result["id"] == 1

    @patch('src.chatbot.config_manager.db.get_session')
    def test_get_active_configuration(self, mock_get_session):
        """Test retrieving active configuration"""
        # Arrange
        mock_session = Mock()
        mock_get_session.return_value = iter([mock_session])

        mock_config = Mock()
        mock_config.config_json = {
            "name": "Active Config",
            "model": "test-model",
            "model_parameters": {"temperature": 0.5},
            "prompt_template": {"system_prompt": "Test prompt"},
            "knowledge_settings": {"enabled": True}
        }

        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_config

        config_manager = ConfigurationManager()

        # Act
        result = config_manager.get_active_configuration()

        # Assert
        assert result.name == "Active Config"
        assert result.model == "test-model"

    @patch('src.chatbot.config_manager.db.get_session')
    def test_activate_configuration(self, mock_get_session):
        """Test activating a configuration"""
        # Arrange
        mock_session = Mock()
        mock_get_session.return_value = iter([mock_session])

        mock_config = Mock()
        mock_config.id = 1
        mock_config.name = "Test Config"
        mock_config.is_active = False

        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_config

        config_manager = ConfigurationManager()

        # Act
        result = config_manager.activate_configuration(1)

        # Assert
        assert mock_config.is_active is True
        assert mock_session.commit.called
        assert result["activated"] is True
