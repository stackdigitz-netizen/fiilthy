"""
YouTube OAuth Setup Helper
==========================
Run this ONCE locally to authorize the YouTube channel and get credentials
that can be pinned in Railway env so uploads work in production.

Usage:
    1. Download client_secrets.json from Google Cloud Console
       (APIs & Services → Credentials → OAuth 2.0 Client → Download JSON)
    2. Run:  python scripts/youtube_oauth_setup.py --client-secrets path/to/client_secrets.json
    3. Follow the browser prompt, authorize the channel
    4. Copy the printed railway command and run it to pin the creds in prod

Requirements:
    pip install google-auth-oauthlib google-api-python-client
"""

import argparse
import base64
import json
import os
import sys
import webbrowser
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

try:
    from google_auth_oauthlib.flow import Flow
    from googleapiclient.discovery import build
except ImportError:
    print("Missing packages. Run:  pip install google-auth-oauthlib google-api-python-client")
    sys.exit(1)

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.readonly",
]

REDIRECT_URI = "http://localhost:8765/callback"
_auth_code: list[str] = []


class _CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/callback":
            params = parse_qs(parsed.query)
            code = params.get("code", [None])[0]
            if code:
                _auth_code.append(code)
                body = b"<h2>Authorization complete. You can close this tab.</h2>"
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"No code received.")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, *args):
        pass  # silence default logging


def _run_server(server: HTTPServer):
    server.handle_request()


def main():
    parser = argparse.ArgumentParser(description="YouTube OAuth setup")
    parser.add_argument(
        "--client-secrets",
        required=True,
        help="Path to client_secrets.json downloaded from Google Cloud Console",
    )
    parser.add_argument(
        "--out",
        default="youtube_credentials.json",
        help="Where to write the credentials JSON (default: youtube_credentials.json)",
    )
    args = parser.parse_args()

    secrets_path = Path(args.client_secrets).expanduser()
    if not secrets_path.exists():
        print(f"ERROR: client_secrets.json not found at {secrets_path}")
        sys.exit(1)

    flow = Flow.from_client_secrets_file(
        str(secrets_path),
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )

    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )

    print("\n=== YouTube OAuth Authorization ===")
    print(f"Opening browser to authorize your channel...")
    print(f"If it doesn't open automatically, visit:\n  {auth_url}\n")

    # Start local server to capture redirect
    server = HTTPServer(("localhost", 8765), _CallbackHandler)
    t = threading.Thread(target=_run_server, args=(server,), daemon=True)
    t.start()

    webbrowser.open(auth_url)
    t.join(timeout=120)

    if not _auth_code:
        print("ERROR: No authorization code received within 2 minutes.")
        sys.exit(1)

    print("Authorization code received. Fetching tokens...")
    flow.fetch_token(code=_auth_code[0])
    creds = flow.credentials

    # Get channel info
    youtube = build("youtube", "v3", credentials=creds)
    resp = youtube.channels().list(part="snippet", mine=True).execute()
    channel_id = None
    channel_name = None
    if resp.get("items"):
        channel_id = resp["items"][0]["id"]
        channel_name = resp["items"][0]["snippet"]["title"]

    # Write credentials file
    creds_data = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": list(creds.scopes) if creds.scopes else SCOPES,
    }
    out_path = Path(args.out)
    out_path.write_text(json.dumps(creds_data, indent=2), encoding="utf-8")

    # Read client secrets for the env var
    client_secrets_raw = secrets_path.read_text(encoding="utf-8")
    client_secrets_b64 = base64.b64encode(client_secrets_raw.encode()).decode()
    creds_b64 = base64.b64encode(json.dumps(creds_data).encode()).decode()

    print(f"\n=== SUCCESS ===")
    if channel_name:
        print(f"Channel: {channel_name} ({channel_id})")
    print(f"Credentials written to: {out_path.absolute()}")
    print("\n=== Run these Railway commands to pin credentials in production ===\n")
    print(f'railway variables --set "YOUTUBE_CLIENT_SECRETS_JSON={client_secrets_b64}" --service adequate-respect')
    print(f'railway variables --set "YOUTUBE_CREDENTIALS_JSON={creds_b64}" --service adequate-respect')
    if channel_id:
        print(f'railway variables --set "YOUTUBE_CHANNEL_ID={channel_id}" --service adequate-respect')
    print()


if __name__ == "__main__":
    main()
