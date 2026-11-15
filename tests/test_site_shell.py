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


def test_simple_topbar_is_replaced_and_keeps_the_quest_trigger():
    page = ('<html><body><header class="topbar"><a class="brand" href="index.html">'
            '<span class="brand-mark" id="quest-trigger">AI</span></a><nav><a href="academy.html">Academy</a></nav>'
            '</header><main>x</main></body></html>')
    out = bps.inject_site_shell(PurePosixPath("index.html"), page)
    assert 'class="topbar"' not in out and out.count('id="quest-trigger"') == 1
    assert out.index('class="site-shell"') < out.index("<main>")


def test_topbar_with_its_own_controls_is_kept():
    page = '<html><body><header class="topbar"><button id="themeToggle">T</button></header><main>x</main></body></html>'
    assert bps.inject_site_shell(PurePosixPath("academy.html"), page).count('class="topbar"') == 1


def test_headers_inside_the_main_content_do_not_count():
    page = '<html><body><main><article><header>card</header></article></main></body></html>'
    assert bps.SHELL_START_MARK in bps.inject_site_shell(PurePosixPath("blog.html"), page)
