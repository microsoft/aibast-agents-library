import json
import hashlib
import pathlib
import uuid

from utils import rapp_protocol as rapp


ROOT = pathlib.Path(__file__).resolve().parents[2]
VECTORS = json.loads(
    (ROOT / "tools" / "rapp1" / "conformance-vectors.json").read_text(
        encoding="utf-8"
    )
)


def test_authority_revision_is_pinned():
    assert rapp.SOURCE_COMMIT == VECTORS["source_commit"]
    assert rapp.SPEC == "rapp/1"


def test_canonicalization_and_domain_hashes_match_shared_vectors():
    for vector in VECTORS["canonical"]:
        value = vector["value"]
        assert rapp.canonical(value) == vector["bytes_utf8"]
        assert rapp.H("rapp/1:particle", value) == vector["particle"]
        assert rapp.H("rapp/1:wave", value) == vector["wave"]
        assert (
            rapp.H("rapp/1:egg-manifest", value)
            == vector["egg_manifest"]
        )


def test_keyless_identity_reuses_the_uuid_memory_anchor():
    vector = VECTORS["identity"]
    identity, anchor = rapp.mint_rappid(
        vector["owner"],
        vector["slug"],
        uuid_anchor=uuid.UUID(vector["uuid_anchor"]),
    )
    assert identity == vector["rappid"]
    assert str(anchor) == vector["uuid_anchor"]
    assert rapp.rappid_valid(identity)


def test_frame_build_and_verify_matches_shared_vector():
    vector = VECTORS["frame"]
    frame = rapp.build_frame(
        vector["kind"],
        vector["stream_id"],
        vector["seq"],
        vector["utc"],
        vector["payload"],
        vector["prev"],
        prev_wave=vector["prev_wave"],
        sig=vector["sig"],
    )
    assert frame["payload_hash"] == vector["payload_hash"]
    assert frame["frame_hash"] == vector["frame_hash"]
    assert rapp.verify_frame(
        frame,
        stream_id_of_record=vector["stream_id"],
    ) == (True, None, "ok")

    tampered = dict(frame)
    tampered["payload"] = {"hello": "tampered"}
    ok, step, _reason = rapp.verify_frame(tampered)
    assert not ok
    assert step == "2"


def test_rapplication_egg_is_deterministic_and_verified():
    identity = VECTORS["identity"]["rappid"]
    egg_vector = VECTORS["rapplication_egg"]
    files = {
        path: content.encode()
        for path, content in egg_vector["files"].items()
    }
    first = rapp.pack_egg(
        "rapplication",
        identity,
        egg_vector["created_utc"],
        files=files,
    )
    second = rapp.pack_egg(
        "rapplication",
        identity,
        egg_vector["created_utc"],
        files=dict(reversed(list(files.items()))),
    )
    assert first == second
    assert len(first) == egg_vector["size"]
    assert hashlib.sha256(first).hexdigest() == egg_vector["sha256"]
    assert rapp.verify_egg(first) == (True, None, "ok")


def test_session_egg_round_trips_as_canonical_json():
    identity = VECTORS["identity"]["rappid"]
    payload = {
        "runtime": {
            "session_id": "session-1",
            "composition_hash": "a" * 64,
        },
        "transcript": [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "hi"},
        ],
    }
    egg = rapp.pack_egg(
        "session",
        identity,
        "2026-08-11T00:00:00.000Z",
        payload=payload,
    )
    manifest, files = rapp.read_egg(egg)
    assert files == {}
    assert manifest["payload"] == payload
    assert rapp.verify_egg(egg) == (True, None, "ok")
