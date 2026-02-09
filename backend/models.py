from sqlmodel import SQLModel, Field, Column
from sqlalchemy import TIMESTAMP, JSON
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class MessageRole(str, Enum):
    """Message role for chat conversations"""
    user = "user"
    assistant = "assistant"


class User(SQLModel, table=True):
    """User model - managed by Better Auth integration"""
    __tablename__ = "users"

    id: str = Field(primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str
    password_hash: str = Field()  # Stores bcrypt hashed password
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Task(SQLModel, table=True):
    """Task model with user ownership and indexes for performance"""
    __tablename__ = "tasks"

    id: Optional[str] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False, index=True)
    priority: str = Field(default="medium")  # low, medium, high, urgent
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSON))  # JSONB array
    due_date: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP(timezone=True)))
    remind_at: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP(timezone=True)))
    recurrence_rule: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))  # JSONB object
    reminded: bool = Field(default=False)  # Internal flag for reminder tracking
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Conversation(SQLModel, table=True):
    """Conversation model for AI chatbot - Phase III"""
    __tablename__ = "conversations"

    id: Optional[str] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Message(SQLModel, table=True):
    """Message model for chat conversations - Phase III"""
    __tablename__ = "messages"

    id: Optional[str] = Field(default=None, primary_key=True)
    conversation_id: str = Field(foreign_key="conversations.id", index=True)
    role: MessageRole = Field()
    content: str = Field(max_length=10000)
    tool_calls: Optional[str] = Field(default=None)  # JSON string for tool call metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
