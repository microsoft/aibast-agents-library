#!/usr/bin/env python3
"""aibast: one command for the library's routine jobs. Each subcommand wraps the existing step.

  python tools/aibast.py api build        rebuild api/ and llms.txt (tools/build_library_api.py)
  python tools/aibast.py api check        fail if api/ or llms.txt does not match its sources
  python tools/aibast.py media verify     check every file in the media map against its sha256
  python tools/aibast.py media verify --live
                                          the same, fetched from the raw base in api/registry.json
  python tools/aibast.py pages size       build the Pages artifact into _site and print its size
  python tools/aibast.py verify --live --base URL [--play]
                                          the whole site as served: every media file from its raw
                                          base against sha256 and, with --play, every solution's
                                          narration in a real browser on every surface
                                          (browser-audit/narration-playback.mjs; npm ci there first)
  python tools/aibast.py demo check <slug> [--base URL]
                                          confirm a solution's demo docs and narration clips exist
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable


def run(*args: str) -> int:
    return subprocess.run([PY, *args], cwd=ROOT).returncode


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def media_items() -> list[dict]:
    index = load("api/v1/media/index.json")
    return [item for group in index["groups"] for item in load(group["doc"])["items"]]


def media_verify(live: bool) -> int:
    raw = load("api/registry.json")["raw"]
    bad = 0
    items = media_items()
    for item in items:
        if live:
            with urllib.request.urlopen(raw + item["path"], timeout=60) as response:
                data = response.read()
        else:
            data = (ROOT / item["path"]).read_bytes()
        if hashlib.sha256(data).hexdigest() != item["sha256"]:
            bad += 1
            print(f"mismatch: {item['path']}")
    print(f"media: {len(items) - bad} of {len(items)} match their sha256" + (f" ({raw})" if live else ""))
    return 1 if bad else 0


def pages_size() -> int:
    ref = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    code = run("scripts/build_pages_site.py", "--root", ".", "--out", "_site",
               "--owner", "microsoft", "--repo", "aibast-agents-library", "--ref", ref)
    if code:
        return code
    files = [p for p in (ROOT / "_site").rglob("*") if p.is_file()]
    print(f"pages: {len(files)} files, {sum(p.stat().st_size for p in files) / 1e6:.1f} MB in _site")
    return 0


def demo_check(slug: str, base: str | None) -> int:
    def get(path: str) -> dict:
        if base:
            with urllib.request.urlopen(base.rstrip("/") + "/" + path, timeout=60) as response:
                return json.load(response)
        return load(path)

    solution = get(f"api/v1/solutions/{slug}.json")
    scenarios = [s for s in solution["try"]["scenarios"] if s.get("doc")]
    clips = 0
    for scenario in scenarios:
        doc = get(scenario["doc"])
        for segment in (doc.get("narration") or {}).get("segments", []):
            if segment.get("media"):
                clips += 1
                if not base and not (ROOT / segment["media"]["url"]).is_file():
                    print(f"missing clip: {segment['media']['url']}")
                    return 1
    print(f"demo {slug}: {len(scenarios)} recorded scenarios, {clips} narration clips")
    return 0 if scenarios else 1


def fetch_bytes(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "aibast-library-verify"})
    last: Exception | None = None
    for _ in range(3):
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                return response.read()
        except Exception as exc:  # retried, then reported
            last = exc
    raise last  # type: ignore[misc]


def verify_live(base: str, play: bool, workers: int, parallel: int = 2,
                report: str = "verify-live.json") -> int:
    from concurrent.futures import ThreadPoolExecutor

    site = base.rstrip("/") + "/"
    raw = json.loads(fetch_bytes(site + "api/registry.json"))["raw"]
    index = json.loads(fetch_bytes(site + "api/v1/media/index.json"))
    items = [i for g in index["groups"] for i in json.loads(fetch_bytes(site + g["doc"]))["items"]]

    def check(item: dict) -> str | None:
        try:
            ok = hashlib.sha256(fetch_bytes(raw + item["path"])).hexdigest() == item["sha256"]
            return None if ok else f"{item['path']}: sha256 mismatch"
        except Exception as exc:
            return f"{item['path']}: {exc}"

    with ThreadPoolExecutor(max(1, min(workers, 16))) as pool:
        media_failures = [f for f in pool.map(check, items) if f]
    print(f"media: {len(items) - len(media_failures)} of {len(items)} match their sha256 ({raw})")
    doc: dict = {"site": site, "raw": raw,
                 "media": {"checked": len(items), "passed": len(items) - len(media_failures),
                           "failures": media_failures},
                 "narration": None}

    def save() -> None:
        Path(report).write_text(json.dumps(doc, indent=1) + "\n")
        print(f"results: {report}")
    for failure in media_failures:
        print(f"  {failure}")
    failures = len(media_failures)
    if play:
        script = ROOT / "browser-audit" / "narration-playback.mjs"
        probe = subprocess.run(["node", "-e", "require.resolve('playwright')"], cwd=script.parent,
                               capture_output=True, text=True)
        if probe.returncode != 0:
            print("narration: not run: Playwright is not installed. Run npm ci in browser-audit/ first.")
            doc["narration"] = {"error": "Playwright is not installed"}
            save()
            return 1
        slugs = [s["slug"] for s in json.loads(fetch_bytes(site + "api/v1/search.json"))["solutions"]]
        surfaces = [s["id"] for s in json.loads(fetch_bytes(site + "api/v1/index.json"))["surfaces"]]
        jobs = [(slug, surface) for slug in slugs for surface in surfaces]

        def run_one(job: tuple[str, str]) -> dict:
            slug, surface = job
            try:
                out = subprocess.run(["node", str(script), site, surface, slug], cwd=script.parent,
                                     capture_output=True, text=True, timeout=480)
                lines = out.stdout.strip().splitlines()
                if not lines:
                    stderr = out.stderr.strip().splitlines()
                    raise RuntimeError(stderr[-1] if stderr else f"no output, exit {out.returncode}")
                result = json.loads(lines[-1])
            except Exception as exc:  # timeout, or no JSON line at all
                result = {"slug": slug, "surface": surface, "crash": str(exc).splitlines()[0][:200]}
            result["ok"] = (not result.get("crash") and result.get("steps", 0) > 0
                            and result["passed"] == result["steps"] and not result["errors"])
            return result

        def describe(r: dict) -> str:
            if r.get("crash"):
                return f"{r['slug']} on {r['surface']}: crashed ({r['crash']})"
            return f"{r['slug']} on {r['surface']}: {r['passed']} of {r['steps']} clips, {r['errors']} page errors"

        with ThreadPoolExecutor(max(1, min(parallel, 4))) as pool:
            results = list(pool.map(run_one, jobs))
        # A crash is a failure of the check, not of the site: retry it exactly once, alone.
        retried = []
        for i, r in enumerate(results):
            if r.get("crash"):
                again = run_one((r["slug"], r["surface"]))
                retried.append((r, again))
                results[i] = again
        passed = sum(1 for r in results if r["ok"])
        on_retry = sum(1 for _, again in retried if again["ok"])
        note = f", {on_retry} passed on retry" if retried else ""
        print(f"narration: {passed} of {len(jobs)} solution and surface pairs play every clip from raw{note}")
        for first, again in retried:
            print(f"  retried after a crash: {describe(first)} -> {'passed' if again['ok'] else describe(again)}")
        play_failures = [describe(r) for r in results if not r["ok"]]
        for failure in play_failures:
            print(f"  {failure}")
        failures += len(play_failures)
        first_try = {(f["slug"], f["surface"]): f for f, _ in retried}
        pairs = []
        for r in results:
            key = (r["slug"], r["surface"])
            status = "pass" if r["ok"] and key not in first_try else "retry" if r["ok"] else "fail"
            entry = {"slug": r["slug"], "surface": r["surface"], "status": status,
                     "steps": r.get("steps"), "passed": r.get("passed"), "errors": r.get("errors")}
            if status != "pass":
                entry["reason"] = describe(first_try[key]) if status == "retry" else describe(r)
            pairs.append(entry)
        doc["narration"] = {"pairs": len(jobs), "passed": passed, "passed_on_retry": on_retry,
                            "results": pairs}
    save()
    return 1 if failures else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="aibast", description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="area", required=True)
    api = sub.add_parser("api").add_subparsers(dest="action", required=True)
    api.add_parser("build")
    api.add_parser("check")
    media = sub.add_parser("media").add_subparsers(dest="action", required=True)
    verify = media.add_parser("verify")
    verify.add_argument("--live", action="store_true")
    pages = sub.add_parser("pages").add_subparsers(dest="action", required=True)
    pages.add_parser("size")
    demo = sub.add_parser("demo").add_subparsers(dest="action", required=True)
    check = demo.add_parser("check")
    check.add_argument("slug")
    check.add_argument("--base")
    live = sub.add_parser("verify")
    live.add_argument("--live", action="store_true", required=True)
    live.add_argument("--base", required=True, help="the site address, for example a ring's Pages URL")
    live.add_argument("--play", action="store_true")
    live.add_argument("--workers", type=int, default=8, help="parallel media downloads (max 16)")
    live.add_argument("--report", default="verify-live.json", help="JSON file listing every result")
    live.add_argument("--parallel", type=int, default=2, help="browsers at once for --play (max 4)")
    args = parser.parse_args(argv)

    if args.area == "api":
        return run("tools/build_library_api.py", *(["--check"] if args.action == "check" else []))
    if args.area == "media":
        return media_verify(args.live)
    if args.area == "verify":
        return verify_live(args.base, args.play, args.workers, args.parallel, args.report)
    if args.area == "pages":
        return pages_size()
    return demo_check(args.slug, args.base)


if __name__ == "__main__":
    sys.exit(main())
