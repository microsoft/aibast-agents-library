"""Write the single-file Rapid Prototyping agent, with every pack file inside it as readable lines.

  python3 pack/build_agent.py <out_dir>

One file the person downloads, reviews and loads is exactly what runs: no download at setup, no
encoded payloads (AIBAST constitution, Article VII). Prints the agent's sha256 for the guide page.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {"__pycache__", "out", ".playwright-cli", ".proto-ports"}
# what runs (never the pack's own tests or build scripts), mapped to where setup writes it
RUNTIME = {"pack/bin/brainstem-proto": "brainstem-proto", "pack/bridge.py": "bridge.py",
           "pack/templates.py": "templates.py", "pack/guide/rapp-guide-live.html": "guide/rapp-guide-live.html"}


def pack_files() -> dict[str, str]:
    """{path inside ~/.brainstem-proto: path in this repo}"""
    files = {dest: src for src, dest in RUNTIME.items()}
    for p in sorted((ROOT / "template").rglob("*")):
        rel = p.relative_to(ROOT)
        if p.is_file() and not (set(rel.parts) & SKIP) and p.suffix != ".pyc":
            files[rel.as_posix()] = rel.as_posix()
    return files


def render(files: dict[str, str]) -> str:
    out = ["PACK = {"]
    for dest, src in files.items():
        text = (ROOT / src).read_text()
        out.append(f"    {json.dumps(dest)}: [")
        out += [f"        {json.dumps(line, ensure_ascii=False)}," for line in text.split("\n")]
        out.append("    ],")
    out.append("}")
    return "\n".join(out) + "\n"


def main() -> None:
    out = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    out.mkdir(parents=True, exist_ok=True)
    src = (ROOT / "pack" / "rapid_prototyping_agent.template.py").read_text()
    marker = "PACK = {}  # filled in by pack/build_agent.py\n"
    assert marker in src
    files = pack_files()
    agent = src.replace(marker, render(files))
    dest = out / "rapid_prototyping_agent.py"
    dest.write_text(agent)
    print(f"{dest}  {len(files)} files inside  {round(len(agent) / 1024)} KB  sha256 {hashlib.sha256(agent.encode()).hexdigest()}")


if __name__ == "__main__":
    main()
