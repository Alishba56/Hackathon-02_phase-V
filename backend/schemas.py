from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class TaskCreate(BaseModel):
    """Schema for creating a new task"""
    title: str = Field(..., min_length=1, max_length=200, description="Task title (required)")
    description: Optional[str] = Field(None, max_length=1000, description="Optional detailed description")
    priority: Optional[str] = Field("medium", description="Task priority level (low, medium, high, urgent)")
    tags: Optional[List[str]] = Field(default_factory=list, description="Array of tag strings")
    due_date: Optional[datetime] = Field(None, description="Optional due date with timezone")
    remind_at: Optional[datetime] = Field(None, description="Optional reminder time with timezone")
    recurrence_rule: Optional[Dict[str, Any]] = Field(None, description="Recurrence pattern (frequency, interval, end_date)")

    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v):
        if v and v not in ['low', 'medium', 'high', 'urgent']:
            raise ValueError('Priority must be one of: low, medium, high, urgent')
        return v or 'medium'

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        if v and len(v) > 10:
            raise ValueError('Maximum 10 tags allowed per task')
        if v and any(len(tag) > 50 for tag in v):
            raise ValueError('Each tag must be 50 characters or less')
        return v or []


class TaskUpdate(BaseModel):
    """Schema for updating an existing task - all fields optional"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    completed: Optional[bool] = Field(None, description="Task completion status")
    priority: Optional[str] = Field(None, description="Task priority level (low, medium, high, urgent)")
    tags: Optional[List[str]] = Field(None, description="Array of tag strings")
    due_date: Optional[datetime] = Field(None, description="Task due date with timezone")
    remind_at: Optional[datetime] = Field(None, description="Reminder time with timezone")
    recurrence_rule: Optional[Dict[str, Any]] = Field(None, description="Recurrence pattern")

    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v):
        if v and v not in ['low', 'medium', 'high', 'urgent']:
            raise ValueError('Priority must be one of: low, medium, high, urgent')
        return v

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        if v and len(v) > 10:
            raise ValueError('Maximum 10 tags allowed per task')
        if v and any(len(tag) > 50 for tag in v):
            raise ValueError('Each tag must be 50 characters or less')
        return v


class TaskResponse(BaseModel):
    """Schema for task API responses"""
    id: str
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    priority: str
    tags: List[str]
    due_date: Optional[datetime]
    remind_at: Optional[datetime]
    recurrence_rule: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
