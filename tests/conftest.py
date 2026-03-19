"""
Test fixtures — discovers all agent .py files, imports them, yields (module, class, path).
"""

import importlib.util
import sys
import os
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = REPO_ROOT / "agents" / "@aibast-agents-library"
TEMPLATES_DIR = AGENTS_DIR / "templates"

# Files to skip (not agents)
SKIP_FILES = {
    "basic_agent.py",
    "__init__.py",
    "d365_base_agent.py",
    "update_agents.py",
}

# Template files to skip (utility templates, not standalone agents)
SKIP_DIRS = {"templates"}


def _discover_agents():
    """Walk the agents directory tree and find all agent .py files."""
    agents = []
    for py_path in sorted(AGENTS_DIR.rglob("*.py")):
        if py_path.name in SKIP_FILES:
            continue
        # Skip templates directory
        rel = py_path.relative_to(AGENTS_DIR)
        if rel.parts[0] in SKIP_DIRS:
            continue
        agents.append(py_path)
    return agents


def _load_module(py_path: Path):
    """Import a .py file as a module and return (module, agent_class, path)."""
    # Ensure templates dir is on path so BasicAgent can be imported
    if str(TEMPLATES_DIR) not in sys.path:
        sys.path.insert(0, str(TEMPLATES_DIR))

    module_name = py_path.stem
    spec = importlib.util.spec_from_file_location(module_name, str(py_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Find agent class (subclass of BasicAgent, excluding BasicAgent itself)
    from basic_agent import BasicAgent
    agent_cls = None
    for attr_name in dir(mod):
        obj = getattr(mod, attr_name)
        if (isinstance(obj, type)
                and issubclass(obj, BasicAgent)
                and obj is not BasicAgent
                and obj.__module__ == mod.__name__):
            agent_cls = obj
            break

    return mod, agent_cls, py_path


AGENT_PATHS = _discover_agents()


@pytest.fixture(params=AGENT_PATHS, ids=[str(p.relative_to(REPO_ROOT)) for p in AGENT_PATHS])
def agent_info(request):
    """Yield (module, agent_class, path) for each agent file."""
    py_path = request.param
    mod, cls, path = _load_module(py_path)
    return mod, cls, path
