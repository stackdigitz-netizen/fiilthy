from pathlib import Path
import sys
import traceback
from typing import Any

from starlette.responses import JSONResponse


BACKEND_DIR = Path(__file__).resolve().parent.parent / "ceo" / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


class AppProxy:
    def __init__(self):
        self.backend_app: Any | None = None

    def _load_backend_app(self):
        if self.backend_app is None:
            from server import app as backend_app

            self.backend_app = backend_app
        return self.backend_app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "lifespan":
            while True:
                message = await receive()
                message_type = message.get("type")
                if message_type == "lifespan.startup":
                    await send({"type": "lifespan.startup.complete"})
                elif message_type == "lifespan.shutdown":
                    await send({"type": "lifespan.shutdown.complete"})
                    return

        if scope["type"] not in {"http", "websocket"}:
            response = JSONResponse(
                status_code=500,
                content={"error": f"Unsupported scope type: {scope['type']}"},
            )
            await response(scope, receive, send)
            return

        try:
            backend_app = self._load_backend_app()
            await backend_app(scope, receive, send)
        except Exception as exc:
            if scope["type"] == "http":
                response = JSONResponse(
                    status_code=500,
                    content={"error": str(exc), "traceback": traceback.format_exc()},
                )
                await response(scope, receive, send)
                return

            await send({"type": "websocket.close", "code": 1011})


app = AppProxy()