from typing import Optional, List
from pydantic import BaseModel, Field


class ModelParameters(BaseModel):
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(500, ge=1, le=4000)
    top_p: float = Field(1.0, ge=0.0, le=1.0)
    frequency_penalty: float = Field(0.0, ge=-2.0, le=2.0)
    presence_penalty: float = Field(0.0, ge=-2.0, le=2.0)


class PromptTemplate(BaseModel):
    system_prompt: str = Field(
        "You are a helpful assistant. Keep your responses concise and clear.",
        min_length=1,
        max_length=2000
    )
    context_template: Optional[str] = Field(
        "Relevant information:\n{context}",
        description="Template for injecting knowledge context"
    )
    error_prompt: Optional[str] = Field(
        "I apologize, but I encountered an error. Please try again.",
        description="Response when errors occur"
    )


class KnowledgeSettings(BaseModel):
    enabled: bool = Field(True, description="Enable knowledge retrieval")
    max_results: int = Field(3, ge=1, le=10)
    score_threshold: float = Field(0.7, ge=0.0, le=1.0)
    knowledge_source_ids: Optional[List[int]] = Field(
        None,
        description="Specific knowledge sources to use, None means all"
    )


class ChatbotConfiguration(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    model: str = Field("qwen/qwen-2.5-72b-instruct")
    model_parameters: ModelParameters = Field(default_factory=ModelParameters)
    prompt_template: PromptTemplate = Field(default_factory=PromptTemplate)
    knowledge_settings: KnowledgeSettings = Field(default_factory=KnowledgeSettings)
    tags: List[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Friendly Assistant",
                "description": "A helpful and friendly chatbot",
                "model": "qwen/qwen-2.5-72b-instruct",
                "model_parameters": {
                    "temperature": 0.8,
                    "max_tokens": 500
                },
                "prompt_template": {
                    "system_prompt": "You are a friendly and helpful assistant."
                },
                "knowledge_settings": {
                    "enabled": True,
                    "max_results": 3
                },
                "tags": ["friendly", "general"]
            }
        }
