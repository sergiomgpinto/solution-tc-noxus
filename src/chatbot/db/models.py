from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(),
        onupdate=datetime.now()
    )


class Conversation(Base):
    __tablename__ = "conversations"

    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"

    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE")
    )
    role: Mapped[str] = mapped_column(String(50))
    content: Mapped[str] = mapped_column(Text)
    conversation: Mapped["Conversation"] = relationship(back_populates="messages")
    feedbacks: Mapped[list["Feedback"]] = relationship(
        back_populates="message",
        cascade="all, delete-orphan"
    )


class KnowledgeSource(Base):
    __tablename__ = "knowledge_sources"

    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    collection_name: Mapped[str] = mapped_column(String(255), unique=True)
    document_count: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(default=True)


class Feedback(Base):
    __tablename__ = "feedback"

    message_id: Mapped[int] = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE")
    )
    feedback_type: Mapped[str] = mapped_column(String(50))
    # value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    message: Mapped["Message"] = relationship(back_populates="feedbacks")


class Configuration(Base):
    __tablename__ = "configurations"

    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    config_json: Mapped[dict] = mapped_column(JSON)
    version: Mapped[int] = mapped_column(Integer, default=1)
    is_active: Mapped[bool] = mapped_column(default=False)
    tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    @property
    def tag_list(self) -> List[str]:
        return self.tags.split(",") if self.tags else []

    @tag_list.setter
    def tag_list(self, tags: List[str]) -> None:
        self.tags = ",".join(tags) if tags else None


class ABTest(Base):
    __tablename__ = "ab_tests"

    name: Mapped[str] = mapped_column(String(255), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    control_config_id: Mapped[int] = mapped_column(ForeignKey("configurations.id"))
    treatment_config_id: Mapped[int] = mapped_column(ForeignKey("configurations.id"))
    traffic_percentage: Mapped[int] = mapped_column(Integer, default=50)  # % to treatment
    is_active: Mapped[bool] = mapped_column(default=True)

    # Relationships
    control_config: Mapped["Configuration"] = relationship(foreign_keys=[control_config_id])
    treatment_config: Mapped["Configuration"] = relationship(foreign_keys=[treatment_config_id])
    assignments: Mapped[List["ABTestAssignment"]] = relationship(
        back_populates="test",
        cascade="all, delete-orphan"
    )


class ABTestAssignment(Base):
    __tablename__ = "ab_test_assignments"

    user_identifier: Mapped[str] = mapped_column(String(255))  # Could be session_id or user_id
    test_id: Mapped[int] = mapped_column(ForeignKey("ab_tests.id"))
    variant: Mapped[str] = mapped_column(String(50))  # 'control' or 'treatment'

    test: Mapped["ABTest"] = relationship(back_populates="assignments")
