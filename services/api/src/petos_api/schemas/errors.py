from pydantic import BaseModel


class ErrorDetail(BaseModel):
    code: str
    message: str
    request_id: str


class ErrorResponse(BaseModel):
    error: ErrorDetail


class ValidationErrorDetail(ErrorDetail):
    details: list[dict]


class ValidationErrorResponse(BaseModel):
    error: ValidationErrorDetail
