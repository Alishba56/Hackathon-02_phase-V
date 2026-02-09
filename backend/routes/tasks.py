from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
import uuid
import logging

from db import get_session
from auth import get_current_user
from models import Task
from schemas import TaskCreate, TaskUpdate, TaskResponse
from services.dapr_client import DaprClient

router = APIRouter(prefix="/api/tasks", tags=["tasks"])
logger = logging.getLogger(__name__)

# Initialize Dapr client for event publishing
dapr_client = DaprClient()


@router.get("", response_model=List[TaskResponse])
async def list_tasks(
    status: str = Query("all", enum=["all", "pending", "completed"]),
    sort: str = Query("created", enum=["created", "title", "due_date"]),
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    List all tasks for authenticated user with filtering and sorting

    - **status**: Filter by completion status (all/pending/completed)
    - **sort**: Sort by field (created/title/due_date)
    """
    # Build query with user_id filter
    query = select(Task).where(Task.user_id == current_user_id)

    # Apply status filter
    if status == "pending":
        query = query.where(Task.completed == False)
    elif status == "completed":
        query = query.where(Task.completed == True)

    # Apply sorting
    if sort == "created":
        query = query.order_by(Task.created_at.desc())
    elif sort == "title":
        query = query.order_by(Task.title)
    elif sort == "due_date":
        query = query.order_by(Task.due_date.desc())

    tasks = session.exec(query).all()
    return tasks


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    task_data: TaskCreate,
    request: Request,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Create a new task for the authenticated user

    - **title**: Task title (required)
    - **description**: Optional detailed description
    - **priority**: Optional priority level (low/medium/high/urgent)
    - **tags**: Optional array of tag strings
    - **due_date**: Optional due date with timezone
    - **remind_at**: Optional reminder time with timezone
    - **recurrence_rule**: Optional recurrence pattern (frequency, interval, end_date)
    """
    # Validate title is not empty
    if not task_data.title or not task_data.title.strip():
        raise HTTPException(
            status_code=400,
            detail="Task title is required"
        )

    # Create new task with user_id from authenticated user
    task = Task(
        id=str(uuid.uuid4()),
        user_id=current_user_id,
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        tags=task_data.tags,
        due_date=task_data.due_date,
        remind_at=task_data.remind_at,
        recurrence_rule=task_data.recurrence_rule,
        completed=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Retrieve a specific task by ID (must belong to authenticated user)
    """
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    # Check ownership
    if task.user_id != current_user_id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this task"
        )

    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    request: Request,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update an existing task (must belong to authenticated user)

    All fields are optional - only provided fields will be updated
    """
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    # Check ownership
    if task.user_id != current_user_id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this task"
        )

    # Validate title if provided
    if task_data.title is not None and (not task_data.title or not task_data.title.strip()):
        raise HTTPException(
            status_code=400,
            detail="Task title cannot be empty"
        )

    # Update only provided fields
    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    # Publish task-updated event to Kafka via Dapr Pub/Sub
    trace_id = request.headers.get("traceparent", "").split("-")[1] if "traceparent" in request.headers else None

    event_data = {
        "task_id": task.id,
        "user_id": task.user_id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "tags": task.tags,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "updated_at": task.updated_at.isoformat(),
        "updated_fields": list(update_data.keys())
    }

    dapr_client.publish_event(
        topic="task-updates",
        event_type="com.todo.task.updated",
        data=event_data,
        source="backend",
        trace_id=trace_id
    )

    return task


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: str,
    request: Request,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete an existing task (must belong to authenticated user)
    """
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    # Check ownership
    if task.user_id != current_user_id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this task"
        )

    # Capture task data before deletion for event
    task_data_for_event = {
        "task_id": task.id,
        "user_id": task.user_id,
        "title": task.title,
        "deleted_at": datetime.utcnow().isoformat()
    }

    session.delete(task)
    session.commit()

    # Publish task-deleted event to Kafka via Dapr Pub/Sub
    trace_id = request.headers.get("traceparent", "").split("-")[1] if "traceparent" in request.headers else None

    dapr_client.publish_event(
        topic="task-events",
        event_type="com.todo.task.deleted",
        data=task_data_for_event,
        source="backend",
        trace_id=trace_id
    )

    return None


@router.patch("/{task_id}/complete", response_model=TaskResponse)
async def toggle_task_completion(
    task_id: str,
    request: Request,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Toggle the completion status of a task (must belong to authenticated user)
    """
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    # Check ownership
    if task.user_id != current_user_id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this task"
        )

    # Toggle completion status
    task.completed = not task.completed
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    # Publish task-completed event to Kafka via Dapr Pub/Sub
    trace_id = request.headers.get("traceparent", "").split("-")[1] if "traceparent" in request.headers else None

    event_data = {
        "task_id": task.id,
        "user_id": task.user_id,
        "title": task.title,
        "completed": task.completed,
        "completed_at": task.updated_at.isoformat()
    }

    dapr_client.publish_event(
        topic="task-events",
        event_type="com.todo.task.completed" if task.completed else "com.todo.task.uncompleted",
        data=event_data,
        source="backend",
        trace_id=trace_id
    )

    return task
