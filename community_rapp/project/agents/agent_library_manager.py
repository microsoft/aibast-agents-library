import json
import logging
import os
import time
import requests
from agents.basic_agent import BasicAgent

logger = logging.getLogger(__name__)

GITHUB_OWNER = "kody-w"
GITHUB_REPO = "AI-Agent-Templates"
MANIFEST_URL = f"https://raw.githubusercontent.com/{GITHUB_OWNER}/{GITHUB_REPO}/main/manifest.json"
INSTALLED_PATH = os.path.join(".local_storage", "installed_agents.json")
CACHE_TTL = 300  # 5 minutes


def _github_headers():
    """Build headers with GitHub token if available (raises rate limits)."""
    headers = {"Accept": "application/vnd.github.v3.raw"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        try:
            import subprocess
            result = subprocess.run(
                ["gh", "auth", "token"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                token = result.stdout.strip()
        except Exception:
            pass
    if token:
        headers["Authorization"] = f"token {token}"
    return headers


class AgentLibraryManager(BasicAgent):
    _registry_cache = None
    _cache_time = 0

    def __init__(self):
        self.name = "AgentLibraryManager"
        self.metadata = {
            "name": self.name,
            "description": (
                "Browse, search, and install agents from the RAPP AI Agent Templates library. "
                "WORKFLOW: First use 'discover' or 'search' to find agents, then 'install' with the exact agent id from results. "
                "Actions: discover (list all), search (find by keyword), install (download agent), "
                "list_installed (show installed), remove (uninstall), info (agent details)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["discover", "search", "install", "list_installed", "remove", "info"],
                        "description": (
                            "Action to perform. Use 'discover' to browse all available agents, "
                            "'search' to find agents by keyword, 'install' to download an agent "
                            "(requires exact agent id from discover/search results), "
                            "'list_installed' to see installed agents, 'remove' to uninstall, "
                            "'info' for detailed agent information."
                        ),
                    },
                    "agent_name": {
                        "type": "string",
                        "description": "Agent id (e.g. 'calendar_agent'). Required for install, remove, and info.",
                    },
                    "search_query": {
                        "type": "string",
                        "description": "Keyword to search for agents by name, description, or features. Required for search action.",
                    },
                },
                "required": ["action"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        action = kwargs.get("action", "discover")
        agent_name = kwargs.get("agent_name", "")
        search_query = kwargs.get("search_query", "")

        actions = {
            "discover": self._discover,
            "search": lambda: self._search(search_query),
            "install": lambda: self._install(agent_name),
            "list_installed": self._list_installed,
            "remove": lambda: self._remove(agent_name),
            "info": lambda: self._info(agent_name),
        }

        handler = actions.get(action)
        if not handler:
            return f"Unknown action '{action}'. Use: discover, search, install, list_installed, remove, info."

        try:
            return handler()
        except requests.RequestException as e:
            logger.error(f"Network error in AgentLibraryManager: {e}")
            return f"Network error: Could not reach the agent library. Check your connection.\nDetails: {e}"
        except Exception as e:
            logger.error(f"AgentLibraryManager error: {e}", exc_info=True)
            return f"Error: {e}"

    # ── Registry ──────────────────────────────────────────────────────

    def _fetch_registry(self, force=False):
        now = time.time()
        if not force and AgentLibraryManager._registry_cache and (now - AgentLibraryManager._cache_time) < CACHE_TTL:
            return AgentLibraryManager._registry_cache

        resp = requests.get(MANIFEST_URL, headers=_github_headers(), timeout=15)
        resp.raise_for_status()
        data = resp.json()
        AgentLibraryManager._registry_cache = data
        AgentLibraryManager._cache_time = now
        return data

    def _find_agent(self, agent_id):
        registry = self._fetch_registry()
        for agent in registry.get("agents", []):
            if agent["id"] == agent_id:
                return agent
        return None

    # ── Actions ───────────────────────────────────────────────────────

    def _discover(self):
        registry = self._fetch_registry(force=True)
        agents = registry.get("agents", [])
        stacks = registry.get("stacks", [])

        lines = [f"**RAPP Agent Library** — {len(agents)} agents, {len(stacks)} stacks available\n"]

        lines.append("**Agents:**")
        for a in sorted(agents, key=lambda x: x["id"]):
            icon = a.get("icon", "")
            lines.append(f"  {icon} `{a['id']}` — {a['description'][:80]}")
        lines.append("")

        if stacks:
            # Group stacks by type
            by_type = {}
            for s in stacks:
                by_type.setdefault(s.get("type", "other"), []).append(s)
            for stype in sorted(by_type):
                group = by_type[stype]
                lines.append(f"**Stacks ({stype}):** ({len(group)})")
                for s in sorted(group, key=lambda x: x.get("id", x.get("name", "")))[:10]:
                    sid = s.get("id", s.get("name", "?"))
                    desc = s.get("description", "")[:80]
                    lines.append(f"  `{sid}` — {desc}")
                if len(group) > 10:
                    lines.append(f"  ... and {len(group) - 10} more. Use `search` to find specific stacks.")
                lines.append("")

        lines.append("Use `search` with a keyword, or `install` with an agent id from above.")
        return "\n".join(lines)

    def _search(self, query):
        if not query:
            return "Please provide a search_query (e.g. 'calendar', 'memory', 'email')."

        registry = self._fetch_registry()
        keywords = query.lower().split()
        results = []

        for a in registry.get("agents", []):
            searchable = " ".join([
                a.get("id", ""), a.get("name", ""),
                a.get("description", ""), " ".join(a.get("features", [])),
            ]).lower()
            if any(kw in searchable for kw in keywords):
                results.append(a)

        if not results:
            return f"No agents found matching '{query}'. Try `discover` to browse all agents."

        lines = [f"**{len(results)} agent(s) matching '{query}':**\n"]
        for a in results:
            icon = a.get("icon", "")
            lines.append(f"  {icon} `{a['id']}` — {a['description'][:80]}")

        lines.append(f"\nTo install: use action `install` with agent_name (e.g. `{results[0]['id']}`).")
        return "\n".join(lines)

    def _install(self, agent_id):
        if not agent_id:
            return "Please provide agent_name (e.g. 'calendar_agent'). Use `discover` or `search` first."

        agent_meta = self._find_agent(agent_id)
        if not agent_meta:
            return f"Agent '{agent_id}' not found in library. Use `discover` to see available agents."

        download_url = agent_meta.get("url")
        if not download_url:
            return f"No download URL for '{agent_id}'."

        # Download agent source
        resp = requests.get(download_url, headers=_github_headers(), timeout=30)
        resp.raise_for_status()
        source = resp.text

        # Save to agents/ folder
        filename = agent_meta.get("filename", f"{agent_id}.py")
        dest = os.path.join("agents", filename)

        os.makedirs("agents", exist_ok=True)
        with open(dest, "w", encoding="utf-8") as f:
            f.write(source)
        logger.info(f"Installed agent {agent_id} -> {dest}")

        # Update local manifest
        manifest = self._read_manifest()
        manifest[agent_id] = {
            "file": filename,
            "installed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "display_name": agent_meta.get("name", agent_id),
            "size": agent_meta.get("size_formatted", "?"),
        }
        self._write_manifest(manifest)

        return (
            f"**Installed `{agent_id}`** -> `{dest}`\n"
            f"Size: {agent_meta.get('size_formatted', '?')}\n"
            f"**Restart the function app** to load the new agent."
        )

    def _list_installed(self):
        manifest = self._read_manifest()
        if not manifest:
            return "No library agents installed yet. Use `discover` to browse available agents."

        lines = ["**Installed library agents:**\n"]
        for name, info in sorted(manifest.items()):
            exists = "installed" if os.path.isfile(os.path.join("agents", info["file"])) else "missing"
            lines.append(f"  `{name}` — {info['file']} ({exists})")
        lines.append(f"\n{len(manifest)} agent(s) installed.")
        return "\n".join(lines)

    def _remove(self, agent_id):
        if not agent_id:
            return "Please provide agent_name to remove. Use `list_installed` to see installed agents."

        manifest = self._read_manifest()
        if agent_id not in manifest:
            return f"`{agent_id}` is not in the installed manifest. Use `list_installed` to check."

        info = manifest.pop(agent_id)
        filepath = os.path.join("agents", info["file"])

        if os.path.isfile(filepath):
            os.remove(filepath)
            logger.info(f"Removed agent file: {filepath}")

        self._write_manifest(manifest)
        return f"**Removed `{agent_id}`** (`{info['file']}` deleted).\nRestart the function app to apply."

    def _info(self, agent_id):
        if not agent_id:
            return "Please provide agent_name (e.g. 'calendar_agent')."

        agent = self._find_agent(agent_id)
        if not agent:
            return f"Agent '{agent_id}' not found in library."

        features = ", ".join(agent.get("features", [])) or "None listed"

        manifest = self._read_manifest()
        status = "Installed" if agent_id in manifest else "Not installed"

        return (
            f"**{agent.get('name', agent_id)}** (`{agent_id}`)\n\n"
            f"**Description:** {agent.get('description', 'N/A')}\n"
            f"**Type:** {agent.get('type', '?')}\n"
            f"**Size:** {agent.get('size_formatted', '?')}\n"
            f"**Features:** {features}\n"
            f"**Status:** {status}\n"
            f"\nTo install: use action `install` with agent_name `{agent_id}`."
        )

    # ── Local manifest persistence ────────────────────────────────────

    def _read_manifest(self):
        if not os.path.isfile(INSTALLED_PATH):
            return {}
        try:
            with open(INSTALLED_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            logger.warning(f"Could not read manifest at {INSTALLED_PATH}")
            return {}

    def _write_manifest(self, data):
        os.makedirs(os.path.dirname(INSTALLED_PATH), exist_ok=True)
        with open(INSTALLED_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
