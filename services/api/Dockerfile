FROM python:3.13.14-slim-bookworm
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:0.4.9 /uv /uvx /bin/

COPY services/api/pyproject.toml services/api/uv.lock ./
# Need to copy the whole services/api for the code
COPY services/api ./services/api
WORKDIR /app/services/api

# Sync dependencies using uv
RUN uv sync --frozen --no-dev

# Ensure the module is in PYTHONPATH
ENV PYTHONPATH=/app/services/api/src
CMD ["uv", "run", "uvicorn", "petos_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
