"""Recapture a solution's locked-case transcripts (solutions/<slug>/evals/transcripts.json) with the library's own
tools/capture_demo_transcripts.py, against a throwaway brainstem (brainfreeze) on its own port instead of the user's
main brainstem on :7071.

    python capture_transcripts.py <repo> <slug> [--tries N]
"""
import importlib.util, os, sys, tempfile
from pathlib import Path

sys.path.insert(0, os.environ.get("BRAINFREEZE_DIR", str(Path.home() / "Documents/GitHub/brainfreeze")))
from brainfreeze import Throwaway  # noqa: E402

repo, slug = Path(sys.argv[1]).expanduser().resolve(), sys.argv[2]
tries = int(sys.argv[sys.argv.index("--tries") + 1]) if "--tries" in sys.argv else 3
spec = importlib.util.spec_from_file_location("capture_demo_transcripts", repo / "tools" / "capture_demo_transcripts.py")
cap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cap)

bs = Throwaway(name=f"capture-{slug}", agents=[], env={"GITHUB_MODEL": os.environ.get("GITHUB_MODEL", "claude-sonnet-5")}).up()
try:
    cap.HEALTH, cap.CHAT = f"{bs.url}/health", f"{bs.url}/chat"
    cap.CAPTURE_LOCK = Path(tempfile.gettempdir()) / f"aibast-capture-{slug}.lock"
    case = repo / "tests" / "demo_cases" / f"{slug}.json"
    out = repo / "solutions" / slug / "evals" / "transcripts.json"
    for attempt in range(1, tries + 1):
        try:
            art = cap.capture(case, out, Path(bs.brainstem_dir) / "agents")
            print(f"[OK] {slug}: {len(art['transcripts'])} transcripts captured (attempt {attempt})")
            break
        except AssertionError as e:
            print(f"[retry {attempt}] {slug}: {e}")
    else:
        sys.exit(f"[FAIL] {slug}: capture did not pass in {tries} attempts")
finally:
    bs.down()
