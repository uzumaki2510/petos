from pydantic import BaseModel
from typing import Generic, TypeVar, List
from .organization import OrganizationResponse
from .project import ProjectResponse

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    limit: int
    offset: int
    total: int


class PaginatedOrganizationResponse(PaginatedResponse[OrganizationResponse]):
    pass


class PaginatedProjectResponse(PaginatedResponse[ProjectResponse]):
    pass
