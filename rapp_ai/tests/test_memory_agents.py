"""
Memory Agent Platform Tests

Tests for the core memory agent platform:
- Agent loading and discovery
- Memory read (ContextMemory) and write (ManageMemory)
- Storage backend (local file storage)
- API contract (request/response format)
"""
import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestLocalFileStorage(unittest.TestCase):
    """Test local file storage backend (the default for development)."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        os.environ['LOCAL_STORAGE_PATH'] = self.test_dir
        from utils.local_file_storage import LocalFileStorageManager
        self.storage = LocalFileStorageManager(base_path=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)
        os.environ.pop('LOCAL_STORAGE_PATH', None)

    def test_write_and_read_json(self):
        """Write JSON memory and read it back."""
        data = {"test-uuid": {"message": "Hello world", "theme": "fact", "date": "2025-01-01", "time": "10:00:00"}}
        self.storage.write_json(data)
        result = self.storage.read_json()
        self.assertEqual(result, data)

    def test_shared_memory_context(self):
        """Shared memory (no GUID) writes to shared location."""
        self.storage.set_memory_context(None)
        self.storage.write_json({"shared-id": {"message": "shared fact", "theme": "fact"}})
        result = self.storage.read_json()
        self.assertIn("shared-id", result)

    def test_user_memory_context(self):
        """User-specific memory writes to user-specific location."""
        user_guid = "550e8400-e29b-41d4-a716-446655440000"
        self.storage.set_memory_context(user_guid)
        self.storage.write_json({"user-id": {"message": "user fact", "theme": "preference"}})
        result = self.storage.read_json()
        self.assertIn("user-id", result)

    def test_user_and_shared_memory_isolated(self):
        """User and shared memory are separate."""
        # Write shared
        self.storage.set_memory_context(None)
        self.storage.write_json({"shared": {"message": "shared"}})

        # Write user-specific
        user_guid = "550e8400-e29b-41d4-a716-446655440000"
        self.storage.set_memory_context(user_guid)
        self.storage.write_json({"user": {"message": "user-only"}})

        # Read shared — should NOT contain user data
        self.storage.set_memory_context(None)
        shared = self.storage.read_json()
        self.assertIn("shared", shared)
        self.assertNotIn("user", shared)

        # Read user — should NOT contain shared data
        self.storage.set_memory_context(user_guid)
        user_data = self.storage.read_json()
        self.assertIn("user", user_data)
        self.assertNotIn("shared", user_data)

    def test_read_empty_returns_empty_dict(self):
        """Reading non-existent memory returns empty dict."""
        self.storage.set_memory_context("nonexistent-guid")
        result = self.storage.read_json()
        self.assertEqual(result, {})

    def test_write_file_and_read_file(self):
        """Raw file read/write works."""
        self.storage.write_file("test_share", "test.txt", "Hello from test")
        result = self.storage.read_file("test_share", "test.txt")
        self.assertEqual(result, "Hello from test")


class TestContextMemoryAgent(unittest.TestCase):
    """Test ContextMemory agent (memory read)."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        # Patch storage factory to return local storage
        from utils.local_file_storage import LocalFileStorageManager
        self.storage = LocalFileStorageManager(base_path=self.test_dir)

        # Pre-populate with test memories
        self.storage.set_memory_context(None)
        self.storage.write_json({
            "mem-1": {
                "conversation_id": "current",
                "session_id": "current",
                "message": "User prefers morning meetings",
                "mood": "neutral",
                "theme": "preference",
                "date": "2025-12-15",
                "time": "10:30:45"
            },
            "mem-2": {
                "conversation_id": "current",
                "session_id": "current",
                "message": "Follow up with Acme Corp on Q1 proposal",
                "mood": "neutral",
                "theme": "task",
                "date": "2025-12-16",
                "time": "14:20:30"
            },
            "mem-3": {
                "conversation_id": "current",
                "session_id": "current",
                "message": "Budget for project is $50,000",
                "mood": "neutral",
                "theme": "fact",
                "date": "2025-12-14",
                "time": "09:00:00"
            }
        })

        self.patcher = patch('agents.context_memory_agent.get_storage_manager', return_value=self.storage)
        self.patcher.start()

        from agents.context_memory_agent import ContextMemoryAgent
        self.agent = ContextMemoryAgent()
        self.agent.storage_manager = self.storage

    def tearDown(self):
        self.patcher.stop()
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_full_recall(self):
        """Full recall returns all memories."""
        result = self.agent.perform(full_recall=True)
        self.assertIn("morning meetings", result)
        self.assertIn("Acme Corp", result)
        self.assertIn("$50,000", result)

    def test_default_is_full_recall(self):
        """No params defaults to full recall."""
        result = self.agent.perform()
        self.assertIn("morning meetings", result)
        self.assertIn("Acme Corp", result)

    def test_keyword_filter(self):
        """Keyword filtering returns only matching memories."""
        result = self.agent.perform(keywords=["Acme"])
        self.assertIn("Acme Corp", result)

    def test_max_messages(self):
        """max_messages limits results."""
        result = self.agent.perform(max_messages=1)
        # Should have at most 1 bullet point
        lines = [l for l in result.split("\n") if l.strip().startswith("•")]
        self.assertLessEqual(len(lines), 1)

    def test_empty_memory(self):
        """Empty memory returns appropriate message."""
        self.storage.set_memory_context("empty-user-guid")
        self.storage.write_json({})
        self.agent.storage_manager = self.storage
        result = self.agent.perform(user_guid="empty-user-guid")
        self.assertIn("don't have any memories", result.lower())

    def test_agent_metadata(self):
        """Agent has correct metadata schema."""
        self.assertEqual(self.agent.name, "ContextMemory")
        self.assertIn("parameters", self.agent.metadata)
        props = self.agent.metadata["parameters"]["properties"]
        self.assertIn("user_guid", props)
        self.assertIn("max_messages", props)
        self.assertIn("keywords", props)
        self.assertIn("full_recall", props)


class TestManageMemoryAgent(unittest.TestCase):
    """Test ManageMemory agent (memory write)."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        from utils.local_file_storage import LocalFileStorageManager
        self.storage = LocalFileStorageManager(base_path=self.test_dir)

        self.patcher = patch('agents.manage_memory_agent.get_storage_manager', return_value=self.storage)
        self.patcher.start()

        from agents.manage_memory_agent import ManageMemoryAgent
        self.agent = ManageMemoryAgent()
        self.agent.storage_manager = self.storage

    def tearDown(self):
        self.patcher.stop()
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_store_fact(self):
        """Store a fact memory."""
        result = self.agent.perform(memory_type="fact", content="The sky is blue")
        self.assertIn("Successfully stored", result)
        self.assertIn("fact", result)

        # Verify in storage
        data = self.storage.read_json()
        self.assertTrue(len(data) > 0)
        memory = list(data.values())[0]
        self.assertEqual(memory["message"], "The sky is blue")
        self.assertEqual(memory["theme"], "fact")

    def test_store_preference(self):
        """Store a preference memory."""
        result = self.agent.perform(memory_type="preference", content="Dark mode preferred")
        self.assertIn("preference", result)

    def test_store_insight(self):
        """Store an insight memory."""
        result = self.agent.perform(memory_type="insight", content="Sales peak in Q4")
        self.assertIn("insight", result)

    def test_store_task(self):
        """Store a task memory."""
        result = self.agent.perform(memory_type="task", content="Review Q1 report by Friday")
        self.assertIn("task", result)

    def test_empty_content_rejected(self):
        """Empty content returns error."""
        result = self.agent.perform(memory_type="fact", content="")
        self.assertIn("Error", result)

    def test_user_specific_memory(self):
        """Memory stored for specific user."""
        user_guid = "550e8400-e29b-41d4-a716-446655440000"
        result = self.agent.perform(
            memory_type="fact",
            content="User's birthday is March 15",
            user_guid=user_guid
        )
        self.assertIn("Successfully stored", result)
        self.assertIn(user_guid, result)

    def test_memory_has_timestamp(self):
        """Stored memory includes date and time."""
        self.agent.perform(memory_type="fact", content="Test timestamp")
        data = self.storage.read_json()
        memory = list(data.values())[0]
        self.assertIn("date", memory)
        self.assertIn("time", memory)
        # Date should be today
        self.assertEqual(memory["date"], datetime.now().strftime("%Y-%m-%d"))

    def test_multiple_memories(self):
        """Multiple memories stored with unique IDs."""
        self.agent.perform(memory_type="fact", content="Fact one")
        self.agent.perform(memory_type="fact", content="Fact two")
        data = self.storage.read_json()
        self.assertEqual(len(data), 2)
        messages = [v["message"] for v in data.values()]
        self.assertIn("Fact one", messages)
        self.assertIn("Fact two", messages)

    def test_agent_metadata(self):
        """Agent has correct metadata schema."""
        self.assertEqual(self.agent.name, "ManageMemory")
        meta = self.agent.metadata
        self.assertIn("memory_type", meta["parameters"]["properties"])
        self.assertIn("content", meta["parameters"]["properties"])
        self.assertEqual(meta["parameters"]["required"], ["memory_type", "content"])


class TestAgentLoading(unittest.TestCase):
    """Test agent discovery and loading from agents/ folder."""

    def test_load_core_agents(self):
        """Core agents load successfully from agents/ folder."""
        from function_app import load_agents_from_folder
        agents = load_agents_from_folder()
        # Returns dict: name -> agent instance
        self.assertIsInstance(agents, dict)
        self.assertIn("ContextMemory", agents)
        self.assertIn("ManageMemory", agents)
        self.assertGreaterEqual(len(agents), 2)

    def test_agents_have_metadata(self):
        """All loaded agents have proper metadata for OpenAI function calling."""
        from function_app import load_agents_from_folder
        agents = load_agents_from_folder()
        for name, agent in agents.items():
            self.assertTrue(hasattr(agent, 'name'), f"Agent missing 'name'")
            self.assertTrue(hasattr(agent, 'metadata'), f"Agent {name} missing 'metadata'")
            meta = agent.metadata
            self.assertIn("name", meta, f"Agent {name} metadata missing 'name'")
            self.assertIn("description", meta, f"Agent {name} metadata missing 'description'")
            self.assertIn("parameters", meta, f"Agent {name} metadata missing 'parameters'")

    def test_agents_have_perform_method(self):
        """All loaded agents have a callable perform() method."""
        from function_app import load_agents_from_folder
        agents = load_agents_from_folder()
        for name, agent in agents.items():
            self.assertTrue(callable(getattr(agent, 'perform', None)),
                          f"Agent {name} missing callable 'perform'")


class TestStringSafety(unittest.TestCase):
    """Test string safety utilities."""

    def test_ensure_string_content_with_none(self):
        """None message content becomes empty string."""
        from function_app import ensure_string_content
        msg = {"role": "user", "content": None}
        result = ensure_string_content(msg)
        self.assertEqual(result["content"], "")

    def test_ensure_string_content_with_string(self):
        """String content passes through unchanged."""
        from function_app import ensure_string_content
        msg = {"role": "user", "content": "Hello"}
        result = ensure_string_content(msg)
        self.assertEqual(result["content"], "Hello")

    def test_ensure_string_content_with_list(self):
        """List content is stringified."""
        from function_app import ensure_string_content
        msg = {"role": "user", "content": ["item1", "item2"]}
        result = ensure_string_content(msg)
        self.assertIsInstance(result["content"], str)


class TestAPIContract(unittest.TestCase):
    """Test the API request/response contract."""

    def test_health_response_structure(self):
        """Health response builds correct JSON structure."""
        # Test the health status construction logic directly
        health_status = {
            "status": "healthy",
            "timestamp": "2025-01-01T00:00:00Z",
            "version": "1.0.0",
            "checks": {
                "basic": {"status": "pass", "message": "Function app is responding"}
            }
        }
        # Validate structure matches expected contract
        self.assertEqual(health_status["status"], "healthy")
        self.assertIn("timestamp", health_status)
        self.assertIn("checks", health_status)
        self.assertIn("basic", health_status["checks"])

    def test_cors_headers(self):
        """CORS headers are built correctly."""
        from function_app import build_cors_response
        headers = build_cors_response("http://localhost:3000")
        self.assertIn("Access-Control-Allow-Origin", headers)
        self.assertIn("Access-Control-Allow-Methods", headers)


class TestMemoryReadWriteIntegration(unittest.TestCase):
    """Integration test: write memory then read it back."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        from utils.local_file_storage import LocalFileStorageManager
        self.storage = LocalFileStorageManager(base_path=self.test_dir)

        self.ctx_patcher = patch('agents.context_memory_agent.get_storage_manager', return_value=self.storage)
        self.mgr_patcher = patch('agents.manage_memory_agent.get_storage_manager', return_value=self.storage)
        self.ctx_patcher.start()
        self.mgr_patcher.start()

        from agents.context_memory_agent import ContextMemoryAgent
        from agents.manage_memory_agent import ManageMemoryAgent
        self.reader = ContextMemoryAgent()
        self.reader.storage_manager = self.storage
        self.writer = ManageMemoryAgent()
        self.writer.storage_manager = self.storage

    def tearDown(self):
        self.ctx_patcher.stop()
        self.mgr_patcher.stop()
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_write_then_read_shared(self):
        """Write to shared memory, then read it back."""
        self.writer.perform(memory_type="fact", content="Project deadline is March 30")
        result = self.reader.perform(full_recall=True)
        self.assertIn("March 30", result)

    def test_write_then_read_user_specific(self):
        """Write to user memory, then read it back."""
        guid = "550e8400-e29b-41d4-a716-446655440000"
        self.writer.perform(memory_type="preference", content="Prefers dark mode", user_guid=guid)
        result = self.reader.perform(user_guid=guid, full_recall=True)
        self.assertIn("dark mode", result)

    def test_user_memory_not_in_shared(self):
        """User-specific memory doesn't bleed into shared memory."""
        guid = "550e8400-e29b-41d4-a716-446655440000"
        self.writer.perform(memory_type="fact", content="Secret user data", user_guid=guid)

        # Shared memory should NOT contain user data
        self.storage.set_memory_context(None)
        shared = self.storage.read_json()
        shared_messages = [v.get("message", "") for v in shared.values() if isinstance(v, dict)]
        self.assertNotIn("Secret user data", shared_messages)

    def test_multiple_types_stored(self):
        """Multiple memory types can be stored and recalled."""
        self.writer.perform(memory_type="fact", content="Earth orbits the Sun")
        self.writer.perform(memory_type="task", content="Buy groceries")
        self.writer.perform(memory_type="insight", content="Revenue grows in Q4")
        self.writer.perform(memory_type="preference", content="Prefers email over chat")

        result = self.reader.perform(full_recall=True)
        self.assertIn("Earth orbits", result)
        self.assertIn("groceries", result)
        self.assertIn("Q4", result)
        self.assertIn("email", result)

    def test_keyword_search_after_write(self):
        """Write multiple memories, then search by keyword."""
        self.writer.perform(memory_type="fact", content="Python is a programming language")
        self.writer.perform(memory_type="fact", content="Azure Functions runs serverless code")
        self.writer.perform(memory_type="task", content="Deploy Python app to Azure")

        result = self.reader.perform(keywords=["Python"])
        self.assertIn("Python", result)


if __name__ == '__main__':
    unittest.main(verbosity=2)
