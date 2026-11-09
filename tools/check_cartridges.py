"""Gate every federated cartridge the same way the three hand runs were gated.

For each federation/<source>/<slug>/*_agent.py:
  1. manifest schema rapp-agent/1.0, portable basic_agent import, exactly one BasicAgent subclass
  2. perform() with defaults returns a non-empty string, twice byte-identical (deterministic)
  3. no network, no AI calls, no env reads in the file
  4. --layered: the transfer layer is present (INSTRUCTIONS, OPERATION_GUIDE, CARRIED) and every guided
     operation returns a non-empty answer
  5. optional: --brainstem URL runs the tool through /chat and the fingerprints must match; with
     --layered it also asks one question per operation (the guide's own "when" text) and the answer
     must call this tool
Prints one line per cartridge and exits non-zero on any failure.
"""
import argparse, hashlib, importlib.util, json, pathlib, re, shutil, sys, tempfile, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASIC = ROOT / "rapp_brainstem" / "agents" / "basic_agent.py"
BANNED = re.compile(r"\b(requests|urllib|http\.client|socket|openai|os\.environ|getenv)\b")


def load(path, workdir):
    shutil.copy(path, workdir / path.name)
    shutil.copy(BASIC, workdir / "basic_agent.py")
    sys.path.insert(0, str(workdir))
    try:
        spec = importlib.util.spec_from_file_location(path.stem, workdir / path.name)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    finally:
        sys.path.pop(0)
        sys.modules.pop("basic_agent", None)
    return mod


def ask(brainstem, text):
    req = urllib.request.Request(brainstem.rstrip("/") + "/chat", method="POST", headers={"content-type": "application/json"},
                                 data=json.dumps({"user_input": text}).encode())
    return json.load(urllib.request.urlopen(req, timeout=180))


def check(path, brainstem=None, layered=False):
    src = path.read_text()
    problems = []
    if "from basic_agent import BasicAgent" not in src:
        problems.append("import is not portable")
    if BANNED.search(src):
        problems.append("network, AI or env use: " + BANNED.search(src).group(0))
    with tempfile.TemporaryDirectory() as tmp:
        mod = load(path, pathlib.Path(tmp))
        if getattr(mod, "__manifest__", {}).get("schema") != "rapp-agent/1.0":
            problems.append("manifest schema")
        classes = [v for k, v in vars(mod).items() if isinstance(v, type) and k.endswith("Agent") and k != "BasicAgent"]
        if len(classes) != 1:
            return path, None, problems + [f"{len(classes)} agent classes"]
        agent = classes[0]()
        a, b = agent.perform(), agent.perform()
        if not isinstance(a, str) or not a.strip():
            problems.append("perform() returned nothing")
        elif a != b:
            problems.append("not deterministic")
        fp = hashlib.sha256(str(a).encode()).hexdigest()[:12]
        guide = {}
        if layered:
            for need in ("INSTRUCTIONS", "OPERATION_GUIDE", "CARRIED"):
                if not hasattr(mod, need):
                    problems.append(f"no {need}")
            guide = getattr(mod, "OPERATION_GUIDE", {}) or {}
            for op in guide:
                out = agent.perform(operation=op)
                if not isinstance(out, str) or not out.strip():
                    problems.append(f"operation {op} returned nothing")
    if brainstem and layered and not problems:
        for op, g in guide.items():
            q = g.get("ask") or (g["when"].replace("Use when someone ", "Someone ").replace("Use when ", "") + f" Use the {agent.name} tool on the sample.")
            logs = str(ask(brainstem, q).get("agent_logs", ""))
            if f"[{agent.name}]" not in logs:
                problems.append(f"Brainstem did not call {agent.name} for {op}")
    if brainstem and not problems:
        req = urllib.request.Request(brainstem.rstrip("/") + "/chat", method="POST",
              headers={"content-type": "application/json"},
              data=json.dumps({"user_input": f"Use the {agent.name} tool with its defaults."}).encode())
        logs = json.load(urllib.request.urlopen(req, timeout=120)).get("agent_logs", "")
        got = logs.split(f"[{agent.name}] ", 1)[1] if f"[{agent.name}] " in logs else ""
        if hashlib.sha256(got.encode()).hexdigest()[:12] != fp:
            problems.append("Brainstem output differs from the script")
    return path, fp, problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brainstem", help="e.g. http://localhost:7199 (its AGENTS_PATH must hold the cartridges)")
    ap.add_argument("--layered", action="store_true", help="also require and exercise the transfer layer")
    ap.add_argument("--only", help="comma-separated slugs")
    ap.add_argument("--expect", help="JSON file: {slug: fingerprint} from the hand runs")
    args = ap.parse_args()
    expect = json.loads(pathlib.Path(args.expect).read_text()) if args.expect else {}
    bad = 0
    for path in sorted((ROOT / "federation").glob("*/*/*_agent.py")):
        slug = path.parent.name
        if args.only and slug not in args.only.split(","):
            continue
        _, fp, problems = check(path, args.brainstem, args.layered)
        if slug in expect and fp != expect[slug]:
            problems.append(f"fingerprint {fp} != hand run {expect[slug]}")
        bad += bool(problems)
        print(f"{'FAIL' if problems else 'ok  '} {slug:40} {fp or '-':12} {'; '.join(problems)}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
