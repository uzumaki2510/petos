import pytest
import asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker
from petos_api.services.auth_service import AuthService
from petos_api.services.project_service import ProjectService
from petos_api.services.task_service import TaskService
from petos_api.schemas.auth import RegisterRequest
from petos_api.schemas.project import ProjectCreateRequest
from petos_api.schemas.task import TaskCreateRequest
from petos_api.schemas.dependency import DependencyCreateRequest
from petos_api.repositories.membership_repository import MembershipRepository
from petos_api.core.errors import AppError


@pytest.mark.asyncio
async def test_concurrent_circular_dependency_locking(engine):
    """
    Test that concurrent requests attempting A->B and B->A simultaneously
    are serialized by pg_advisory_xact_lock. Exactly one succeeds, the other fails.
    """
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    # 1. Setup User, Org, Project, and Tasks A and B
    async with async_session() as session:
        auth_service = AuthService(session)
        user, _ = await auth_service.register(
            RegisterRequest(
                email="conc_dep@example.com",
                password="SuperPassword123!",
                display_name="Conc User",
            )
        )
        membership_repo = MembershipRepository(session)
        orgs, _ = await membership_repo.get_organizations_for_user(user.id)
        org_id = orgs[0].id

        proj_service = ProjectService(session)
        project = await proj_service.create_project(
            user.id, org_id, ProjectCreateRequest(name="Conc Dep Proj", key="CDEP")
        )

        task_service = TaskService(session)
        tA = await task_service.create_task(
            user.id, project.id, TaskCreateRequest(title="Task A")
        )
        tB = await task_service.create_task(
            user.id, project.id, TaskCreateRequest(title="Task B")
        )

        user_id = user.id
        taskA_id = tA.id
        taskB_id = tB.id

    # Task function for worker 1: A depends on B
    async def try_add_A_depends_on_B():
        async with async_session() as s:
            srv = TaskService(s)
            try:
                await srv.add_dependency(
                    user_id,
                    taskA_id,
                    DependencyCreateRequest(depends_on_task_id=taskB_id),
                )
                return True, None
            except Exception as e:
                return False, e

    # Task function for worker 2: B depends on A
    async def try_add_B_depends_on_A():
        async with async_session() as s:
            srv = TaskService(s)
            try:
                await srv.add_dependency(
                    user_id,
                    taskB_id,
                    DependencyCreateRequest(depends_on_task_id=taskA_id),
                )
                return True, None
            except Exception as e:
                return False, e

    # Run simultaneously
    res1, res2 = await asyncio.gather(
        try_add_A_depends_on_B(), try_add_B_depends_on_A(), return_exceptions=True
    )

    successes = [r for r in [res1, res2] if r[0] is True]
    failures = [r for r in [res1, res2] if r[0] is False]

    assert len(successes) == 1, f"Expected exactly 1 success, got {len(successes)}"
    assert len(failures) == 1, f"Expected exactly 1 failure, got {len(failures)}"

    exc = failures[0][1]
    assert isinstance(exc, AppError)
    assert exc.status_code == 400
    assert exc.code == "circular_dependency_detected"
