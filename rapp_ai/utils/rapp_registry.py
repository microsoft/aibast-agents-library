"""RAPP/1 identity registry for Hippocampus.

Mutable lookup names point to immutable, canonical RAPP/1 identity records.
Azure uses Blob `overwrite=False` for atomic create-if-absent semantics.
"""

from __future__ import annotations

import json
import os
import pathlib
import threading
from datetime import datetime, timezone
from typing import Protocol

from utils.rapp_protocol import H, build_frame, canonical_bytes, mint_rappid


IDENTITY_SCHEMA = "rapp/1-identity-binding"
DEFAULT_CONTAINER = "rapp-registry"


def fixed_utc(now: datetime | None = None) -> str:
    value = now or datetime.now(timezone.utc)
    value = value.astimezone(timezone.utc)
    return value.strftime("%Y-%m-%dT%H:%M:%S.") + f"{value.microsecond // 1000:03d}Z"


class RegistryStore(Protocol):
    def read(self, name: str) -> bytes | None:
        ...

    def create(self, name: str, data: bytes) -> bool:
        """Atomically create and return False when the name already exists."""


class LocalRegistryStore:
    def __init__(self, root: str | os.PathLike[str]):
        self.root = pathlib.Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        try:
            self.root.chmod(0o700)
        except OSError:
            pass

    def _path(self, name: str) -> pathlib.Path:
        candidate = (self.root / name).resolve()
        if self.root not in candidate.parents:
            raise ValueError("registry path escapes its root")
        return candidate

    def read(self, name: str) -> bytes | None:
        path = self._path(name)
        try:
            return path.read_bytes()
        except FileNotFoundError:
            return None

    def create(self, name: str, data: bytes) -> bool:
        path = self._path(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            descriptor = os.open(
                path,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                0o600,
            )
        except FileExistsError:
            return False
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        return True


class AzureBlobRegistryStore:
    def __init__(self, blob_service, container_name: str = DEFAULT_CONTAINER):
        from azure.core.exceptions import ResourceExistsError

        self._resource_exists = ResourceExistsError
        self.container = blob_service.get_container_client(container_name)
        try:
            self.container.create_container()
        except ResourceExistsError:
            pass

    def read(self, name: str) -> bytes | None:
        from azure.core.exceptions import ResourceNotFoundError

        try:
            return self.container.download_blob(name).readall()
        except ResourceNotFoundError:
            return None

    def create(self, name: str, data: bytes) -> bool:
        try:
            self.container.upload_blob(name, data, overwrite=False)
            return True
        except self._resource_exists:
            return False


def create_registry_store(storage_manager=None) -> RegistryStore:
    if storage_manager is not None and hasattr(storage_manager, "blob_service"):
        return AzureBlobRegistryStore(
            storage_manager.blob_service,
            os.environ.get("RAPP_REGISTRY_CONTAINER", DEFAULT_CONTAINER),
        )
    root = os.environ.get(
        "RAPP_LOCAL_REGISTRY_PATH",
        os.path.join(os.path.dirname(os.path.dirname(__file__)), ".local_storage", "rapp1"),
    )
    return LocalRegistryStore(root)


class PrincipalIdentityRegistry:
    _lock = threading.Lock()

    def __init__(self, store: RegistryStore, owner: str):
        self.store = store
        self.owner = owner

    @staticmethod
    def principal_hash(issuer: str, subject: str) -> str:
        return H("rapp/1:particle", {
            "issuer": str(issuer),
            "subject": str(subject),
        })

    @staticmethod
    def binding_name(principal_hash: str) -> str:
        return f"identity/principals/{principal_hash}.json"

    @staticmethod
    def frame_name(frame_hash: str) -> str:
        return f"frames/body/{frame_hash}.json"

    def read(self, issuer: str, subject: str) -> dict | None:
        principal_hash = self.principal_hash(issuer, subject)
        data = self.store.read(self.binding_name(principal_hash))
        if data is None:
            return None
        binding = json.loads(data)
        self._validate_binding(binding, principal_hash)
        return binding

    def resolve_or_mint(
        self,
        *,
        issuer: str,
        subject: str,
        slug: str,
    ) -> dict:
        existing = self.read(issuer, subject)
        if existing:
            return existing

        with self._lock:
            existing = self.read(issuer, subject)
            if existing:
                return existing
            rappid, memory_anchor = mint_rappid(self.owner, slug)
            created_utc = fixed_utc()
            principal_hash = self.principal_hash(issuer, subject)
            genesis = build_frame(
                "body.pulse",
                rappid,
                0,
                created_utc,
                {
                    "event": "identity-created",
                    "principal_hash": principal_hash,
                    "memory_guid": str(memory_anchor),
                },
                prev=None,
            )
            binding = {
                "schema": IDENTITY_SCHEMA,
                "principal_hash": principal_hash,
                "rappid": rappid,
                "memory_guid": str(memory_anchor),
                "created_utc": created_utc,
                "genesis_frame_hash": genesis["frame_hash"],
            }
            self.store.create(
                self.frame_name(genesis["frame_hash"]),
                canonical_bytes(genesis),
            )
            created = self.store.create(
                self.binding_name(principal_hash),
                canonical_bytes(binding),
            )
            if created:
                return binding
            winner = self.read(issuer, subject)
            if winner is None:
                raise RuntimeError("identity binding race did not produce a winner")
            return winner

    @staticmethod
    def _validate_binding(binding: dict, expected_hash: str) -> None:
        required = {
            "schema",
            "principal_hash",
            "rappid",
            "memory_guid",
            "created_utc",
            "genesis_frame_hash",
        }
        if not isinstance(binding, dict) or set(binding) != required:
            raise ValueError("invalid RAPP/1 identity binding shape")
        if binding["schema"] != IDENTITY_SCHEMA:
            raise ValueError("invalid identity binding schema")
        if binding["principal_hash"] != expected_hash:
            raise ValueError("identity binding principal mismatch")
