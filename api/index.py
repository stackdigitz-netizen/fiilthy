from pathlib import Path
import sys
import traceback

BACKEND_DIR = Path(__file__).resolve().parent.parent / "ceo" / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

try:
    from server import app
except Exception as e:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    _err = traceback.format_exc()
    app = FastAPI()

    @app.get("/{path:path}")
    @app.post("/{path:path}")
    async def crash_info(path: str = ""):
        return JSONResponse(status_code=500, content={"error": str(e), "traceback": _err})