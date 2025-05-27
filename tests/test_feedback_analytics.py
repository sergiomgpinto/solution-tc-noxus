from unittest.mock import patch, Mock
from fastapi.testclient import TestClient


class TestFeedbackAnalytics:
    def test_feedback_summary_empty(self, client: TestClient) -> None:
        response = client.get("/api/v1/feedback/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["total_feedback"] == 0
        assert data["satisfaction_rate"] == 0

    @patch('src.chatbot.main.OpenAI')
    def test_feedback_workflow(self, mock_openai: Mock, client: TestClient) -> None:
        # Mock OpenAI
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test response"))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        # Create a message
        chat_response = client.post("/api/v1/chat", json={"message": "Test"})
        message_id = chat_response.json()["message_id"]

        # Submit feedback
        feedback_response = client.post(
            "/api/v1/feedback",
            json={"message_id": message_id, "feedback_type": "thumbs_up"}
        )
        assert feedback_response.status_code == 200

        # Check summary
        summary_response = client.get("/api/v1/feedback/summary")
        summary = summary_response.json()
        assert summary["total_feedback"] == 1
        assert summary["thumbs_up"] == 1
        assert summary["satisfaction_rate"] == 100.0
