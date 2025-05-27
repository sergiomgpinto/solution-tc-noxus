from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from src.chatbot.db.models import Conversation, Message


class TestChatEndpoints:
    def test_health_check(self, client: TestClient) -> None:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_root_endpoint(self, client: TestClient) -> None:
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data

    @patch('src.chatbot.main.OpenAI')
    def test_chat_new_conversation(self, mock_openai: Mock, client: TestClient) -> None:
        # Mock only the OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Hello! I'm doing well."))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        # Make the request - this will create real database entries
        response = client.post(
            "/api/v1/chat",
            json={"message": "Hello, how are you?"}
        )

        # Debug output if needed
        if response.status_code != 200:
            print(f"Error: {response.json()}")

        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "Hello! I'm doing well."
        assert "conversation_id" in data
        assert "message_id" in data
        assert isinstance(data["conversation_id"], int)
        assert isinstance(data["message_id"], int)

    @patch('src.chatbot.main.OpenAI')
    def test_chat_continue_conversation(self, mock_openai: Mock, client: TestClient) -> None:
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="First response"))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        first_response = client.post(
            "/api/v1/chat",
            json={"message": "First message"}
        )
        conversation_id = first_response.json()["conversation_id"]

        mock_response.choices = [Mock(message=Mock(content="Second response"))]

        second_response = client.post(
            "/api/v1/chat",
            json={"message": "Second message", "conversation_id": conversation_id}
        )

        assert second_response.status_code == 200
        data = second_response.json()
        assert data["conversation_id"] == conversation_id

    def test_list_conversations_empty(self, client: TestClient) -> None:
        response = client.get("/api/v1/conversations")
        assert response.status_code == 200
        assert response.json() == []

    @patch('src.chatbot.main.OpenAI')
    def test_list_conversations_with_data(self, mock_openai: Mock, client: TestClient) -> None:
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test response"))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        client.post("/api/v1/chat", json={"message": "Test message"})

        response = client.get("/api/v1/conversations")
        assert response.status_code == 200
        conversations = response.json()
        assert len(conversations) == 1

        # Expect 3 messages: system + user + assistant
        assert conversations[0]["message_count"] == 3

    def test_get_conversation_messages_not_found(self, client: TestClient) -> None:
        response = client.get("/api/v1/conversations/999/messages")
        assert response.status_code == 404

    @patch('src.chatbot.main.OpenAI')
    def test_submit_feedback(self, mock_openai: Mock, client: TestClient) -> None:
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test response"))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        chat_response = client.post("/api/v1/chat", json={"message": "Test"})
        message_id = chat_response.json()["message_id"]

        feedback_response = client.post(
            "/api/v1/feedback",
            json={"message_id": message_id, "feedback_type": "thumbs_up"}
        )

        assert feedback_response.status_code == 200
        data = feedback_response.json()
        assert data["status"] == "recorded"
        assert "feedback_id" in data


class TestKnowledgeEndpoints:
    @patch('src.chatbot.knowledge.manager.chromadb.PersistentClient')
    def test_create_knowledge_source(self, mock_chromadb: Mock, client: TestClient) -> None:
        mock_chromadb.return_value.create_collection.return_value = Mock()

        response = client.post(
            "/api/v1/knowledge-sources",
            json={"name": "Test Source", "description": "Test description"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Source"
        assert data["description"] == "Test description"
        assert data["document_count"] == 0

    def test_list_knowledge_sources_empty(self, client: TestClient) -> None:
        response = client.get("/api/v1/knowledge-sources")
        assert response.status_code == 200
        assert response.json() == []

    def test_add_documents_source_not_found(self, client: TestClient) -> None:
        response = client.post(
            "/api/v1/knowledge-sources/999/documents",
            json={"documents": ["test document"]}
        )
        assert response.status_code == 404

    def test_search_knowledge_empty(self, client: TestClient) -> None:
        response = client.post(
            "/api/v1/search",
            json={"query": "test query"}
        )
        assert response.status_code == 200
        assert response.json() == []
