import pytest
import uuid
from petos_api.services.auth_service import AuthService
from petos_api.services.project_service import ProjectService
from petos_api.services.task_service import TaskService
from petos_api.schemas.auth import RegisterRequest
from petos_api.schemas.project import ProjectCreateRequest
from petos_api.schemas.task import (
    TaskCreateRequest,
    TaskUpdateRequest,
    TaskTransitionRequest,
    TaskArchiveRequest,
)
from petos_api.schemas.comment import CommentCreateRequest, CommentUpdateRequest
from petos_api.schemas.dependency import DependencyCreateRequest
from petos_api.repositories.membership_repository import MembershipRepository
from petos_api.core.errors import AppError


@pytest.mark.asyncio
async def test_full_task_lifecycle(db_session):
    # Setup User & Org & Project
    auth_service = AuthService(db_session)
    user1, _ = await auth_service.register(
        RegisterRequest(
            email="t1@example.com", password="SuperPassword123!", display_name="User 1"
        )
    )
    membership_repo = MembershipRepository(db_session)
    orgs, _ = await membership_repo.get_organizations_for_user(user1.id)
    org_id = orgs[0].id

    proj_service = ProjectService(db_session)
    project = await proj_service.create_project(
        user1.id, org_id, ProjectCreateRequest(name="Lifecycle Proj", key="LIFE")
    )

    task_service = TaskService(db_session)

    # 1. Create Task -> PET-1 (LIFE-1)
    task1 = await task_service.create_task(
        user1.id,
        project.id,
        TaskCreateRequest(title="Task One", description="First task", priority="high"),
    )
    assert task1.display_id == "LIFE-1"
    assert task1.status == "backlog"
    assert task1.version == 1

    # 2. Transition backlog -> ready
    task1 = await task_service.transition_task(
        user1.id,
        task1.id,
        TaskTransitionRequest(expected_version=1, target_status="ready"),
    )
    assert task1.status == "ready"
    assert task1.version == 2

    # 3. Transition ready -> in_progress (started_at set)
    task1 = await task_service.transition_task(
        user1.id,
        task1.id,
        TaskTransitionRequest(expected_version=2, target_status="in_progress"),
    )
    assert task1.status == "in_progress"
    assert task1.started_at is not None
    assert task1.version == 3

    # 4. Transition in_progress -> review
    task1 = await task_service.transition_task(
        user1.id,
        task1.id,
        TaskTransitionRequest(expected_version=3, target_status="review"),
    )
    assert task1.status == "review"
    assert task1.version == 4

    # 5. Transition review -> completed (completed_at set)
    task1 = await task_service.transition_task(
        user1.id,
        task1.id,
        TaskTransitionRequest(expected_version=4, target_status="completed"),
    )
    assert task1.status == "completed"
    assert task1.completed_at is not None
    assert task1.version == 5

    # 6. Reopen completed -> in_progress requires reason
    with pytest.raises(AppError) as exc_info:
        await task_service.transition_task(
            user1.id,
            task1.id,
            TaskTransitionRequest(expected_version=5, target_status="in_progress"),
        )
    assert exc_info.value.code == "transition_reason_required"

    # Reopen with reason succeeds, clears completed_at
    task1 = await task_service.transition_task(
        user1.id,
        task1.id,
        TaskTransitionRequest(
            expected_version=5, target_status="in_progress", reason="Needs fix"
        ),
    )
    assert task1.status == "in_progress"
    assert task1.completed_at is None
    assert task1.version == 6


@pytest.mark.asyncio
async def test_task_occ_concurrency_conflict(db_session):
    auth_service = AuthService(db_session)
    user1, _ = await auth_service.register(
        RegisterRequest(
            email="occ@example.com",
            password="SuperPassword123!",
            display_name="User OCC",
        )
    )
    membership_repo = MembershipRepository(db_session)
    orgs, _ = await membership_repo.get_organizations_for_user(user1.id)
    org_id = orgs[0].id

    proj_service = ProjectService(db_session)
    project = await proj_service.create_project(
        user1.id, org_id, ProjectCreateRequest(name="OCC Proj", key="OCC")
    )

    task_service = TaskService(db_session)
    task = await task_service.create_task(
        user1.id, project.id, TaskCreateRequest(title="OCC Task")
    )
    assert task.version == 1

    # Stale version update returns 409
    with pytest.raises(AppError) as exc_info:
        await task_service.update_task(
            user1.id,
            task.id,
            TaskUpdateRequest(expected_version=99, title="Stale Title"),
        )
    assert exc_info.value.status_code == 409
    assert exc_info.value.code == "concurrency_conflict"


@pytest.mark.asyncio
async def test_archived_task_read_only(db_session):
    auth_service = AuthService(db_session)
    user1, _ = await auth_service.register(
        RegisterRequest(
            email="arch@example.com",
            password="SuperPassword123!",
            display_name="Arch User",
        )
    )
    membership_repo = MembershipRepository(db_session)
    orgs, _ = await membership_repo.get_organizations_for_user(user1.id)
    org_id = orgs[0].id

    proj_service = ProjectService(db_session)
    project = await proj_service.create_project(
        user1.id, org_id, ProjectCreateRequest(name="Arch Proj", key="ARCH")
    )

    task_service = TaskService(db_session)
    task = await task_service.create_task(
        user1.id, project.id, TaskCreateRequest(title="Archived Task")
    )

    # Archive task
    archived_task = await task_service.archive_task(
        user1.id,
        task.id,
        TaskArchiveRequest(expected_version=1, reason="Completed project"),
    )
    assert archived_task.archived_at is not None

    # Mutation attempt on archived task returns 409 task_archived
    with pytest.raises(AppError) as exc_info:
        await task_service.update_task(
            user1.id, task.id, TaskUpdateRequest(expected_version=2, title="New Title")
        )
    assert exc_info.value.status_code == 409
    assert exc_info.value.code == "task_archived"


@pytest.mark.asyncio
async def test_comment_editing_permissions(db_session):
    auth_service = AuthService(db_session)
    u1, _ = await auth_service.register(
        RegisterRequest(
            email="c1@example.com", password="SuperPassword123!", display_name="User 1"
        )
    )
    u2, _ = await auth_service.register(
        RegisterRequest(
            email="c2@example.com", password="SuperPassword123!", display_name="User 2"
        )
    )

    membership_repo = MembershipRepository(db_session)
    orgs, _ = await membership_repo.get_organizations_for_user(u1.id)
    org_id = orgs[0].id

    # Add u2 to u1's org
    from petos_api.models.organization_membership import OrganizationMembership

    membership_repo.add(
        OrganizationMembership(
            id=uuid.uuid4(), organization_id=org_id, user_id=u2.id, role="member"
        )
    )
    await db_session.commit()

    proj_service = ProjectService(db_session)
    project = await proj_service.create_project(
        u1.id, org_id, ProjectCreateRequest(name="Comment Proj", key="COMM")
    )

    task_service = TaskService(db_session)
    task = await task_service.create_task(
        u1.id, project.id, TaskCreateRequest(title="Comment Task")
    )

    comment = await task_service.add_comment(
        u1.id, task.id, CommentCreateRequest(body="Original comment")
    )
    assert comment.version == 1

    # u2 attempts to edit u1's comment -> 403 comment_not_owned
    with pytest.raises(AppError) as exc_info:
        await task_service.update_comment(
            u2.id,
            comment.id,
            CommentUpdateRequest(expected_version=1, body="Hacked comment"),
        )
    assert exc_info.value.status_code == 403
    assert exc_info.value.code == "comment_not_owned"

    # u1 edits own comment -> succeeds
    updated = await task_service.update_comment(
        u1.id,
        comment.id,
        CommentUpdateRequest(expected_version=1, body="Edited comment"),
    )
    assert updated.body == "Edited comment"
    assert updated.version == 2


@pytest.mark.asyncio
async def test_circular_dependency_rejection(db_session):
    auth_service = AuthService(db_session)
    u1, _ = await auth_service.register(
        RegisterRequest(
            email="dep@example.com",
            password="SuperPassword123!",
            display_name="Dep User",
        )
    )
    membership_repo = MembershipRepository(db_session)
    orgs, _ = await membership_repo.get_organizations_for_user(u1.id)
    org_id = orgs[0].id

    proj_service = ProjectService(db_session)
    project = await proj_service.create_project(
        u1.id, org_id, ProjectCreateRequest(name="Dep Proj", key="DEP")
    )

    task_service = TaskService(db_session)
    tA = await task_service.create_task(
        u1.id, project.id, TaskCreateRequest(title="Task A")
    )
    tB = await task_service.create_task(
        u1.id, project.id, TaskCreateRequest(title="Task B")
    )

    # tA depends on tB
    await task_service.add_dependency(
        u1.id, tA.id, DependencyCreateRequest(depends_on_task_id=tB.id)
    )

    # Attempting tB depends on tA -> 400 circular_dependency_detected
    with pytest.raises(AppError) as exc_info:
        await task_service.add_dependency(
            u1.id, tB.id, DependencyCreateRequest(depends_on_task_id=tA.id)
        )
    assert exc_info.value.status_code == 400
    assert exc_info.value.code == "circular_dependency_detected"


@pytest.mark.asyncio
async def test_organization_members_endpoint_service(db_session):
    auth_service = AuthService(db_session)
    u1, _ = await auth_service.register(
        RegisterRequest(
            email="m1@example.com",
            password="SuperPassword123!",
            display_name="Member User 1",
        )
    )
    membership_repo = MembershipRepository(db_session)
    orgs, _ = await membership_repo.get_organizations_for_user(u1.id)
    org_id = orgs[0].id

    task_service = TaskService(db_session)
    members, total = await task_service.get_organization_members(u1.id, org_id)

    assert total == 1
    assert members[0].user_id == u1.id
    assert members[0].role == "owner"
