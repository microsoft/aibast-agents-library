#!/usr/bin/env python3
"""Tests for brainstem local-first agent adaptation."""

import os
import sys
import json
import shutil
import tempfile
import unittest

# Ensure brainstem dir is importable
BRAINSTEM_DIR = os.path.dirname(os.path.abspath(__file__))
if BRAINSTEM_DIR not in sys.path:
    sys.path.insert(0, BRAINSTEM_DIR)


class TestLocalStorage(unittest.TestCase):
    """Test LocalStorageManager (AzureFileStorageManager shim)."""

    def setUp(self):
        # Use a temp dir for test data
        self._orig_data_dir = None
        import local_storage
        self._orig_data_dir = local_storage._DATA_DIR
        self._tmp = tempfile.mkdtemp()
        local_storage._DATA_DIR = self._tmp

    def tearDown(self):
        import local_storage
        local_storage._DATA_DIR = self._orig_data_dir
        shutil.rmtree(self._tmp, ignore_errors=True)

    def test_read_empty(self):
        from local_storage import AzureFileStorageManager
        mgr = AzureFileStorageManager()
        self.assertEqual(mgr.read_json(), {})

    def test_write_and_read(self):
        from local_storage import AzureFileStorageManager
        mgr = AzureFileStorageManager()
        data = {"key1": {"message": "hello", "theme": "test"}}
        mgr.write_json(data)
        result = mgr.read_json()
        self.assertEqual(result, data)

    def test_user_context_isolation(self):
        from local_storage import AzureFileStorageManager
        mgr = AzureFileStorageManager()

        # Write to shared
        mgr.set_memory_context(None)
        mgr.write_json({"shared": True})

        # Write to user-specific
        mgr.set_memory_context("user-abc")
        mgr.write_json({"user": True})

        # Read shared — should not contain user data
        mgr.set_memory_context(None)
        self.assertEqual(mgr.read_json(), {"shared": True})

        # Read user-specific
        mgr.set_memory_context("user-abc")
        self.assertEqual(mgr.read_json(), {"user": True})

    def test_set_memory_context(self):
        from local_storage import AzureFileStorageManager
        mgr = AzureFileStorageManager()
        mgr.set_memory_context("guid-123")
        self.assertEqual(mgr.current_guid, "guid-123")
        mgr.set_memory_context(None)
        self.assertIsNone(mgr.current_guid)

    def test_file_ops(self):
        from local_storage import AzureFileStorageManager
        mgr = AzureFileStorageManager()
        mgr.write_file("test/hello.txt", "world")
        self.assertTrue(mgr.file_exists("test/hello.txt"))
        self.assertEqual(mgr.read_file("test/hello.txt"), "world")
        self.assertIn("hello.txt", mgr.list_files("test"))
        mgr.delete_file("test/hello.txt")
        self.assertFalse(mgr.file_exists("test/hello.txt"))


class TestShimRegistration(unittest.TestCase):
    """Test that sys.modules shims work for remote agent imports."""

    def setUp(self):
        # Clean any previously registered shims so we can test fresh
        import brainstem
        brainstem._shims_registered = False
        for mod in list(sys.modules):
            if mod.startswith("utils.azure") or mod.startswith("utils.dynamics"):
                del sys.modules[mod]

    def test_azure_storage_shim_imports(self):
        """After _register_shims(), `from utils.azure_file_storage import AzureFileStorageManager` should work."""
        import brainstem
        brainstem._register_shims()

        from utils.azure_file_storage import AzureFileStorageManager
        mgr = AzureFileStorageManager()
        self.assertTrue(hasattr(mgr, "read_json"))
        self.assertTrue(hasattr(mgr, "write_json"))
        self.assertTrue(hasattr(mgr, "set_memory_context"))

    def test_basic_agent_shim_imports(self):
        """After _register_shims(), `from agents.basic_agent import BasicAgent` should work."""
        import brainstem
        brainstem._register_shims()

        from agents.basic_agent import BasicAgent
        agent = BasicAgent(name="Test", metadata={"name": "Test", "description": "test"})
        self.assertEqual(agent.name, "Test")

    def test_dynamics_storage_shim(self):
        """utils.dynamics_storage should also be shimmed."""
        import brainstem
        brainstem._register_shims()

        from utils.dynamics_storage import DynamicsStorageManager
        mgr = DynamicsStorageManager()
        self.assertTrue(hasattr(mgr, "read_json"))


class TestAgentLoading(unittest.TestCase):
    """Test loading remote agents with cloud deps through shims."""

    def setUp(self):
        self._tmp = tempfile.mkdtemp()
        import local_storage
        self._orig_data_dir = local_storage._DATA_DIR
        local_storage._DATA_DIR = self._tmp
        import brainstem
        brainstem._shims_registered = False

    def tearDown(self):
        import local_storage
        local_storage._DATA_DIR = self._orig_data_dir
        shutil.rmtree(self._tmp, ignore_errors=True)

    def test_load_agent_with_azure_import(self):
        """An agent that imports AzureFileStorageManager should load via the local shim."""
        agent_code = '''
from agents.basic_agent import BasicAgent
from utils.azure_file_storage import AzureFileStorageManager

class TestMemoryAgent(BasicAgent):
    def __init__(self):
        self.name = "TestMemory"
        self.metadata = {
            "name": self.name,
            "description": "Test agent using Azure storage shim",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
        self.storage = AzureFileStorageManager()
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        self.storage.write_json({"test": True})
        data = self.storage.read_json()
        return f"Storage works: {data}"
'''
        filepath = os.path.join(self._tmp, "test_memory_agent.py")
        with open(filepath, "w") as f:
            f.write(agent_code)

        import brainstem
        agents = brainstem._load_agent_from_file(filepath)
        self.assertIn("TestMemory", agents)
        result = agents["TestMemory"].perform()
        self.assertIn("Storage works", result)

    def test_load_agent_with_missing_pip_dep(self):
        """An agent that imports a missing package should trigger auto-install."""
        # We'll use a package we know is installed (json) to avoid actually pip installing
        agent_code = '''
from agents.basic_agent import BasicAgent
import json  # always available

class SimplePipAgent(BasicAgent):
    def __init__(self):
        self.name = "SimplePip"
        self.metadata = {
            "name": self.name,
            "description": "Test agent",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        return json.dumps({"status": "ok"})
'''
        filepath = os.path.join(self._tmp, "simple_pip_agent.py")
        with open(filepath, "w") as f:
            f.write(agent_code)

        import brainstem
        agents = brainstem._load_agent_from_file(filepath)
        self.assertIn("SimplePip", agents)

    def test_load_agent_with_to_tool(self):
        """Loaded agents should have working to_tool() method."""
        agent_code = '''
from agents.basic_agent import BasicAgent

class ToolTestAgent(BasicAgent):
    def __init__(self):
        self.name = "ToolTest"
        self.metadata = {
            "name": self.name,
            "description": "Tests to_tool",
            "parameters": {"type": "object", "properties": {"q": {"type": "string"}}, "required": []}
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        return "ok"
'''
        filepath = os.path.join(self._tmp, "tool_test_agent.py")
        with open(filepath, "w") as f:
            f.write(agent_code)

        import brainstem
        agents = brainstem._load_agent_from_file(filepath)
        tool = agents["ToolTest"].to_tool()
        self.assertEqual(tool["type"], "function")
        self.assertEqual(tool["function"]["name"], "ToolTest")


class TestExtractPackageName(unittest.TestCase):
    """Test pip package name extraction from errors."""

    def test_simple_module(self):
        import brainstem
        err = ModuleNotFoundError("No module named 'bs4'")
        self.assertEqual(brainstem._extract_package_name(err), "beautifulsoup4")

    def test_dotted_module(self):
        import brainstem
        err = ModuleNotFoundError("No module named 'PIL.Image'")
        self.assertEqual(brainstem._extract_package_name(err), "Pillow")

    def test_unknown_module(self):
        import brainstem
        err = ModuleNotFoundError("No module named 'somethingweird'")
        self.assertEqual(brainstem._extract_package_name(err), "somethingweird")


class TestMemoryAgentIntegration(unittest.TestCase):
    """End-to-end: load the real context_memory_agent and manage_memory_agent from remote repo."""

    def setUp(self):
        self._tmp = tempfile.mkdtemp()
        import local_storage
        self._orig = local_storage._DATA_DIR
        local_storage._DATA_DIR = self._tmp
        import brainstem
        brainstem._shims_registered = False

    def tearDown(self):
        import local_storage
        local_storage._DATA_DIR = self._orig
        shutil.rmtree(self._tmp, ignore_errors=True)

    def test_manage_then_recall_memory(self):
        """ManageMemory stores, ContextMemory recalls — both using local storage."""
        # Download the real agents
        import requests
        base = "https://raw.githubusercontent.com/kody-w/AI-Agent-Templates/main/agents"

        for name in ["manage_memory_agent.py", "context_memory_agent.py"]:
            resp = requests.get(f"{base}/{name}", timeout=10)
            with open(os.path.join(self._tmp, name), "w") as f:
                f.write(resp.text)

        import brainstem

        # Load both agents
        manage_agents = brainstem._load_agent_from_file(os.path.join(self._tmp, "manage_memory_agent.py"))
        context_agents = brainstem._load_agent_from_file(os.path.join(self._tmp, "context_memory_agent.py"))

        self.assertIn("ManageMemory", manage_agents)
        self.assertIn("ContextMemory", context_agents)

        # Store a memory
        result = manage_agents["ManageMemory"].perform(
            memory_type="fact",
            content="The brainstem project uses local-first storage"
        )
        self.assertIn("Successfully stored", result)

        # Recall it
        result = context_agents["ContextMemory"].perform(full_recall=True)
        self.assertIn("brainstem", result.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
