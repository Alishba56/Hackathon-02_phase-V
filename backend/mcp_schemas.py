"""
MCP (Model Context Protocol) tool schemas in Cohere-compatible format.
Defines the structure and parameters for all AI chatbot tools.
"""
from typing import Dict, List, Any


# MCP Tool Schemas for Cohere API
MCP_TOOLS: List[Dict[str, Any]] = [
    {
        "name": "add_task",
        "description": "Create a new task for the authenticated user. Use this when the user wants to add, create, or make a new todo item. Supports priority levels, tags, due dates, reminders, and recurrence.",
        "parameter_definitions": {
            "title": {
                "type": "string",
                "description": "The title or name of the task. This is the main description of what needs to be done.",
                "required": True
            },
            "description": {
                "type": "string",
                "description": "Optional detailed description or notes about the task. Provides additional context.",
                "required": False
            },
            "priority": {
                "type": "string",
                "description": "Priority level: 'low', 'medium' (default), 'high', or 'urgent'. Use this when user specifies importance.",
                "required": False
            },
            "tags": {
                "type": "array",
                "description": "Array of tag strings for categorization (e.g., ['work', 'urgent']). Use when user mentions categories or labels.",
                "required": False
            },
            "due_date": {
                "type": "string",
                "description": "Due date in ISO format (e.g., '2026-02-15T10:00:00'). Use when user specifies a deadline.",
                "required": False
            },
            "remind_at": {
                "type": "string",
                "description": "Reminder time in ISO format (e.g., '2026-02-15T09:00:00'). Use when user wants a reminder.",
                "required": False
            },
            "recurrence_rule": {
                "type": "object",
                "description": "Recurrence pattern with 'frequency' (daily/weekly/monthly/custom), 'interval' (number), and optional 'end_date'. Use for recurring tasks.",
                "required": False
            }
        }
    },
    {
        "name": "list_tasks",
        "description": "List tasks. The tool returns a formatted table in markdown code block. Display it exactly as provided.",
        "parameter_definitions": {
            "status": {
                "type": "string",
                "description": "Filter: 'pending', 'completed', or omit for all",
                "required": False
            }
        }
    },
    {
        "name": "complete_task",
        "description": "Mark a task as completed. Use this when the user indicates they have finished or completed a task.",
        "parameter_definitions": {
            "task_id": {
                "type": "string",
                "description": "The unique identifier (UUID) of the task to mark as complete.",
                "required": True
            }
        }
    },
    {
        "name": "delete_task",
        "description": "Permanently delete a task. Use this when the user wants to remove or delete a task from their list.",
        "parameter_definitions": {
            "task_id": {
                "type": "string",
                "description": "The unique identifier (UUID) of the task to delete.",
                "required": True
            }
        }
    },
    {
        "name": "update_task",
        "description": "Update one or more fields of an existing task. Use this when the user wants to change, modify, or edit a task. Supports updating priority, tags, due dates, reminders, and recurrence.",
        "parameter_definitions": {
            "task_id": {
                "type": "string",
                "description": "The unique identifier (UUID) of the task to update.",
                "required": True
            },
            "title": {
                "type": "string",
                "description": "New title for the task",
                "required": False
            },
            "description": {
                "type": "string",
                "description": "New description for the task",
                "required": False
            },
            "completed": {
                "type": "boolean",
                "description": "New completion status",
                "required": False
            },
            "priority": {
                "type": "string",
                "description": "New priority level: 'low', 'medium', 'high', or 'urgent'",
                "required": False
            },
            "tags": {
                "type": "array",
                "description": "New array of tag strings for categorization",
                "required": False
            },
            "due_date": {
                "type": "string",
                "description": "New due date in ISO format (e.g., '2026-02-15T10:00:00')",
                "required": False
            },
            "remind_at": {
                "type": "string",
                "description": "New reminder time in ISO format",
                "required": False
            },
            "recurrence_rule": {
                "type": "object",
                "description": "New recurrence pattern with 'frequency', 'interval', and optional 'end_date'",
                "required": False
            }
        }
    },
    {
        "name": "get_user_profile",
        "description": "Retrieve the authenticated user's profile information including ID, email, name, and account creation date. Use this when the user asks about their account, email, name, or profile.",
        "parameter_definitions": {}
    }
]


def get_mcp_tools() -> List[Dict[str, Any]]:
    """
    Get all MCP tool definitions for Cohere API.

    Returns:
        List of tool definitions in Cohere-compatible format
    """
    return MCP_TOOLS
