import pytest
from petos_api.services.auth_service import AuthService
from petos_api.services.organization_service import OrganizationService
from petos_api.services.project_service import ProjectService
from petos_api.repositories.membership_repository import MembershipRepository
from petos_api.models.organization_membership import OrganizationMembership
from petos_api.schemas.auth import RegisterRequest
from petos_api.schemas.organization import OrganizationUpdateRequest
from petos_api.schemas.project import ProjectCreateRequest, ProjectUpdateRequest
from petos_api.core.errors import AppError
import uuid


async def _register(db_session, email: str, name: str):
    auth = AuthService(db_session)
    return await auth.register(
        RegisterRequest(
            email=email,
            password="SuperSecretPassword123!",
            display_name=name,
        )
    )


async def _get_first_org(db_session, user_id):
    org_service = OrganizationService(db_session)
    orgs, _ = await org_service.get_user_organizations(user_id)
    return orgs[0]


async def _add_member(db_session, user_id, org_id, role: str):
    membership = OrganizationMembership(
        id=uuid.uuid4(),
        user_id=user_id,
        organization_id=org_id,
        role=role,
    )
    membership_repo = MembershipRepository(db_session)
    membership_repo.add(membership)
    await db_session.commit()


@pytest.mark.asyncio
async def test_owner_can_archive_project(db_session):
    owner, _ = await _register(db_session, "owner_arch@example.com", "Owner Arch")
    org = await _get_first_org(db_session, owner.id)
    project_svc = ProjectService(db_session)
    proj = await project_svc.create_project(
        owner.id, org.id, ProjectCreateRequest(name="Archivable")
    )
    archived = await project_svc.archive_project(owner.id, proj.id)
    assert archived.status == "archived"


@pytest.mark.asyncio
async def test_admin_can_archive_project(db_session):
    owner, _ = await _register(
        db_session, "admin_arch_owner@example.com", "Admin Arch Owner"
    )
    admin_user, _ = await _register(db_session, "admin_arch@example.com", "Admin Arch")
    org = await _get_first_org(db_session, owner.id)
    await _add_member(db_session, admin_user.id, org.id, "admin")

    project_svc = ProjectService(db_session)
    proj = await project_svc.create_project(
        owner.id, org.id, ProjectCreateRequest(name="Admin Archive")
    )
    archived = await project_svc.archive_project(admin_user.id, proj.id)
    assert archived.status == "archived"


@pytest.mark.asyncio
async def test_member_cannot_archive_project(db_session):
    owner, _ = await _register(
        db_session, "member_arch_owner@example.com", "Member Arch Owner"
    )
    member_user, _ = await _register(
        db_session, "member_arch@example.com", "Member Arch"
    )
    org = await _get_first_org(db_session, owner.id)
    await _add_member(db_session, member_user.id, org.id, "member")

    project_svc = ProjectService(db_session)
    proj = await project_svc.create_project(
        owner.id, org.id, ProjectCreateRequest(name="Member No Archive")
    )

    with pytest.raises(AppError) as exc:
        await project_svc.archive_project(member_user.id, proj.id)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_member_can_create_and_update_project(db_session):
    owner, _ = await _register(
        db_session, "member_cu_owner@example.com", "Member CU Owner"
    )
    member_user, _ = await _register(db_session, "member_cu@example.com", "Member CU")
    org = await _get_first_org(db_session, owner.id)
    await _add_member(db_session, member_user.id, org.id, "member")

    project_svc = ProjectService(db_session)
    proj = await project_svc.create_project(
        member_user.id, org.id, ProjectCreateRequest(name="Member Project")
    )
    assert proj.name == "Member Project"

    updated = await project_svc.update_project(
        member_user.id, proj.id, ProjectUpdateRequest(name="Member Updated")
    )
    assert updated.name == "Member Updated"


@pytest.mark.asyncio
async def test_viewer_can_only_read(db_session):
    owner, _ = await _register(db_session, "viewer_owner@example.com", "Viewer Owner")
    viewer, _ = await _register(db_session, "viewer_user@example.com", "Viewer User")
    org = await _get_first_org(db_session, owner.id)
    await _add_member(db_session, viewer.id, org.id, "viewer")

    project_svc = ProjectService(db_session)
    proj = await project_svc.create_project(
        owner.id, org.id, ProjectCreateRequest(name="Viewer Read")
    )

    # Viewer can read
    read_proj = await project_svc.get_project(viewer.id, proj.id)
    assert read_proj.id == proj.id

    # Viewer cannot create
    with pytest.raises(AppError) as exc:
        await project_svc.create_project(
            viewer.id, org.id, ProjectCreateRequest(name="Viewer Create")
        )
    assert exc.value.status_code == 403

    # Viewer cannot update
    with pytest.raises(AppError) as exc:
        await project_svc.update_project(
            viewer.id, proj.id, ProjectUpdateRequest(name="Viewer Update")
        )
    assert exc.value.status_code == 403

    # Viewer cannot archive
    with pytest.raises(AppError) as exc:
        await project_svc.archive_project(viewer.id, proj.id)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_archived_project_can_be_read(db_session):
    owner, _ = await _register(
        db_session, "arch_read_owner@example.com", "Arch Read Owner"
    )
    org = await _get_first_org(db_session, owner.id)
    project_svc = ProjectService(db_session)
    proj = await project_svc.create_project(
        owner.id, org.id, ProjectCreateRequest(name="Archived Readable")
    )
    await project_svc.archive_project(owner.id, proj.id)

    read = await project_svc.get_project(owner.id, proj.id)
    assert read.status == "archived"


@pytest.mark.asyncio
async def test_archived_project_cannot_be_updated(db_session):
    owner, _ = await _register(
        db_session, "arch_update_owner@example.com", "Arch Update Owner"
    )
    org = await _get_first_org(db_session, owner.id)
    project_svc = ProjectService(db_session)
    proj = await project_svc.create_project(
        owner.id, org.id, ProjectCreateRequest(name="Archived Update")
    )
    await project_svc.archive_project(owner.id, proj.id)

    with pytest.raises(AppError) as exc:
        await project_svc.update_project(
            owner.id, proj.id, ProjectUpdateRequest(name="New Name")
        )
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_archive_is_idempotent(db_session):
    owner, _ = await _register(
        db_session, "arch_idem_owner@example.com", "Arch Idem Owner"
    )
    org = await _get_first_org(db_session, owner.id)
    project_svc = ProjectService(db_session)
    proj = await project_svc.create_project(
        owner.id, org.id, ProjectCreateRequest(name="Idem Archive")
    )
    await project_svc.archive_project(owner.id, proj.id)
    # Second archive call must not raise
    result = await project_svc.archive_project(owner.id, proj.id)
    assert result.status == "archived"


@pytest.mark.asyncio
async def test_owner_can_update_organization(db_session):
    owner, _ = await _register(
        db_session, "org_update_owner@example.com", "Org Update Owner"
    )
    org = await _get_first_org(db_session, owner.id)
    org_svc = OrganizationService(db_session)
    updated = await org_svc.update_organization(
        owner.id, org.id, OrganizationUpdateRequest(name="New Org Name")
    )
    assert updated.name == "New Org Name"


@pytest.mark.asyncio
async def test_viewer_cannot_update_organization(db_session):
    owner, _ = await _register(
        db_session, "org_view_owner@example.com", "Org View Owner"
    )
    viewer, _ = await _register(db_session, "org_viewer@example.com", "Org Viewer")
    org = await _get_first_org(db_session, owner.id)
    await _add_member(db_session, viewer.id, org.id, "viewer")
    org_svc = OrganizationService(db_session)
    with pytest.raises(AppError) as exc:
        await org_svc.update_organization(
            viewer.id, org.id, OrganizationUpdateRequest(name="Viewer Attempt")
        )
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_member_cannot_update_organization(db_session):
    owner, _ = await _register(
        db_session, "org_mem_owner@example.com", "Org Member Owner"
    )
    member_user, _ = await _register(db_session, "org_member@example.com", "Org Member")
    org = await _get_first_org(db_session, owner.id)
    await _add_member(db_session, member_user.id, org.id, "member")
    org_svc = OrganizationService(db_session)
    with pytest.raises(AppError) as exc:
        await org_svc.update_organization(
            member_user.id, org.id, OrganizationUpdateRequest(name="Member Attempt")
        )
    assert exc.value.status_code == 403
