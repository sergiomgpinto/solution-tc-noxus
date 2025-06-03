# Data Fly Wheel Chatbot

An adaptive AI chatbot system that learns from user feedback to continuously improve its responses.

## Overview

This project implements a chatbot platform with the following key features:
- Multi-turn conversational capabilities with context retention
- Integration with external knowledge sources via vector database
- User feedback collection and analysis
- Dynamic configuration system for behavior modification
- Comprehensive CRUD operations for all system components

## Architecture

### System Components

1. **Backend API** - FastAPI-based REST API serving as the core application server
2. **Database** - PostgreSQL for persistent storage of conversations, configurations, and feedback
3. **Vector Store** - ChromaDB for knowledge base storage and semantic search
4. **LLM Integration** - OpenRouter API for language model capabilities
5. **Frontend** - React/TypeScript single-page application

### Technology Stack

- **Backend**: Python 3.11, FastAPI, SQLAlchemy, Uvicorn
- **Frontend**: React 18, TypeScript, Axios
- **Database**: PostgreSQL 15
- **Vector Database**: ChromaDB
- **Containerization**: Docker, Docker Compose
- **LLM Provider**: OpenRouter API

## Installation and Setup

### Quick Start

1. Clone the repository:
```bash
git clone <repository-url>
cd solution-tc-noxus
```

2. Run the setup script:
```bash
./setup.sh
```

3. Configure environment variables:
```bash
# Edit .env file and add your OpenRouter API key
# Replace 'your_api_key_here' with actual key
OPENROUTER_API_KEY=your_actual_key
```

4. Start the application:
```bash
./start.sh
```

5. Access the application:
- API Documentation: http://localhost:8000/docs
- Backend API: http://localhost:8000
- Frontend: http://localhost:3000 (if enabled)

### Manual Setup

If scripts are not executable:
```bash
chmod +x *.sh
./setup.sh
```

## Project Structure

```
solution-tc-noxus/
├── src/
│   └── chatbot/
│       ├── api/                 # API routes and FastAPI app
│       │   ├── app.py          # FastAPI application
│       │   ├── routes.py       # API endpoints
│       │   └── models.py       # Pydantic models
│       ├── db/                 # Database layer
│       │   ├── database.py     # Database connection
│       │   └── models.py       # SQLAlchemy models
│       ├── knowledge/          # Knowledge management
│       │   └── manager.py      # ChromaDB integration
│       ├── main.py             # Core chatbot logic
│       ├── config_manager.py   # Configuration management
│       ├── feedback_analytics.py # Feedback analysis
│       └── run_server.py       # Server entry point
├── frontend-react/             # React frontend
├── tests/                      # Test suite
├── docker-compose.yml          # Container orchestration
├── Dockerfile                  # Backend container definition
├── requirements.txt            # Python dependencies
└── .env.example               # Environment template
```

## API Endpoints

### Chat Operations
- `POST /api/v1/chat` - Send message and receive response
- `GET /api/v1/conversations` - List all conversations
- `GET /api/v1/conversations/{id}/messages` - Get conversation messages
- `DELETE /api/v1/conversations/{id}` - Delete conversation

### Configuration Management
- `GET /api/v1/configurations` - List configurations
- `POST /api/v1/configurations` - Create configuration
- `PUT /api/v1/configurations/{id}` - Update configuration
- `DELETE /api/v1/configurations/{id}` - Delete configuration
- `POST /api/v1/configurations/{id}/activate` - Activate configuration

### Knowledge Management
- `GET /api/v1/knowledge-sources` - List knowledge sources
- `POST /api/v1/knowledge-sources` - Create knowledge source
- `POST /api/v1/knowledge-sources/{id}/documents` - Add documents
- `POST /api/v1/search` - Search knowledge base

### Feedback System
- `POST /api/v1/feedback` - Submit feedback
- `GET /api/v1/feedback/summary` - Get feedback analytics
- `GET /api/v1/feedback/worst-performing` - Get poorly rated messages

### AB Testing
- `POST /api/v1/ab-tests` - Create AB Test
- `GET /api/v1//ab-tests/{test_id}/results` - Get AB Test results

## Configuration System

The chatbot behavior can be modified through JSON configurations including:
- Model selection and parameters (temperature, max_tokens)
- System prompts and response templates
- Knowledge retrieval settings
- Feature flags

Example configuration:
```json
{
  "name": "Technical Assistant",
  "model": "qwen/qwen-2.5-72b-instruct",
  "model_parameters": {
    "temperature": 0.3,
    "max_tokens": 500
  },
  "prompt_template": {
    "system_prompt": "You are a technical expert. Provide detailed, accurate information."
  }
}
```

## Development

### Running Tests
```bash
./run_tests.sh
```

### Viewing Logs
```bash
./logs.sh
# Or specific service
./logs.sh backend
```

### Stopping Services
```bash
./stop.sh
```

# Thought Process

The core insight is that this isn't just about building a chatbot, but creating a system that learns and adapts. The "data flywheel" concept implies a self-reinforcing cycle where more usage leads to better performance, which attracts more usage.

```
More Users → More Interactions → More Feedback → Better Models
    ↑                                                    │
    └────────────── Improved Experience ←───────────────┘
```

The fundamental problem is mental model inference. Each user has a latent mental model (their knowledge level, preferences, communication style), and our system needs to infer this model from limited interactions. This framing led to treating the problem as a Partially Observable Markov Decision Process (POMDP) where:
- The true user mental model M* is unobservable
- We maintain a belief state M̂ (our estimate)
- Each interaction provides information to refine our estimate

## Mathematical Framework

### Core Optimization Problem
The system fundamentally solves a mental model inference problem:

```
minimize E[KL(M* || M̂)]
```

Where:
- **M*** = User's true mental model (unobservable latent state)
- **M̂** = System's estimate of user's mental model
- **KL** = Kullback-Leibler divergence (measures difference between distributions)

### System State Representation

**User State:**
```
U = {M*, H}
- M* ∈ ℝᵈ: True mental model (d-dimensional latent vector)
- H = {I₁, I₂, ..., Iₜ}: Interaction history
- Iᵢ = (qᵢ, rᵢ, fᵢ, tᵢ): Query, response, feedback, timestamp
```

**System State:**
```
S = {M̂, Σ, Θ}
- M̂ ∈ ℝᵈ: Estimated mental model
- Σ ∈ ℝᵈˣᵈ: Uncertainty covariance matrix
- Θ: System parameters (prompts, configurations)
```

### Information-Theoretic View

Each interaction provides information gain:
```
IG(Iₖ) = H(M*|I₁...Iₖ₋₁) - H(M*|I₁...Iₖ)
```
- Measures uncertainty reduction about user's mental model
- Guides active learning decisions

### Belief Update Mechanism

```
M̂ₜ₊₁ = M̂ₜ + α·∇L(fₜ, rₜ, M̂ₜ) + β·Prior(M*) + γ·Reg(M̂ₜ, M̂_pop)
```
- Gradient update from feedback
- Bayesian prior from user features
- Regularization toward population clusters

### RL Components
- **State (s)**: M* (true mental model) - unobservable
- **Observation (o)**: User queries, feedback
- **Action (a)**: Generated responses
- **Reward (r)**: Thumbs up (+1) / Thumbs down (-1)
- **Policy π(a|o)**: Response generation strategy
- **Belief State b(s)**: Probability distribution over mental models

### Value Function
```
V(b) = E[Σ γᵗ r_t | b₀ = b]
```
Expected cumulative satisfaction given current belief about user


### Dual Memory Architecture (Future Work)

Inspired by hippocampal-neocortical consolidation:

```
Working Memory (Redis)          Long-term Memory (PostgreSQL + ChromaDB)
- Recent interactions     →     - Consolidated patterns
- Fast updates                  - Stable knowledge
- Session context              - User models

        Consolidation Process (Nightly)
        Extracts patterns and updates models
```

## Design Philosophy

- Start Simple, Enable Complexity: MVP focuses on core feedback loop, but architecture supports advanced features
- Separation of Concerns: Clear boundaries between chat logic, configuration, knowledge, and analytics
- Feedback-Driven: Every design decision is oriented around collecting and using feedback

## Stack Decisions

1. **FastAPI**: Chosen for async support, automatic documentation, and type safety
2. **PostgreSQL**: Reliable ACID-compliant storage for conversations and configurations and has support for JSON
3. **ChromaDB**: Embedded vector database for simple deployment and good performance

## Implementation Journey
Phase-Based Development
Divided implementation into 11 phases to maintain focus and ensure incremental progress:

- Hello Chatbot: Core conversation loop
- Memory Bank: Persistence layer
- Knowledge Seeker: Vector search integration
- Web Service: REST API
- Feedback Loop: User feedback collection
- Configuration Station: Dynamic behavior
- Simple Frontend: User interface
- Docker Debut: Containerization
- CRUD Complete: Full operations
- Test Suite: Quality assurance
- A/B Testing: Config effectiveness