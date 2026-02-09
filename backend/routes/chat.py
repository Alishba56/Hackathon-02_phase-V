"""
Chat API endpoint for AI chatbot integration.
Handles natural language task management through conversational interface.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import Annotated, List
from db import get_session
from auth import get_current_user
from models import User, Conversation, Message
from chat_schemas import ChatRequest, ChatResponse, ErrorResponse
from chat_agent import ChatAgent
import logging

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])


@router.post(
    "/{user_id}/chat",
    response_model=ChatResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid message or validation error"},
        401: {"model": ErrorResponse, "description": "Missing or invalid authentication token"},
        403: {"model": ErrorResponse, "description": "User doesn't have permission to access this resource"},
        500: {"model": ErrorResponse, "description": "Internal server error or Cohere API failure"}
    },
    summary="Send message to AI chatbot",
    description="""
    Send a natural language message to the AI chatbot for task management.

    The chatbot can execute the following operations:
    - **Task Management**: Add, list, complete, delete, and update tasks
    - **User Profile**: Query user information (email, name, account creation date)
    - **Multilingual**: Supports English and Urdu natural language commands

    **Examples:**
    - "Add task: Buy groceries"
    - "Show all my pending tasks"
    - "Mark task X as complete"
    - "What is my email?"
    - "Mera naam kya hai?" (Urdu: What is my name?)

    **Features:**
    - Conversation history is automatically persisted
    - Tool calls are executed in parallel for better performance
    - Responses include action confirmations and friendly messages
    - Maximum message length: 5000 characters

    **Authentication:**
    Requires JWT token in Authorization header: `Bearer <token>`
    """,
    tags=["AI Chatbot"]
)
async def chat(
    user_id: str,
    request: ChatRequest,
    session: Annotated[Session, Depends(get_session)],
    current_user_id: str = Depends(get_current_user)
):
    """
    Chat endpoint for natural language task management.

    Args:
        user_id: User ID from path (must match authenticated user)
        request: Chat request with message and optional conversation_id
        session: Database session
        current_user_id: Authenticated user ID from JWT

    Returns:
        ChatResponse with conversation_id, response text, and tool calls

    Raises:
        HTTPException: 403 if user_id doesn't match authenticated user
        HTTPException: 400 if message is invalid
        HTTPException: 500 if processing fails
    """
    # Verify user_id matches authenticated user
    if current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this resource"
        )

    # Validate message
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty"
        )

    # Validate message length (max 5000 characters)
    if len(request.message) > 5000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message is too long. Maximum 5000 characters allowed."
        )

    try:
        logger.info(f"Chat request from user {user_id}")

        # Initialize chat agent
        agent = ChatAgent(session, user_id)

        # Process message
        conversation_id, response_text, tool_calls = agent.process_message(
            message=request.message,
            conversation_id=request.conversation_id
        )

        # Format tool calls for response
        formatted_tool_calls = None
        if tool_calls:
            formatted_tool_calls = [
                {
                    "name": tc["name"],
                    "parameters": tc["parameters"],
                    "result": tc["result"]
                }
                for tc in tool_calls
            ]

        return ChatResponse(
            conversation_id=conversation_id,
            response=response_text,
            tool_calls=formatted_tool_calls
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat message: {str(e)}"
        )


@router.get(
    "/{user_id}/conversations/{conversation_id}/messages",
    summary="Get conversation history",
    description="""
    Retrieve all messages from a specific conversation in chronological order.

    **Use Cases:**
    - Load conversation history when reopening chat window
    - Display past interactions with the AI chatbot
    - Restore context after page refresh or session restart

    **Response Format:**
    Returns all messages with:
    - Message ID, role (user/assistant), content
    - Tool calls metadata (if any tools were executed)
    - Timestamps for each message

    **Authentication:**
    Requires JWT token. Users can only access their own conversations.
    """,
    tags=["AI Chatbot"]
)
async def get_conversation_messages(
    user_id: str,
    conversation_id: str,
    session: Annotated[Session, Depends(get_session)],
    current_user_id: str = Depends(get_current_user)
):
    """
    Get conversation history endpoint.

    Args:
        user_id: User ID from path (must match authenticated user)
        conversation_id: Conversation ID to retrieve messages from
        session: Database session
        current_user_id: Authenticated user ID from JWT

    Returns:
        List of messages in chronological order

    Raises:
        HTTPException: 403 if user_id doesn't match or conversation not found
    """
    # Verify user_id matches authenticated user
    if current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this resource"
        )

    try:
        # Verify conversation belongs to user
        conversation = session.get(Conversation, conversation_id)
        if not conversation or conversation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Get all messages for this conversation
        query = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        messages = session.exec(query).all()

        # Format messages for response
        formatted_messages = [
            {
                "id": msg.id,
                "role": msg.role.value,
                "content": msg.content,
                "tool_calls": msg.tool_calls,
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ]

        return {
            "conversation_id": conversation_id,
            "messages": formatted_messages
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve conversation history: {str(e)}"
        )
