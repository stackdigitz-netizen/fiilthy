from pathlib import Path
import sys
import traceback

BACKEND_DIR = Path(__file__).resolve().parent.parent / "ceo" / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

try:
    from server import app
except Exception as _import_error:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse

    app = FastAPI()
    _error_detail = traceback.format_exc()

    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
    async def crash_handler(path: str = ""):
        return JSONResponse(
            status_code=500,
            content={"error": str(_import_error), "traceback": _error_detail}
        )