import concurrent.futures
import pathlib

from utils.rapp_registry import LocalRegistryStore, PrincipalIdentityRegistry
from utils.rapp_protocol import rappid_valid


def test_principal_identity_is_minted_once_under_concurrency(tmp_path):
    store = LocalRegistryStore(tmp_path)
    registry = PrincipalIdentityRegistry(store, "microsoft")

    def resolve():
        return registry.resolve_or_mint(
            issuer="https://login.microsoftonline.com/example/v2.0",
            subject="entra-object-id",
            slug="example-user",
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        bindings = list(pool.map(lambda _value: resolve(), range(32)))

    assert len({binding["rappid"] for binding in bindings}) == 1
    assert len({binding["memory_guid"] for binding in bindings}) == 1
    binding = bindings[0]
    assert rappid_valid(binding["rappid"])
    assert len(binding["genesis_frame_hash"]) == 64

    principal_files = list(pathlib.Path(tmp_path).glob("identity/principals/*.json"))
    assert len(principal_files) == 1


def test_principal_hash_does_not_store_raw_subject_in_path(tmp_path):
    registry = PrincipalIdentityRegistry(LocalRegistryStore(tmp_path), "microsoft")
    binding = registry.resolve_or_mint(
        issuer="issuer",
        subject="private-user@example.com",
        slug="private-user",
    )
    paths = [str(path) for path in pathlib.Path(tmp_path).rglob("*")]
    assert all("private-user@example.com" not in path for path in paths)
    assert binding["principal_hash"] in paths[-1] or any(
        binding["principal_hash"] in path for path in paths
    )
