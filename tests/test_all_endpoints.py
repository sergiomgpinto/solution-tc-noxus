import pytest
import requests
import time

BASE_URL = "http://localhost:8000/api/v1"


class TestAPIEndpoints:
    """Comprehensive test suite for all API endpoints"""

    @classmethod
    def setup_class(cls):
        """Setup test data that will be used across tests"""
        cls.created_ids = {
            "conversation_id": None,
            "message_id": None,
            "configuration_id": None,
            "knowledge_source_id": None,
            "feedback_id": None
        }

    def test_root_endpoint(self):
        response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data

    def test_health_endpoint(self):
        response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    # Configuration Endpoints

    def test_create_configuration(self):
        payload = {
            "name": f"Test Config {time.time()}",
            "description": "Automated test configuration",
            "model": "qwen/qwen-2.5-72b-instruct",
            "model_parameters": {
                "temperature": 0.5,
                "max_tokens": 500
            },
            "prompt_template": {
                "system_prompt": "You are a test assistant."
            },
            "knowledge_settings": {
                "enabled": False,
                "max_results": 3
            }
        }
        response = requests.post(f"{BASE_URL}/configurations", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["name"] == payload["name"]
        self.__class__.created_ids["configuration_id"] = data["id"]

    def test_list_configurations(self):
        response = requests.get(f"{BASE_URL}/configurations")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_configuration(self):
        config_id = self.created_ids["configuration_id"]
        if not config_id:
            pytest.skip("No configuration created")

        response = requests.get(f"{BASE_URL}/configurations/{config_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == config_id
        assert "config" in data

    def test_update_configuration(self):
        config_id = self.created_ids["configuration_id"]
        if not config_id:
            pytest.skip("No configuration created")

        payload = {
            "name": f"Updated Test Config {time.time()}",
            "description": "Updated automated test configuration",
            "model": "qwen/qwen-2.5-72b-instruct",
            "model_parameters": {
                "temperature": 0.7,
                "max_tokens": 600
            },
            "prompt_template": {
                "system_prompt": "You are an updated test assistant."
            },
            "knowledge_settings": {
                "enabled": True,
                "max_results": 5
            }
        }
        response = requests.put(f"{BASE_URL}/configurations/{config_id}", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["version"] > 1

    def test_activate_configuration(self):
        config_id = self.created_ids["configuration_id"]
        if not config_id:
            pytest.skip("No configuration created")

        response = requests.post(f"{BASE_URL}/configurations/{config_id}/activate")
        assert response.status_code == 200
        data = response.json()
        assert data["activated"] == True

    # Chat Endpoints

    def test_create_chat(self):
        payload = {
            "message": "Hello, this is an automated test message"
        }
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "conversation_id" in data
        assert "message_id" in data
        self.__class__.created_ids["conversation_id"] = data["conversation_id"]
        self.__class__.created_ids["message_id"] = data["message_id"]

    def test_continue_chat(self):
        conversation_id = self.created_ids["conversation_id"]
        if not conversation_id:
            pytest.skip("No conversation created")

        payload = {
            "message": "This is a follow-up message",
            "conversation_id": conversation_id
        }
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["conversation_id"] == conversation_id

    # Conversation Endpoints

    def test_list_conversations(self):
        response = requests.get(f"{BASE_URL}/conversations")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_conversation_messages(self):
        conversation_id = self.created_ids["conversation_id"]
        if not conversation_id:
            pytest.skip("No conversation created")

        response = requests.get(f"{BASE_URL}/conversations/{conversation_id}/messages")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2  # At least system message and user message

    # Feedback Endpoints

    def test_submit_feedback(self):
        message_id = self.created_ids["message_id"]
        if not message_id:
            pytest.skip("No message created")

        payload = {
            "message_id": message_id,
            "feedback_type": "thumbs_up"
        }
        response = requests.post(f"{BASE_URL}/feedback", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "recorded"
        assert "feedback_id" in data
        self.__class__.created_ids["feedback_id"] = data["feedback_id"]

    def test_get_feedback_summary(self):
        response = requests.get(f"{BASE_URL}/feedback/summary")
        assert response.status_code == 200
        data = response.json()
        assert "total_feedback" in data
        assert "thumbs_up" in data
        assert "thumbs_down" in data
        assert "satisfaction_rate" in data

    def test_get_conversation_feedback(self):
        conversation_id = self.created_ids["conversation_id"]
        if not conversation_id:
            pytest.skip("No conversation created")

        response = requests.get(f"{BASE_URL}/feedback/conversation/{conversation_id}")
        assert response.status_code in [200, 404]

    def test_get_worst_performing_messages(self):
        response = requests.get(f"{BASE_URL}/feedback/worst-performing?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    # Knowledge Source Endpoints

    def test_create_knowledge_source(self):
        payload = {
            "name": f"Test Knowledge Source {time.time()}",
            "description": "Automated test knowledge source"
        }
        response = requests.post(f"{BASE_URL}/knowledge-sources", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["name"] == payload["name"]
        self.__class__.created_ids["knowledge_source_id"] = data["id"]

    def test_list_knowledge_sources(self):
        response = requests.get(f"{BASE_URL}/knowledge-sources")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_add_documents_to_knowledge_source(self):
        source_id = self.created_ids["knowledge_source_id"]
        if not source_id:
            pytest.skip("No knowledge source created")

        payload = {
            "documents": [
                "This is a test document for automated testing.",
                "This is another test document with different content."
            ]
        }
        response = requests.post(f"{BASE_URL}/knowledge-sources/{source_id}/documents", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["documents_added"] == 2

    def test_search_knowledge(self):
        payload = {
            "query": "test document",
            "n_results": 3
        }
        response = requests.post(f"{BASE_URL}/search", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    # Cleanup Methods

    def test_cleanup_conversation(self):
        conversation_id = self.created_ids["conversation_id"]
        if not conversation_id:
            pytest.skip("No conversation to delete")

        response = requests.delete(f"{BASE_URL}/conversations/{conversation_id}")
        assert response.status_code in [200, 404]

    def test_cleanup_knowledge_source(self):
        source_id = self.created_ids["knowledge_source_id"]
        if not source_id:
            pytest.skip("No knowledge source to delete")

        response = requests.delete(f"{BASE_URL}/knowledge-sources/{source_id}")
        assert response.status_code in [200, 404]

    def test_cleanup_configuration(self):
        config_id = self.created_ids["configuration_id"]
        if not config_id:
            pytest.skip("No configuration to delete")

        response = requests.delete(f"{BASE_URL}/configurations/{config_id}")
        assert response.status_code in [200, 400, 404]


class TestErrorHandling:
    """Test error handling for various endpoints"""

    def test_get_nonexistent_configuration(self):
        response = requests.get(f"{BASE_URL}/configurations/99999")
        assert response.status_code == 404

    def test_get_nonexistent_conversation_messages(self):
        response = requests.get(f"{BASE_URL}/conversations/99999/messages")
        assert response.status_code == 404

    def test_create_configuration_with_invalid_data(self):
        payload = {
            "name": "",  # Empty name should fail
            "model": "invalid-model"
        }
        response = requests.post(f"{BASE_URL}/configurations", json=payload)
        assert response.status_code in [400, 422]

    def test_submit_feedback_for_nonexistent_message(self):
        payload = {
            "message_id": 99999,
            "feedback_type": "thumbs_up"
        }
        response = requests.post(f"{BASE_URL}/feedback", json=payload)
        assert response.status_code in [400, 404, 500]

    def test_add_documents_to_nonexistent_knowledge_source(self):
        payload = {
            "documents": ["Test document"]
        }
        response = requests.post(f"{BASE_URL}/knowledge-sources/99999/documents", json=payload)
        assert response.status_code == 404


# class TestConcurrency:
#     """Test concurrent requests"""
#
#     def test_concurrent_chat_requests(self):
#         import concurrent.futures
#
#         def send_chat_request(message_num):
#             payload = {"message": f"Concurrent test message {message_num}"}
#             return requests.post(f"{BASE_URL}/chat", json=payload)
#
#         with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
#             futures = [executor.submit(send_chat_request, i) for i in range(5)]
#             results = [f.result() for f in concurrent.futures.as_completed(futures)]
#
#         for response in results:
#             assert response.status_code == 200
#