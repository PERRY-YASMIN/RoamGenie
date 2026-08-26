import sys
from pathlib import Path

# Add project root and backend to sys.path
root_dir = Path(__file__).resolve().parent.parent
backend_dir = root_dir / "backend"

for d in (str(root_dir), str(backend_dir)):
    if d not in sys.path:
        sys.path.insert(0, d)

try:
    from backend.tests.conftest import (
        admin_headers,
        client,
        db_session,
        traveller_headers,
        traveller_token,
    )
except (ImportError, ModuleNotFoundError):
    from tests.conftest import (  # fallback when pytest root is backend
        admin_headers,
        client,
        db_session,
        traveller_headers,
        traveller_token,
    )

__all__ = [
    "db_session",
    "client",
    "traveller_token",
    "traveller_headers",
    "admin_headers",
]
