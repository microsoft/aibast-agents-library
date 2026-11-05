"""RAPP Brainstem mouse-first terminal UI.

A Textual (github.com/Textualize/textual) chat client for headless/SSH
sessions where no GUI browser is available. It launches `brainstem.py` as a
background subprocess (the same server the browser UI talks to), waits for
`/health`, then renders a mouse-clickable chat: scroll with the wheel or by
dragging, click the input box, click buttons — no keyboard-only navigation
required. All communication is loopback HTTP against the same /chat/stream
and /health contract the browser UI already uses; nothing about the server
or the wire protocol changes.

This is a FALLBACK UI, not a replacement for the browser. install.sh only
launches it when:
  - no GUI browser could be opened (headless/SSH/container), AND
  - stdin is a real interactive terminal, AND
  - the `textual` package is import-able (installed on demand, best-effort).
Any terminal that can't satisfy those (old machines, dumb terminals, CI,
piped input) keeps getting today's plain `python brainstem.py` log output.
That raw-shell path is the permanent backward-compatible fallback and must
keep working unmodified.
"""
from __future__ import annotations

import functools
import json
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path

import requests
from dotenv import load_dotenv

try:
    from textual.app import App, ComposeResult
    from textual.containers import Horizontal, Vertical
    from textual.widgets import Button, Footer, Header, Input, RichLog, Static
except ImportError as exc:  # pragma: no cover - import guard for callers
    raise SystemExit(
        "The 'textual' package is required for the mouse-first terminal UI. "
        "Install it with: pip install textual\n"
        f"(import error: {exc})"
    )

HOST = "127.0.0.1"
HEALTH_TIMEOUT_S = 60


def _resolve_port() -> int:
    """Mirror brainstem.py's own PORT resolution exactly (same .env, same
    fallback-on-invalid-value behavior) so the TUI always polls the port the
    server it just spawned will actually bind — never a stale hardcoded 7071
    when `.env` sets a custom PORT."""
    load_dotenv(Path(__file__).resolve().parent / ".env")
    try:
        return int((os.getenv("PORT") or "7071").strip())
    except ValueError:
        return 7071


PORT = _resolve_port()
BASE_URL = f"http://{HOST}:{PORT}"


def _wait_for_health(base_url: str, timeout_s: int = HEALTH_TIMEOUT_S) -> bool:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            resp = requests.get(f"{base_url}/health", timeout=1)
            if resp.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(0.5)
    return False


class BrainstemTUI(App):
    """Mouse-clickable chat client for the local Brainstem server."""

    CSS = """
    Screen {
        layout: vertical;
    }
    #chat-log {
        height: 1fr;
        border: round $accent;
        padding: 0 1;
    }
    #composer {
        height: 3;
        padding: 0 1;
    }
    #input-box {
        width: 1fr;
    }
    #send-btn {
        width: 12;
    }
    """

    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
        ("ctrl+q", "quit", "Quit"),
    ]

    def __init__(self, server_process: "subprocess.Popen | None" = None):
        super().__init__()
        self.server_process = server_process
        self.session_id = str(uuid.uuid4())
        self.conversation_history: list[dict] = []
        self._busy = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(
            "RAPP Brainstem — mouse-first terminal  "
            "(click, scroll, or type below; browser UI still at "
            f"{BASE_URL})",
            id="banner",
        )
        yield RichLog(id="chat-log", wrap=True, markup=True, highlight=True)
        with Horizontal(id="composer"):
            yield Input(placeholder="Ask Brainstem anything…", id="input-box")
            yield Button("Send", id="send-btn", variant="primary")
        yield Footer()

    def on_mount(self) -> None:
        log = self.query_one("#chat-log", RichLog)
        log.write(
            "[bold green]Brainstem is ready.[/bold green] Click the input box "
            "below, type, then click Send (or press Enter). "
            "Scroll this pane with your mouse wheel."
        )
        self.query_one("#input-box", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "send-btn":
            self._submit()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "input-box":
            self._submit()

    def _submit(self) -> None:
        if self._busy:
            return
        box = self.query_one("#input-box", Input)
        text = box.value.strip()
        if not text:
            return
        box.value = ""
        self._busy = True
        log = self.query_one("#chat-log", RichLog)
        log.write(f"[bold cyan]You:[/bold cyan] {text}")
        self.run_worker(
            functools.partial(self._send, text), exclusive=False, thread=True
        )

    def _send(self, text: str) -> None:
        log = self.query_one("#chat-log", RichLog)
        payload = {
            "user_input": text,
            "conversation_history": self.conversation_history,
            "session_id": self.session_id,
        }
        reply_parts: list[str] = []
        try:
            with requests.post(
                f"{BASE_URL}/chat/stream",
                json=payload,
                stream=True,
                timeout=120,
            ) as resp:
                resp.raise_for_status()
                for raw_line in resp.iter_lines(decode_unicode=True):
                    if not raw_line or not raw_line.startswith("data: "):
                        continue
                    try:
                        event = json.loads(raw_line[len("data: "):])
                    except json.JSONDecodeError:
                        continue
                    kind = event.get("type")
                    if kind == "delta":
                        reply_parts.append(event.get("text", ""))
                    elif kind == "error":
                        self.call_from_thread(
                            log.write,
                            f"[bold red]Error:[/bold red] {event.get('error', 'unknown error')}",
                        )
                    elif kind == "done":
                        reply = event.get("response") or "".join(reply_parts)
                        self.call_from_thread(
                            log.write, f"[bold magenta]Brainstem:[/bold magenta] {reply}"
                        )
                        self.conversation_history.append({"role": "user", "content": text})
                        self.conversation_history.append({"role": "assistant", "content": reply})
        except requests.exceptions.RequestException as exc:
            self.call_from_thread(
                log.write, f"[bold red]Connection error:[/bold red] {exc}"
            )
        finally:
            self._busy = False

    def action_quit(self) -> None:  # noqa: D401 - Textual action hook
        self.exit()

    def on_unmount(self) -> None:
        if self.server_process and self.server_process.poll() is None:
            try:
                self.server_process.terminate()
            except Exception:
                pass


def main() -> int:
    brainstem_dir = Path(__file__).resolve().parent
    venv_python = os.environ.get("BRAINSTEM_VENV_PYTHON") or sys.executable

    server_process = None
    if not _wait_for_health(BASE_URL, timeout_s=1):
        server_process = subprocess.Popen(
            [venv_python, str(brainstem_dir / "brainstem.py")],
            cwd=str(brainstem_dir),
        )

    if not _wait_for_health(BASE_URL):
        print("[brainstem-tui] Server did not become healthy in time; "
              "falling back to raw log output.")
        if server_process is not None and server_process.poll() is None:
            # The server may genuinely still be alive but stuck — don't block
            # main() (and therefore install.sh's launch) forever waiting on it.
            try:
                server_process.terminate()
                server_process.wait(timeout=5)
            except Exception:
                pass
        return 1

    app = BrainstemTUI(server_process=server_process)
    try:
        app.run()
    except Exception as exc:  # noqa: BLE001 - any TUI crash must still fall back cleanly
        print(f"[brainstem-tui] Terminal UI crashed: {exc}")
        return 1
    finally:
        # Guaranteed cleanup regardless of how app.run() exits (clean quit,
        # an exception here, or a crash inside a Textual worker/handler that
        # app.run() swallows internally — see the return_code check below) —
        # a crashed TUI must never leave an orphaned server holding the port.
        if server_process is not None and server_process.poll() is None:
            try:
                server_process.terminate()
                server_process.wait(timeout=5)
            except Exception:
                pass

    # Textual catches exceptions raised inside event handlers and thread
    # workers internally (App._handle_exception) and lets app.run() return
    # normally with app.return_code set, rather than re-raising — so a crash
    # inside _send() (a thread worker, the core chat path) would otherwise
    # look identical to a clean quit here. Propagate the real code so
    # install.sh's fallback gate can tell them apart.
    return app.return_code or 0


if __name__ == "__main__":
    raise SystemExit(main())
