# Demo

---

## 1. Shell Scripts


### setup.sh

Initializes environment and pulls necessary images.

```bash
./setup.sh
```

### start.sh

Builds, initializes, and starts all services.

```bash
./start.sh
```

### stop.sh

Stops running containers.

```bash
./stop.sh
```

### logs.sh

Tails container logs.

```bash
./logs.sh
```

### status.sh

Shows container status and ports.

```bash
./status.sh
```

---

## 2. System Overview

**Services:**

* Frontend: [http://localhost:3000](http://localhost:3000)
* Backend API: [http://localhost:8000](http://localhost:8000)
* API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

Use this command to verify running containers:

```bash
docker ps
```

---

## 3. Configuration Management (via CLI)

### Create default configs:

```bash
docker-compose run --rm backend python -m chatbot.config_cli init
```

### List all configurations:

```bash
docker-compose run --rm backend python -m chatbot.config_cli list
```

### Activate one:

```bash
docker-compose run --rm backend python -m chatbot.config_cli activate <config_id>
```

### Example:

```bash
docker-compose run --rm backend python -m chatbot.config_cli activate 2
```

### Add new configuration:

Example modification snippet:

```python
{
  "name": "Minimalist Assistant",
  "description": "Gives brief and concise answers",
  "model_parameters": {"temperature": 0.4},
  "prompt_template": {
    "system_prompt": "You are a minimalist assistant. Answer clearly and concisely."
  }
}
```

---

## 4. Chatbot Core Demo

### Start from frontend:

* Open [http://localhost:3000](http://localhost:3000)
* Start chatting with the assistant
* Observe how responses differ based on the active configuration

### Or use API directly:

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, what is Python?"}'
```

Add `"conversation_id"` to continue a chat with memory.

---

## 5. Knowledge Integration (RAG)

### CLI: Create and list sources

```bash
docker-compose run --rm backend python -m chatbot.knowledge_cli create "AI Concepts" "Includes FastAPI, ML topics"
docker-compose run --rm backend python -m chatbot.knowledge_cli list
```

### CLI: Add documents

```bash
docker-compose run --rm backend python -m chatbot.knowledge_cli add 1 "FastAPI is a modern Python web framework..."
```

### Search from CLI:

```bash
docker-compose run --rm backend python -m chatbot.knowledge_cli search "What is FastAPI?"
```

---

## 6. Feedback Analytics (CLI)

Get insights from user feedback:

### Summary report (last 7 days):

```bash
docker-compose run --rm backend python -m chatbot.feedback_cli summary
```

### Worst-performing messages:

```bash
docker-compose run --rm backend python -m chatbot.feedback_cli worst
```

### Feedback for a conversation:

```bash
docker-compose run --rm backend python -m chatbot.feedback_cli conversation <conversation_id>
```

---

## 7. Running Tests

Use this script to run all unit and integration tests:

```bash
./run_tests.sh
```

You can also run tests manually:

```bash
docker-compose run --rm backend pytest tests/
```

---

## 8. A/B Testing (via CLI)

### Create A/B test:

```bash
docker-compose run --rm backend python -m chatbot.ab_test_cli create 1 2 50
```

This creates a test comparing config ID 1 (control) vs 2 (treatment).

### Simulate user traffic:

```bash
for i in {1..3}; do
  curl -X POST http://localhost:8000/api/v1/chat \
    -H "Content-Type: application/json" \
    -H "X-User-ID: user_$i" \
    -d '{"message": "Explain neural networks"}'
  echo "User $i complete"
done
```

### Get results:

```bash
curl http://localhost:8000/api/v1/ab-tests/1/results | jq '.'
```

---

## 9. Architecture & Scaling

```
MVP Phase                          Scalable Production Phase
━━━━━━━━━━━━━━━━━━                ━━━━━━━━━━━━━━━━━━━━━━━━━━━
Single Docker Container     →     Load-Balanced API Instances
Embedded ChromaDB          →     Scalable Vector DB Cluster
Synchronous Requests        →     Event Queues / Async Tasks
Simple Feedback Logging     →     ML-Driven Evaluation & Tuning
```

---
