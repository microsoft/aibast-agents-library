"""The site build asks GitHub for the tree once per deploy. A server error is retried; a client error is not."""
import io
import json
from unittest import mock
from urllib.error import HTTPError

import pytest

from scripts import build_pages_site as pages


class _Reply(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _error(code):
    return HTTPError("https://api.github.com/x", code, "error", {}, None)


def _tree():
    return _Reply(json.dumps({"tree": [], "truncated": False}).encode())


def test_a_server_error_is_retried_and_the_build_goes_on():
    replies = [_error(500), _error(502), _tree()]
    with mock.patch.object(pages, "urlopen", side_effect=replies) as opened, \
            mock.patch.object(pages.time, "sleep") as slept:
        assert pages.fetch_github_tree_metadata("o", "r", "main") == {}
    assert opened.call_count == 3
    assert slept.call_count == 2


def test_a_server_error_that_never_clears_fails_after_the_last_try():
    with mock.patch.object(pages, "urlopen", side_effect=lambda *a, **k: (_ for _ in ()).throw(_error(500))) as opened, \
            mock.patch.object(pages.time, "sleep"):
        with pytest.raises(pages.BuildError, match="HTTP 500"):
            pages.fetch_github_tree_metadata("o", "r", "main")
    assert opened.call_count == pages.TREE_METADATA_ATTEMPTS


def test_a_client_error_fails_at_once():
    with mock.patch.object(pages, "urlopen", side_effect=[_error(404)]) as opened, \
            mock.patch.object(pages.time, "sleep") as slept:
        with pytest.raises(pages.BuildError, match="HTTP 404"):
            pages.fetch_github_tree_metadata("o", "r", "main")
    assert opened.call_count == 1
    assert slept.call_count == 0
