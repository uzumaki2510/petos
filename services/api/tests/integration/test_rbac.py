import pytest
from petos_api.services.organization_service import OrganizationService
from petos_api.services.project_service import ProjectService
from petos_api.services.auth_service import AuthService
from petos_api.schemas.auth import RegisterRequest
from petos_api.schemas.project import ProjectCreateRequest
from petos_api.core.errors import AppError


@pytest.mark.asyncio
async def test_org_and_project_flow(db_session):
    auth_service = AuthService(db_session)
    user_res, _ = await auth_service.register(
        RegisterRequest(
            email="owner@example.com",
            password="SuperSecretPassword123!",
            display_name="Owner User",
        )
    )

    org_service = OrganizationService(db_session)
    orgs, total = await org_service.get_user_organizations(user_res.id)
    assert total == 1
    assert len(orgs) == 1
    org = orgs[0]

    project_service = ProjectService(db_session)
    # Create project
    proj = await project_service.create_project(
        user_res.id,
        org.id,
        ProjectCreateRequest(name="My First Project", description="Test"),
    )
    assert proj.name == "My First Project"
    assert proj.status == "active"

    # Get project
    proj_fetched = await project_service.get_project(user_res.id, proj.id)
    assert proj_fetched.id == proj.id

    # List projects
    projs, p_total = await project_service.get_projects(user_res.id, org.id)
    assert p_total == 1
    assert projs[0].id == proj.id

    # Archive project
    archived_proj = await project_service.archive_project(user_res.id, proj.id)
    assert archived_proj.status == "archived"


@pytest.mark.asyncio
async def test_cross_tenant_access_denied(db_session):
    auth_service = AuthService(db_session)
    owner, _ = await auth_service.register(
        RegisterRequest(
            email="owner2@example.com",
            password="SuperSecretPassword123!",
            display_name="Owner 2",
        )
    )
    stranger, _ = await auth_service.register(
        RegisterRequest(
            email="stranger@example.com",
            password="SuperSecretPassword123!",
            display_name="Stranger",
        )
    )

    org_service = OrganizationService(db_session)
    owner_orgs, _ = await org_service.get_user_organizations(owner.id)
    owner_org = owner_orgs[0]

    project_service = ProjectService(db_session)
    with pytest.raises(AppError) as exc_info:
        await project_service.get_projects(stranger.id, owner_org.id)
    assert exc_info.value.status_code == 404
