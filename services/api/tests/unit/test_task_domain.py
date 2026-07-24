import pytest
from petos_api.services.task_service import TaskService
from petos_api.schemas.task import (
    TaskCreateRequest,
    TaskTransitionRequest,
)


def test_status_transition_rules():
    allowed = TaskService.ALLOWED_TRANSITIONS

    # Valid transitions
    assert "ready" in allowed["backlog"]
    assert "in_progress" in allowed["ready"]
    assert "review" in allowed["in_progress"]
    assert "completed" in allowed["review"]
    assert "in_progress" in allowed["completed"]
    assert "backlog" in allowed["cancelled"]

    # Invalid transitions
    assert "completed" not in allowed["backlog"]
    assert "in_progress" not in allowed["backlog"]
    assert "completed" not in allowed["in_progress"]
    assert "cancelled" not in allowed["completed"]


def test_task_create_schema_validation():
    # Title non-empty validation
    with pytest.raises(ValueError):
        TaskCreateRequest(title="", priority="medium")

    # Priority pattern validation
    with pytest.raises(ValueError):
        TaskCreateRequest(title="Valid Title", priority="ultra_high")


def test_task_transition_schema_validation():
    # Target status validation
    with pytest.raises(ValueError):
        TaskTransitionRequest(
            expected_version=1, target_status="archived"
        )  # archived is NOT in status enum!
