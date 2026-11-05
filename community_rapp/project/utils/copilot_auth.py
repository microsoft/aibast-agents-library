"""
GitHub Copilot authentication for local development.

Allows CommunityRAPP to use GitHub Copilot as the LLM backend when running
locally, using the same auth the RAPP Brainstem uses. Falls back gracefully
if no GitHub token is available.

Token priority:
  1. GITHUB_TOKEN env var (must be ghu_ prefix from device code flow)
  2. .copilot_token file in project root
  3. Brainstem's .copilot_token (~/rapp-installer/rapp_brainstem/.copilot_token)
  4. gh auth token CLI (may not work — gho_ tokens are rejected by Copilot API)

Usage:
  from utils.copilot_auth import get_copilot_client
  client = get_copilot_client()  # Returns OpenAI client or None
"""

import json
import logging
import os
import subprocess
import time

import requests

logger = logging.getLogger(__name__)

# GitHub Copilot OAuth App (device code flow)
GITHUB_CLIENT_ID = "Iv1.b507a08c87ecfe98"
COPILOT_TOKEN_EXCHANGE_URL = "https://api.github.com/copilot_internal/v2/token"

COPILOT_HEADERS = {
    "Editor-Version": "vscode/1.95.0",
    "Editor-Plugin-Version": "copilot/1.0.0",
    "User-Agent": "GitHubCopilotChat/0.22.2024",
}

# Cached Copilot session
_copilot_session = None
_copilot_session_lock = None

try:
    import threading
    _copilot_session_lock = threading.Lock()
except ImportError:
    pass


class CopilotSession:
    """Holds the exchanged Copilot token and endpoint."""

    def __init__(self, token, endpoint, expires_at):
        self.token = token
        self.endpoint = endpoint
        self.expires_at = expires_at

    def is_expired(self):
        return time.time() >= (self.expires_at - 60)  # 60s buffer


def _find_github_token():
    """Find a GitHub token from available sources."""
    # 1. Environment variable
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        logger.info("Using GitHub token from environment variable")
        return token

    # 2. .copilot_token file in project root
    local_token_file = os.path.join(os.getcwd(), ".copilot_token")
    token = _read_token_file(local_token_file)
    if token:
        logger.info("Using GitHub token from local .copilot_token")
        return token

    # 3. Brainstem's .copilot_token
    brainstem_paths = [
        os.path.expanduser("~/rapp-installer/rapp_brainstem/.copilot_token"),
        os.path.expanduser("~/.brainstem/.copilot_token"),
    ]
    for path in brainstem_paths:
        token = _read_token_file(path)
        if token:
            logger.info(f"Using GitHub token from brainstem: {path}")
            return token

    # 4. gh CLI (last resort — gho_ tokens may not work)
    try:
        result = subprocess.run(
            ["gh", "auth", "token"], capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            token = result.stdout.strip()
            if not token.startswith("gho_"):
                logger.info("Using GitHub token from gh CLI")
                return token
            else:
                logger.warning(
                    "gh CLI token has gho_ prefix which may not work with "
                    "Copilot API. Use device code auth for reliable access."
                )
                return token  # Try anyway, will fail gracefully
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return None


def _read_token_file(path):
    """Read a GitHub token from a JSON file."""
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r") as f:
            data = json.load(f)
        return data.get("access_token")
    except (json.JSONDecodeError, IOError, KeyError):
        return None


def _exchange_for_copilot_token(github_token):
    """Exchange a GitHub token for a Copilot API token."""
    headers = {
        **COPILOT_HEADERS,
        "Accept": "application/json",
    }

    # ghu_ tokens use "token" prefix, others use "Bearer"
    if github_token.startswith("ghu_"):
        headers["Authorization"] = f"token {github_token}"
    else:
        headers["Authorization"] = f"Bearer {github_token}"

    try:
        resp = requests.get(
            COPILOT_TOKEN_EXCHANGE_URL, headers=headers, timeout=10,
        )

        if resp.status_code == 200:
            data = resp.json()
            token = data.get("token")
            endpoints = data.get("endpoints", {})
            endpoint = endpoints.get("api", "https://api.individual.githubcopilot.com")
            expires_at = data.get("expires_at", time.time() + 1800)
            return CopilotSession(token, endpoint, expires_at)

        if resp.status_code in (401, 403, 404):
            logger.warning(
                f"Copilot token exchange failed ({resp.status_code}). "
                "Your GitHub account may not have Copilot access, or the "
                "token type is not supported."
            )
            return None

        logger.warning(f"Copilot token exchange unexpected status: {resp.status_code}")
        return None

    except requests.RequestException as e:
        logger.warning(f"Copilot token exchange network error: {e}")
        return None


def _get_copilot_session():
    """Get a valid Copilot session, exchanging tokens as needed."""
    global _copilot_session

    if _copilot_session and not _copilot_session.is_expired():
        return _copilot_session

    github_token = _find_github_token()
    if not github_token:
        return None

    session = _exchange_for_copilot_token(github_token)
    if session:
        _copilot_session = session

    return session


def get_copilot_client():
    """
    Get an OpenAI-compatible client backed by GitHub Copilot.

    Returns (client, model_name) tuple, or (None, None) if unavailable.
    The client is a standard OpenAI client pointed at the Copilot API.
    """
    if _copilot_session_lock:
        _copilot_session_lock.acquire()

    try:
        session = _get_copilot_session()
        if not session:
            return None, None

        from openai import OpenAI

        client = OpenAI(
            base_url=f"{session.endpoint}",
            api_key=session.token,
            default_headers={
                **COPILOT_HEADERS,
                "Copilot-Integration-Id": "vscode-chat",
            },
            timeout=45,
            max_retries=2,
        )

        model = os.environ.get("GITHUB_MODEL", "gpt-4o")
        logger.info(f"Copilot client ready (endpoint: {session.endpoint}, model: {model})")
        return client, model

    except ImportError:
        logger.error("openai package not installed — cannot create Copilot client")
        return None, None
    except Exception as e:
        logger.error(f"Failed to create Copilot client: {e}")
        return None, None
    finally:
        if _copilot_session_lock:
            _copilot_session_lock.release()


def is_copilot_available():
    """Quick check: is a GitHub token available for Copilot auth?"""
    return _find_github_token() is not None


def start_device_code_flow():
    """
    Start the GitHub device code OAuth flow.

    Returns a dict with 'user_code' and 'verification_uri' that the user
    must use to authorize, plus 'device_code' for polling.
    Returns None on failure.
    """
    try:
        resp = requests.post(
            "https://github.com/login/device/code",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data=f"client_id={GITHUB_CLIENT_ID}",
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json()
        return None
    except requests.RequestException:
        return None


def poll_device_code(device_code):
    """
    Poll for the device code authorization result.

    Returns a dict with 'access_token' on success, or
    {'status': 'pending'} / {'status': 'expired'} / None.
    """
    try:
        resp = requests.post(
            "https://github.com/login/oauth/access_token",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data=(
                f"client_id={GITHUB_CLIENT_ID}"
                f"&device_code={device_code}"
                f"&grant_type=urn:ietf:params:oauth:grant-type:device_code"
            ),
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            if "access_token" in data:
                return data
            error = data.get("error", "")
            if error == "authorization_pending":
                return {"status": "pending"}
            if error == "expired_token":
                return {"status": "expired"}
            return {"status": error}
        return None
    except requests.RequestException:
        return None


def save_token(token_data, path=None):
    """Save a GitHub token to disk for reuse."""
    if path is None:
        path = os.path.join(os.getcwd(), ".copilot_token")
    with open(path, "w") as f:
        json.dump(token_data, f, indent=2)
    logger.info(f"GitHub token saved to {path}")
