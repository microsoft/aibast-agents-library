"""agent.py -> solutions/<slug>/manual/: the AIBAST library package, generated from the transfer layer.

The agent.py is the one source. It carries INSTRUCTIONS, OPERATION_GUIDE {op: {title, when}}, its
records, and CARRIED (what the original solution does that is not code). This writes the manual
folder that tools/promote_solution_draft.py pushes to Copilot Studio:
  GLOBAL-INSTRUCTIONS.md, skills/<prefix>_<op>_NN/SKILL.md (one per operation),
  knowledge/<prefix>_<slug>-synthetic-records.md (the records, as the agent returns them).
Written text is copied word for word; evidence lines are taken from the agent's own output.

    python3 tools/agent_to_package.py <agent.py> <slug> <out_dir> [--knowledge file.md]
"""
import argparse, importlib.util, pathlib, re, shutil, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASIC = ROOT / "rapp_brainstem" / "agents" / "basic_agent.py"
SAFETY = ("Do not claim to have changed a system, contacted a person or supplier, made a decision, or completed a "
          "transaction. Stop at a reviewable brief or draft.")


def load(agent_file):
    tmp = pathlib.Path(tempfile.mkdtemp())
    shutil.copy(agent_file, tmp / pathlib.Path(agent_file).name)
    shutil.copy(BASIC, tmp / "basic_agent.py")
    sys.path.insert(0, str(tmp))
    spec = importlib.util.spec_from_file_location("transfer_agent", tmp / pathlib.Path(agent_file).name)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    cls = next(v for k, v in vars(mod).items() if isinstance(v, type) and k.endswith("Agent") and k != "BasicAgent")
    return mod, cls()


def evidence(text, n=3):
    """Exact strings the answer must carry: table rows' first cells and the count line."""
    rows = [[c.strip() for c in r.strip("|").split("|")] for r in text.splitlines() if r.startswith("|") and not set(r) <= set("|-: ")]
    keep = [next((c for c in r if c and not c.isdigit()), "") for r in rows[1:]][:n]
    keep = [k for k in keep if k]
    if not keep:  # list answers: the bold item names, highest first as the agent ordered them
        keep = re.findall(r"^\s*[-*]\s+\*\*(.+?)\*\*", text, re.M)[:n]
    count = next((l.strip() for l in text.splitlines() if re.search(r"\b\d+ (of \d+ )?\w+ (not met|findings?|shown)\b|^\d+ findings", l)), None)
    if not keep and not count and text.strip() and len(text.strip()) <= 240:
        count = text.strip()  # a one-line verdict is itself the evidence
    return list(dict.fromkeys(keep + ([count] if count else [])))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("agent"); ap.add_argument("slug"); ap.add_argument("out")
    ap.add_argument("--prefix", default="aibast"); ap.add_argument("--knowledge", help="authored records file to carry")
    a = ap.parse_args()
    mod, agent = load(a.agent)
    for need in ("INSTRUCTIONS", "OPERATION_GUIDE"):
        if not hasattr(mod, need):
            sys.exit(f"{a.agent}: transfer layer is missing {need}; write it in the file, never generate it")
    out = pathlib.Path(a.out) / "manual"
    if out.exists():
        shutil.rmtree(out)
    (out / "skills").mkdir(parents=True); (out / "knowledge").mkdir()
    guide = mod.OPERATION_GUIDE
    routing = "\n".join(f"- Use **{g['title'].lower()}** for: {g['when'][len('Use when '):] if g['when'].startswith('Use when ') else g['when']}" for g in guide.values())
    carried = getattr(mod, "CARRIED", [])
    display = (getattr(mod, "__manifest__", {}) or {}).get("display_name") or a.slug.replace("-", " ").title()
    instr = [f"# {display} — Manual Global Instructions",
             "", mod.INSTRUCTIONS.strip(), "", "## Natural-language routing", "", routing]
    if carried:
        instr += ["", "## Stays with the AI and the reviewer", "", "These parts of the original solution are not part of the fixed snapshot. Offer them only when the user asks, and label them as not checked against the records:", ""] + [f"- {c}" for c in carried]
    (out / "GLOBAL-INSTRUCTIONS.md").write_text("\n".join(instr) + "\n")
    for i, (op, g) in enumerate(guide.items(), 1):
        name = op.replace("_", "-")
        ev = evidence(agent.perform(operation=op, **(g.get("args") or {})))
        body = [f"---", f"name: {name}", f'description: "{g["when"]}"', "---", f"# {g['title']}", "", g["when"], "", "## Procedure", "",
                "1. Use only the uploaded synthetic records and rules.", "2. Lead with the result table this skill returns.",
                "3. Keep every record id, amount, date, and count exactly as recorded.", "4. Explain what needs a qualified person's confirmation.",
                "5. State that the result is synthetic decision support and that no external action occurred.", "",
                "## Deterministic pilot evidence", ""] + [f"- `{e}`" for e in ev] + ["", "## Safety gate", "", SAFETY]
        d = out / "skills" / f"{a.prefix}_{name}_{i:02d}"; d.mkdir()
        (d / "SKILL.md").write_text("\n".join(body) + "\n")
    title = re.sub(r"(?<!^)(?=[A-Z])", " ", agent.__class__.__name__.replace("Agent", ""))
    rules = [f"# {a.slug.replace('-', ' ').title()} — Exact Evidence, Decision, and Authorization Rules", "",
             "## Fixed-snapshot authority", "",
             f"Use only `{a.prefix}_{a.slug}-synthetic-records.md` and the {len(guide)} packaged skills. Every organization, person, record, "
             "identifier, amount and date is invented. The current date is not a source; the snapshot is. Never invent a value, and never "
             "substitute general knowledge for a value in the records.", "",
             "## Natural-language routing", ""]
    rules += [f"{i}. `{op}` ({g['title']}): {g['when']}" for i, (op, g) in enumerate(guide.items(), 1)]
    rules += ["", "## Do not browse", "", "Do not use web search, external policy, market data or any live system. Every answer comes from the two "
              "knowledge files and the skills. If a value is not in the records, say that it is not in the snapshot.", "",
              "## External-side-effect prohibition", "", SAFETY, ""]
    if carried:
        rules += ["## Outside the snapshot", "", "The original solution also does the following. They are not part of this package; say so if asked:", ""] + [f"- {c}" for c in carried] + [""]
    (out / "knowledge" / f"{a.prefix}_{a.slug}-rules-and-guardrails.md").write_text("\n".join(rules) + "\n")
    if a.knowledge:
        shutil.copy(a.knowledge, out / "knowledge" / f"{a.prefix}_{a.slug}-synthetic-records.md")
    print(f"{a.slug}: {len(guide)} skills, {len(list((out / 'knowledge').iterdir()))} knowledge file(s), {len(carried)} carried -> {out}")


if __name__ == "__main__":
    main()
