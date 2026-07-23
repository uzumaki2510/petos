#!/usr/bin/env python3
"""
Export PetOS FastAPI OpenAPI schema without starting the server.
Usage: uv run --frozen python scripts/export_openapi.py
Outputs:
  services/api/openapi.json          — canonical backend schema
  apps/web/openapi/petos.openapi.json — committed frontend copy for drift detection
"""

import json
import sys
from pathlib import Path

# Ensure src is on the path
repo_root = Path(__file__).parent.parent.parent.parent
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from petos_api.main import app  # noqa: E402

schema = app.openapi()

# Write the canonical backend copy
backend_path = Path(__file__).parent.parent / "openapi.json"
with open(backend_path, "w") as f:
    json.dump(schema, f, indent=2, sort_keys=True)
    f.write("\n")

# Write the canonical frontend copy (committed for drift detection)
frontend_dir = repo_root / "apps" / "web" / "openapi"
frontend_dir.mkdir(parents=True, exist_ok=True)
frontend_path = frontend_dir / "petos.openapi.json"
with open(frontend_path, "w") as f:
    json.dump(schema, f, indent=2, sort_keys=True)
    f.write("\n")

print(f"Exported {len(schema['paths'])} paths")
print(f"  → {backend_path}")
print(f"  → {frontend_path}")
