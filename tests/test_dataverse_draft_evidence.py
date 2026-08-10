from tools import capture_dataverse_draft_evidence as capture


def test_fetch_bot_sends_runtime_bearer_token(monkeypatch):
    observed = {}

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self):
            return b"{}"

    def fake_urlopen(request, timeout):
        observed["authorization"] = request.get_header("Authorization")
        observed["timeout"] = timeout
        return Response()

    monkeypatch.setattr(capture.urllib.request, "urlopen", fake_urlopen)
    capture.fetch_bot(
        "test-token",
        "11111111-1111-1111-1111-111111111111",
    )

    assert observed == {
        "authorization": "Bearer test-token",
        "timeout": 60,
    }
