"""Contract tests for the metrics dashboard preservation/theme audit."""

from pathlib import Path

import pytest

from tools.audit_metrics_page import (
    DEFAULT_CONTRACT,
    DEFAULT_PAGE,
    audit_html,
    build_contract,
    load_contract,
)

CONTRACT = load_contract(DEFAULT_CONTRACT)


def test_actual_page_exposes_accessible_verified_achievement_surface():
    html = DEFAULT_PAGE.read_text(encoding="utf-8")
    for element_id in (
        "achievements-points",
        "achievements-heading",
        "achievements-summary",
        "achievements-coverage",
        "achievements-profile-hint",
        "achievements-leaderboard",
        "achievements-workshop-hint",
        "achievements-workshop-table",
        "achievements-rollup-heading",
        "achievements-rollup-hint",
        "achievements-rollup-table",
    ):
        assert f'id="{element_id}"' in html
    assert 'aria-labelledby="achievements-heading"' in html
    assert 'role="status"' in html.split('id="achievements-coverage"', 1)[1].split(
        ">", 1
    )[0]
    assert 'aria-live="polite"' in html.split('id="achievements-summary"', 1)[1].split(
        ">", 1
    )[0]
    assert (
        '<caption>Verified public achievement profiles ranked by points</caption>'
        in html
    )
    assert '<caption>Canonical workshops ranked by verified achievement points</caption>' in html
    assert '<caption>Verified claims by canonical achievement</caption>' in html
    assert "function renderAchievementPoints()" in html
    assert "renderAchievementPoints();" in html
    assert "href=\"achievements.html\"" in html
    assert "href=\"docs/metrics-admin-setup.html\"" in html
    assert ".achievements-card {\n  min-width: 0;\n}" in html


def test_feedback_targets_pages_owner_with_microsoft_fallback():
    html = DEFAULT_PAGE.read_text(encoding="utf-8")
    assert "function resolveFeedbackOwner(hostname)" in html
    assert r"\.github\.io$/i" in html
    assert "return pagesHost ? pagesHost[1] : 'microsoft';" in html
    assert "const issueOwner = resolveFeedbackOwner(location.hostname);" in html
    assert (
        "new URL(`https://github.com/${issueOwner}/aibast-agents-library/issues/new`)"
        in html
    )
    feedback_function = html.split("function wireFeedback()", 1)[1].split(
        "$('tabs').addEventListener", 1
    )[0]
    assert "github.com/microsoft/aibast-agents-library/issues/new" not in feedback_function


def _theme_block(selector, variables):
    declarations = "\n".join(f"  {name}: {value};" for name, value in variables.items())
    return f"{selector} {{\n{declarations}\n}}"


def valid_fixture():
    theme = CONTRACT["workshop_theme"]
    preservation = CONTRACT["preservation"]
    headings = []
    for item in preservation["headings"]:
        headings.append(f"<{item['level']}>{item['text']}</{item['level']}>")
        if item["text"] == "Traffic over time":
            headings.append(
                '<svg id="chart" role="img" aria-label="Daily clones, page views, '
                'and CDN hits"></svg>'
            )
        elif item["text"] == "Agent leaderboards":
            headings.append('<div id="board-hint"></div><div id="tabs" role="tablist"></div><div id="board"></div>')
        elif item["text"] == "Stacks":
            headings.append(
                '<div id="stack-hint"></div><div class="table-scroll">'
                '<table id="stack-table" aria-label="Stack metrics">'
                '<thead><tr><th scope="col">Stack</th></tr></thead><tbody></tbody>'
                "</table></div>"
            )
        elif item["text"] == "Verticals":
            headings.append('<div id="vert-bars"></div>')
        elif item["text"] == "Categories":
            headings.append('<div id="cat-bars"></div>')
        elif item["text"] == "Quality tiers":
            headings.append('<div id="tier-bars"></div>')
        elif item["text"] == "Most downloaded files":
            headings.append('<div id="cdn-files"></div>')
        elif item["text"] == "Most visited pages":
            headings.append('<div id="paths"></div>')
        elif item["text"] == "Traffic sources":
            headings.append('<div id="referrers"></div>')
        elif item["text"] == "Releases":
            headings.append('<div id="releases"></div>')
        elif item["text"] == "Where these numbers come from":
            headings.append('<div id="sources"></div>')
            headings.extend(
                f"<p>{item['normalized_text']}</p>"
                for item in preservation["source_explanations"]
            )

    css = "\n".join(
        [
            _theme_block(":root", theme["light_variables"]),
            _theme_block('html[data-theme="dark"]', theme["dark_variables"]),
            """
* { box-sizing: border-box; }
body { font-family: "Segoe UI", Aptos, sans-serif; color: var(--cp-text); background: var(--cp-bg); }
code, .mono { font-family: Consolas, monospace; }
a:focus-visible, button:focus-visible { outline: 3px solid var(--cp-highlight); }
.cards { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); }
.table-scroll { overflow-x: auto; }
@media (max-width: 48rem) { .cards { grid-template-columns: 1fr; } }
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0s; transition-duration: 0s; }
}
""",
        ]
    )

    script = r"""
const SITE = 'https://microsoft.github.io/aibast-agents-library/';
const OWNER = 'microsoft', REPO = 'aibast-agents-library';
const $ = id => document.getElementById(id);
let M = null;
async function getJSON(paths) {
  for (const p of paths) {
    const response = await fetch(p, {cache: 'no-store'});
    if (response.ok) return response.json();
  }
  return null;
}
async function load() {
  M = await getJSON(['state/metrics.json', SITE + 'state/metrics.json']);
  if (!M) { $('kpis').textContent = 'Metrics unavailable'; return; }
  render();
  liveTopUp();
}
async function liveTopUp() {
  $('stamp-mode').textContent = 'Checking live sources';
  const [repo, cdn] = await Promise.all([
    getJSON([`https://api.github.com/repos/${OWNER}/${REPO}`]),
    getJSON([`https://data.jsdelivr.com/v1/stats/packages/gh/${OWNER}/${REPO}?period=year`])
  ]);
  if (repo) {
    M.repo.stars = repo.stargazers_count;
    M.repo.forks = repo.forks_count;
    M.repo.open_issues = repo.open_issues_count;
  }
  if (cdn && cdn.hits) {
    const hits = cdn.hits.total || 0;
    if (hits > M.totals.cdn_hits) {
      M.totals.downloads += (hits - M.totals.cdn_hits);
      M.totals.cdn_hits = hits;
    }
  }
  renderKPIs();
}
function render() {
  const t = M.totals;
  const tr = M.traffic || {};
  $('stamp-time').textContent = M.generated_at;
  $('stamp-src').textContent = tr.live ? 'traffic read live' : tr.as_of;
  $('stamp-window').textContent = `${t.tracking_since} ${t.days_tracked}`;
  $('traffic-gap').textContent = tr.unavailable_reason || '';
  const trafficUnavailable = tr.live !== true;
  if (trafficUnavailable) appendAdminSetupNotice($('traffic-gap'));
  $('board-hint').textContent = t.agents;
  renderKPIs();
  renderWorkshops();
  renderChart();
  renderBoards();
  renderStacks();
  renderBars('vert-bars', (M.leaderboards.verticals || []).map(v => ({
    label: v.name, value: v.agents, extra: v.stacks
  })));
  renderBars('cat-bars', (M.leaderboards.categories || []).map(c => ({
    label: c.name, value: c.agents, extra: c.lines
  })));
  renderBars('tier-bars', Object.entries(M.leaderboards.tiers || {}));
  renderCDNFiles();
  renderFileLedger();
  renderPaths();
  renderReferrers();
  renderReleases();
  renderSources();
}
function renderKPIs() {
  const t = M.totals, r = M.repo || {};
  const workshopTotals = (M.workshops || {}).totals || {};
  const cards = [
    { label: 'Agent upvotes', value: t.agent_upvotes },
    { label: 'Repository stars', value: r.stars }
  ];
  const fields = [
    t.downloads, t.clones, t.cdn_hits, t.release_downloads,
    t.agent_file_downloads, t.installer_downloads, t.skill_downloads, t.agents, t.stacks,
    t.verticals, t.total_lines, t.total_kb, t.clone_uniques_14d,
    t.clone_uniques_daily_sum, t.tracking_since, t.page_views,
    t.view_uniques_14d, t.agent_upvotes,
    r.stars, r.forks, r.open_issues,
    workshopTotals.usage_events, workshopTotals.workshops
  ];
  $('kpis').textContent = `Total downloads Workshop usage events Agent downloads Installer fetches ${cards.map(card => `${card.label} ${card.value}`).join(' ')} ${fields.join(' ')}`;
}
const WORKSHOP_SORTS = [
  { id: 'usage_events', label: 'Usage' },
  { id: 'views_14d', label: 'Views' },
  { id: 'file_downloads', label: 'File downloads' },
  { id: 'bundle_downloads', label: 'Bundle downloads' },
  { id: 'feedback_reports', label: 'Feedback' }
];
const WORKSHOP_UPVOTE_SORT = { id: 'agent_upvotes', label: 'Agent upvotes' };
const ALL_WORKSHOP_SORTS = [
  WORKSHOP_SORTS[0],
  WORKSHOP_UPVOTE_SORT,
  ...WORKSHOP_SORTS.slice(1)
];
let activeWorkshopSort = 'usage_events';
function renderWorkshopControls() {
  $('workshop-tabs').innerHTML = ALL_WORKSHOP_SORTS.map(option =>
    `<button type="button" aria-pressed="${option.id === activeWorkshopSort}" aria-controls="workshop-table" data-workshop-sort="${option.id}">${option.label}</button>`
  ).join('');
}
function renderWorkshops() {
  const workshops = M.workshops || {};
  const totals = workshops.totals || {};
  const rows = Array.isArray(workshops.rows) ? workshops.rows.slice() : [];
  $('workshop-summary').textContent = `${totals.usage_events || 0} ${totals.agent_upvotes || 0} ${totals.workshops || 0}`;
  $('workshop-hint').textContent = totals.workshops === undefined
    ? 'workshop metrics are not present in this snapshot'
    : `${totals.workshops} catalog-advertised workshop quests`;
  const coverage = workshops.coverage || {};
  const workshopViewsUnavailable = !(coverage.views || {}).status;
  $('workshop-coverage').textContent = coverage.status || 'unavailable';
  if (coverage.status === 'unavailable' || workshopViewsUnavailable) {
    appendAdminSetupNotice($('workshop-coverage'));
  }
  renderWorkshopControls();
  const sort = ALL_WORKSHOP_SORTS.some(option => option.id === activeWorkshopSort)
    ? activeWorkshopSort
    : 'usage_events';
  rows.sort((left, right) => (Number(right[sort]) || 0) - (Number(left[sort]) || 0));
  $('workshop-table').innerHTML = rows.map(row => {
    const fallbackQuest = `solutions/${encodeURIComponent(row.slug)}/quest.html`;
    return `<tr><td><a href="${fallbackQuest}">${row.display_name || row.slug}</a></td>
      <td>${num(row.usage_events)}</td>
      <td>${num(row.agent_upvotes)} ${row.agent_name || ''}</td>
      <td>${row.views_14d}</td>
      <td>${row.view_uniques_14d}</td><td>${row.file_downloads}</td>
      <td>${row.bundle_downloads}</td><td>${row.feedback_reports}</td></tr>`;
  }).join('');
}
function renderChart() {
  (M.daily || []).forEach(d => { void [d.date, d.clones, d.views, d.cdn]; });
  $('chart').innerHTML = '<rect fill="var(--cp-accent)"></rect>';
}
const BOARDS = [
  { id: 'most_downloaded', label: 'Most downloaded', metric: 'downloads', unit: 'CDN fetches' },
  { id: 'newest', label: 'Newest', metric: 'added_at', unit: 'added' },
  { id: 'largest', label: 'Most code', metric: 'lines', unit: 'lines' }
];
const AGENT_UPVOTE_BOARD = {
  id: 'most_upvoted',
  label: 'Most upvoted',
  metric: 'upvotes',
  unit: 'agent upvotes'
};
const ALL_BOARDS = [
  BOARDS[0],
  AGENT_UPVOTE_BOARD,
  ...BOARDS.slice(1)
];
let activeBoard = 'most_downloaded';
function renderBoards() {
  $('tabs').innerHTML = ALL_BOARDS.map(board =>
    `<button role="tab" aria-selected="${board.id === activeBoard}" aria-controls="board">${board.label}</button>`
  ).join('');
  $('tabs').addEventListener("keydown", event => {
    if (event.key === "ArrowLeft" || event.key === "ArrowRight") event.preventDefault();
  });
  const cfg = ALL_BOARDS.find(b => b.id === activeBoard);
  const agentMetrics = Array.isArray(M.agent_metrics) ? M.agent_metrics : [];
  const signalBoard = activeBoard === 'most_upvoted';
  const rows = signalBoard
    ? agentMetrics
    : (M.leaderboards || {})[activeBoard] || [];
  rows.forEach(r => {
    const url = r.file ? r.file : `https://github.com/${OWNER}/${REPO}`;
    const rowLinks = `<a href="library.html#agent/${encodeURIComponent(r.name)}"></a><a href="${url}"></a>`;
    void [
      r[cfg.metric], r.file, r.name, r.display_name, r.tier, r.category,
      r.stack, r.upvote_discussion_url, rowLinks
    ];
  });
  $('board').innerHTML = 'No agent release-asset downloads have been recorded yet.';
}
function renderStacks() {
  const rows = (M.leaderboards || {}).stacks || [];
  const total = M.totals.stacks;
  rows.forEach(s => {
    const source = `https://github.com/${OWNER}/${REPO}/tree/main/${encodeURI(s.path)}`;
    void [s.path, s.display_name, s.vertical, s.agents, s.lines, s.downloads, source];
  });
  $('stack-hint').textContent = total;
  $('stack-table').innerHTML = '<thead><tr><th scope="col">Stack</th></tr></thead>';
}
function renderBars(target, rows) {
  rows.forEach(r => { void [r.label, r.value]; });
  $(target).textContent = rows.length;
}
function renderCDNFiles() {
  const files = (M.cdn || {}).files || [];
  files.forEach(f => { void [f.file, f.agent, f.kind, f.hits]; });
  $('cdn-files').textContent = `${M.cdn.total_hits} ${M.cdn.bandwidth} ${M.cdn.rank}`;
}
const FILE_LEDGER_PAGE_SIZE = 50;
let fileLedgerPage = 1;
function fileKindLabel(kind) {
  return kind === 'skill' ? 'Skill (SKILL.md)' : kind;
}
function renderFileLedgerControls(rows) {
  const select = $('file-ledger-kind');
  const selected = select.value || 'all';
  const kinds = Array.from(new Set(rows.map(row => row.kind).filter(Boolean))).sort();
  select.innerHTML = '<option value="all">All kinds</option>' + kinds.map(kind =>
    `<option value="${kind}">${fileKindLabel(kind)}</option>`
  ).join('');
  select.value = kinds.includes(selected) ? selected : 'all';
}
function renderFileLedger(resetPage = false) {
  const metrics = M.file_metrics || {};
  const rows = Array.isArray(metrics.rows) ? metrics.rows.slice() : [];
  renderFileLedgerControls(rows);
  if (resetPage) fileLedgerPage = 1;
  const query = $('file-ledger-search').value.trim().toLocaleLowerCase();
  const kind = $('file-ledger-kind').value;
  const sort = $('file-ledger-sort').value;
  const filtered = rows.filter(row => {
    if (kind !== 'all' && row.kind !== kind) return false;
    return !query || [row.path, row.kind, row.agent_name, row.workshop_slug]
      .some(value => String(value || '').toLocaleLowerCase().includes(query));
  });
  filtered.sort((left, right) => sort === 'path'
    ? String(left.path).localeCompare(String(right.path))
    : (Number(right.downloads) || 0) - (Number(left.downloads) || 0));
  const pageCount = Math.max(1, Math.ceil(filtered.length / FILE_LEDGER_PAGE_SIZE));
  fileLedgerPage = Math.min(Math.max(1, fileLedgerPage), pageCount);
  const start = (fileLedgerPage - 1) * FILE_LEDGER_PAGE_SIZE;
  const visible = filtered.slice(start, start + FILE_LEDGER_PAGE_SIZE);
  const totals = metrics.totals || {};
  const byKind = totals.by_kind || {};
  const kindSummary = Object.entries(byKind).map(([name, values]) =>
    `${fileKindLabel(name)} ${values.downloads}`
  ).join(' ');
  $('file-ledger-table').innerHTML = visible.map(row =>
    `<tr><td>${row.path}</td><td>${fileKindLabel(row.kind)}</td>
      <td>${row.agent_name}</td><td>${row.workshop_slug}</td>
      <td>${num(row.downloads)}</td><td>${row.status}</td></tr>`
  ).join('');
  $('file-ledger-summary').textContent =
    `${filtered.length} of ${totals.files || rows.length} tracked files · ${metrics.source_status || 'unknown'} · ${kindSummary}`;
  $('file-ledger-page').textContent = `Page ${fileLedgerPage} of ${pageCount}`;
  $('file-ledger-prev').disabled = fileLedgerPage <= 1;
  $('file-ledger-next').disabled = fileLedgerPage >= pageCount;
}
function renderPaths() {
  const rows = (M.traffic || {}).paths || [];
  rows.forEach(p => {
    const url = `https://github.com${esc(p.path)}`;
    void [p.path, p.count, url];
  });
  $('paths').textContent = rows.length;
}
function renderReferrers() {
  const rows = (M.traffic || {}).referrers || [];
  rows.forEach(r => { void [r.referrer, r.count]; });
  $('referrers').textContent = rows.length;
}
function renderReleases() {
  const rel = M.releases || {releases: []};
  rel.releases.forEach(r => {
    const url = `https://github.com/${OWNER}/${REPO}/releases/tag/${encodeURIComponent(r.tag)}`;
    void [r.tag, r.name, r.published_at, r.assets, r.downloads, url];
  });
  $('releases').textContent = rel.releases.length;
}
function renderSources() {
  (M.sources || []).forEach(s => {
    const link = `<a href="${esc(s.url)}"></a>`;
    void [s.name, s.metric, s.url, link];
  });
  $('sources').textContent = M.sources.length;
}
function appendAdminSetupNotice(parent) {
  parent.appendChild(document.createTextNode(
    ' Configure METRICS_TOKEN with Administration: read and authorize organization SSO. '
  ));
  const link = document.createElement('a');
  link.href = 'docs/metrics-admin-setup.html';
  link.textContent = 'Admin setup checklist';
  parent.appendChild(link);
}
function toggleTheme() {
  const button = $('themeToggle');
  const next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  button.setAttribute('aria-pressed', button.getAttribute('aria-pressed') === 'false' ? 'true' : 'false');
}
const feedbackSchema = "aibast-workshop-feedback/1.0";
function wireFeedback() {
  const issueUrl = new URL('https://github.com/microsoft/aibast-agents-library/issues/new');
  issueUrl.searchParams.set('title', '[Metrics] Feedback');
  issueUrl.searchParams.set('body', `<!-- aibast-workshop-feedback:v1 -->\nFeedback schema: ${feedbackSchema}`);
  $('reportIssue').href = issueUrl.toString();
}
$('workshop-tabs').addEventListener('click', event => {
  const control = event.target.closest('button[data-workshop-sort]');
  if (!control) return;
  activeWorkshopSort = control.dataset.workshopSort;
  renderWorkshops();
});
$('file-ledger-search').addEventListener('input', () => renderFileLedger(true));
$('file-ledger-kind').addEventListener('change', () => renderFileLedger(true));
$('file-ledger-sort').addEventListener('change', () => renderFileLedger(true));
$('file-ledger-prev').addEventListener('click', () => {
  fileLedgerPage -= 1;
  renderFileLedger();
});
$('file-ledger-next').addEventListener('click', () => {
  fileLedgerPage += 1;
  renderFileLedger();
});
$('refresh').addEventListener("click", load);
$('themeToggle').addEventListener("click", toggleTheme);
wireFeedback();
"""

    return f"""<!doctype html>
<html lang="en"><head>
<script>{theme["first_script"]}</script>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Library Metrics — AIBAST Agents Library</title>
<style>{css}</style></head><body>
<a class="skip-link" href="#mainContent">Skip to main content</a>
<header><nav aria-label="AIBAST resources">
<a href="index.html">Home</a>
<a href="library.html">Library</a>
<a href="docs/rapp-guide.html">Production Guide</a>
<a href="solutions/_shared/workshop-settings.html">Workshop settings</a>
<a href="metrics.html" aria-current="page">Metrics</a>
<a id="reportIssue" href="https://github.com/microsoft/aibast-agents-library/issues/new">Report an issue</a>
</nav>
<button id="refresh" type="button" aria-label="Refresh live metrics" aria-controls="kpis stamp-mode">Refresh live</button>
<button id="themeToggle" type="button" aria-label="Toggle theme" aria-pressed="false" data-theme-toggle>Theme</button>
</header>
<main id="mainContent">
<p>AIBAST distribution, engagement, and learning impact</p>
<p>Agent upvotes require a signed-in GitHub account. GitHub permits one active
upvote per account and agent. Upvotes record community preference; agent downloads
are counted separately from GitHub Release assets.
RAR is intentionally excluded from these counts.</p>
<a href="library.html">Browse agents</a>
<div id="kpis" class="cards"></div>
<span id="stamp-time"></span><span id="stamp-window"></span><span id="stamp-src"></span>
<span id="stamp-mode" role="status" aria-live="polite" aria-atomic="true"></span>
<div id="traffic-gap"></div>
<section aria-labelledby="workshop-heading">
<h2 id="workshop-heading">Workshop adoption</h2>
<div id="workshop-hint"></div>
<div id="workshop-summary"></div>
<p id="workshop-coverage" role="status" aria-live="polite" aria-atomic="true"></p>
<p>Workshop usage events are counted public signals. This is a floor and an event sum,
not people, users, or unique usage. These sources use mixed measurement windows, and
one person or action can create multiple events. Agent upvotes are shown separately
and are never added to usage events.</p>
<p>Views cover only observed GitHub top popular-path rows in the 14-day API window.
Raw GitHub and direct GitHub Pages fetches are uncounted.</p>
<div id="workshop-tabs" role="group" aria-label="Sort workshop adoption table"></div>
<table id="workshop-table" aria-label="Workshop adoption metrics">
<thead><tr><th scope="col">Workshop</th><th scope="col">Usage events</th>
<th scope="col">Agent upvotes</th></tr></thead><tbody></tbody></table>
</section>
<p><a href="docs/metrics-admin-setup.html">Admin setup checklist</a>:
configure <code>METRICS_TOKEN</code> with <b>Administration: read</b> and authorize
organization SSO.</p>
<section id="file-download-ledger" aria-labelledby="file-ledger-heading">
<h2 id="file-ledger-heading">File downloads</h2>
<p>Every tracked repository file is represented, including every <code>SKILL.md</code>.
<code>raw.githubusercontent.com</code>, GitHub Pages, and direct GitHub downloads remain
unobservable. Complete coverage can report zero downloads; censored coverage keeps
downloads unavailable as <code>null</code>. Workshop file and source-bundle totals
reconcile from this ledger.</p>
<label for="file-ledger-search">Search
<input id="file-ledger-search" type="search" aria-controls="file-ledger-table"></label>
<label for="file-ledger-kind">Kind
<select id="file-ledger-kind" aria-controls="file-ledger-table">
<option value="all">All kinds</option><option value="skill">Skill (SKILL.md)</option>
</select></label>
<label for="file-ledger-sort">Sort
<select id="file-ledger-sort" aria-controls="file-ledger-table">
<option value="downloads">Downloads</option><option value="path">Path</option>
</select></label>
<p id="file-ledger-summary" role="status" aria-live="polite" aria-atomic="true"></p>
<table id="file-ledger-table" aria-label="Tracked file download metrics">
<thead><tr><th scope="col">Path</th><th scope="col">Kind</th>
<th scope="col">Mapped agent</th><th scope="col">Mapped workshop</th>
<th scope="col">Downloads</th><th scope="col">Status</th></tr></thead><tbody></tbody>
</table>
<nav aria-label="File download ledger pages">
<button id="file-ledger-prev" type="button" aria-controls="file-ledger-table">Previous</button>
<span id="file-ledger-page" role="status" aria-live="polite" aria-atomic="true">Page 1</span>
<button id="file-ledger-next" type="button" aria-controls="file-ledger-table">Next</button>
</nav>
</section>
{''.join(headings)}
</main>
<footer><a href="state/metrics.json">state/metrics.json</a>
<a href="https://github.com/microsoft/aibast-agents-library">Microsoft repository</a></footer>
<!-- aibast-workshop-feedback:v1 -->
<script>{script}</script>
</body></html>"""


def failure_messages(result, category):
    return "\n".join(result.failures.get(category, []))


def test_contract_is_deterministically_extracted_from_trusted_blob():
    assert build_contract() == CONTRACT


def test_minimal_valid_fixture_passes():
    result = audit_html(valid_fixture(), CONTRACT)
    assert result.passed, result.failures


def test_missing_target_fails_closed():
    html = valid_fixture().replace("$('paths').textContent = rows.length;", "void rows.length;")
    result = audit_html(html, CONTRACT)
    assert "renderPaths lost contracted targets: paths" in failure_messages(result, "mappings")


def test_missing_function_fails_closed():
    html = valid_fixture().replace("function renderSources()", "function renderSourceList()")
    result = audit_html(html, CONTRACT)
    assert "required function missing: renderSources" in failure_messages(result, "javascript")


def test_get_json_fetch_behavior_fails_closed():
    html = valid_fixture().replace(
        "const response = await fetch(p, {cache: 'no-store'});",
        "const response = {ok: true, json: () => ({})};",
    )
    result = audit_html(html, CONTRACT)
    assert "getJSON lost contracted data mappings" in failure_messages(result, "mappings")


def test_missing_source_caveat_fails_closed():
    html = valid_fixture().replace("treat every figure on this page as a floor", "treat these figures as estimates")
    result = audit_html(html, CONTRACT)
    assert "source caveat missing or altered" in failure_messages(result, "sources")


def test_altered_download_formula_fails_closed():
    html = valid_fixture().replace(
        "M.totals.downloads += (hits - M.totals.cdn_hits);",
        "M.totals.downloads = hits;",
    )
    result = audit_html(html, CONTRACT)
    assert "live download top-up formula changed" in failure_messages(result, "downloads")


def test_repository_stars_cannot_be_presented_as_upvotes():
    html = valid_fixture().replace(
        "<p>AIBAST distribution, engagement, and learning impact</p>",
        "<p>AIBAST distribution, engagement, and learning impact</p>"
        "<p>Community upvotes are public GitHub stars.</p>",
    )
    result = audit_html(html, CONTRACT)
    assert "repository-star upvote language/action is forbidden" in failure_messages(
        result, "upvotes"
    )


def test_repository_link_cannot_be_an_upvote_action():
    html = valid_fixture().replace(
        '<a href="library.html">Browse agents</a>',
        '<a id="upvote-github" class="upvote" '
        'href="https://github.com/microsoft/aibast-agents-library">'
        "Upvote on GitHub</a>",
    )
    result = audit_html(html, CONTRACT)
    assert "repository-star upvote language/action is forbidden" in failure_messages(
        result, "upvotes"
    )


def test_agent_upvotes_cannot_be_added_into_usage_events():
    html = valid_fixture().replace(
        "${num(row.usage_events)}",
        "${num(row.usage_events + row.agent_upvotes)}",
    )
    result = audit_html(html, CONTRACT)
    assert "never be added into workshop usage_events" in failure_messages(
        result, "workshops"
    )


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        (
            lambda html: html.replace(
                "const agentMetrics = Array.isArray(M.agent_metrics) ? M.agent_metrics : [];",
                "const agentMetrics = (M.leaderboards || {}).most_upvoted || [];",
            ),
            "guarded agent_metrics signal rows",
        ),
        (
            lambda html: html.replace(
                "metric: 'upvotes'",
                "metric: 'stars'",
            ),
            "Most upvoted agent board definition or upvote metric binding is missing",
        ),
    ],
)
def test_missing_most_upvoted_bindings_fail_closed(mutation, expected):
    result = audit_html(mutation(valid_fixture()), CONTRACT)
    assert expected in failure_messages(result, "upvotes")


@pytest.mark.parametrize(
    ("mutation", "category", "expected"),
    [
        (
            lambda html: html.replace(
                'id="workshop-summary"', 'id="workshop-summary-removed"'
            ),
            "workshops",
            "required workshop IDs missing: workshop-summary",
        ),
        (
            lambda html: html.replace(
                "function renderWorkshops()", "function renderWorkshopList()"
            ),
            "javascript",
            "required function missing: renderWorkshops",
        ),
        (
            lambda html: html.replace(
                "function renderWorkshopControls()",
                "function renderWorkshopSortControls()",
            ),
            "javascript",
            "required function missing: renderWorkshopControls",
        ),
    ],
)
def test_missing_workshop_id_or_function_fails_closed(
    mutation, category, expected
):
    result = audit_html(mutation(valid_fixture()), CONTRACT)
    assert expected in failure_messages(result, category)


def test_render_must_invoke_workshop_renderer():
    html = valid_fixture().replace(
        "  renderWorkshops();\n  renderChart();",
        "  renderChart();",
    )
    result = audit_html(html, CONTRACT)
    assert "render() must invoke renderWorkshops()" in failure_messages(
        result, "workshops"
    )


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        (
            lambda html: html.replace(
                "row.bundle_downloads", "row.bundle_download_total"
            ),
            "Workshop table row is not bound to bundle_downloads",
        ),
        (
            lambda html: html.replace(
                "solutions/${encodeURIComponent(row.slug)}/quest.html",
                "library.html#workshop/${encodeURIComponent(row.slug)}",
            ),
            "Workshop rows must link to solutions/<slug>/quest.html",
        ),
    ],
)
def test_missing_workshop_field_or_quest_link_fails_closed(mutation, expected):
    result = audit_html(mutation(valid_fixture()), CONTRACT)
    assert expected in failure_messages(result, "workshops")


def test_wrong_workshop_usage_terminology_fails_closed():
    html = valid_fixture().replace(
        "This is a floor and an event sum",
        "This estimates workshop adoption",
    )
    result = audit_html(html, CONTRACT)
    assert "floor and an event sum" in failure_messages(result, "workshops")


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        (
            lambda html: html.replace(
                "  { id: 'bundle_downloads', label: 'Bundle downloads' },\n",
                "",
            ),
            "workshop sort controls, labels, or order changed",
        ),
        (
            lambda html: html.replace(
                "const WORKSHOP_UPVOTE_SORT = { id: 'agent_upvotes', label: 'Agent upvotes' };",
                "const WORKSHOP_UPVOTE_SORT = { id: 'usage_events', label: 'Usage' };",
            ),
            "Agent upvotes workshop sort is missing",
        ),
    ],
)
def test_missing_workshop_sort_fails_closed(mutation, expected):
    html = mutation(valid_fixture())
    result = audit_html(html, CONTRACT)
    assert expected in failure_messages(result, "workshops")


def test_missing_admin_setup_fails_closed():
    html = valid_fixture().replace(
        "docs/metrics-admin-setup.html",
        "docs/metrics-help.html",
    )
    result = audit_html(html, CONTRACT)
    assert "Admin setup checklist" in failure_messages(result, "admin")


def test_live_top_up_must_not_mutate_per_workshop_rows():
    html = valid_fixture().replace(
        "  renderKPIs();\n}\nfunction render()",
        "  M.workshops.rows[0].file_downloads += hits;\n"
        "  renderKPIs();\n}\nfunction render()",
    )
    result = audit_html(html, CONTRACT)
    assert "must not mutate per-workshop rows" in failure_messages(
        result, "workshops"
    )


def test_old_schema_crash_prone_direct_access_fails_closed():
    html = valid_fixture().replace(
        "const workshopTotals = (M.workshops || {}).totals || {};",
        "const workshopTotals = M.workshops.totals;",
    )
    result = audit_html(html, CONTRACT)
    assert "must guard absent M.workshops/totals" in failure_messages(
        result, "workshops"
    )


@pytest.mark.parametrize(
    ("mutation", "category", "expected"),
    [
        (
            lambda html: html.replace(
                'id="file-ledger-table"', 'id="file-ledger-table-removed"'
            ),
            "file-ledger",
            "required file ledger IDs missing: file-ledger-table",
        ),
        (
            lambda html: html.replace(
                "function renderFileLedger(resetPage = false)",
                "function renderTrackedFiles(resetPage = false)",
            ),
            "javascript",
            "required function missing: renderFileLedger",
        ),
    ],
)
def test_missing_file_ledger_id_or_function_fails_closed(
    mutation, category, expected
):
    result = audit_html(mutation(valid_fixture()), CONTRACT)
    assert expected in failure_messages(result, category)


def test_missing_skill_filter_fails_closed():
    html = valid_fixture().replace(
        "kind === 'skill' ? 'Skill (SKILL.md)' : kind",
        "kind === 'documentation' ? 'Documentation' : kind",
    )
    result = audit_html(html, CONTRACT)
    assert "SKILL.md filter" in failure_messages(result, "file-ledger")


def test_censored_file_downloads_cannot_fabricate_zero():
    html = valid_fixture().replace(
        "${num(row.downloads)}",
        "${num(row.downloads ?? 0)}",
    )
    result = audit_html(html, CONTRACT)
    assert "never fabricated zero" in failure_messages(result, "file-ledger")


def test_missing_raw_download_caveat_fails_closed():
    html = valid_fixture().replace(
        "raw.githubusercontent.com",
        "a raw content host",
    )
    result = audit_html(html, CONTRACT)
    assert "raw.githubusercontent.com" in failure_messages(result, "file-ledger")


def test_live_top_up_must_not_mutate_file_ledger_rows():
    html = valid_fixture().replace(
        "  renderKPIs();\n}\nfunction render()",
        "  M.file_metrics.rows[0].downloads += hits;\n"
        "  renderKPIs();\n}\nfunction render()",
    )
    result = audit_html(html, CONTRACT)
    assert "must not mutate per-file rows" in failure_messages(
        result, "file-ledger"
    )


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        (
            lambda html: html.replace(
                "* { box-sizing: border-box; }",
                ":root { --bg: var(--cp-bg); }\n* { box-sizing: border-box; }",
            ),
            "legacy theme variable",
        ),
        (
            lambda html: html.replace(
                ".cards { display: grid;",
                ".bad { background: linear-gradient(var(--cp-bg), var(--cp-surface)); }\n.cards { display: grid;",
            ),
            "gradients are forbidden",
        ),
        (
            lambda html: html.replace(
                "function toggleTheme()",
                "const badSvg = '<rect fill=\"#fff\"></rect>';\nfunction toggleTheme()",
            ),
            "generated SVG/markup contains a hardcoded color literal",
        ),
        (
            lambda html: html.replace(
                "* { box-sizing: border-box; }",
                ".bad { color: #f7f4ef; }\n* { box-sizing: border-box; }",
            ),
            "hardcoded presentation color",
        ),
    ],
)
def test_old_tokens_gradients_and_svg_colors_fail(mutation, expected):
    result = audit_html(mutation(valid_fixture()), CONTRACT)
    assert expected in failure_messages(result, "theme")


def test_missing_dark_theme_fails_closed():
    html = valid_fixture().replace('html[data-theme="dark"]', 'html[data-theme="night"]')
    result = audit_html(html, CONTRACT)
    assert "dark theme block missing" in failure_messages(result, "theme")


def test_malformed_javascript_fails_closed():
    html = valid_fixture().replace(
        "function wireFeedback() {",
        "function broken(\nfunction wireFeedback() {",
    )
    result = audit_html(html, CONTRACT)
    assert "malformed" in failure_messages(result, "javascript")


def test_missing_feedback_wiring_fails_closed():
    html = (
        valid_fixture()
        .replace("aibast-workshop-feedback:v1", "feedback-disabled")
        .replace("aibast-workshop-feedback/1.0", "feedback-disabled/0")
    )
    result = audit_html(html, CONTRACT)
    assert "feedback marker/schema" in failure_messages(result, "feedback")


def test_theme_toggle_must_change_document_theme():
    html = valid_fixture().replace(
        "document.documentElement.setAttribute('data-theme', next);",
        "void next;",
    )
    result = audit_html(html, CONTRACT)
    assert "theme toggle is not wired" in failure_messages(result, "navigation")


@pytest.mark.parametrize(
    "mutation",
    [
        lambda html: html.replace('role="tablist"', ""),
        lambda html: html.replace('aria-controls="kpis stamp-mode"', "").replace(
            'aria-label="Refresh live metrics"', ""
        ),
        lambda html: html.replace(":focus-visible", ":focus"),
        lambda html: html.replace('role="img"', ""),
    ],
)
def test_missing_accessibility_controls_fail_closed(mutation):
    result = audit_html(mutation(valid_fixture()), CONTRACT)
    assert "accessibility" in result.failures


def test_current_metrics_page_passes_post_migration_gate():
    result = audit_html(DEFAULT_PAGE.read_text(encoding="utf-8"), CONTRACT)
    assert result.passed, result.failures
