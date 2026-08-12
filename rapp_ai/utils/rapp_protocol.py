"""RAPP/1 protocol primitives pinned to kody-w/rapp-1 rev-5.

Authority commit:
    d2cd5abed48d3f52b86bbb975ac3558286d1db41
"""

from __future__ import annotations

import hashlib
import io
import json
import math
import re
import uuid
import zipfile
from typing import Any

import rfc8785


SPEC = "rapp/1"
SOURCE_COMMIT = "d2cd5abed48d3f52b86bbb975ac3558286d1db41"
MAX_CANONICAL_BYTES = 1024 * 1024
MAX_DEPTH = 64
MAX_SAFE_INTEGER = 2**53 - 1

_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_UTC = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:(?:[0-5]\d)\.\d{3}Z$"
)
_LCLABEL = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_KIND = re.compile(
    r"^[a-z0-9]+(?:-[a-z0-9]+)*\.[a-z0-9]+(?:-[a-z0-9]+)*$"
)
_RAPPID = re.compile(
    r"^rappid:@([a-z0-9]+(?:-[a-z0-9]+)*)/"
    r"([a-z0-9]+(?:-[a-z0-9]+)*):([0-9a-f]{64})$"
)

FRAME_KEYS = {
    "spec",
    "kind",
    "stream_id",
    "seq",
    "utc",
    "payload",
    "payload_hash",
    "frame_hash",
    "prev",
    "prev_wave",
    "sig",
}
EGG_VARIANTS = {
    "organism",
    "rapplication",
    "session",
    "invite",
    "neighborhood",
    "estate",
}
_JSON_EGG_VARIANTS = {"session", "invite"}
_EGG_MANIFEST_KEYS = {
    "schema",
    "variant",
    "rappid",
    "created_utc",
    "contents",
    "payload",
    "sig",
}


def _validate_value(value: Any, depth: int = 1) -> None:
    if depth > MAX_DEPTH:
        raise ValueError(f"RAPP/1 JSON nesting exceeds {MAX_DEPTH}")
    if value is None or isinstance(value, bool):
        return
    if isinstance(value, int):
        if abs(value) > MAX_SAFE_INTEGER:
            raise ValueError("RAPP/1 integers must round-trip through binary64")
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("RAPP/1 numbers must be finite")
        return
    if isinstance(value, str):
        value.encode("utf-8", "strict")
        return
    if isinstance(value, list):
        for item in value:
            _validate_value(item, depth + 1)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("RAPP/1 object keys must be strings")
            key.encode("utf-8", "strict")
            _validate_value(item, depth + 1)
        return
    raise ValueError(f"RAPP/1 value is not I-JSON: {type(value).__name__}")


def canonical_bytes(value: Any) -> bytes:
    """Return RFC 8785 canonical UTF-8 after enforcing the RAPP/1 profile."""
    _validate_value(value)
    encoded = rfc8785.dumps(value)
    if len(encoded) > MAX_CANONICAL_BYTES:
        raise ValueError("RAPP/1 canonical form exceeds 1 MiB")
    return encoded


def canonical(value: Any) -> str:
    return canonical_bytes(value).decode("utf-8")


def H(space: str, value: Any) -> str:
    return hashlib.sha256(
        space.encode("ascii") + b"\n" + canonical_bytes(value)
    ).hexdigest()


def Hb(space: str, octets: bytes) -> str:
    if not isinstance(octets, bytes):
        raise TypeError("Hb requires bytes")
    return hashlib.sha256(space.encode("ascii") + b"\n" + octets).hexdigest()


def _validate_owner_slug(owner: str, slug: str) -> None:
    if not (
        isinstance(owner, str)
        and 1 <= len(owner) <= 39
        and _LCLABEL.fullmatch(owner)
    ):
        raise ValueError("RAPP/1 owner must be a lowercase GitHub-login label")
    if not (
        isinstance(slug, str)
        and 1 <= len(slug) <= 100
        and _LCLABEL.fullmatch(slug)
    ):
        raise ValueError("RAPP/1 slug must be a lowercase label")


def mint_rappid(
    owner: str,
    slug: str,
    *,
    uuid_anchor: uuid.UUID | str | None = None,
    spki_der: bytes | None = None,
) -> tuple[str, uuid.UUID | None]:
    """Mint one canonical identity and return its UUID anchor when keyless."""
    _validate_owner_slug(owner, slug)
    if spki_der is not None and uuid_anchor is not None:
        raise ValueError("Choose keyed or keyless RAPPID minting, not both")
    if spki_der is not None:
        tail = Hb("rapp/1:rappid", spki_der)
        anchor = None
    else:
        anchor = (
            uuid_anchor
            if isinstance(uuid_anchor, uuid.UUID)
            else uuid.UUID(str(uuid_anchor))
            if uuid_anchor is not None
            else uuid.uuid4()
        )
        tail = Hb("rapp/1:rappid", anchor.bytes)
    return f"rappid:@{owner}/{slug}:{tail}", anchor


def rappid_valid(value: str) -> bool:
    match = _RAPPID.fullmatch(value or "")
    if not match:
        return False
    owner, slug, _tail = match.groups()
    return len(owner) <= 39 and len(slug) <= 100


def build_frame(
    kind: str,
    stream_id: str,
    seq: int,
    utc: str,
    payload: dict[str, Any],
    prev: str | None,
    *,
    prev_wave: str | None = None,
    sig: str | None = None,
) -> dict[str, Any]:
    frame = {
        "spec": SPEC,
        "kind": kind,
        "stream_id": stream_id,
        "seq": seq,
        "utc": utc,
        "payload": payload,
        "payload_hash": H("rapp/1:particle", payload),
        "prev": prev,
        "prev_wave": prev_wave,
        "sig": sig,
    }
    preimage = {
        key: frame[key]
        for key in frame
        if key not in {"frame_hash", "sig"}
    }
    frame["frame_hash"] = H("rapp/1:wave", preimage)
    return frame


def verify_frame(
    frame: dict[str, Any],
    *,
    head: dict[str, Any] | None = None,
    stream_id_of_record: str | None = None,
) -> tuple[bool, str | None, str]:
    if not isinstance(frame, dict) or set(frame) != FRAME_KEYS:
        return False, "1", "frame must contain exactly the 11 RAPP/1 keys"
    if frame["spec"] != SPEC:
        return False, "1", "spec != rapp/1"
    if not isinstance(frame["kind"], str) or not _KIND.fullmatch(frame["kind"]):
        return False, "1", "invalid kind"
    if not isinstance(frame["stream_id"], str):
        return False, "1", "invalid stream_id type"
    if not (
        isinstance(frame["seq"], int)
        and not isinstance(frame["seq"], bool)
        and 0 <= frame["seq"] <= MAX_SAFE_INTEGER
    ):
        return False, "1", "seq is not uint53"
    if not isinstance(frame["utc"], str) or not _UTC.fullmatch(frame["utc"]):
        return False, "1", "utc is not fixed millisecond UTC"
    if not isinstance(frame["payload"], dict):
        return False, "1", "payload is not an object"
    for field in ("payload_hash", "frame_hash"):
        if not isinstance(frame[field], str) or not _HEX64.fullmatch(frame[field]):
            return False, "1", f"{field} is not lowercase 64-hex"
    for field in ("prev", "prev_wave"):
        value = frame[field]
        if value is not None and (
            not isinstance(value, str) or not _HEX64.fullmatch(value)
        ):
            return False, "1", f"{field} is not null or lowercase 64-hex"
    if (
        stream_id_of_record is not None
        and frame["stream_id"] != stream_id_of_record
    ):
        return False, "1a", "stream_id mismatch"
    try:
        if frame["payload_hash"] != H("rapp/1:particle", frame["payload"]):
            return False, "2", "payload_hash mismatch"
        preimage = {
            key: frame[key]
            for key in frame
            if key not in {"frame_hash", "sig"}
        }
        if frame["frame_hash"] != H("rapp/1:wave", preimage):
            return False, "3", "frame_hash mismatch"
    except (TypeError, ValueError) as exc:
        return False, "1", str(exc)
    if head is None:
        if frame["seq"] != 0 or frame["prev"] is not None:
            return False, "4", "genesis must be seq=0 and prev=null"
    else:
        if frame["seq"] != head["seq"] + 1:
            return False, "4", "seq is not contiguous"
        if frame["prev"] != head["payload_hash"]:
            return False, "4", "prev does not match head particle"
        if frame["utc"] < head["utc"]:
            return False, "4", "utc moved backwards"
    is_swarm = frame["stream_id"].startswith("net:")
    if is_swarm and frame["seq"] > 0:
        if head is not None and frame["prev_wave"] != head["frame_hash"]:
            return False, "5", "prev_wave does not match swarm head"
    elif frame["prev_wave"] is not None:
        return False, "5", "prev_wave must be null off swarm"
    if is_swarm and frame["sig"] is None:
        return False, "6", "swarm frame must be signed"
    return True, None, "ok"


def egg_address(manifest: dict[str, Any]) -> str:
    return H(
        "rapp/1:egg-manifest",
        {key: value for key, value in manifest.items() if key != "sig"},
    )


def _egg_contents(files: dict[str, bytes]) -> list[dict[str, str]]:
    contents = [
        {"path": path, "hash": Hb("rapp/1:egg", octets)}
        for path, octets in files.items()
    ]
    contents.sort(key=lambda item: item["path"].encode("utf-8"))
    return contents


def pack_egg(
    variant: str,
    rappid: str,
    created_utc: str,
    *,
    files: dict[str, bytes] | None = None,
    payload: dict[str, Any] | None = None,
    sig: str | None = None,
) -> bytes:
    if variant not in EGG_VARIANTS:
        raise ValueError(f"Unknown RAPP/1 egg variant: {variant}")
    if not rappid_valid(rappid):
        raise ValueError("Invalid RAPPID")
    if not _UTC.fullmatch(created_utc):
        raise ValueError("Invalid RAPP/1 created_utc")
    files = dict(files or {})
    payload = {} if payload is None else payload
    is_json = variant in _JSON_EGG_VARIANTS
    if is_json and files:
        raise ValueError(f"{variant} is a JSON egg and cannot contain files")
    manifest = {
        "schema": "rapp/1-egg",
        "variant": variant,
        "rappid": rappid,
        "created_utc": created_utc,
        "contents": [] if is_json else _egg_contents(files),
        "payload": payload,
        "sig": sig,
    }
    manifest_bytes = canonical_bytes(manifest)
    if is_json:
        return manifest_bytes
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_STORED) as archive:
        def write_entry(name: str, data: bytes) -> None:
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED
            info.flag_bits |= 0x800
            archive.writestr(info, data)

        write_entry("manifest.json", manifest_bytes)
        for entry in manifest["contents"]:
            write_entry(entry["path"], files[entry["path"]])
    return output.getvalue()


def read_egg(blob: bytes) -> tuple[dict[str, Any], dict[str, bytes]]:
    if blob[:2] == b"PK":
        with zipfile.ZipFile(io.BytesIO(blob)) as archive:
            manifest = json.loads(archive.read("manifest.json"))
            files = {
                name: archive.read(name)
                for name in archive.namelist()
                if name != "manifest.json"
            }
            return manifest, files
    return json.loads(blob), {}


def verify_egg(blob: bytes) -> tuple[bool, str | None, str]:
    try:
        manifest, files = read_egg(blob)
    except Exception as exc:
        return False, "parse", str(exc)
    if not isinstance(manifest, dict) or set(manifest) != _EGG_MANIFEST_KEYS:
        return False, "9.1", "manifest must contain exactly seven members"
    if manifest["schema"] != "rapp/1-egg":
        return False, "9.1", "schema != rapp/1-egg"
    variant = manifest["variant"]
    if variant not in EGG_VARIANTS:
        return False, "9.2", "unknown egg variant"
    if not rappid_valid(manifest["rappid"]):
        return False, "6.1", "invalid RAPPID"
    if not isinstance(manifest["created_utc"], str) or not _UTC.fullmatch(
        manifest["created_utc"]
    ):
        return False, "7.4", "invalid created_utc"
    contents = manifest["contents"]
    if not isinstance(contents, list):
        return False, "9.1", "contents is not an array"
    paths = [entry.get("path") for entry in contents if isinstance(entry, dict)]
    if len(paths) != len(contents):
        return False, "9.1", "invalid contents entry"
    for path in paths:
        if (
            not isinstance(path, str)
            or path.startswith("/")
            or "\\" in path
            or any(segment in {"", ".", ".."} for segment in path.split("/"))
        ):
            return False, "9.1", f"invalid egg path: {path}"
    if paths != sorted(paths, key=lambda path: path.encode("utf-8")):
        return False, "9.1", "egg paths are not byte-sorted"
    if len(paths) != len(set(paths)):
        return False, "9.1", "duplicate egg path"
    if variant in _JSON_EGG_VARIANTS:
        if contents:
            return False, "9.1", "JSON egg contents must be empty"
        try:
            if blob != canonical_bytes(manifest):
                return False, "9.1", "JSON egg is not canonical"
        except ValueError as exc:
            return False, "9.1", str(exc)
    else:
        if set(files) != set(paths):
            return False, "9.1", "archive entries do not match contents"
        for entry in contents:
            if Hb("rapp/1:egg", files[entry["path"]]) != entry.get("hash"):
                return False, "5", f"content hash mismatch: {entry['path']}"
    if variant == "organism" and not {
        "rappid.json",
        "soul.md",
    }.issubset(files):
        return False, "9.2", "organism requires rappid.json and soul.md"
    if variant == "rapplication":
        if "rappid.json" not in files:
            return False, "9.2", "rapplication requires rappid.json"
        root_python = [
            path for path in files if "/" not in path and path.endswith(".py")
        ]
        if len(root_python) != 1:
            return False, "9.2", "rapplication requires one root agent.py"
    if variant == "session" and set(manifest["payload"]) != {
        "runtime",
        "transcript",
    }:
        return False, "9.2", "session payload must be {runtime, transcript}"
    if variant == "invite":
        if set(manifest["payload"]) != {
            "target_rappid",
            "target_url",
            "target_kind",
        }:
            return False, "9.2", "invite payload has the wrong members"
        if manifest["sig"] is None:
            return False, "9.2", "invite signature is required"
    return True, None, "ok"
