"""In-process CommunityRAPP candidate for the shared Grail conformance suite."""

import importlib.util
import inspect
import json
import os
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _load_fixture_agents(agents_dir):
    fixture = agents_dir / "echo_agent.py"
    spec = importlib.util.spec_from_file_location(
        "_shared_grail_fixture_agents",
        fixture,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load shared Grail agents from {fixture}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    agents = {}
    for _, candidate in inspect.getmembers(module, inspect.isclass):
        if (
            candidate.__module__ == module.__name__
            and candidate.__name__ != "BasicAgent"
            and hasattr(candidate, "perform")
        ):
            instance = candidate()
            agents[instance.name] = instance
    return agents


class CommunityCandidate:
    def __init__(self, context):
        os.environ.update(
            AZURE_OPENAI_DEPLOYMENT_NAME=context.model,
            USE_CLOUD_STORAGE="false",
            VOICE_MODE="false",
        )
        for name in (
            "WEBSITE_INSTANCE_ID",
            "WEBSITE_SITE_NAME",
            "APPSETTING_WEBSITE_SITE_NAME",
            "AZURE_STORAGE_ACCOUNT_NAME",
            "AZURE_FILES_SHARE_NAME",
        ):
            os.environ.pop(name, None)

        import azure.functions as func
        from openai import OpenAI

        import function_app

        self.func = func
        self.app = function_app
        self.client = OpenAI(
            api_key="fake",
            base_url=context.fake_model_url,
        )
        self.agents = _load_fixture_agents(context.agents_dir)

        function_app._openai_client = self.client
        function_app._openai_client_created_at = time.time()
        function_app._llm_backend = "azure"
        function_app._copilot_model = None
        function_app._get_openai_client = lambda: self.client
        function_app._get_cached_agents = (
            lambda force_refresh=False: self.agents.copy()
        )
        function_app.get_storage_manager = lambda: object()

    @staticmethod
    def _invoke(handler, request):
        if hasattr(handler, "_function"):
            handler = handler._function.get_user_function()
        return handler(request)

    def call(self, method, path, body):
        raw_body = b""
        if body is not None:
            raw_body = (
                body if isinstance(body, bytes) else json.dumps(body).encode()
            )
        request = self.func.HttpRequest(
            method=method,
            url=f"http://localhost/api{path}",
            headers={"Content-Type": "application/json"},
            params={},
            route_params={},
            body=raw_body,
        )

        if path == "/health" and method == "GET":
            return self._invoke(self.app.health_check, request)
        if path == "/version" and method == "GET":
            return self._invoke(self.app.version, request)
        if path == "/chat" and method == "POST":
            return self._invoke(self.app.chat, request)
        return 404, {"error": "not found"}


def create_candidate(context):
    return CommunityCandidate(context)
