import json
import logging
import os
import time
import requests
from agents.basic_agent import BasicAgent

logger = logging.getLogger(__name__)

GITHUB_OWNER = "billwhalenmsft"
GITHUB_REPO = "RAPP-Agent-Repo"
GITHUB_API_BASE = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"
MANIFEST_PATH = os.path.join(".local_storage", "installed_agents.json")
CACHE_TTL = 300  # 5 minutes


def _github_headers():
    """Build headers with GitHub token if available (for private repos)."""
    headers = {"Accept": "application/vnd.github.v3.raw"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        # Try reading from gh CLI config
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
                "Browse, search, and install agents from the RAPP Agent Repo. "
                "WORKFLOW: First use 'discover' or 'search' to find agents, then 'install' with the exact agent_name from results. "
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
                            "(requires exact agent_name from discover/search results), "
                            "'list_installed' to see installed agents, 'remove' to uninstall, "
                            "'info' for detailed agent information."
                        ),
                    },
                    "agent_name": {
                        "type": "string",
                        "description": "Fully qualified agent name (e.g. '@billwhalen/dynamics-crud'). Required for install, remove, and info.",
                    },
                    "search_query": {
                        "type": "string",
                        "description": "Keyword to search for agents by name, description, or tags. Required for search action.",
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
            return f"❌ Unknown action '{action}'. Use: discover, search, install, list_installed, remove, info."

        try:
            return handler()
        except requests.RequestException as e:
            logger.error(f"Network error in AgentLibraryManager: {e}")
            return f"❌ Network error: Could not reach the RAPP Agent Repo. Check your connection.\nDetails: {e}"
        except Exception as e:
            logger.error(f"AgentLibraryManager error: {e}", exc_info=True)
            return f"❌ Error: {e}"

    # ── Registry ──────────────────────────────────────────────────────

    def _fetch_registry(self, force=False):
        now = time.time()
        if not force and AgentLibraryManager._registry_cache and (now - AgentLibraryManager._cache_time) < CACHE_TTL:
            return AgentLibraryManager._registry_cache

        url = f"{GITHUB_API_BASE}/contents/registry.json"
        resp = requests.get(url, headers=_github_headers(), timeout=15)
        resp.raise_for_status()
        data = resp.json()
        AgentLibraryManager._registry_cache = data
        AgentLibraryManager._cache_time = now
        return data

    def _find_agent(self, name):
        registry = self._fetch_registry()
        for agent in registry.get("agents", []):
            if agent["name"] == name:
                return agent
        return None

    # ── Actions ───────────────────────────────────────────────────────

    def _discover(self):
        registry = self._fetch_registry(force=True)
        agents = registry.get("agents", [])
        stats = registry.get("stats", {})

        by_category = {}
        for a in agents:
            by_category.setdefault(a.get("category", "other"), []).append(a)

        category_icons = {
            "core": "🧠", "pipeline": "🔧", "integrations": "🔌",
            "productivity": "📊", "devtools": "🛠️",
        }

        lines = [f"📦 **RAPP Agent Library** — {stats.get('total_agents', len(agents))} agents available\n"]
        for cat in sorted(by_category):
            icon = category_icons.get(cat, "📁")
            group = by_category[cat]
            lines.append(f"{icon} **{cat.title()}** ({len(group)}):")
            for a in sorted(group, key=lambda x: x["name"]):
                tier = " ✅" if a.get("quality_tier") == "verified" else ""
                lines.append(f"  `{a['name']}`{tier} — {a['description'][:80]}")
            lines.append("")

        lines.append("💡 Use `search` with a keyword, or `install` with an exact agent name from above.")
        return "\n".join(lines)

    def _search(self, query):
        if not query:
            return "❌ Please provide a search_query (e.g. 'crm', 'email', 'pipeline')."

        registry = self._fetch_registry()
        keywords = query.lower().split()
        results = []

        for a in registry.get("agents", []):
            searchable = " ".join([
                a.get("name", ""), a.get("display_name", ""),
                a.get("description", ""), " ".join(a.get("tags", [])),
                a.get("category", ""), a.get("author", ""),
            ]).lower()
            if any(kw in searchable for kw in keywords):
                results.append(a)

        if not results:
            return f"🔍 No agents found matching '{query}'. Try `discover` to browse all agents."

        lines = [f"🔍 **{len(results)} agent(s) matching '{query}':**\n"]
        for a in results:
            env = f" ⚠️ Requires: {', '.join(a['requires_env'])}" if a.get("requires_env") else ""
            lines.append(f"  `{a['name']}` — {a['description'][:80]}{env}")

        lines.append(f"\n💡 To install: use action `install` with agent_name (e.g. `{results[0]['name']}`).")
        return "\n".join(lines)

    def _install(self, agent_name):
        if not agent_name:
            return "❌ Please provide agent_name (e.g. '@billwhalen/dynamics-crud'). Use `discover` or `search` first."

        agent_meta = self._find_agent(agent_name)
        if not agent_meta:
            return f"❌ Agent '{agent_name}' not found in registry. Use `discover` to see available agents."

        file_path = agent_meta.get("_file")
        if not file_path:
            return f"❌ No file path in registry for '{agent_name}'."

        # Download agent source via GitHub API
        url = f"{GITHUB_API_BASE}/contents/{file_path}"
        resp = requests.get(url, headers=_github_headers(), timeout=30)
        resp.raise_for_status()
        source = resp.text

        # Save to agents/ folder
        slug = agent_name.split("/")[-1]
        filename = slug.replace("-", "_") + "_agent.py"
        dest = os.path.join("agents", filename)

        os.makedirs("agents", exist_ok=True)
        with open(dest, "w", encoding="utf-8") as f:
            f.write(source)
        logger.info(f"Installed agent {agent_name} -> {dest}")

        # Update manifest
        manifest = self._read_manifest()
        manifest[agent_name] = {
            "file": filename,
            "version": agent_meta.get("version", "1.0.0"),
            "installed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "display_name": agent_meta.get("display_name", slug),
        }
        self._write_manifest(manifest)

        env_note = ""
        if agent_meta.get("requires_env"):
            env_note = f"\n⚠️ **Required env vars:** {', '.join(agent_meta['requires_env'])}"

        return (
            f"✅ **Installed `{agent_name}`** → `{dest}`\n"
            f"Version: {agent_meta.get('version', '1.0.0')} | "
            f"Size: {agent_meta.get('_size_kb', '?')} KB{env_note}\n"
            f"🔄 **Restart the function app** to load the new agent."
        )

    def _list_installed(self):
        manifest = self._read_manifest()
        if not manifest:
            return "📭 No library agents installed yet. Use `discover` to browse available agents."

        lines = ["📋 **Installed library agents:**\n"]
        for name, info in sorted(manifest.items()):
            exists = "✅" if os.path.isfile(os.path.join("agents", info["file"])) else "❌ missing"
            lines.append(f"  `{name}` v{info.get('version', '?')} — {info['file']} {exists}")
        lines.append(f"\n{len(manifest)} agent(s) installed.")
        return "\n".join(lines)

    def _remove(self, agent_name):
        if not agent_name:
            return "❌ Please provide agent_name to remove. Use `list_installed` to see installed agents."

        manifest = self._read_manifest()
        if agent_name not in manifest:
            return f"❌ `{agent_name}` is not in the installed manifest. Use `list_installed` to check."

        info = manifest.pop(agent_name)
        filepath = os.path.join("agents", info["file"])

        if os.path.isfile(filepath):
            os.remove(filepath)
            logger.info(f"Removed agent file: {filepath}")

        self._write_manifest(manifest)
        return f"🗑️ **Removed `{agent_name}`** (`{info['file']}` deleted).\n🔄 Restart the function app to apply."

    def _info(self, agent_name):
        if not agent_name:
            return "❌ Please provide agent_name (e.g. '@billwhalen/dynamics-crud')."

        agent = self._find_agent(agent_name)
        if not agent:
            return f"❌ Agent '{agent_name}' not found in registry."

        env = ", ".join(agent.get("requires_env", [])) or "None"
        deps = ", ".join(agent.get("dependencies", [])) or "None"
        tags = ", ".join(agent.get("tags", []))

        manifest = self._read_manifest()
        status = "✅ Installed" if agent_name in manifest else "⬜ Not installed"

        return (
            f"📄 **{agent.get('display_name', agent_name)}** (`{agent_name}`)\n\n"
            f"**Description:** {agent.get('description', 'N/A')}\n"
            f"**Author:** {agent.get('author', 'Unknown')}\n"
            f"**Version:** {agent.get('version', '?')} | **Category:** {agent.get('category', '?')} | **Tier:** {agent.get('quality_tier', '?')}\n"
            f"**Tags:** {tags}\n"
            f"**Size:** {agent.get('_size_kb', '?')} KB ({agent.get('_lines', '?')} lines)\n"
            f"**Required env vars:** {env}\n"
            f"**Dependencies:** {deps}\n"
            f"**Status:** {status}\n"
            f"\n💡 To install: use action `install` with agent_name `{agent_name}`."
        )

    # ── Manifest persistence ──────────────────────────────────────────

    def _read_manifest(self):
        if not os.path.isfile(MANIFEST_PATH):
            return {}
        try:
            with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            logger.warning(f"Could not read manifest at {MANIFEST_PATH}")
            return {}

    def _write_manifest(self, data):
        os.makedirs(os.path.dirname(MANIFEST_PATH), exist_ok=True)
        with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
