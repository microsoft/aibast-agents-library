"""Lossless adapters for the experimental rapp-exchange/1 profile."""

from __future__ import annotations

import argparse
import ast
import base64
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath


SCHEMA = "rapp-exchange/1"
MARKER_RE = re.compile(
    rb"<!--\s*rapp-exchange/1\s*\n(.*?)\n-->", re.DOTALL
)
PROTOCOL = {
    "name": "rapp/1",
    "authority": "https://github.com/kody-w/rapp-1",
    "spec": "https://github.com/kody-w/rapp-1/blob/main/SPEC.md",
    "orient": "https://raw.githubusercontent.com/kody-w/rapp-1/main/anchor/orient.json",
}


class ExchangeError(ValueError):
    pass


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _source_record(data: bytes, media_type: str) -> dict:
    return {
        "encoding": "base64",
        "media_type": media_type,
        "bytes": len(data),
        "sha256": _sha256(data),
        "data": base64.b64encode(data).decode("ascii"),
    }


def _decode_source(record: dict) -> bytes:
    required = {"encoding", "media_type", "bytes", "sha256", "data"}
    if set(record) != required or record["encoding"] != "base64":
        raise ExchangeError("invalid source record")
    try:
        data = base64.b64decode(record["data"], validate=True)
    except Exception as exc:
        raise ExchangeError("invalid base64 source") from exc
    if len(data) != record["bytes"] or _sha256(data) != record["sha256"]:
        raise ExchangeError("source length or hash mismatch")
    return data


def _safe_literal(node: ast.AST, values: dict[str, object]) -> object:
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name) and node.id in values:
        return values[node.id]
    if (
        isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "self"
        and node.attr in values
    ):
        return values[node.attr]
    if isinstance(node, ast.Dict):
        return {
            _safe_literal(key, values): _safe_literal(value, values)
            for key, value in zip(node.keys, node.values)
        }
    if isinstance(node, (ast.List, ast.Tuple)):
        result = [_safe_literal(item, values) for item in node.elts]
        return result if isinstance(node, ast.List) else tuple(result)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return _safe_literal(node.left, values) + _safe_literal(node.right, values)
    raise ExchangeError(f"unsupported static expression: {type(node).__name__}")


def _module_assignment(tree: ast.Module, name: str) -> object | None:
    values: dict[str, object] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            continue
        try:
            value = _safe_literal(node.value, values)
        except ExchangeError:
            continue
        values[target.id] = value
        if target.id == name:
            return value
    return None


def _agent_metadata(data: bytes) -> tuple[str, str, dict]:
    try:
        tree = ast.parse(data.decode("utf-8-sig"))
    except (UnicodeDecodeError, SyntaxError) as exc:
        raise ExchangeError(f"agent source is not valid UTF-8 Python: {exc}") from exc

    manifest = _module_assignment(tree, "__manifest__")
    values: dict[str, object] = {}
    metadata: dict = {}
    class_name = "ExchangedAgent"
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        if not any(
            (isinstance(base, ast.Name) and base.id == "BasicAgent")
            or (isinstance(base, ast.Attribute) and base.attr == "BasicAgent")
            for base in node.bases
        ):
            continue
        class_name = node.name
        for member in node.body:
            if not isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if member.name != "__init__":
                continue
            for statement in member.body:
                if not isinstance(statement, ast.Assign) or len(statement.targets) != 1:
                    continue
                target = statement.targets[0]
                if (
                    not isinstance(target, ast.Attribute)
                    or not isinstance(target.value, ast.Name)
                    or target.value.id != "self"
                ):
                    continue
                try:
                    values[target.attr] = _safe_literal(statement.value, values)
                except ExchangeError:
                    continue
        if isinstance(values.get("metadata"), dict):
            metadata = values["metadata"]
        break

    manifest = manifest if isinstance(manifest, dict) else {}
    name = str(
        manifest.get("display_name")
        or manifest.get("name")
        or values.get("name")
        or metadata.get("name")
        or class_name
    )
    description = str(
        manifest.get("description")
        or metadata.get("description")
        or f"Brainstem agent {name}"
    )
    return name, description, metadata


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "rapp-exchanged-capability"


def _class_name(value: str) -> str:
    parts = re.findall(r"[A-Za-z0-9]+", value)
    result = "".join(part[:1].upper() + part[1:] for part in parts)
    if not result or result[0].isdigit():
        result = f"Exchanged{result}"
    return f"{result}Agent" if not result.endswith("Agent") else result


def _frontmatter(data: bytes) -> tuple[str, str]:
    text = data.decode("utf-8-sig")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    block = match.group(1) if match else ""
    name_match = re.search(r"^name:\s*(.+?)\s*$", block, re.MULTILINE)
    description_match = re.search(
        r"^description:\s*(.+?)\s*$", block, re.MULTILINE
    )
    name = (name_match.group(1).strip(" '\"") if name_match else "Exchanged Skill")
    description = (
        description_match.group(1).strip(" '\"")
        if description_match
        else f"Guidance adapted from {name}"
    )
    return name, description


def _envelope_comment(envelope: dict) -> bytes:
    payload = json.dumps(
        envelope, ensure_ascii=True, indent=2, sort_keys=True
    ).encode("utf-8")
    return b"<!-- rapp-exchange/1\n" + payload + b"\n-->\n"


def _read_envelope(data: bytes) -> dict | None:
    match = MARKER_RE.search(data)
    if not match:
        return None
    try:
        envelope = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        raise ExchangeError(f"invalid exchange envelope JSON: {exc}") from exc
    if envelope.get("schema") != SCHEMA:
        raise ExchangeError("unsupported exchange schema")
    return envelope


def _write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def agent_to_skill(source: Path, destination: Path) -> None:
    data = source.read_bytes()
    tree = ast.parse(data.decode("utf-8-sig"))
    carried = _module_assignment(tree, "__rapp_exchange_source__")
    if isinstance(carried, dict) and carried.get("schema") == SCHEMA:
        record = carried.get("source")
        if (
            isinstance(record, dict)
            and record.get("media_type") == "text/markdown; profile=skill"
        ):
            _write(destination, _decode_source(record))
            return

    name, description, metadata = _agent_metadata(data)
    record = _source_record(data, "text/x-python")
    envelope = {
        "schema": SCHEMA,
        "protocol": PROTOCOL,
        "artifact": {
            "kind": "brainstem-agent",
            "name": name,
            "description": description,
            "tool_schema": metadata,
            "source": record,
        },
        "mapping": {
            "source_host": "rapp-brainstem",
            "target_host": "skill-consumer",
            "conversion": "lossless-envelope",
        },
    }
    frontmatter = (
        "---\n"
        f"name: {_slug(name)}\n"
        f"description: {json.dumps(description, ensure_ascii=True)}\n"
        "metadata: "
        + json.dumps(
            {
                "exchange": SCHEMA,
                "source_kind": "brainstem-agent",
                "source_sha256": record["sha256"],
            },
            separators=(",", ":"),
            sort_keys=True,
        )
        + "\n---\n\n"
    )
    body = (
        f"# {name}\n\n{description}\n\n"
        "This skill carries a lossless Brainstem agent. A compatible host should "
        "inspect the normalized tool schema, verify the source hash, and use "
        "`exchange.py skill-to-agent` to restore the exact Python bytes.\n\n"
    )
    _write(
        destination,
        frontmatter.encode("utf-8")
        + body.encode("utf-8")
        + _envelope_comment(envelope),
    )


def skill_to_agent(source: Path, destination: Path) -> None:
    data = source.read_bytes()
    envelope = _read_envelope(data)
    if envelope:
        artifact = envelope.get("artifact", {})
        record = artifact.get("source")
        if (
            artifact.get("kind") == "brainstem-agent"
            and isinstance(record, dict)
            and record.get("media_type") == "text/x-python"
        ):
            _write(destination, _decode_source(record))
            return

    name, description = _frontmatter(data)
    record = _source_record(data, "text/markdown; profile=skill")
    carried = {"schema": SCHEMA, "source": record}
    tool_name = _class_name(name)
    metadata = {
        "name": tool_name,
        "description": (
            f"Guidance-only adapter for the skill '{name}'. Returns the preserved "
            "instructions; it does not claim executable parity."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "request": {
                    "type": "string",
                    "description": "Optional context for using the skill guidance.",
                }
            },
            "required": [],
        },
    }
    generated = f'''"""Generated guidance adapter for {name}.

The original SKILL.md bytes are preserved in __rapp_exchange_source__.
"""
import base64

from agents.basic_agent import BasicAgent

__rapp_exchange_source__ = {carried!r}


class {tool_name}(BasicAgent):
    def __init__(self):
        self.name = {tool_name!r}
        self.metadata = {metadata!r}
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, request="", **kwargs):
        record = __rapp_exchange_source__["source"]
        return base64.b64decode(record["data"]).decode("utf-8-sig")
'''
    _write(destination, generated.encode("utf-8"))


def _safe_relative(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if (
        not value
        or path.is_absolute()
        or ".." in path.parts
        or "." in path.parts
        or any(not part for part in path.parts)
    ):
        raise ExchangeError(f"unsafe relative path: {value!r}")
    return path


def squad_to_skill(source: Path, destination: Path) -> None:
    if not source.is_dir():
        raise ExchangeError("squad source must be a directory")
    files = []
    for path in sorted(source.rglob("*")):
        if path.is_symlink():
            raise ExchangeError(f"symlinks are not exchangeable: {path}")
        if not path.is_file():
            continue
        relative = path.relative_to(source).as_posix()
        _safe_relative(relative)
        record = _source_record(path.read_bytes(), "application/octet-stream")
        files.append({"path": relative, **record})
    if not files:
        raise ExchangeError("squad contains no files")

    name = source.name.lstrip(".") or "squad"
    envelope = {
        "schema": SCHEMA,
        "protocol": PROTOCOL,
        "artifact": {
            "kind": "scout-squad",
            "name": name,
            "files": files,
        },
        "mapping": {
            "source_host": "microsoft-scout",
            "target_host": "skill-consumer",
            "conversion": "lossless-directory-envelope",
        },
    }
    frontmatter = (
        "---\n"
        f"name: {_slug(name)}-squad\n"
        f"description: Lossless Scout squad exchange for {name}.\n"
        f'metadata: {{"exchange":"{SCHEMA}","source_kind":"scout-squad"}}\n'
        "---\n\n"
    )
    body = (
        f"# {name} squad\n\n"
        f"This exchange contains {len(files)} preserved squad files. Restore it "
        "with `exchange.py skill-to-squad`.\n\n"
    )
    _write(
        destination,
        frontmatter.encode("utf-8")
        + body.encode("utf-8")
        + _envelope_comment(envelope),
    )


def skill_to_squad(source: Path, destination: Path) -> None:
    envelope = _read_envelope(source.read_bytes())
    if not envelope or envelope.get("artifact", {}).get("kind") != "scout-squad":
        raise ExchangeError("skill does not carry a Scout squad")
    files = envelope["artifact"].get("files")
    if not isinstance(files, list) or not files:
        raise ExchangeError("squad envelope has no files")
    destination.mkdir(parents=True, exist_ok=True)
    root = destination.resolve()
    for record in files:
        if not isinstance(record, dict):
            raise ExchangeError("invalid squad file record")
        relative = _safe_relative(str(record.get("path", "")))
        output = destination.joinpath(*relative.parts)
        resolved_parent = output.parent.resolve()
        if resolved_parent != root and root not in resolved_parent.parents:
            raise ExchangeError("squad output escapes destination")
        source_record = {key: record[key] for key in (
            "encoding", "media_type", "bytes", "sha256", "data"
        )}
        _write(output, _decode_source(source_record))


def inspect_exchange(source: Path) -> None:
    envelope = _read_envelope(source.read_bytes())
    if not envelope:
        raise ExchangeError("file has no rapp-exchange/1 envelope")
    artifact = envelope.get("artifact", {})
    summary = {
        "schema": envelope["schema"],
        "kind": artifact.get("kind"),
        "name": artifact.get("name"),
        "mapping": envelope.get("mapping"),
    }
    if "source" in artifact:
        summary["source"] = {
            key: artifact["source"].get(key)
            for key in ("media_type", "bytes", "sha256")
        }
    if "files" in artifact:
        summary["files"] = [
            {
                "path": record.get("path"),
                "bytes": record.get("bytes"),
                "sha256": record.get("sha256"),
            }
            for record in artifact["files"]
        ]
    print(json.dumps(summary, indent=2, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("agent-to-skill", "skill-to-agent", "squad-to-skill"):
        child = subparsers.add_parser(command)
        child.add_argument("source", type=Path)
        child.add_argument("destination", type=Path)
    child = subparsers.add_parser("skill-to-squad")
    child.add_argument("source", type=Path)
    child.add_argument("destination", type=Path)
    child = subparsers.add_parser("inspect")
    child.add_argument("source", type=Path)
    args = parser.parse_args(argv)

    try:
        if args.command == "agent-to-skill":
            agent_to_skill(args.source, args.destination)
        elif args.command == "skill-to-agent":
            skill_to_agent(args.source, args.destination)
        elif args.command == "squad-to-skill":
            squad_to_skill(args.source, args.destination)
        elif args.command == "skill-to-squad":
            skill_to_squad(args.source, args.destination)
        else:
            inspect_exchange(args.source)
    except (ExchangeError, OSError, SyntaxError) as exc:
        print(f"exchange refused: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

