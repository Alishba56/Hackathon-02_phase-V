"""
Chat API request and response schemas using Pydantic.
Defines the structure for chat endpoint communication.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatRequest(BaseModel):
    """Request schema for chat endpoint"""
    conversation_id: Optional[str] = Field(
        None,
        description="Optional conversation ID to continue existing conversation. If not provided, a new conversation will be created."
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="User's natural language message"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "660e8400-e29b-41d4-a716-446655440000",
                "message": "Add task: Buy groceries"
            }
        }


class ToolCallResult(BaseModel):
    """Result of a tool call execution"""
    name: str = Field(..., description="Name of the tool that was called")
    parameters: Dict[str, Any] = Field(..., description="Parameters passed to the tool")
    result: Dict[str, Any] = Field(..., description="Result returned by the tool")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "add_task",
                "parameters": {"title": "Buy groceries"},
                "result": {
                    "success": True,
                    "data": {
                        "id": "770e8400-e29b-41d4-a716-446655440000",
                        "title": "Buy groceries",
                        "completed": False
                    }
                }
            }
        }


class ChatResponse(BaseModel):
    """Response schema for chat endpoint"""
    conversation_id: str = Field(..., description="Conversation ID (new or existing)")
    response: str = Field(..., description="Chatbot's natural language response")
    tool_calls: Optional[List[ToolCallResult]] = Field(
        None,
        description="List of tools called during processing (for transparency)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "660e8400-e29b-41d4-a716-446655440000",
                "response": "✓ Task 'Buy groceries' add kar diya gaya!",
                "tool_calls": [
                    {
                        "name": "add_task",
                        "parameters": {"title": "Buy groceries"},
                        "result": {
                            "success": True,
                            "data": {
                                "id": "770e8400-e29b-41d4-a716-446655440000",
                                "title": "Buy groceries",
                                "completed": False
                            }
                        }
                    }
                ]
            }
        }


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str = Field(..., description="Error type or summary")
    detail: Optional[str] = Field(None, description="Detailed error message")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Bad request",
                "detail": "Message cannot be empty"
            }
        }
