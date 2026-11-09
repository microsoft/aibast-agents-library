"""Record what the layered agent.py answers locally, as the reference the deployed version must match later.

For each operation in OPERATION_GUIDE: the exact tool output (and its sha256), plus the local Brainstem's
answer to the guide's own question. Writes <slug>/reference-answers.json beside the agent.py.

    python3 tools/record_reference_answers.py <agent.py> --brainstem http://localhost:<port>
"""
import argparse, datetime, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from check_cartridges import ask, load
import tempfile

ap = argparse.ArgumentParser(); ap.add_argument("agent"); ap.add_argument("--brainstem", required=True)
a = ap.parse_args()
path = pathlib.Path(a.agent)
with tempfile.TemporaryDirectory() as tmp:
    mod = load(path, pathlib.Path(tmp))
    cls = next(v for k, v in vars(mod).items() if isinstance(v, type) and k.endswith("Agent") and k != "BasicAgent")
    agent = cls()
    cases = []
    for op, g in mod.OPERATION_GUIDE.items():
        out = agent.perform(operation=op, **g.get("args", {}))
        q = g.get("ask") or (g["when"].replace("Use when someone ", "Someone ").replace("Use when ", "") + f" Use the {agent.name} tool on the sample.")
        r = ask(a.brainstem, q)
        cases.append({"operation": op, "question": q, "tool_output": out,
                      "tool_sha256": hashlib.sha256(out.encode()).hexdigest(),
                      "local_called_tool": f"[{agent.name}]" in str(r.get("agent_logs", "")),
                      "local_answer": r.get("response", "")})
doc = {"schema": "aibast-reference-answers/1.0", "agent": path.name,
       "agent_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
       "recorded": datetime.date.today().isoformat(),
       "rule": "A deployed version passes when, for each case, its answer carries the same facts as tool_output.",
       "cases": cases}
(path.parent / "reference-answers.json").write_text(json.dumps(doc, indent=1) + "\n")
print(f"{path.parent.name}: {len(cases)} cases, {sum(c['local_called_tool'] for c in cases)} called the tool")
