"""Battery: this computer's battery level and whether it's plugged in. Works on Mac, Windows and Linux.

A desktop with no battery says so ("no battery; running on wall power"). Read-only. Short, speakable answers.
"""
import glob
import json
import platform
import re
import subprocess

from agents.basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@kody-w/battery_agent",
    "version": "1.0.0",
    "display_name": "Battery",
    "description": "This computer's battery level and whether it's plugged in, on Mac, Windows or Linux.",
    "author": "kody-w",
    "tags": ["device", "battery", "estate"],
    "category": "operations",
    "quality_tier": "community",
    "requires_env": [],
    "dependencies": ["@rapp/basic_agent"],
    "say": ["check the battery", "check my battery", "how is the battery"],
}


def mac():
    out = subprocess.run(["pmset", "-g", "batt"], capture_output=True, text=True, timeout=10).stdout
    m = re.search(r"(\d+)%", out)
    if not m:
        return "No battery; running on wall power."
    plugged = "AC Power" in out
    return f"Battery is at {m.group(1)}% and {'plugged in' if plugged else 'not plugged in'}."


def windows():
    ps = ("Get-CimInstance Win32_Battery | Select-Object EstimatedChargeRemaining,BatteryStatus | ConvertTo-Json")
    out = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True, timeout=20).stdout.strip()
    if not out:
        return "No battery; this computer runs on wall power."
    b = json.loads(out)
    b = b[0] if isinstance(b, list) else b
    plugged = b.get("BatteryStatus") in (2, 6, 7, 8, 9)  # on AC / charging states
    return f"Battery is at {b.get('EstimatedChargeRemaining')}% and {'plugged in' if plugged else 'not plugged in'}."


def linux():
    caps = glob.glob("/sys/class/power_supply/BAT*/capacity")
    if not caps:
        return "No battery; running on wall power."
    pct = open(caps[0]).read().strip()
    status = open(caps[0].replace("capacity", "status")).read().strip()
    return f"Battery is at {pct}% and {'not plugged in' if status == 'Discharging' else 'plugged in'}."


class BatteryAgent(BasicAgent):
    def __init__(self):
        self.name = "Battery"
        self.metadata = {
            "name": self.name,
            "description": "Reports this computer's battery percent and whether it is plugged in. Use for 'what's my battery'.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **_):
        try:
            return {"Darwin": mac, "Windows": windows}.get(platform.system(), linux)()
        except Exception as e:
            return f"I couldn't read the battery ({e})."
