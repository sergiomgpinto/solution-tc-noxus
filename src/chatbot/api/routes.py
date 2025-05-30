from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from chatbot.main import ChatBot
from chatbot.db.database import db
from chatbot.db.models import Conversation, Message, Feedback
from chatbot.knowledge.manager import knowledge_manager
from chatbot.feedback_analytics import feedback_analytics
from chatbot.config_manager import config_manager
from chatbot.config_schemas import ChatbotConfiguration
from chatbot.api.models import (
    ChatRequest, ChatResponse, FeedbackRequest, FeedbackResponse,
    ConversationSummary, KnowledgeSourceRequest, KnowledgeSourceResponse,
    AddDocumentsRequest, SearchRequest, SearchResult
)


router = APIRouter()


def get_db() -> Session:
    session_gen = db.get_session()
    return next(session_gen)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, session: Session = Depends(get_db)) -> ChatResponse:
    try:
        chatbot = ChatBot(conversation_id=request.conversation_id)
        response = chatbot.chat(request.message)

        last_message = session.query(Message).filter_by(
            conversation_id=chatbot.conversation_id,
            role="assistant"
        ).order_by(Message.created_at.desc()).first()

        return ChatResponse(
            response=response,
            conversation_id=chatbot.conversation_id,
            message_id=last_message.id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if hasattr(chatbot, 'session') and chatbot.session:
            chatbot.session.close()


@router.get("/conversations", response_model=List[ConversationSummary])
async def list_conversations(session: Session = Depends(get_db)) -> List[ConversationSummary]:
    conversations = session.query(Conversation).order_by(
        Conversation.updated_at.desc()
    ).all()

    summaries = []
    for conv in conversations:
        message_count = session.query(Message).filter_by(
            conversation_id=conv.id
        ).count()

        summaries.append(ConversationSummary(
            id=conv.id,
            title=conv.title,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            message_count=message_count
        ))

    return summaries


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
        conversation_id: int,
        session: Session = Depends(get_db)
) -> List[dict]:
    messages = session.query(Message).filter_by(
        conversation_id=conversation_id
    ).order_by(Message.created_at).all()

    if not messages:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return [
        {
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at
        }
        for msg in messages
    ]


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
        request: FeedbackRequest,
        session: Session = Depends(get_db)
) -> FeedbackResponse:
    feedback = Feedback(
        message_id=request.message_id,
        feedback_type=request.feedback_type
    )
    session.add(feedback)
    session.commit()

    return FeedbackResponse(
        status="recorded",
        feedback_id=feedback.id
    )


@router.post("/knowledge-sources", response_model=KnowledgeSourceResponse)
async def create_knowledge_source(
        request: KnowledgeSourceRequest
) -> KnowledgeSourceResponse:
    source = knowledge_manager.create_knowledge_source(
        request.name,
        request.description
    )

    return KnowledgeSourceResponse(
        id=source["id"],
        name=source["name"],
        description=source["description"],
        document_count=0
    )


@router.get("/knowledge-sources", response_model=List[KnowledgeSourceResponse])
async def list_knowledge_sources() -> List[KnowledgeSourceResponse]:
    sources = knowledge_manager.list_knowledge_sources()

    return [
        KnowledgeSourceResponse(
            id=source["id"],
            name=source["name"],
            description=source["description"],
            document_count=source["document_count"]
        )
        for source in sources
    ]


@router.post("/knowledge-sources/{source_id}/documents")
async def add_documents(
        source_id: int,
        request: AddDocumentsRequest
) -> dict:
    try:
        count = knowledge_manager.add_documents(source_id, request.documents)
        return {"status": "success", "documents_added": count}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/search", response_model=List[SearchResult])
async def search_knowledge(request: SearchRequest) -> List[SearchResult]:
    results = knowledge_manager.search(
        request.query,
        request.knowledge_source_ids,
        request.n_results
    )

    return [
        SearchResult(
            document=doc,
            score=score,
            metadata=metadata
        )
        for doc, score, metadata in results
    ]


@router.get("/feedback/summary")
async def get_feedback_summary(
    days: int = 7,
    session: Session = Depends(get_db)
) -> dict:
    return feedback_analytics.get_feedback_summary(session, days)


@router.get("/feedback/conversation/{conversation_id}")
async def get_conversation_feedback(
    conversation_id: int,
    session: Session = Depends(get_db)
) -> List[dict]:
    feedback = feedback_analytics.get_conversation_feedback(conversation_id, session)
    if not feedback:
        raise HTTPException(status_code=404, detail="No feedback found for this conversation")
    return feedback


@router.get("/feedback/worst-performing")
async def get_worst_performing_messages(
    limit: int = 10,
    session: Session = Depends(get_db)
) -> List[dict]:
    return feedback_analytics.get_worst_performing_messages(limit, session)

@router.post("/configurations", response_model=dict)
async def create_configuration(
    config: ChatbotConfiguration,
    activate: bool = False
) -> dict:
    try:
        return config_manager.create_configuration(config, activate)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/configurations", response_model=List[dict])
async def list_configurations(
    tags: Optional[str] = None,
    active_only: bool = False
) -> List[dict]:
    tag_list = tags.split(",") if tags else None
    return config_manager.list_configurations(tag_list, active_only)


@router.get("/configurations/{config_id}", response_model=dict)
async def get_configuration(config_id: int) -> dict:
    config = config_manager.get_configuration(config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return config


@router.put("/configurations/{config_id}", response_model=dict)
async def update_configuration(
    config_id: int,
    config: ChatbotConfiguration
) -> dict:
    try:
        return config_manager.update_configuration(config_id, config)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/configurations/{config_id}/activate", response_model=dict)
async def activate_configuration(config_id: int) -> dict:
    try:
        return config_manager.activate_configuration(config_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/configurations/{config_id}")
async def delete_configuration(config_id: int) -> dict:
    try:
        if config_manager.delete_configuration(config_id):
            return {"status": "deleted"}
        else:
            raise HTTPException(status_code=404, detail="Configuration not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))