"""
LocalStorageManager — drop-in replacement for AzureFileStorageManager.
Mirrors the CommunityRAPP storage layout:
  shared_memories/memory.json   — shared memories
  memory/{guid}/user_memory.json — per-user memories
Data lives in .brainstem_data/ next to this file.
"""

import os
import json

_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".brainstem_data")


def _safe_join(*parts):
    """Join path parts under _DATA_DIR and refuse anything that escapes it.

    user_guid and agent-supplied file paths are attacker-influenced (they come from
    LLM tool-call arguments), so a value like '../../.env' or an absolute path must
    not be able to read or write outside the data directory. Returns an absolute path
    guaranteed to live under _DATA_DIR, or raises ValueError."""
    base = os.path.abspath(_DATA_DIR)
    target = os.path.abspath(os.path.join(base, *[str(p) for p in parts]))
    if target != base and not target.startswith(base + os.sep):
        raise ValueError(f"path escapes data directory: {os.path.join(*[str(p) for p in parts])}")
    return target


def _atomic_write(path, write_fn):
    """Write via a temp file in the same directory + os.replace, so a crash or a
    concurrent reader never sees a half-written (and on the next write, silently
    wiped) file. write_fn receives the open file handle."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.{os.getpid()}.tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            write_fn(f)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass


class AzureFileStorageManager:
    """
    Local-first shim that mirrors the AzureFileStorageManager API from
    CommunityRAPP.  Agents import this transparently via the shim in brainstem.py.
    """

    DEFAULT_MARKER_GUID = "c0p110t0-aaaa-bbbb-cccc-123456789abc"

    def __init__(self, share_name=None, **kwargs):
        self.current_guid = None
        # Matches CommunityRAPP paths
        self.shared_memory_path = "shared_memories"
        self.default_file_name = "memory.json"
        self.current_memory_path = self.shared_memory_path
        os.makedirs(_DATA_DIR, exist_ok=True)

    # ── Context ───────────────────────────────────────────────────────────

    def set_memory_context(self, user_guid=None):
        """Set the memory context — matches CommunityRAPP's set_memory_context."""
        if not user_guid or user_guid == self.DEFAULT_MARKER_GUID:
            self.current_guid = None
            self.current_memory_path = self.shared_memory_path
            return True

        # Valid GUID — set up user-specific path (memory/{guid})
        self.current_guid = user_guid
        self.current_memory_path = f"memory/{user_guid}"
        return True

    # ── Core I/O ──────────────────────────────────────────────────────────

    def _file_path(self):
        """Return the absolute path for the current memory file.
        Shared:  .brainstem_data/shared_memories/memory.json
        User:    .brainstem_data/memory/{guid}/user_memory.json
        A malicious user_guid (e.g. '../../') is contained by _safe_join.
        """
        if self.current_guid:
            rel = os.path.join(self.current_memory_path, "user_memory.json")
        else:
            rel = os.path.join(self.shared_memory_path, self.default_file_name)
        path = _safe_join(rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        return path

    def read_json(self, file_path=None):
        """Read JSON data from local storage."""
        path = _safe_join(file_path) if file_path else self._file_path()
        if not os.path.exists(path):
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}

    def write_json(self, data, file_path=None):
        """Write JSON data to local storage (atomically)."""
        path = _safe_join(file_path) if file_path else self._file_path()
        _atomic_write(path, lambda f: json.dump(data, f, indent=2, default=str))
        return True

    # ── Convenience methods used by some agents ───────────────────────────

    def read_file(self, file_path):
        full = _safe_join(file_path)
        if not os.path.exists(full):
            return None
        with open(full, "r", encoding="utf-8") as f:
            return f.read()

    def write_file(self, file_path, content):
        full = _safe_join(file_path)
        _atomic_write(full, lambda f: f.write(content))
        return True

    def list_files(self, directory=""):
        full = _safe_join(directory) if directory else os.path.abspath(_DATA_DIR)
        if not os.path.exists(full):
            return []
        return os.listdir(full)

    def delete_file(self, file_path):
        full = _safe_join(file_path)
        if os.path.exists(full):
            os.remove(full)
            return True
        return False

    def file_exists(self, file_path):
        try:
            return os.path.exists(_safe_join(file_path))
        except ValueError:
            return False
