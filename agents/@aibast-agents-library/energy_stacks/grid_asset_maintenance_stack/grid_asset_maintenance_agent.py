"""
Grid Asset Maintenance Agent for Energy and Utilities.

Read-only predictive maintenance support for an electricity distribution company's reliability engineers,
maintenance planners and asset managers, built on a synthetic snapshot of the condition-monitoring feed for its
grid assets: power transformers, switchgear, underground cables and overhead lines. It ranks assets by failure
probability over 30, 90 and 180 days, drafts the preventive work order with asset history, materials and the crew
and parts pre-plan, checks a completed job's field record before the asset register is updated, and summarizes
fleet health and the replacement pipeline for capital planning. Today the snapshot is a set of constants; in
production the same accessors read the Dataverse tables that Power Automate fills from the condition-monitoring
system, Field Service and the ERP. Every work order, order, assignment and register change is a draft for an
authorized engineer to approve.
"""

import sys
import os
import re
from datetime import datetime, timedelta
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/grid-asset-maintenance",
    "version": "1.0.0",
    "display_name": "Predictive Asset Maintenance Intelligence Agent",
    "description": "Rank a distribution company's grid assets (power transformers, switchgear, underground cables and overhead lines) by failure probability over 30, 90 and 180 days from a synthetic condition-monitoring snapshot, draft the preventive work order with asset history, materials, long-lead parts and crew pre-assignment, check a completed job's field record before the asset register and fixed asset register are updated, and summarize fleet health with the replacement pipeline and capital needed. The agent never raises a work order, orders parts, assigns a crew or changes a register; an authorized engineer approves every step through future authenticated tools.",
    "author": "AIBAST",
    "tags": ["energy", "utilities", "grid-assets", "predictive-maintenance", "asset-management", "reliability"],
    "category": "energy",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ---- DATA PLANE ------------------------------------------------------------
# Synthetic today; swap this block for the Dataverse tables that Power Automate fills from the condition-monitoring
# system (asset health), Field Service (work orders and completed jobs) and the ERP (stores and fixed assets).
# Nothing below this block reads the constants directly; it calls _assets(), _completed_jobs(), _fleet(),
# _pipeline() and _policy().

UTILITY = "Larkfield Electric Networks"

# A work order is drafted when the 90-day failure probability reaches this threshold; planning starts at the
# 180-day threshold. Health is 0-100 (100 = as new); remaining useful life is in years.
POLICY = {"work_order_p90": 20, "plan_p180": 25, "long_lead_days": 30}

ASSETS = [
    {"id": "TX-0417", "class": "Power transformer", "name": "Primary transformer T2, 33/11 kV 20 MVA",
     "site": "Millbrook Primary Substation", "age_years": 47, "customers": 8400,
     "health": 31, "rul_years": 1.5, "p30": 9, "p90": 27, "p180": 46,
     "keywords": ["tx-0417", "millbrook", "t2", "transformer"],
     "anomaly": "Dissolved acetylene 9 ppm against a 1 ppm baseline; top-oil temperature 8 C above the "
                "load-corrected baseline",
     "action": "Offline inspection and on-load tap changer overhaul",
     "history": [(410, "On-load tap changer contacts inspected; moderate wear noted"),
                 (190, "Oil sample: acetylene first detected at 3 ppm"),
                 (21, "Oil sample: acetylene 9 ppm; reliability engineer flagged for review")],
     "materials": [("Tap changer contact kit", 1, 0, 35), ("Transformer oil, 200 L drum", 4, 12, 3),
                   ("Gasket set, T2 tank", 1, 2, 5)],
     "crew": "Substation Crew B (two HV fitters and a test engineer)",
     "start_in_days": 42,
     "outage": "Transfer the 11 kV load to transformer T1 (peak 14.2 MVA against a 20 MVA rating) for three days",
     "replacement_cost": 2400000},
    {"id": "SG-1123", "class": "Switchgear", "name": "11 kV switchboard panel 4",
     "site": "Ashby Road Substation", "age_years": 39, "customers": 3100,
     "health": 38, "rul_years": 2.0, "p30": 7, "p90": 22, "p180": 39,
     "keywords": ["sg-1123", "ashby", "panel 4", "switchgear", "switchboard"],
     "anomaly": "Partial discharge 410 pC against a 60 pC baseline, rising for six weeks",
     "action": "Partial discharge investigation and panel refurbishment",
     "history": [(730, "Routine maintenance; no defects"),
                 (44, "Partial discharge alarm at 180 pC"),
                 (6, "Partial discharge 410 pC confirmed by handheld survey")],
     "materials": [("Cable termination kit, 11 kV", 3, 4, 7), ("Busbar insulating boots", 6, 0, 21)],
     "crew": "Substation Crew A (two HV fitters)",
     "start_in_days": 28,
     "outage": "Open the bus section and back-feed panel 4 customers from feeder 9 for one day",
     "replacement_cost": 640000},
    {"id": "CB-2208", "class": "Underground cable", "name": "11 kV feeder 7, 1.2 km paper-insulated section",
     "site": "Harbour Street", "age_years": 54, "customers": 1900,
     "health": 44, "rul_years": 3.0, "p30": 4, "p90": 15, "p180": 31,
     "keywords": ["cb-2208", "harbour", "feeder 7", "cable"],
     "anomaly": "Partial discharge at joint 2 of 3, 260 pC against a 40 pC baseline",
     "action": "Replace joint 2 and plan the section replacement",
     "history": [(1100, "Fault at joint 1; joint replaced"), (95, "Online partial discharge monitor fitted")],
     "materials": [("11 kV transition joint kit", 1, 2, 14)],
     "crew": "Cable Jointing Team 2",
     "start_in_days": 120,
     "outage": "Feeder 7 back-fed from feeder 11 during the joint change",
     "replacement_cost": 1100000},
    {"id": "OH-3310", "class": "Overhead line", "name": "33 kV line Fenwick to Millbrook, spans 112 to 118",
     "site": "Fenwick corridor", "age_years": 31, "customers": 5200,
     "health": 52, "rul_years": 6.0, "p30": 5, "p90": 12, "p180": 20,
     "keywords": ["oh-3310", "fenwick", "overhead", "line", "clamp"],
     "anomaly": "Thermal survey: two compression clamps 22 C above conductor temperature",
     "action": "Replace two compression clamps",
     "history": [(365, "Annual thermal survey; no hotspots"), (12, "Thermal survey found two hot clamps")],
     "materials": [("Compression clamp, 33 kV", 2, 10, 3)],
     "crew": "Overhead Line Crew 3",
     "start_in_days": 60,
     "outage": "None; live-line clamp replacement",
     "replacement_cost": 380000},
    {"id": "TX-0388", "class": "Power transformer", "name": "Primary transformer T1, 33/11 kV 15 MVA",
     "site": "Calder Lane Substation", "age_years": 36, "customers": 6100,
     "health": 61, "rul_years": 9.0, "p30": 2, "p90": 8, "p180": 17,
     "keywords": ["tx-0388", "calder", "t1"],
     "anomaly": "Oil level 6% below normal; slow weep at the radiator flange",
     "action": "Repair the radiator flange and top up the oil",
     "history": [(300, "Oil sample normal")],
     "materials": [("Radiator flange gasket", 2, 6, 5)],
     "crew": "Substation Crew B", "start_in_days": 90, "outage": "None", "replacement_cost": 1900000},
    {"id": "SG-1140", "class": "Switchgear", "name": "11 kV ring main unit RMU-22",
     "site": "Orchard Way", "age_years": 24, "customers": 700,
     "health": 72, "rul_years": 12.0, "p30": 1, "p90": 4, "p180": 9,
     "keywords": ["sg-1140", "rmu-22", "orchard"],
     "anomaly": "None; SF6 gas pressure stable", "action": "Routine inspection",
     "history": [(400, "Routine inspection")], "materials": [], "crew": "Substation Crew A",
     "start_in_days": 180, "outage": "None", "replacement_cost": 45000},
    {"id": "CB-2215", "class": "Underground cable", "name": "11 kV feeder 12, XLPE section",
     "site": "Quarry Road", "age_years": 18, "customers": 1400,
     "health": 76, "rul_years": 20.0, "p30": 1, "p90": 3, "p180": 7,
     "keywords": ["cb-2215", "quarry", "feeder 12"],
     "anomaly": "None", "action": "Monitor", "history": [], "materials": [], "crew": "Cable Jointing Team 1",
     "start_in_days": 180, "outage": "None", "replacement_cost": 600000},
    {"id": "OH-3302", "class": "Overhead line", "name": "11 kV line Calder Lane spur",
     "site": "Calder valley", "age_years": 14, "customers": 900,
     "health": 80, "rul_years": 25.0, "p30": 1, "p90": 3, "p180": 6,
     "keywords": ["oh-3302", "calder spur"],
     "anomaly": "None", "action": "Monitor", "history": [], "materials": [], "crew": "Overhead Line Crew 1",
     "start_in_days": 180, "outage": "None", "replacement_cost": 150000},
]

# Field records captured on the Power Apps job form after maintenance; the register update waits for every
# required measurement.
COMPLETED_JOBS = [
    {"work_order": "WO-55102", "asset": "SG-1131", "asset_name": "11 kV switchboard panel 2, Ashby Road Substation",
     "completed_days_ago": 2, "crew_lead": "Rowan Pettigrew", "keywords": ["wo-55102", "sg-1131", "panel 2"],
     "work_done": "Replaced three vacuum interrupters and cleaned the cable box",
     "parts": [("Vacuum interrupter, 11 kV", 3, 6200)],
     "required": ["Contact resistance", "Insulation resistance", "Partial discharge after energization"],
     "measurements": {"Contact resistance": "38 micro-ohm (limit 60)",
                      "Insulation resistance": "12 G-ohm (minimum 1)",
                      "Partial discharge after energization": "35 pC (baseline 60)"},
     "condition_before": 4, "condition_after": 2, "fixed_asset": "FA-SG-1131"},
    {"work_order": "WO-55097", "asset": "CB-2190", "asset_name": "11 kV feeder 3 cable, joint 4, Mill Lane",
     "completed_days_ago": 1, "crew_lead": "Dara Whitcombe", "keywords": ["wo-55097", "cb-2190", "mill lane"],
     "work_done": "Replaced joint 4 with a transition joint",
     "parts": [("11 kV transition joint kit", 1, 2900)],
     "required": ["Insulation resistance", "Sheath test", "Partial discharge after energization"],
     "measurements": {"Sheath test": "Pass at 10 kV",
                      "Partial discharge after energization": "28 pC (baseline 40)"},
     "condition_before": 4, "condition_after": 2, "fixed_asset": "FA-CB-2190"},
]

# Fleet by asset class. Condition grade: poor = health below 40.
FLEET = [
    {"class": "Power transformers", "count": "64 units", "avg_health": 66, "poor": "5 units",
     "at_risk_180": "3 units"},
    {"class": "Switchgear", "count": "410 panels", "avg_health": 71, "poor": "22 panels", "at_risk_180": "9 panels"},
    {"class": "Underground cables", "count": "1,280 km", "avg_health": 63, "poor": "41 km", "at_risk_180": "12 km"},
    {"class": "Overhead lines", "count": "2,350 km", "avg_health": 74, "poor": "18 km", "at_risk_180": "6 km"},
]

# Replacement candidates; year_offset counts financial years from this one.
PIPELINE = [
    {"asset": "TX-0417", "plan": "Replace T2 once the tap changer overhaul (about two more years of life) runs out",
     "year_offset": 2, "capital": 2400000},
    {"asset": "SG-1123", "plan": "Replace the Ashby Road 11 kV switchboard (8 panels)",
     "year_offset": 1, "capital": 640000},
    {"asset": "CB-2208", "plan": "Replace the 1.2 km paper-insulated section of feeder 7",
     "year_offset": 1, "capital": 1100000},
    {"asset": "Program", "plan": "Cable replacement program: the worst 9 km of the 41 km in poor condition",
     "year_offset": 3, "capital": 7200000},
]

DEFAULT_ASSET = "TX-0417"
DEFAULT_JOB = "WO-55102"


def _policy():
    """Replace with the maintenance policy table. Everything downstream is unchanged."""
    return POLICY


def _assets():
    """Replace with the asset health query (condition-monitoring feed). Everything downstream is unchanged."""
    return ASSETS


def _completed_jobs():
    """Replace with the completed Field Service jobs query. Everything downstream is unchanged."""
    return COMPLETED_JOBS


def _fleet():
    """Replace with the fleet summary query. Everything downstream is unchanged."""
    return FLEET


def _pipeline():
    """Replace with the replacement plan table. Everything downstream is unchanged."""
    return PIPELINE

# ---- END DATA PLANE --------------------------------------------------------


BOUNDARY = ("> Read-only synthetic snapshot of a fictional utility. No work order was raised, no part was ordered, "
            "no crew was assigned and no register was changed; an authorized engineer approves every step.")


def _now():
    return datetime.now()


def _money(value):
    return f"${value:,.0f}"


def _date(days):
    return f"{_now() + timedelta(days=days):%d %b %Y}"


def _recommendation(asset):
    policy = _policy()
    if asset["p90"] >= policy["work_order_p90"]:
        return "Raise work order now"
    if asset["p180"] >= policy["plan_p180"]:
        return "Plan within 180 days"
    return "Monitor"


def _action_text(asset):
    rec = _recommendation(asset)
    if asset["action"] == "Monitor":
        return rec
    if rec == "Monitor":
        return f"Monitor; at next visit: {asset['action']}"
    return f"{rec}: {asset['action']}"


def _ranked():
    return sorted(_assets(), key=lambda a: (-a["p90"], -a["p180"]))


_STOPWORDS = {"the", "a", "an", "of", "for", "to", "on", "at", "in", "and", "our", "its", "asset", "job", "one", "ones"}


def _words(text):
    """Lower-case words and ids (TX-0417 stays one word); a trailing plural s is dropped so 'cables' meets 'cable'.

    Numbers are not words: a number only tells assets apart through _qualifiers (a voltage, or a panel, feeder,
    joint, RMU or transformer number), so '1.2 km' in a cable's name never meets a '1' or '2' in the request, and
    'one' is a pronoun ('the Millbrook one'), not a number, unless it follows a designator.
    """
    words = set()
    for word in re.findall(r"[a-z0-9]+(?:[-.][a-z0-9]+)*", str(text).lower()):
        if re.fullmatch(r"[\d.]+", word) or len(word) < 2:
            continue
        if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
            word = word[:-1]
        if word not in _STOPWORDS:
            words.add(word)
    return words


def _record_words(item, key):
    """(Words that name the record: its id, site and keywords; words that only describe it: name and class)."""
    naming = [item[key], item.get("site", ""), item.get("asset", "")] + list(item.get("keywords", []))
    describing = [item.get("name", ""), item.get("class", ""), item.get("asset_name", "")]
    primary = set().union(*(_words(f) for f in naming))
    return primary, set().union(*(_words(f) for f in describing)) - primary


def _id_named(item_id, text):
    """True when the id appears anywhere in the text, with its hyphen, a space or nothing: 'TX-0417', 'asset tx 0417'
    and 'tx0417' all name TX-0417."""
    parts = [re.escape(p) for p in str(item_id).lower().split("-") if p]
    return re.search(r"\b" + r"[\s-]?".join(parts) + r"\b", text) is not None


_UNITS = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
          "nine": 9}
_TEENS = {"ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
          "seventeen": 17, "eighteen": 18, "nineteen": 19}
_TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80,
         "ninety": 90}
_NUMBER = (r"(?:(?:" + "|".join(_TENS) + r")(?:[\s-]+(?:" + "|".join(_UNITS) + r"))?|(?:"
           + "|".join(list(_TEENS) + list(_UNITS)) + r"))")
_SPELLED = re.compile(r"\b(?:(" + "|".join(_TENS) + r")(?:[\s-]+(" + "|".join(_UNITS) + r"))?|("
                      + "|".join(list(_TEENS) + list(_UNITS)) + r"))\b")
_KINDS = r"(panel|feeder|joint|t|rmu|transformer)"
_NUMBER_WORD = r"(?:\s+(?:number|no\.?|#))?"
# A spelled number counts as a number in exactly two places: right after a designator ('panel two', 'T one',
# 'transformer number one', 'RMU twenty two'), or in a run that ends in a unit ('eleven kV', 'thirty-three eleven
# kV' = 33/11 kV). Anywhere else it is an ordinary word ('the Millbrook one').
_SPELLED_DESIGNATOR = re.compile(r"\b" + _KINDS + _NUMBER_WORD + r"([\s-]+)(" + _NUMBER + r")\b")
_SPELLED_MEASURE = re.compile(r"\b(" + _NUMBER + r"(?:[\s/-]+" + _NUMBER + r")?)\s*(?=kv\b|kva\b|mva\b)")


def _spelled(words):
    """'twenty two' -> '22', 'eleven' -> '11'."""
    def number(match):
        tens, unit, single = match.groups()
        if single:
            return str(_TEENS.get(single, _UNITS.get(single)))
        return str(_TENS[tens] + _UNITS.get(unit or "zero", 0))
    return _SPELLED.sub(number, words)


def _digits(text):
    """Spelled-out numbers as digits where they are numbers, so a spoken request reads like a typed one:
    'panel two' -> 'panel 2', 'eleven kV' -> '11 kV', 'thirty-three eleven kV' -> '33/11 kV', 'RMU twenty two' ->
    'RMU 22'. 'The Millbrook one' is unchanged."""
    text = str(text).lower()
    text = _SPELLED_MEASURE.sub(
        lambda m: "/".join(_spelled(part) for part in re.findall(_NUMBER, m.group(1))) + " ", text)
    return _SPELLED_DESIGNATOR.sub(
        lambda m: m.group(0)[:m.start(3) - m.start(0)] + _spelled(m.group(3)), text)


# A measure is a number with its unit: a voltage ('11 kV', '33/11 kV'), a rating ('20 MVA', '500 kVA') or a length
# ('1.2 km'). Every unit works the same way: a measure the request states rules out a record that states a
# different one of the same unit, so '15 MVA transformer' never drafts the 20 MVA unit and '11 kV line' never picks
# the 33 kV line.
_UNIT_WORDS = ("kv", "kva", "mva", "km")
_MEASURE = re.compile(r"\b(\d+(?:\.\d+)?)(?:\s*/\s*(\d+(?:\.\d+)?))?\s*(" + "|".join(_UNIT_WORDS) + r")\b")
# 'transformer 1' and 'transformer number 1' are transformer T1. A number followed by a unit, a slash or a decimal
# point is a measure, not a designator: 'transformer 33/11 kV', 'transformer 33 kV' and 'transformer 20 MVA' name
# a voltage or a rating, never transformer number 33 or 20.
_DESIGNATOR = re.compile(r"\b" + _KINDS + _NUMBER_WORD + r"[\s-]?(\d+)\b"
                         r"(?!\s*(?:[/.]\d|kv\b|kva\b|mva\b|km\b|mm\b|m\b|%))")


def _qualifiers(text):
    """Numbers that tell assets apart: {'kv': {'11', '33'}, 'mva': {'20'}, 'km': {'1.2'}, 'panel': {'4'}, 't': {'2'},
    ...}."""
    found = {}
    text = _digits(text)
    for first, second, unit in _MEASURE.findall(text):
        found.setdefault(unit, set()).update(str(float(v)) for v in (first, second) if v)
    for kind, number in _DESIGNATOR.findall(text):
        found.setdefault("t" if kind == "transformer" else kind, set()).add(str(int(number)))
    return found


def _record_qualifiers(item, key):
    fields = [item[key], item.get("name", ""), item.get("site", ""), item.get("asset", ""),
              item.get("asset_name", "")] + list(item.get("keywords", []))
    return _qualifiers(" ".join(fields))


def _conflicts(asked, carried):
    """True when the request names a number of a kind the record also has, and the record's number differs:
    'panel 2' against panel 4, '11 kV' against a 33 kV line, 'T1' against transformer T2."""
    return any(kind in carried and not (numbers & carried[kind]) for kind, numbers in asked.items())


def _resolve(value, default, items, key):
    """Id or words from the record; empty -> the default; no match -> None; a tie -> the tied records (a list).

    Every record is scored on the whole words it shares with the request. A word only one record has (a site such
    as Orchard Way, or an id) counts in full; a word several records share (a class word such as transformer, or
    Calder, which names both a substation and a line) counts for less, and a word that only describes a record
    counts half as much as one that names it. The best record wins only when it beats the next one; a tie is
    returned so the caller asks which one was meant instead of guessing.
    """
    if not value:
        return next(i for i in items if i[key] == default)
    q = str(value).lower().strip()
    for item in items:
        if q == item[key].lower():
            return item
    named = [item for item in items if _id_named(item[key], q)]
    if named:
        return named[0] if len(named) == 1 else named
    q = _digits(q)
    asked = _words(q)
    # A measure (voltage, rating, length) or a panel, feeder, joint or transformer number in the request rules out
    # every record that carries a different one, so 'Ashby Road panel 2' never drafts panel 4's work order, '11 kV
    # line' never picks the 33 kV line and '15 MVA transformer' never picks the 20 MVA one.
    wanted = _qualifiers(q)
    ruled_out = [item for item in items if _conflicts(wanted, _record_qualifiers(item, key))]
    items = [item for item in items if item not in ruled_out]
    vocab = [(item, *_record_words(item, key)) for item in items]
    # A designator the request names ('RMU 22', 'RMU22', 'panel 4') counts as a naming word for every record that
    # carries it, however the record spells it (SG-1140's keyword is 'rmu-22').
    designators = {(kind, n) for kind, numbers in wanted.items() if kind not in _UNIT_WORDS for n in numbers}
    carried = {id(item): {(kind, n) for kind, numbers in _record_qualifiers(item, key).items() for n in numbers}
               for item in items}
    scores = []
    for item, primary, secondary in vocab:
        score = 0.0
        for word in asked & (primary | secondary):
            shared = sum(1 for _, p, s in vocab if word in p or word in s)
            score += (1.0 if word in primary else 0.5) / shared
        for designator in designators & carried[id(item)]:
            score += 1.0 / sum(1 for other in items if designator in carried[id(other)])
        if score:
            scores.append((score, item))
    if not scores:
        return None
    scores.sort(key=lambda pair: -pair[0])
    best = scores[0][0]
    tied = [item for score, item in scores if abs(score - best) < 1e-9]
    if len(tied) == 1 and ruled_out:
        # A word that names only a ruled-out record ('Millbrook' in 'T1 at Millbrook', where the Millbrook
        # transformer is T2) means the request describes an asset that is not monitored; no substitute is offered.
        winner = set().union(*_record_words(tied[0], key))
        named_elsewhere = set().union(*(_record_words(item, key)[0] for item in ruled_out))
        if (asked & named_elsewhere) - winner:
            return None
    return tied[0] if len(tied) == 1 else tied


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

OPERATIONS = ["risk_ranking", "work_order_draft", "register_update", "replacement_plan"]


class GridAssetMaintenanceAgent(BasicAgent):
    """Predictive maintenance agent for grid assets (read-only, synthetic)."""

    def __init__(self):
        self.name = "GridAssetMaintenanceAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                "Answers questions about the health of the utility's grid assets: power transformers, switchgear, "
                "underground cables and overhead lines. It ranks which assets are most likely to fail in the next "
                "30, 90 and 180 days and why, drafts the preventive work order for an at-risk asset with its "
                "history, materials, long-lead parts, crew and outage, checks whether a completed job's field "
                "record is complete before the asset register is updated, and summarizes fleet health with the "
                "replacement pipeline and capital needed. Always call this tool for asset health, failure risk, "
                "maintenance backlog, work order, parts, crew, asset register or replacement planning questions "
                "from reliability engineers, maintenance planners, field engineers and asset managers. Call it "
                "right away; every operation has demo defaults. It is read-only: it drafts but never raises work "
                "orders, orders parts, assigns crews or changes registers, so never offer to do those."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(OPERATIONS),
                        "description": (
                            "risk_ranking for the risk-prioritized backlog: assets ranked by 30, 90 and 180-day "
                            "failure probability with health score, the anomaly behind it and the recommended "
                            "action; work_order_draft for the preventive work order on one asset with history, "
                            "materials, long-lead parts to order and the crew and outage pre-plan; "
                            "register_update to check a completed job's field record and draft the asset "
                            "register and fixed asset register update; replacement_plan for fleet health by "
                            "asset class, the replacement pipeline and capital by year."
                        ),
                    },
                    "asset": {
                        "type": "string",
                        "description": (
                            "Asset id such as TX-0417 or words from it such as 'Millbrook transformer' or 'Ashby "
                            "Road switchgear'. Optional; the work order defaults to the Millbrook T2 transformer."
                        ),
                    },
                    "work_order": {
                        "type": "string",
                        "description": (
                            "Completed work order id such as WO-55102 or words such as 'Mill Lane joint'. "
                            "Optional; defaults to WO-55102 on Ashby Road panel 2."
                        ),
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "risk_ranking")
        handlers = {
            "risk_ranking": self._risk_ranking,
            "work_order_draft": self._work_order_draft,
            "register_update": self._register_update,
            "replacement_plan": self._replacement_plan,
        }
        handler = handlers.get(op)
        if not handler:
            return f"**Error:** Unknown operation `{op}`. Operations: {', '.join(OPERATIONS)}."
        return handler(**kwargs)

    # -- risk_ranking ---------------------------------------------------------
    def _risk_ranking(self, **kwargs) -> str:
        policy = _policy()
        ranked = _ranked()
        now_wo = [a for a in ranked if _recommendation(a) == "Raise work order now"]
        plan = [a for a in ranked if _recommendation(a) == "Plan within 180 days"]
        lines = [
            f"# Grid Asset Risk Ranking - {UTILITY}",
            "",
            f"**As of:** {_now():%d %b %Y} condition-monitoring snapshot | **Assets monitored:** {len(ranked)} | "
            f"**Work orders recommended:** {len(now_wo)} | **To plan within 180 days:** {len(plan)}",
            "",
        ]
        if now_wo:
            top = now_wo[0]
            lines += [f"**Act first:** {top['id']} {top['name']} at {top['site']}: {top['p90']}% chance of failure "
                      f"in 90 days, {top['customers']:,} customers on it. {top['anomaly']}.", ""]
        lines += ["| Rank | Asset | Class | Site | Health | Fail 30 d | Fail 90 d | Fail 180 d | Remaining life | "
                  "Recommended action |",
                  "|------|-------|-------|------|--------|-----------|-----------|------------|----------------|"
                  "--------------------|"]
        for rank, a in enumerate(ranked, 1):
            lines.append(f"| {rank} | {a['id']} | {a['class']} | {a['site']} | {a['health']} | {a['p30']}% | "
                         f"{a['p90']}% | {a['p180']}% | {a['rul_years']:g} yr | {_action_text(a)} |")
        lines += ["", "## What is driving the top risks"]
        lines += [f"- {a['id']}: {a['anomaly']}." for a in now_wo + plan]
        lines += ["", f"Work orders are recommended at {policy['work_order_p90']}% or more 90-day failure "
                      f"probability; planning starts at {policy['plan_p180']}% over 180 days.", "", BOUNDARY]
        return "\n".join(lines)

    # -- work_order_draft -----------------------------------------------------
    def _work_order_draft(self, **kwargs) -> str:
        asset = _resolve(kwargs.get("asset"), DEFAULT_ASSET, _assets(), "id")
        if asset is None:
            return self._unknown("asset", kwargs.get("asset"), [a["id"] for a in _assets()])
        if isinstance(asset, list):
            return self._ambiguous("asset", kwargs.get("asset"),
                                   [f"{a['id']} ({a['name']}, {a['site']})" for a in asset])
        policy = _policy()
        rec = _recommendation(asset)
        head = [f"# Preventive Work Order Draft - {asset['id']}", "",
                f"**Asset:** {asset['name']}, {asset['site']} ({asset['class']}, {asset['age_years']} years old)",
                f"**Risk:** health {asset['health']}; failure probability {asset['p30']}% in 30 days, "
                f"{asset['p90']}% in 90 days, {asset['p180']}% in 180 days; {asset['customers']:,} customers",
                ""]
        if rec != "Raise work order now":
            head += [f"**No work order drafted.** {asset['id']} is below the {policy['work_order_p90']}% 90-day "
                     f"threshold ({asset['p90']}%). Recommendation: {_action_text(asset)}.", "", BOUNDARY]
            return "\n".join(head)
        start = asset["start_in_days"]
        lines = head + [
            f"**Work:** {asset['action']}",
            f"**Why now:** {asset['anomaly']}.",
            f"**Planned start:** {_date(start)} (day {start}) | **Priority:** High | "
            f"**Crew:** {asset['crew']}",
            f"**Outage plan:** {asset['outage']}",
            "",
            "## Asset history",
        ]
        lines += [f"- {_date(-days)}: {event}" for days, event in asset["history"]]
        lines += ["", "## Materials and parts pre-plan", "",
                  "| Part | Needed | In stores | Lead time | Action |",
                  "|------|--------|-----------|-----------|--------|"]
        long_lead = []
        for part, need, on_hand, lead in asset["materials"]:
            if on_hand >= need:
                action = "Reserve from stores"
            else:
                order_by = start - lead
                action = f"Order by {_date(order_by)} (day {order_by})"
                if lead > policy["long_lead_days"]:
                    long_lead.append(part)
                    action = "Long-lead: " + action
            lines.append(f"| {part} | {need} | {on_hand} | {lead} days | {action} |")
        if long_lead:
            lines += ["", f"**Long-lead parts to order first:** {', '.join(long_lead)}."]
        lines += ["", "**Status:** Draft - a maintenance planner approves it in Field Service, which raises the work "
                      "order, reserves the stores items and sends purchase requisitions for the parts to order. "
                      "Nothing has been raised, ordered or assigned.", "", BOUNDARY]
        return "\n".join(lines)

    # -- register_update ------------------------------------------------------
    def _register_update(self, **kwargs) -> str:
        job = _resolve(kwargs.get("work_order"), DEFAULT_JOB, _completed_jobs(), "work_order")
        if job is None:
            return self._unknown("work order", kwargs.get("work_order"),
                                 [j["work_order"] for j in _completed_jobs()])
        if isinstance(job, list):
            return self._ambiguous("work order", kwargs.get("work_order"),
                                   [f"{j['work_order']} ({j['asset_name']})" for j in job])
        missing = [m for m in job["required"] if m not in job["measurements"]]
        parts_cost = sum(qty * cost for _, qty, cost in job["parts"])
        lines = [f"# Asset Register Update Check - {job['work_order']}", "",
                 f"**Asset:** {job['asset']} {job['asset_name']}",
                 f"**Completed:** {_date(-job['completed_days_ago'])} by {job['crew_lead']} | "
                 f"**Work done:** {job['work_done']}", "",
                 "## Field record", "",
                 "| Required measurement | Recorded |", "|----------------------|----------|"]
        for m in job["required"]:
            lines.append(f"| {m} | {job['measurements'].get(m, 'MISSING')} |")
        lines += [""]
        if missing:
            lines += [f"**Not ready for the register.** Missing: {', '.join(missing)}. Ask {job['crew_lead']} to "
                      f"add it on the job form; the register update stays on hold until the record is complete.",
                      "", BOUNDARY]
            return "\n".join(lines)
        lines += ["**Ready for the register.** Every required measurement is recorded and within limits.", "",
                  "## Draft register update", "",
                  f"- **Asset management system:** condition grade {job['condition_before']} to "
                  f"{job['condition_after']} (1 = as new, 5 = end of life); last maintenance "
                  f"{_date(-job['completed_days_ago'])}; measurements attached; health score recalculated on the "
                  "next monitoring cycle.",
                  "- **Parts replaced:** " + "; ".join(f"{name} x{qty} at {_money(cost)} each"
                                                        for name, qty, cost in job["parts"]),
                  f"- **ERP fixed asset register:** component replacement of {_money(parts_cost)} against "
                  f"{job['fixed_asset']}; useful-life review requested from the asset accountant.",
                  "", "**Status:** Draft - the reliability engineer approves it, then Power Automate writes it to "
                      "the asset management system and the ERP. No register has been changed.", "", BOUNDARY]
        return "\n".join(lines)

    # -- replacement_plan -----------------------------------------------------
    def _replacement_plan(self, **kwargs) -> str:
        year = _now().year
        pipeline = sorted(_pipeline(), key=lambda p: p["year_offset"])
        total = sum(p["capital"] for p in pipeline)
        lines = [f"# Fleet Health and Replacement Plan - {UTILITY}", "",
                 f"**Capital needed in the plan:** {_money(total)} over the next "
                 f"{max(p['year_offset'] for p in pipeline)} financial years.", "",
                 "| Asset class | Fleet | Average health | Poor condition | At risk in 180 days |",
                 "|-------------|-------|----------------|----------------|---------------------|"]
        for f in _fleet():
            lines.append(f"| {f['class']} | {f['count']} | {f['avg_health']} | {f['poor']} | {f['at_risk_180']} |")
        lines += ["", "## Replacement pipeline", "",
                  "| Year | Asset | Plan | Capital |", "|------|-------|------|---------|"]
        for p in pipeline:
            lines.append(f"| FY{year + p['year_offset']} | {p['asset']} | {p['plan']} | {_money(p['capital'])} |")
        by_year = {}
        for p in pipeline:
            by_year[year + p["year_offset"]] = by_year.get(year + p["year_offset"], 0) + p["capital"]
        lines += ["", "**Capital by year:** " + "; ".join(f"FY{y} {_money(v)}" for y, v in sorted(by_year.items())),
                  "", "> Recommendation only: the investment committee approves the replacement program. "
                  + BOUNDARY[2:]]
        return "\n".join(lines)

    def _unknown(self, kind, value, ids) -> str:
        return (f"# Unknown {kind.title()}\n\nNo {kind} in the synthetic snapshot matches `{value}`; no substitute "
                f"was used. Known: {', '.join(ids)}.\n\n{BOUNDARY}")

    def _ambiguous(self, kind, value, candidates) -> str:
        return (f"# Which {kind} did you mean?\n\n`{value}` matches more than one {kind} equally well, so none was "
                f"picked. Name one of these by its id:\n\n" + "\n".join(f"- {c}" for c in candidates)
                + f"\n\n{BOUNDARY}")


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    agent = GridAssetMaintenanceAgent()
    for op in OPERATIONS:
        print(f"\n{'=' * 60}")
        print(f"Operation: {op}")
        print("=" * 60)
        print(agent.perform(operation=op))
