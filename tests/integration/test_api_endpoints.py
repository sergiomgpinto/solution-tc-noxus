from datetime import datetime

import pytest
from unittest.mock import patch, Mock


class TestChatEndpoints:
    """Test chat-related API endpoints"""

    @patch('src.chatbot.main.OpenAI')
    def test_create_chat_conversation(self, mock_openai, client):
        """Test creating a new chat conversation"""
        # Arrange
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Hello! How can I help?"))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        # Act
        response = client.post(
            "/api/v1/chat",
            json={"message": "Hello"}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "conversation_id" in data
        assert "message_id" in data

    def test_list_conversations(self, client):
        """Test listing conversations"""
        # Act
        response = client.get("/api/v1/conversations")

        # Assert
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_nonexistent_conversation(self, client):
        """Test getting messages from non-existent conversation"""
        # Act
        response = client.get("/api/v1/conversations/99999/messages")

        # Assert
        assert response.status_code == 404


class TestConfigurationEndpoints:
    """Test configuration management endpoints"""

    def test_create_configuration(self, client):
        """Test creating a new configuration"""
        # Arrange
        name = f'Configuration {datetime.now()}'
        config_data = {
            "name": name,
            "description": "Test config for integration tests",
            "model": "qwen/qwen-2.5-72b-instruct",
            "model_parameters": {
                "temperature": 0.5,
                "max_tokens": 100
            },
            "prompt_template": {
                "system_prompt": "You are a test assistant."
            },
            "knowledge_settings": {
                "enabled": False
            }
        }

        # Act
        response = client.post("/api/v1/configurations", json=config_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == name

    def test_list_configurations(self, client):
        """Test listing all configurations"""
        # Act
        response = client.get("/api/v1/configurations")

        # Assert
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_update_nonexistent_configuration(self, client):
        """Test updating non-existent configuration"""
        # Arrange
        config_data = {
            "name": "Updated Config",
            "model": "test-model"
        }

        # Act
        response = client.put("/api/v1/configurations/99999", json=config_data)

        # Assert
        assert response.status_code == 404


class TestFeedbackEndpoints:
    """Test feedback-related endpoints"""

    def test_submit_feedback_invalid_message(self, client):
        """Test submitting feedback for invalid message"""
        # Arrange
        feedback_data = {
            "message_id": 99999,
            "feedback_type": "thumbs_up"
        }

        # Act
        response = client.post("/api/v1/feedback", json=feedback_data)

        assert response.status_code == 404

    def test_get_feedback_summary(self, client):
        """Test getting feedback summary"""
        # Act
        response = client.get("/api/v1/feedback/summary")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "total_feedback" in data
        assert "satisfaction_rate" in data


class TestHealthEndpoints:
    """Test system health endpoints"""

    def test_health_check(self, client):
        """Test health check endpoint"""
        # Act
        response = client.get("/health")

        # Assert
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_root_endpoint(self, client):
        """Test root endpoint"""
        # Act
        response = client.get("/")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
