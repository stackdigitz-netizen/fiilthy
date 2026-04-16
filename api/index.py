from pathlib import Path
import sys
import traceback
from fastapi import FastAPI
from fastapi.responses import JSONResponse

BACKEND_DIR = Path(__file__).resolve().parent.parent / "ceo" / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

_import_error = None
_import_traceback = None

try:
    from server import app as _server_app
    app = _server_app
except Exception as e:
    _import_error = str(e)
    _import_traceback = traceback.format_exc()
    app = FastAPI()

    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
    async def crash_info(path: str = ""):
        return JSONResponse(status_code=500, content={"error": _import_error, "traceback": _import_traceback})