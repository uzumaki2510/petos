import pytest
import re
from petos_api.services.auth_service import AuthService
from petos_api.services.project_service import ProjectService
from petos_api.schemas.auth import RegisterRequest
from petos_api.schemas.project import ProjectCreateRequest
from petos_api.repositories.membership_repository import MembershipRepository
from petos_api.core.errors import AppError


@pytest.mark.asyncio
async def test_project_key_schema_and_constraints(db_session):
    """Verify that project key is saved, returned, and validated correctly."""
    from uuid import uuid4

    auth_service = AuthService(db_session)
    user_res, _ = await auth_service.register(
        RegisterRequest(
            email=f"key_test1_{uuid4().hex[:8]}@example.com",
            password="SuperSecretPassword123!",
            display_name="Key User 1",
        )
    )
    membership_repo = MembershipRepository(db_session)
    orgs, _ = await membership_repo.get_organizations_for_user(user_res.id)
    org_id = orgs[0].id

    service = ProjectService(db_session)

    # 1. Create project with explicit valid key
    req = ProjectCreateRequest(
        name="Alpha Project", key="ALPHA", description="Test desc"
    )
    p1 = await service.create_project(user_res.id, org_id, req)
    assert p1.key == "ALPHA"

    # 2. Verify duplicate key in same organization raises HTTP 409
    req_dup = ProjectCreateRequest(name="Alpha Two", key="ALPHA")
    with pytest.raises(AppError) as exc_info:
        await service.create_project(user_res.id, org_id, req_dup)
    assert exc_info.value.status_code == 409
    assert exc_info.value.code == "duplicate_key"

    # 3. Create project without key -> auto-generated key from name
    req_auto = ProjectCreateRequest(name="Beta Project")
    p2 = await service.create_project(user_res.id, org_id, req_auto)
    assert p2.key.startswith("BETA")
    assert re.match(r"^[A-Z][A-Z0-9]{1,9}$", p2.key)


@pytest.mark.asyncio
async def test_project_key_collision_resolution(db_session):
    """Verify key collision resolution appends numeric index."""
    from uuid import uuid4

    auth_service = AuthService(db_session)
    user_res, _ = await auth_service.register(
        RegisterRequest(
            email=f"key_test2_{uuid4().hex[:8]}@example.com",
            password="SuperSecretPassword123!",
            display_name="Key User 2",
        )
    )
    membership_repo = MembershipRepository(db_session)
    orgs, _ = await membership_repo.get_organizations_for_user(user_res.id)
    org_id = orgs[0].id

    service = ProjectService(db_session)

    req1 = ProjectCreateRequest(name="Pet OS Project")
    p1 = await service.create_project(user_res.id, org_id, req1)
    assert p1.key == "PETOSPROJE"

    req2 = ProjectCreateRequest(name="Pet OS Project")
    p2 = await service.create_project(user_res.id, org_id, req2)
    assert p2.key == "PETOSPROJ1"

    req3 = ProjectCreateRequest(name="Pet OS Project")
    p3 = await service.create_project(user_res.id, org_id, req3)
    assert p3.key == "PETOSPROJ2"


@pytest.mark.asyncio
async def test_project_key_special_character_and_numeric_fallback(db_session):
    """Verify fallback for numeric/symbolic names."""
    from uuid import uuid4

    auth_service = AuthService(db_session)
    user_res, _ = await auth_service.register(
        RegisterRequest(
            email=f"key_test3_{uuid4().hex[:8]}@example.com",
            password="SuperSecretPassword123!",
            display_name="Key User 3",
        )
    )
    membership_repo = MembershipRepository(db_session)
    orgs, _ = await membership_repo.get_organizations_for_user(user_res.id)
    org_id = orgs[0].id

    service = ProjectService(db_session)

    # Starts with numbers -> prepends PET
    req1 = ProjectCreateRequest(name="12345")
    p1 = await service.create_project(user_res.id, org_id, req1)
    assert p1.key.startswith("PET")
    assert re.match(r"^[A-Z][A-Z0-9]{1,9}$", p1.key)

    # Pure symbols -> prepends PET
    req2 = ProjectCreateRequest(name="!!! @@@ ###")
    p2 = await service.create_project(user_res.id, org_id, req2)
    assert p2.key.startswith("PET")
    assert re.match(r"^[A-Z][A-Z0-9]{1,9}$", p2.key)
