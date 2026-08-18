"""Hot-loadable agent that operates the visible RAPP Brainstem Frontier frontend."""

import json
import os
import urllib.error
import urllib.request

from agents.basic_agent import BasicAgent


def _driver_file():
    explicit = os.getenv("BRAINSTEM_BETA_UI_DRIVER_FILE")
    if explicit:
        return os.path.expanduser(explicit)
    brainstem_home = os.getenv(
        "BRAINSTEM_HOME",
        os.path.join(os.path.expanduser("~"), ".brainstem"),
    )
    return os.path.join(brainstem_home, "beta-launcher", "ui-driver.json")


def _camelize(value):
    key_map = {
        "alt_key": "altKey",
        "ctrl_key": "ctrlKey",
        "duration_ms": "durationMs",
        "meta_key": "metaKey",
        "max_duration_ms": "maxDurationMs",
        "settle_ms": "settleMs",
        "shift_key": "shiftKey",
        "target_text": "targetText",
        "timeout_ms": "timeoutMs",
        "typing_delay_ms": "typingDelayMs",
    }
    if isinstance(value, list):
        return [_camelize(item) for item in value]
    if isinstance(value, dict):
        return {
            key_map.get(key, key): _camelize(item)
            for key, item in value.items()
            if item is not None
        }
    return value


class BrainstemUiDriver(BasicAgent):
    def __init__(self):
        self.name = "BrainstemUiDriver"
        step_properties = {
            "action": {
                "type": "string",
                "enum": [
                    "announce",
                    "click",
                    "inspect",
                    "press",
                    "read",
                    "type",
                    "wait",
                ],
            },
            "selector": {
                "type": "string",
                "description": "CSS selector for the visible target.",
            },
            "target_text": {
                "type": "string",
                "description": "Visible control text when a selector is not known.",
            },
            "text": {
                "type": "string",
                "description": "Text to wait for or announce.",
            },
            "value": {
                "type": "string",
                "description": "Text to type into an input or textarea.",
            },
            "key": {"type": "string"},
            "label": {
                "type": "string",
                "description": "Short narration shown beside the animated AI cursor.",
            },
            "optional": {"type": "boolean"},
            "replace": {"type": "boolean"},
            "timeout_ms": {"type": "integer"},
            "typing_delay_ms": {"type": "integer"},
            "settle_ms": {"type": "integer"},
            "duration_ms": {"type": "integer"},
            "max_duration_ms": {
                "type": "integer",
                "description": "Maximum recording duration before automatic stop.",
            },
            "alt_key": {"type": "boolean"},
            "ctrl_key": {"type": "boolean"},
            "meta_key": {"type": "boolean"},
            "shift_key": {"type": "boolean"},
            "target": {
                "type": "string",
                "enum": ["brainstem", "shell"],
                "description": "Use brainstem unless operating the Electron wrapper.",
            },
            "force_mode": {
                "type": "boolean",
                "description": (
                    "AI force mode: light the whole window's edges while this action runs so "
                    "the person can see an AI is driving. Only when the user asked for it."
                ),
            },
            "step": {
                "type": "string",
                "description": "For action=tour with value=goto: the click-through step id or index.",
            },
        }
        self.metadata = {
            "name": self.name,
            "description": (
                "Operate the actual visible RAPP Brainstem Frontier frontend. "
                "Every click and typed character is animated with an AI cursor so "
                "the user can watch and follow along. Prefer one run action with a "
                "short ordered steps array. Inspect first only when selectors are unknown."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    **step_properties,
                    "action": {
                        "type": "string",
                        "enum": [
                            "announce",
                            "click",
                            "force_mode",
                            "inspect",
                            "press",
                            "read",
                            "run",
                            "screenshot",
                            "start_recording",
                            "stop_recording",
                            "tour",
                            "type",
                            "wait",
                        ],
                        "description": (
                            "force_mode: value on|off|status lights or clears AI force mode. "
                            "tour: value start|next|prev|goto|stop|status drives the Show Mode "
                            "click-through preview in the shell."
                        ),
                    },
                    "steps": {
                        "type": "array",
                        "description": "Ordered visible UI actions for a single guided run.",
                        "items": {
                            "type": "object",
                            "properties": step_properties,
                            "required": ["action"],
                        },
                    },
                },
                "required": ["action"],
            },
        }
        super().__init__()

    def system_context(self):
        return (
            "When the user asks you to operate, demonstrate, configure, or test the "
            "visible RAPP Brainstem Frontier application, use BrainstemUiDriver. The user "
            "is watching the real interface: narrate actions briefly, prefer stable "
            "selectors, and use one run call for a sequence. After an important click "
            "or completed workflow, call screenshot so you and the user can inspect "
            "what the real window shows. If recording, finish with stop_recording; it "
            "already includes the final screenshot. Do not click a destructive "
            "confirmation unless the user's request authorizes that outcome. "
            "AI force mode is hidden until asked for: when the user tells you to use "
            "AI force mode (or to drive the Brainstem for them while they watch), "
            "send force_mode on first, pass force_mode=true on your run, and send "
            "force_mode off when you hand control back. The Show Mode click-through "
            "preview is driven with action tour (start, next, prev, goto+step, stop)."
        )

    def perform(self, action="", **kwargs):
        metadata_path = _driver_file()
        try:
            with open(metadata_path, "r", encoding="utf-8") as handle:
                metadata = json.load(handle)
        except (OSError, ValueError) as error:
            return (
                "The RAPP Brainstem Frontier UI driver is unavailable. "
                f"Expected a running Frontier client at {metadata_path}: {error}"
            )

        command = _camelize({"action": action, **kwargs})
        request = urllib.request.Request(
            f"http://{metadata['host']}:{metadata['port']}/v1/command",
            data=json.dumps(command).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {metadata['token']}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=130) as response:
                payload = json.load(response)
        except urllib.error.HTTPError as error:
            body = error.read().decode("utf-8", errors="replace")
            return f"Visible UI action failed: HTTP {error.code}: {body}"
        except (OSError, ValueError) as error:
            return f"Visible UI action failed: {error}"

        if not payload.get("ok"):
            return f"Visible UI action failed: {payload.get('error', 'unknown error')}"
        result = payload.get("result")
        if (
            action == "screenshot"
            and isinstance(result, dict)
            and isinstance(result.get("recording"), dict)
        ):
            action = "stop_recording"
        if action == "stop_recording" and isinstance(result, dict):
            recording = result.get("recording") or {}
            screenshot = result.get("screenshot") or {}
            screenshot.pop("dataUrl", "")
            visible_text = screenshot.pop("visibleText", "")
            content = (
                "Stopped the RAPP Brainstem Frontier window recording. "
                f"Saved {recording.get('path', 'the recording')} and captured "
                "the final visible state."
            )
            if visible_text:
                content += f"\n\nVisible window text:\n{visible_text}"
            structured = {
                "content": content,
                "log": content,
                "captures": [{
                    "url": screenshot.get("captureUrl"),
                    "path": screenshot.get("path"),
                    "alt": "Final RAPP Brainstem Frontier state after the recording",
                }],
                "recordings": [{
                    "url": recording.get("url"),
                    "path": recording.get("path"),
                    "mime_type": recording.get("mimeType"),
                    "duration_ms": recording.get("durationMs"),
                    "alt": "Autopilot demonstration recorded by the Brainstem",
                }],
            }
            return structured
        if action == "screenshot" and isinstance(result, dict):
            result.pop("dataUrl", "")
            visible_text = result.pop("visibleText", "")
            capture_url = result.get("captureUrl", "")
            content = (
                "Captured the actual RAPP Brainstem Frontier window after the UI action. "
                f"Saved locally at {result.get('path', 'unknown path')}."
            )
            if visible_text:
                content += f"\n\nVisible window text:\n{visible_text}"
            structured = {
                "content": content,
                "log": content,
                "captures": [{
                    "url": capture_url,
                    "path": result.get("path"),
                    "alt": "RAPP Brainstem Frontier after the agent action",
                }],
            }
            return structured
        return json.dumps(result, indent=2, ensure_ascii=True)
