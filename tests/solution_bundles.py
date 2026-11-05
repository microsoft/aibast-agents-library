"""Fresh solution source bundles for tests.

Source bundles are published as release assets and are not committed, so tests
that inspect a bundle build it from the current tree with the repository
bundler. Builds are cached for the test session.
"""

import atexit
import shutil
import tempfile
from functools import lru_cache
from pathlib import Path

from tools import build_solution_export


ROOT = Path(__file__).resolve().parent.parent
_STAGING = Path(tempfile.mkdtemp(prefix="aibast-solution-bundles-"))
atexit.register(shutil.rmtree, _STAGING, ignore_errors=True)


@lru_cache(maxsize=None)
def built_bundle(slug: str) -> Path:
    """Return the path of a freshly built ``<slug>-source.zip``."""
    target = _STAGING / f"{slug}-source.zip"
    build_solution_export.build(
        ROOT / "solutions" / slug / "export-manifest.json",
        target,
        root=ROOT,
    )
    return target
