"""
Chat agent runner with Cohere integration and tool calling.
Handles conversation management, tool execution, and response generation.
"""
from typing import List, Dict, Any, Optional, Tuple
from sqlmodel import Session, select
from models import Conversation, Message, MessageRole
from mcp_tools import MCPToolExecutor
from mcp_schemas import get_mcp_tools
from cohere_client import get_cohere_client
from datetime import datetime
import uuid
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ChatAgent:
    """Main chat agent with Cohere tool calling integration"""

    def __init__(self, session: Session, user_id: str):
        """
        Initialize chat agent.

        Args:
            session: Database session
            user_id: Authenticated user ID
        """
        self.session = session
        self.user_id = user_id
        self.cohere_client = get_cohere_client()
        self.tool_executor = MCPToolExecutor(session, user_id)
        self.model = "command-r-08-2024"  # Current working model (Sept 2025+)

    def process_message(
        self,
        message: str,
        conversation_id: Optional[str] = None
    ) -> Tuple[str, str, List[Dict[str, Any]]]:
        """
        Process a user message and return response.

        Args:
            message: User's message
            conversation_id: Optional existing conversation ID

        Returns:
            Tuple of (conversation_id, response_text, tool_calls)
        """
        # Get or create conversation
        conversation = self._get_or_create_conversation(conversation_id)

        # Load conversation history (last 20 messages)
        history = self._load_conversation_history(conversation.id)

        # Save user message
        self._save_message(conversation.id, MessageRole.user, message)

        # Call Cohere with tools
        try:
            tool_calls_data = []

            logger.info(f"Processing message for user {self.user_id}, conversation {conversation.id}")

            # Initial call to Cohere
            response = self.cohere_client.chat(
                message=message,
                model=self.model,
                tools=get_mcp_tools(),
                chat_history=history,
                preamble="""You are a helpful task management assistant with advanced features.

Tasks support the following fields:
- title (required): Task title
- description (optional): Detailed description
- priority (optional): Priority level - low, medium (default), high, or urgent
- tags (optional): Array of tag strings for categorization
- due_date (optional): Due date in ISO format (e.g., 2026-02-15T10:00:00)
- remind_at (optional): Reminder time in ISO format
- recurrence_rule (optional): Recurrence pattern with frequency (daily/weekly/monthly/custom), interval, and optional end_date
- completed: Completion status (true/false)

When users ask to create tasks with priorities, tags, due dates, or reminders, use the appropriate parameters in the add_task tool.

When displaying task lists, you MUST output the exact text from the tool's 'data' field without any modifications, summaries, or interpretations. Do not count, group, or reformat tasks - just show the exact formatted string provided by the tool."""
            )

            # Check if tools were called
            if response.tool_calls:
                logger.info(f"Tool calls detected: {len(response.tool_calls)} tools")
                # Execute tools in parallel
                tool_results = self._execute_tools(response.tool_calls)
                tool_calls_data = tool_results

                # Get final response with tool results using single step mode
                response = self.cohere_client.chat(
                    message="",  # Empty message when providing tool results
                    model=self.model,
                    tools=get_mcp_tools(),
                    tool_results=self._format_tool_results_for_cohere(tool_results),
                    chat_history=history,
                    force_single_step=True,  # Required for tool results
                    preamble="You are a task management assistant. When the list_tasks tool returns data, output it EXACTLY as provided without any interpretation, counting, grouping, or reformatting. Just show the raw data field content."
                )

            # Get response text
            response_text = response.text

            # Save assistant message with tool calls
            self._save_message(
                conversation.id,
                MessageRole.assistant,
                response_text,
                tool_calls_data if tool_calls_data else None
            )

            # Update conversation timestamp
            conversation.updated_at = datetime.utcnow()
            self.session.commit()

            logger.info(f"Message processed successfully for conversation {conversation.id}")
            return conversation.id, response_text, tool_calls_data

        except Exception as e:
            # Handle Cohere API errors
            logger.error(f"Error processing message: {str(e)}", exc_info=True)

            # Provide user-friendly error messages
            if "rate limit" in str(e).lower():
                error_message = "I'm experiencing high demand right now. Please try again in a moment."
            elif "timeout" in str(e).lower():
                error_message = "The request took too long. Please try again."
            elif "api key" in str(e).lower():
                error_message = "Service is temporarily unavailable. Please contact support."
            else:
                error_message = "I'm sorry, I encountered an error processing your request. Please try again."

            self._save_message(conversation.id, MessageRole.assistant, error_message)
            return conversation.id, error_message, []

    def _get_or_create_conversation(self, conversation_id: Optional[str]) -> Conversation:
        """Get existing conversation or create new one"""
        if conversation_id:
            conversation = self.session.get(Conversation, conversation_id)
            if conversation and conversation.user_id == self.user_id:
                return conversation

        # Create new conversation
        conversation = Conversation(
            id=str(uuid.uuid4()),
            user_id=self.user_id
        )
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)
        return conversation

    def _load_conversation_history(self, conversation_id: str) -> List[Dict[str, str]]:
        """
        Load last 20 messages from conversation for Cohere context.

        Args:
            conversation_id: Conversation UUID

        Returns:
            List of message dicts in Cohere format
        """
        query = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(20)
        )
        messages = self.session.exec(query).all()

        # Reverse to chronological order
        messages = list(reversed(messages))

        # Convert to Cohere format
        history = []
        for msg in messages:
            # Map database roles to Cohere's expected roles
            cohere_role = "User" if msg.role == MessageRole.user else "Chatbot"

            history.append({
                "role": cohere_role,
                "message": msg.content
            })

        return history

    def _save_message(
        self,
        conversation_id: str,
        role: MessageRole,
        content: str,
        tool_calls: Optional[List[Dict[str, Any]]] = None
    ):
        """Save message to database"""
        message = Message(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_calls=json.dumps(tool_calls) if tool_calls else None
        )
        self.session.add(message)
        self.session.commit()

        # Auto-generate conversation title from first user message
        if role == MessageRole.user:
            conversation = self.session.get(Conversation, conversation_id)
            if conversation and not conversation.title:
                conversation.title = self._generate_title(content)
                self.session.commit()

    def _generate_title(self, first_message: str) -> str:
        """
        Generate conversation title from first message.

        Args:
            first_message: First user message

        Returns:
            Generated title (max 50 chars, truncated at word boundary)
        """
        max_length = 50
        if len(first_message) <= max_length:
            return first_message

        truncated = first_message[:max_length]
        last_space = truncated.rfind(' ')
        if last_space > 0:
            truncated = truncated[:last_space]

        return truncated + "..."

    def _execute_tools(self, tool_calls) -> List[Dict[str, Any]]:
        """
        Execute tool calls in parallel.

        Args:
            tool_calls: Cohere tool calls

        Returns:
            List of tool call results
        """
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.name
            parameters = tool_call.parameters

            logger.info(f"Executing tool: {tool_name} with parameters: {parameters}")

            # Execute tool
            result = self.tool_executor.execute_tool(tool_name, parameters)

            if not result.get('success'):
                logger.warning(f"Tool execution failed: {tool_name} - {result.get('error')}")

            results.append({
                "name": tool_name,
                "parameters": parameters,
                "result": result
            })

        return results

    def _format_tool_results_for_cohere(
        self,
        tool_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Format tool results for Cohere API.

        Args:
            tool_results: Tool execution results

        Returns:
            Formatted results for Cohere
        """
        formatted = []
        for result in tool_results:
            formatted.append({
                "call": {
                    "name": result["name"],
                    "parameters": result["parameters"]
                },
                "outputs": [result["result"]]
            })
        return formatted
