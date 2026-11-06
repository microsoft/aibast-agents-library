"""Open apps: which apps are still open on this computer. Mac, Windows, Linux. Read-only."""
import platform, subprocess
from agents.basic_agent import BasicAgent

__manifest__ = {"schema": "rapp-agent/1.0", "name": "@brainstem/open_apps_agent", "version": "1.0.0", "display_name": "Open apps",
                "description": "Which apps are still open on this computer.", "category": "device",
                "dependencies": ["@rapp/basic_agent"],
                "say": ["tell me what's still open", "see what's still open", "what's still open", "check what's open"]}


def _apps():
    sysname = platform.system()
    if sysname == "Darwin":
        out = subprocess.run(["osascript", "-e", 'tell application "System Events" to get name of every process whose background only is false'],
                             capture_output=True, text=True, timeout=20).stdout
        return [a.strip() for a in out.split(",") if a.strip()]
    if sysname == "Windows":
        ps = "Get-Process | Where-Object {$_.MainWindowTitle} | Select-Object -ExpandProperty ProcessName"
        out = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True, timeout=30).stdout
        return sorted(set(l.strip() for l in out.splitlines() if l.strip()))
    out = subprocess.run(["wmctrl", "-lx"], capture_output=True, text=True, timeout=10).stdout if shutil_which("wmctrl") else ""
    return sorted(set(l.split()[2].split(".")[-1] for l in out.splitlines() if len(l.split()) > 2))


def shutil_which(x):
    import shutil
    return shutil.which(x)


class OpenAppsAgent(BasicAgent):
    def __init__(self):
        self.name = "OpenApps"
        self.metadata = {"name": self.name, "description": "Lists the apps that are still open on this computer.",
                         "parameters": {"type": "object", "properties": {}, "required": []}}
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **_):
        try:
            apps = _apps()
        except Exception as e:
            return f"I couldn't see the open apps ({e})."
        if not apps:
            return "Nothing else is open."
        return f"{len(apps)} apps are open: " + ", ".join(apps[:12]) + ("..." if len(apps) > 12 else "") + "."
