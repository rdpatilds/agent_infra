"""Example API routes for Celery task management."""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from app.core.celery_utils import get_task_result
from app.example.tasks import process_data, send_email

router = APIRouter(prefix="/example", tags=["example"])


class EmailRequest(BaseModel):
    """Request model for sending emails."""

    to: EmailStr
    subject: str
    body: str


class DataRequest(BaseModel):
    """Request model for data processing."""

    data: dict[str, Any]


class TaskResponse(BaseModel):
    """Response model for task submission."""

    task_id: str
    status: str
    message: str


class TaskStatusResponse(BaseModel):
    """Response model for task status."""

    task_id: str
    state: str
    result: Any | None = None
    error: str | None = None


@router.post("/send-email", response_model=TaskResponse)
async def trigger_send_email(request: EmailRequest) -> TaskResponse:
    """Trigger an async email sending task.

    Args:
        request: Email request with recipient, subject, and body

    Returns:
        TaskResponse with task_id for tracking
    """
    task = send_email.delay(to=request.to, subject=request.subject, body=request.body)

    return TaskResponse(
        task_id=task.id,
        status="queued",
        message=f"Email task queued with ID: {task.id}",
    )


@router.post("/process-data", response_model=TaskResponse)
async def trigger_process_data(request: DataRequest) -> TaskResponse:
    """Trigger an async data processing task.

    Args:
        request: Data processing request

    Returns:
        TaskResponse with task_id for tracking
    """
    task = process_data.delay(data=request.data)

    return TaskResponse(
        task_id=task.id,
        status="queued",
        message=f"Data processing task queued with ID: {task.id}",
    )


@router.get("/task/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str) -> TaskStatusResponse:
    """Get the status of a task by its ID.

    Args:
        task_id: The Celery task ID to check

    Returns:
        TaskStatusResponse with current task state and result

    Raises:
        HTTPException: If task_id is invalid
    """
    try:
        result = get_task_result(task_id)

        response = TaskStatusResponse(
            task_id=task_id,
            state=result.state,
        )

        if result.state == "SUCCESS":
            response.result = result.result
        elif result.state == "FAILURE":
            response.error = str(result.info)
        elif result.state == "PENDING":
            response.result = None
        else:
            # STARTED, RETRY, etc.
            response.result = result.info

        return response

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid task ID: {e!s}") from e
