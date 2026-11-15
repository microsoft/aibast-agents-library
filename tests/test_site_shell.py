from pathlib import PurePosixPath

from scripts import build_pages_site as bps

PAGE = "<html><head></head><body><main><h1>Hi</h1></main></body></html>"


def test_frame_added_once_to_a_bare_page():
    out = bps.inject_site_shell(PurePosixPath("why.html"), PAGE)
    assert out.count(bps.SHELL_START_MARK) == 1 and out.count(bps.SHELL_FOOTER_MARK) == 1
    assert out.index('class="site-shell"') < out.index("<main>") < out.index('class="site-footer"')
    assert bps.inject_site_shell(PurePosixPath("why.html"), out) == out


def test_links_follow_page_depth():
    out = bps.inject_site_shell(PurePosixPath("docs/installer.html"), PAGE)
    assert 'href="../index.html"' in out and 'href="../start.html"' in out


def test_pages_with_their_own_header_and_footer_are_left_alone():
    own = "<html><body><header>x</header><footer>y</footer></body></html>"
    assert bps.inject_site_shell(PurePosixPath("index.html"), own) == own


def test_redirects_and_deep_pages_are_skipped():
    for p in ("library.html", "qr.html", "solutions/a/quest.html", "beta/index.html"):
        assert bps.inject_site_shell(PurePosixPath(p), PAGE) == PAGE


def test_frame_uses_tokens_without_declaring_them():
    assert "--cp-" in bps.SHELL_STYLE and "--cp-accent:" not in bps.SHELL_STYLE.replace(" ", "")
