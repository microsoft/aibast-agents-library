"""Storage: how much room is left on this computer's main drive. Mac, Windows, Linux. Read-only."""
import shutil, os
from agents.basic_agent import BasicAgent

__manifest__ = {"schema": "rapp-agent/1.0", "name": "@brainstem/storage_agent", "version": "1.0.0", "display_name": "Storage",
                "description": "How much room is left on this computer's main drive.", "category": "device",
                "dependencies": ["@rapp/basic_agent"], "say": ["check my storage", "check the storage", "how much room is left"]}


class StorageAgent(BasicAgent):
    def __init__(self):
        self.name = "Storage"
        self.metadata = {"name": self.name, "description": "Reports how much free space is left on this computer's main drive.",
                         "parameters": {"type": "object", "properties": {}, "required": []}}
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **_):
        total, used, free = shutil.disk_usage(os.path.abspath(os.sep))
        gb = lambda b: round(b / 1e9)
        return f"{gb(free)} GB free of {gb(total)} GB ({round(100 * free / total)}% left)."
