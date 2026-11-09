/* AIBAST Agents Library — the one script. Gallery search and filters (state in the URL),
   solution tabs, copy buttons, the download acknowledgement, contributor directory search.
   No framework, no network calls. */
(function () {
  "use strict";
  var $ = function (sel, root) { return (root || document).querySelector(sel); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };

  /* ---------------- gallery ---------------- */
  var grid = $("#grid");
  if (grid && $("#q")) {
    var cards = $$(".card", grid);
    var q = $("#q");
    var count = $("#count");
    var empty = $("#empty");
    var applied = $("#applied");
    var dialog = $("#filters");
    var filterCount = $("#filter-count");
    var total = cards.length;
    var state = { q: "", industry: [], category: [], tag: [], contains: [] };
    var FACETS = ["industry", "category", "tag", "contains"];
    var ANY = { industry: true, category: true, tag: false, contains: false };
    var ATTR = { industry: "industries", category: "category", tag: "tags", contains: "contains" };

    function readUrl() {
      var p = new URLSearchParams(location.search);
      state.q = p.get("q") || "";
      FACETS.forEach(function (f) { state[f] = p.getAll(f).filter(Boolean); });
    }
    function writeUrl() {
      var p = new URLSearchParams();
      if (state.q) p.set("q", state.q);
      FACETS.forEach(function (f) { state[f].forEach(function (v) { p.append(f, v); }); });
      var qs = p.toString();
      history.replaceState(null, "", location.pathname + (qs ? "?" + qs : "") + location.hash);
    }
    function values(card, facet) {
      var raw = card.getAttribute("data-" + ATTR[facet]) || "";
      return raw ? raw.split("|") : [];
    }
    function matches(card) {
      var words = state.q.toLowerCase().split(/\s+/).filter(Boolean);
      var blob = card.getAttribute("data-search") || "";
      if (!words.every(function (w) { return blob.indexOf(w) !== -1; })) return false;
      return FACETS.every(function (f) {
        if (!state[f].length) return true;
        var have = values(card, f);
        return ANY[f] ? state[f].some(function (v) { return have.indexOf(v) !== -1; })
                      : state[f].every(function (v) { return have.indexOf(v) !== -1; });
      });
    }
    function render() {
      var shown = 0;
      cards.forEach(function (c) { var ok = matches(c); c.hidden = !ok; if (ok) shown++; });
      if (count) count.textContent = shown + " of " + total;
      if (empty) empty.hidden = shown !== 0;
      $$(".chip[data-industry]").forEach(function (b) {
        b.setAttribute("aria-pressed", state.industry.indexOf(b.getAttribute("data-industry")) !== -1 ? "true" : "false");
      });
      var more = $("#more-industries");
      if (more) more.value = state.industry.length === 1 && $$('option', more).some(function (o) { return o.value === state.industry[0]; }) ? state.industry[0] : "";
      var n = FACETS.reduce(function (s, f) { return s + state[f].length; }, 0);
      if (filterCount) { filterCount.hidden = !n; filterCount.textContent = n; }
      if (applied) {
        applied.innerHTML = "";
        FACETS.forEach(function (f) {
          state[f].forEach(function (v) {
            var b = document.createElement("button");
            b.type = "button"; b.textContent = v; b.setAttribute("aria-label", "Remove filter " + v);
            b.onclick = function () { state[f] = state[f].filter(function (x) { return x !== v; }); sync(); };
            applied.appendChild(b);
          });
        });
        applied.hidden = !n;
      }
      if (q.value !== state.q) q.value = state.q;
    }
    function sync() { writeUrl(); render(); }

    q.addEventListener("input", function () { state.q = q.value; sync(); });
    $$(".chip[data-industry]").forEach(function (b) {
      b.addEventListener("click", function () {
        var v = b.getAttribute("data-industry");
        state.industry = state.industry.indexOf(v) !== -1 ? [] : [v];
        sync();
      });
    });
    var more = $("#more-industries");
    if (more) more.addEventListener("change", function () { state.industry = more.value ? [more.value] : []; sync(); });

    if (dialog && typeof dialog.showModal === "function") {
      var open = $("#open-filters");
      function loadDraft() {
        FACETS.forEach(function (f) {
          $$('input[name="' + f + '"]', dialog).forEach(function (i) { i.checked = state[f].indexOf(i.value) !== -1; });
        });
      }
      open.addEventListener("click", function () { loadDraft(); dialog.showModal(); });
      $("[data-close]", dialog).addEventListener("click", function () { dialog.close(); });
      $("[data-clear]", dialog).addEventListener("click", function () { $$("input[type=checkbox]", dialog).forEach(function (i) { i.checked = false; }); });
      $("[data-apply]", dialog).addEventListener("click", function (e) {
        e.preventDefault();
        FACETS.forEach(function (f) {
          state[f] = $$('input[name="' + f + '"]:checked', dialog).map(function (i) { return i.value; });
        });
        dialog.close(); sync();
      });
      var picker = $("[data-picker]", dialog);
      if (picker) picker.addEventListener("input", function () {
        var w = picker.value.toLowerCase();
        $$('input[name="tag"]', dialog).forEach(function (i) { i.parentNode.hidden = w && i.value.indexOf(w) === -1; });
      });
    } else if ($("#open-filters")) {
      $("#open-filters").hidden = true;
    }
    readUrl(); render();
  }

  /* ---------------- solution tabs ---------------- */
  var tablist = $(".tabs[role=tablist]");
  if (tablist) {
    var tabs = $$(".tab", tablist);
    function show(tab) {
      tabs.forEach(function (t) {
        var on = t === tab;
        t.setAttribute("aria-selected", on ? "true" : "false");
        t.tabIndex = on ? 0 : -1;
        var panel = document.getElementById(t.getAttribute("aria-controls"));
        if (panel) panel.hidden = !on;
      });
      if (tab.id !== tabs[0].id) history.replaceState(null, "", "#" + tab.id.replace("tab-", ""));
      else history.replaceState(null, "", location.pathname + location.search);
    }
    tabs.forEach(function (t, i) {
      t.addEventListener("click", function () { show(t); });
      t.addEventListener("keydown", function (e) {
        var j = e.key === "ArrowRight" ? i + 1 : e.key === "ArrowLeft" ? i - 1 : -1;
        if (j < 0 || j >= tabs.length) return;
        e.preventDefault(); tabs[j].focus(); show(tabs[j]);
      });
    });
    var wanted = location.hash && document.getElementById("tab-" + location.hash.slice(1));
    if (wanted) show(wanted);
  }

  /* ---------------- copy buttons ---------------- */
  $$("[data-copy]").forEach(function (b) {
    b.addEventListener("click", function () {
      var code = b.parentNode.querySelector("code");
      if (!code || !navigator.clipboard) return;
      navigator.clipboard.writeText(code.textContent).then(function () {
        var was = b.textContent; b.textContent = "Copied"; setTimeout(function () { b.textContent = was; }, 1400);
      });
    });
  });

  /* ---------------- download acknowledgement ---------------- */
  var ack = $("[data-ack]");
  var dl = $("[data-download]");
  if (ack && dl) {
    var update = function () { dl.setAttribute("aria-disabled", ack.checked ? "false" : "true"); };
    ack.addEventListener("change", update); update();
  }

  /* ---------------- contributor directory ---------------- */
  var dir = $("#directory");
  var dq = $("#dir-q");
  if (dir && dq) {
    dq.addEventListener("input", function () {
      var w = dq.value.toLowerCase();
      $$("[data-search]", dir).forEach(function (li) { li.hidden = w && li.getAttribute("data-search").indexOf(w) === -1; });
    });
  }
})();

/* Section pages: source-relative links and explicit, non-evaluating event adapters. */
function sectionRuntime(source) {
  "use strict";
  var base = document.body.getAttribute("data-base");
  var root = new URL(base || "./", location.href);
  var routes = {
    "index.html": "", "library.html": "", "academy.html": "learn/academy/",
    "docs/tutorial.html": "learn/tutorial/", "docs/rapp-guide.html": "learn/guide/",
    "docs/installer.html": "install/", "why.html": "why/", "metrics.html": "metrics/",
    "achievements.html": "achievements/", "front-page.html": "about/",
    "blog.html": "blog/", "release-notes.html": "releases/", "request-info.html": "request/",
    "community-agents.html": "community/", "partner-standards.html": "partners/"
  };
  function url(value) {
    if (typeof value !== "string" || !value || /^[a-z][a-z0-9+.-]*:|^\/\/|^#/i.test(value)) return value;
    if (base && value.startsWith(base)) return value;
    var resolved = new URL(value, new URL(source, root));
    var relative = decodeURIComponent(resolved.pathname.slice(root.pathname.length));
    if (Object.prototype.hasOwnProperty.call(routes, relative)) {
      return new URL(routes[relative] + resolved.search + resolved.hash, root).href;
    }
    return resolved.href;
  }
  function rewrite(node) {
    if (node.nodeType !== 1) return;
    var links = [node].concat(Array.from(node.querySelectorAll("[href], [src]")));
    links.forEach(function (element) {
      ["href", "src"].forEach(function (attr) {
        var value = element.getAttribute(attr);
        if (value) element.setAttribute(attr, url(value));
      });
    });
  }
  var content = document.querySelector(".section-content");
  new MutationObserver(function (records) {
    records.forEach(function (record) { record.addedNodes.forEach(rewrite); });
  }).observe(content, { childList: true, subtree: true });
  function bind(handlers) {
    ["click", "change"].forEach(function (type) {
      content.querySelectorAll("[data-port-" + type + "]").forEach(function (element) {
        var expression = element.getAttribute("data-port-" + type);
        element.addEventListener(type, function (event) {
          if (expression === "event.stopPropagation()") { event.stopPropagation(); return; }
          if (expression.startsWith("var b=this.nextElementSibling;")) {
            var sibling = element.nextElementSibling;
            var show = sibling.style.display === "none";
            sibling.style.display = show ? "block" : "none";
            element.textContent = (show ? "Collapse" : "Expand") + " advanced manual steps";
            return;
          }
          if (expression === "window.open('http://localhost:7071','_blank')") {
            window.open("http://localhost:7071", "_blank", "noopener"); return;
          }
          var call = expression.replace(/^event.stopPropagation\(\);\s*/, "");
          if (call !== expression) event.stopPropagation();
          var match = /^(\w+)\((.*)\)$/.exec(call);
          if (!match || typeof handlers[match[1]] !== "function") {
            throw new Error("Unsupported section action: " + expression);
          }
          var args = match[2].trim() ? match[2].split(/\s*,\s*/).map(function (arg) {
            if (arg === "event") return event;
            if (arg === "this") return element;
            if (arg === "this.parentElement.nextElementSibling") return element.parentElement.nextElementSibling;
            if (arg === "false") return false;
            if (arg === "true") return true;
            if (/^\d+$/.test(arg)) return Number(arg);
            if (/^'[^']*'$|^"[^"]*"$/.test(arg)) return arg.slice(1, -1);
            throw new Error("Unsupported section argument: " + arg);
          }) : [];
          handlers[match[1]].apply(null, args);
        });
      });
    });
  }
  return { url: url, bind: bind, fetch: function (input, options) { return window.fetch(url(input), options); } };
}

/* Learn: the complete catalog is already in HTML; filters never need a request. */
if (document.body.dataset.page === "learn-academy") {
  (function () {
    "use strict";
    var search = document.getElementById("course-search");
    var path = document.getElementById("course-path");
    var courses = Array.from(document.querySelectorAll("[data-course]"));
    var query = new URLSearchParams(location.search);
    search.value = query.get("q") || "";
    path.value = query.get("path") || "";
    function filter() {
      var words = search.value.toLowerCase().split(/\s+/).filter(Boolean);
      var shown = 0;
      courses.forEach(function (course) {
        var matches = words.every(function (word) { return course.dataset.search.includes(word); })
          && (!path.value || course.dataset.paths.split("|").includes(path.value));
        course.hidden = !matches;
        if (matches) shown++;
      });
      document.getElementById("course-count").textContent = shown + " of " + courses.length + " courses";
      document.getElementById("course-empty").hidden = shown !== 0;
      var params = new URLSearchParams();
      if (search.value) params.set("q", search.value);
      if (path.value) params.set("path", path.value);
      history.replaceState(null, "", location.pathname + (params.size ? "?" + params : "") + location.hash);
    }
    search.addEventListener("input", filter);
    path.addEventListener("change", filter);
    filter();
    var notice = document.getElementById("academy-progress");
    try {
      var profile = JSON.parse(localStorage.getItem("aibast:achievement-profile:v1") || "{}");
      var workshops = profile && profile.workshops;
      var started = workshops && typeof workshops === "object" && !Array.isArray(workshops)
        ? Object.keys(workshops).filter(function (slug) {
          return courses.some(function (course) { return course.dataset.course === slug; });
        }).length : 0;
      notice.textContent = started + " catalog courses have saved local progress on this device.";
    } catch (error) {
      notice.textContent = "Local progress could not be read. Use Achievements to review or restore your profile.";
      console.warn("Academy local progress unavailable", error);
    }
  })();
}

/* install: content behavior ported from docs/installer.html; the shell owns navigation and theme. */
if (document.body.dataset.page === 'install') {
(function () {
"use strict";
const runtime = sectionRuntime('docs/installer.html');
const fetch = runtime.fetch;

  // ── Install widget ──
  const publishedBase = (
    location.protocol === 'https:' && location.hostname.endsWith('.github.io')
      ? new URL('..', location.href).href
      : 'https://microsoft.github.io/aibast-agents-library/'
  );
  function buildInstallCommands(hostname, base) {
    // The published install.sh / install.ps1 already carry the repository and
    // ref for the host that serves them (the staging ring renders its own
    // copies), so the one-liner is identical on every host.
    const pagesHost = /^([a-z0-9](?:[a-z0-9-]{0,37}[a-z0-9])?)\.github\.io$/i.exec(hostname);
    const owner = pagesHost ? pagesHost[1].toLowerCase() : 'microsoft';
    const staging = owner !== 'microsoft';
    const ref = staging ? 'staging' : 'main';
    const repoUrl = `https://github.com/${owner}/aibast-agents-library.git`;
    return {
      staging,
      owner,
      ref,
      bash: `curl -fsSL ${base}install.sh | bash`,
      windows: `irm ${base}install.ps1 | iex`,
      macManual: `git clone --branch ${ref} ${repoUrl} ~/.brainstem/src && cd ~/.brainstem/src/rapp_brainstem && pip3 install -r requirements.txt && ./start.sh`,
      windowsManual: `git clone --branch ${ref} ${repoUrl} %USERPROFILE%\\.brainstem\\src && cd %USERPROFILE%\\.brainstem\\src\\rapp_brainstem && pip install -r requirements.txt && python brainstem.py`
    };
  }
  const installCommands = buildInstallCommands(location.hostname, publishedBase);
  const installs = {
    'macOS/Linux': {
      'one-liner': {
        comment: '# Your local learning platform. Installs everything.',
        cmd: installCommands.bash,
        hint: 'Works on macOS & Linux. Auto-installs Python 3.11 if missing.'
      },
      'manual': {
        comment: '# Clone, install deps, done.',
        cmd: installCommands.macManual,
        hint: 'Requires Python 3.11+ and Git already installed.'
      }
    },
    'Windows': {
      'one-liner': {
        comment: '# Your local learning platform. Factory Windows 11 ready, installs via winget.',
        cmd: installCommands.windows,
        hint: 'Run in PowerShell. Auto-installs Python, Git & GitHub CLI via winget.'
      },
      'manual': {
        comment: '# Clone, install deps, done.',
        cmd: installCommands.windowsManual,
        hint: 'Requires Python 3.11+ and Git already installed.'
      }
    }
  };

  let currentOS = navigator.platform.includes('Win') ? 'Windows' : 'macOS/Linux';
  let currentTab = 'one-liner';

  function buildInstallerDownloads(commands) {
    if (!commands.staging) {
      return {
        'macOS/Linux': {
          href: '../install.command',
          filename: 'install.command',
          label: '↓ Download installer (.command)'
        },
        'Windows': {
          href: '../install.cmd',
          filename: 'install.cmd',
          label: '↓ Download installer (.cmd)'
        }
      };
    }
    const macPayload = `#!/bin/bash\n${commands.bash}\n`;
    const windowsPayload = [
      '@echo off',
      'powershell -NoProfile -ExecutionPolicy Bypass -Command "' + commands.windows + '"',
      'if %ERRORLEVEL% neq 0 exit /b 1',
      ''
    ].join('\r\n');
    return {
      'macOS/Linux': {
        href: URL.createObjectURL(new Blob([macPayload], { type: 'application/x-sh' })),
        filename: 'install-staging.command',
        label: '↓ Download staging installer (.command)'
      },
      'Windows': {
        href: URL.createObjectURL(new Blob([windowsPayload], { type: 'application/octet-stream' })),
        filename: 'install-staging.cmd',
        label: '↓ Download staging installer (.cmd)'
      }
    };
  }
  const downloads = buildInstallerDownloads(installCommands);

  function renderInstall() {
    const data = installs[currentOS][currentTab];
    document.getElementById('brainstem-cmd').textContent =
      installs['macOS/Linux']['one-liner'].cmd;
    document.getElementById('brainstem-win-cmd').textContent =
      installs.Windows['one-liner'].cmd;
    document.getElementById('os-label').textContent = currentOS;
    document.getElementById('install-comment').textContent = data.comment;
    document.getElementById('install-cmd').textContent = data.cmd;
    document.getElementById('install-hint').innerHTML = data.hint;
    document.getElementById('copy-icon').textContent = '⧉';
    const dlDiv = document.getElementById('install-download');
    if (currentTab === 'one-liner') {
      const dl = downloads[currentOS];
      const link = document.getElementById('download-link');
      link.href = dl.href;
      link.download = dl.filename;
      link.textContent = dl.label;
      dlDiv.style.display = '';
    } else {
      dlDiv.style.display = 'none';
    }
  }

  function flipOS() {
    currentOS = currentOS === 'macOS/Linux' ? 'Windows' : 'macOS/Linux';
    renderInstall();
  }

  function switchTab(btn) {
    document.querySelectorAll('.install-tab').forEach(t => t.classList.remove('active'));
    btn.classList.add('active');
    currentTab = btn.dataset.tab;
    renderInstall();
  }

  function copyInstall(el) {
    const text = document.getElementById('install-cmd').textContent;
    navigator.clipboard.writeText(text);
    document.getElementById('copy-icon').textContent = '✓';
    el.classList.add('copied');
    setTimeout(() => {
      document.getElementById('copy-icon').textContent = '⧉';
      el.classList.remove('copied');
    }, 2000);
  }

  renderInstall();

  // VS Code prompt: one line that names this site's own copy of the guide (the skill holds every step)
  const vscodePromptEl = document.getElementById('vscode-prompt');
  vscodePromptEl.textContent = vscodePromptEl.textContent.replace('https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/docs/start/skill.md', publishedBase + 'docs/start/skill.md');
  // what you'll see: plays once when the card scrolls into view; honours reduced motion
  let vsdRun = 0;
  const vsdSleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const vsdIcons = {
    run: '<svg viewBox="0 0 24 24"><path d="M4 5h16v14H4z" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="m7 9 3 2.5L7 14M12 15h5" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>',
    check: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8.5" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="m8 12 3 3 5-6" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>',
    read: '<svg viewBox="0 0 24 24"><path d="M3 5h7a3 3 0 0 1 3 3v12a2 2 0 0 0-2-2H3zM21 5h-7a3 3 0 0 0-3 3v12a2 2 0 0 1 2-2h8z" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>',
    open: '<svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="16" rx="2" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M3 9h18" stroke="currentColor" stroke-width="1.6"/></svg>'
  };
  async function vsdSay(who, html, typeMs) {
    const chat = document.getElementById('vsd-chat');
    const d = document.createElement('div'); d.className = 'msg ' + who; chat.appendChild(d);
    await vsdSleep(30); d.classList.add('show');
    if (typeMs) { d.classList.add('typing'); for (let i = 1; i <= html.length; i++) { d.textContent = html.slice(0, i); await vsdSleep(typeMs); } d.classList.remove('typing'); }
    else { d.innerHTML = html; }
    return d;
  }
  async function vsdStep(icon, html, wait) {
    await vsdSay('vsd-step', vsdIcons[icon] + '<span>' + html + '</span>');
    await vsdSleep(wait);
  }
  async function vsdPlay() {
    const me = ++vsdRun; const ok = () => me === vsdRun;
    const chat = document.getElementById('vsd-chat'); chat.querySelectorAll('.msg').forEach((m) => m.remove());
    document.getElementById('vsd-editor').classList.remove('browser');
    const cap = document.getElementById('vsd-caption'); cap.textContent = 'You paste one line. Copilot does the rest while you watch.';
    const fast = matchMedia('(prefers-reduced-motion: reduce)').matches;
    const w = (ms) => (fast ? 150 : ms);
    await vsdSay('you', document.getElementById('vscode-prompt').textContent, fast ? 0 : 10); if (!ok()) return;
    await vsdSleep(w(600));
    await vsdStep('read', 'Read <code>skill.md</code>', w(900)); if (!ok()) return;
    await vsdStep('run', 'Ran <code>install.sh</code> in the terminal', w(1400)); if (!ok()) return;
    await vsdStep('check', 'Checked <code>localhost:7071/health</code> <b>ok</b>', w(900)); if (!ok()) return;
    await vsdStep('read', 'Read <code>agents/</code>, 4 helpers loaded', w(900)); if (!ok()) return;
    await vsdStep('open', 'Opened <code>localhost:7071</code> in Simple Browser', w(300)); if (!ok()) return;
    document.getElementById('vsd-editor').classList.add('browser'); await vsdSleep(w(500)); if (!ok()) return;
    await vsdSay('ai', 'Your Brainstem is running beside this chat. Say hello to it whenever you like, and I will show you your first trick.'); if (!ok()) return;
    cap.textContent = 'About 20 minutes, start to finish. You only talk.';
  }
  new IntersectionObserver((entries, obs) => { if (entries[0].isIntersecting) { obs.disconnect(); vsdPlay(); } }, { threshold: 0.4 }).observe(document.getElementById('vscode-demo'));
  function copyVscodePrompt() {
    navigator.clipboard.writeText(vscodePromptEl.textContent);
    const btn = document.getElementById('vscode-copy');
    btn.textContent = 'Copied';
    setTimeout(() => { btn.textContent = 'Copy prompt'; }, 2000);
  }

  // ── Tier commands ──

  function copyPrompt(e, btn) {
    e.stopPropagation();
    const text = btn.closest('.copilot-chat').querySelector('.cc-prompt').textContent.trim();
    navigator.clipboard.writeText(text);
    const was = btn.textContent;
    btn.textContent = 'Copied. Now paste it into Copilot Chat';
    btn.classList.add('copied');
    setTimeout(() => { btn.textContent = was; btn.classList.remove('copied'); }, 2500);
  }
  function copyCmd(e, el) {
    e.stopPropagation();
    const text = el.textContent.trim();
    navigator.clipboard.writeText(text);
    el.classList.add('copied');
    setTimeout(() => el.classList.remove('copied'), 1500);
  }

  function toggleTier(e, el) {
    if (e.target.closest('.cmd') || e.target.closest('a')) return;
    el.classList.toggle('open');
    if (el.id && el.classList.contains('open')) {
      history.replaceState(null, '', '#' + el.id);
    } else if (location.hash) {
      history.replaceState(null, '', location.pathname);
    }
  }

  async function checkBrainstem() {
    const dot = document.getElementById('dot');
    const label = document.getElementById('status-label');
    const btn = document.getElementById('open-btn');
    try {
      const r = await fetch('http://localhost:7071/health/public', { signal: AbortSignal.timeout(3000) });
      const d = await r.json();
      if (d.status === 'ok') {
        dot.className = 'dot online';
        label.textContent = `Brainstem running · v${d.version}`;
        btn.disabled = false;
      } else {
        dot.className = 'dot offline';
        label.textContent = 'Brainstem running but not authenticated — visit localhost:7071';
        btn.disabled = false;
      }
    } catch {
      dot.className = 'dot offline';
      label.textContent = 'Brainstem not detected — install and run brainstem to get started';
      btn.disabled = true;
    }
  }
  checkBrainstem();
  setInterval(checkBrainstem, 5000);

  // ── Deep link: #hippocampus opens Tier 2, collapses others ──
  function applyHash() {
    const hash = location.hash.replace('#', '');
    if (!hash) return;
    const target = document.getElementById(hash);
    if (!target || !target.classList.contains('tier')) return;
    document.querySelectorAll('.tier').forEach(t => t.classList.remove('open'));
    target.classList.add('open');
    setTimeout(() => target.scrollIntoView({ behavior: 'smooth', block: 'start' }), 100);
  }
  applyHash();
  window.addEventListener('hashchange', applyHash);

runtime.bind({copyVscodePrompt,vsdPlay,switchTab,flipOS,copyInstall,toggleTier,copyPrompt,copyCmd});

})();
}

/* learn-tutorial: content behavior ported from docs/tutorial.html; the shell owns navigation and theme. */
if (document.body.dataset.page === 'learn-tutorial') {
(function () {
"use strict";
const runtime = sectionRuntime('docs/tutorial.html');
const fetch = runtime.fetch;

function showPlatform(event, platform) {
    document.querySelectorAll('.platform-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.platform-tabs button').forEach(el => el.classList.remove('active'));
    document.getElementById(platform).classList.add('active');
    event.target.classList.add('active');
}

function copyCode(btn) {
    const code = btn.parentElement.textContent.replace('Copy', '').trim();
    navigator.clipboard.writeText(code);
    btn.textContent = 'Copied!';
    setTimeout(() => btn.textContent = 'Copy', 2000);
}

runtime.bind({showPlatform,copyCode});

})();
}

/* learn-guide: content behavior ported from docs/rapp-guide.html; the shell owns navigation and theme. */
if (document.body.dataset.page === 'learn-guide') {
(function () {
"use strict";
const runtime = sectionRuntime('docs/rapp-guide.html');
const fetch = runtime.fetch;
document.body.classList.add("js-enabled");

        const feedbackSchema = "aibast-workshop-feedback/1.0";
        let currentSectionIndex = 0;
        const sections = [
            'overview', 'architecture', 'principles',
            'step1', 'step2', 'step3', 'step4', 'step5', 'step6', 'step7',
            'step8', 'step9', 'step10', 'step11', 'step12', 'step13', 'step14',
            'team-setup', 'scaling', 'roadmap', 'reference', 'tools'
        ];

        function prefersReducedMotion() {
            return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        }

        function announceStatus(message) {
            const status = document.getElementById('liveStatus');
            if (!status) return;
            status.textContent = '';
            window.setTimeout(() => {
                status.textContent = message;
            }, 20);
            window.setTimeout(() => {
                if (status.textContent === message) status.textContent = '';
            }, 3000);
        }

        function updateReportIssueLink(sectionId = sections[currentSectionIndex]) {
            const reportLink = document.getElementById('reportIssue');
            if (!reportLink) return;
            const pageUrl = window.location.href.split('#')[0];
            const issueUrl = new URL('https://github.com/microsoft/aibast-agents-library/issues/new');
            issueUrl.searchParams.set('title', `[Production Guide] Feedback on ${sectionId}`);
            issueUrl.searchParams.set(
                'body',
                `<!-- aibast-workshop-feedback:v1 -->\nFeedback schema: ${feedbackSchema}\nPage: ${pageUrl}\nSection: ${sectionId}\n\nWhat should be improved?\n`
            );
            reportLink.href = issueUrl.toString();
        }

        function updateNavigationState() {
            document.querySelectorAll('.nav-controls').forEach(control => {
                const buttons = control.querySelectorAll('.nav-btn');
                if (buttons.length >= 2) {
                    buttons[0].disabled = currentSectionIndex === 0;
                    buttons[1].disabled = currentSectionIndex === sections.length - 1;
                }
            });
        }

        function closeMobileSidebar({ restoreFocus = false } = {}) {
            if (!window.matchMedia('(max-width: 64rem)').matches) return;
            const sidebar = document.getElementById('sidebar');
            const wasOpen = sidebar.classList.contains('visible');
            if (!wasOpen) return;
            const scrim = document.getElementById('sidebarScrim');
            const menuButton = document.getElementById('menuButton');
            sidebar.classList.remove('visible');
            sidebar.setAttribute('aria-hidden', 'true');
            sidebar.inert = true;
            scrim.hidden = true;
            menuButton.setAttribute('aria-expanded', 'false');
            document.body.classList.remove('sidebar-open');
            setMobileBackgroundInert(false);
            if (restoreFocus) menuButton.focus();
        }

        function setMobileBackgroundInert(inert) {
            const targets = [
                document.getElementById('mainContent'),
                document.querySelector('.feedback-notice'),
                document.querySelector('.topbar-nav'),
                document.querySelector('.brand'),
                document.getElementById('reportIssue'),
                document.getElementById('themeToggle')
            ];
            targets.forEach(target => {
                if (target) target.inert = inert;
            });
        }

        function navigateToSection(sectionId, { historyMode = 'push' } = {}) {
            const sectionIndex = sections.indexOf(sectionId);
            if (sectionIndex === -1) return;
            const destination = document.getElementById(sectionId);
            const fromSidebar = Boolean(document.activeElement?.closest('#sidebar'));
            currentSectionIndex = sectionIndex;

            document.querySelectorAll('.content-section').forEach(section => {
                section.classList.toggle('active', section.id === sectionId);
            });

            document.querySelectorAll('#sidebar .nav-item').forEach(item => {
                const active = item.getAttribute('href') === `#${sectionId}`;
                item.classList.toggle('active', active);
                if (active) item.setAttribute('aria-current', 'page');
                else item.removeAttribute('aria-current');
            });

            if (window.location.hash !== `#${sectionId}`) {
                if (historyMode === 'push') {
                    history.pushState(null, '', `#${sectionId}`);
                } else if (historyMode === 'replace') {
                    history.replaceState(null, '', `#${sectionId}`);
                }
            }

            updateProgress();
            updateNavigationState();
            updateReportIssueLink(sectionId);
            closeMobileSidebar();
            window.scrollTo({ top: 0, behavior: prefersReducedMotion() ? 'auto' : 'smooth' });
            if (fromSidebar) {
                const heading = destination?.querySelector('.section-title, h1, h2');
                if (heading) {
                    heading.setAttribute('tabindex', '-1');
                    window.requestAnimationFrame(() => heading.focus());
                }
            }
        }

        function nextSection() {
            if (currentSectionIndex < sections.length - 1) {
                navigateToSection(sections[currentSectionIndex + 1]);
            }
        }

        function previousSection() {
            if (currentSectionIndex > 0) {
                navigateToSection(sections[currentSectionIndex - 1]);
            }
        }

        function updateProgress() {
            const progress = ((currentSectionIndex + 1) / sections.length) * 100;
            document.querySelectorAll('.progress-fill').forEach(fill => {
                fill.style.width = `${progress}%`;
            });
            document.querySelectorAll('[role="progressbar"]').forEach(bar => {
                bar.setAttribute('aria-valuenow', String(Math.round(progress)));
            });
            document.querySelectorAll('.progress-text').forEach(text => {
                text.textContent = `${Math.round(progress)}%`;
            });
        }

        function toggleSidebar(forceOpen) {
            const sidebar = document.getElementById('sidebar');
            const mainContent = document.getElementById('mainContent');
            const notice = document.querySelector('.feedback-notice');
            const scrim = document.getElementById('sidebarScrim');
            const menuButton = document.getElementById('menuButton');
            const mobile = window.matchMedia('(max-width: 64rem)').matches;

            if (mobile) {
                const shouldOpen = typeof forceOpen === 'boolean' ? forceOpen : !sidebar.classList.contains('visible');
                sidebar.classList.toggle('visible', shouldOpen);
                sidebar.setAttribute('aria-hidden', String(!shouldOpen));
                sidebar.inert = !shouldOpen;
                scrim.hidden = !shouldOpen;
                menuButton.setAttribute('aria-expanded', String(shouldOpen));
                document.body.classList.toggle('sidebar-open', shouldOpen);
                setMobileBackgroundInert(shouldOpen);
                if (shouldOpen) sidebar.focus();
                return;
            }

            const shouldHide = typeof forceOpen === 'boolean' ? !forceOpen : !sidebar.classList.contains('hidden');
            sidebar.classList.toggle('hidden', shouldHide);
            sidebar.setAttribute('aria-hidden', String(shouldHide));
            sidebar.inert = shouldHide;
            mainContent.classList.toggle('expanded', shouldHide);
            if (notice) notice.classList.toggle('expanded', shouldHide);
            menuButton.setAttribute('aria-expanded', String(!shouldHide));
        }

        function syncSidebarForViewport() {
            const sidebar = document.getElementById('sidebar');
            const mainContent = document.getElementById('mainContent');
            const notice = document.querySelector('.feedback-notice');
            const scrim = document.getElementById('sidebarScrim');
            const menuButton = document.getElementById('menuButton');
            const mobile = window.matchMedia('(max-width: 64rem)').matches;

            sidebar.classList.remove('hidden', 'visible');
            mainContent.classList.remove('expanded');
            if (notice) notice.classList.remove('expanded');
            scrim.hidden = true;
            document.body.classList.remove('sidebar-open');
            setMobileBackgroundInert(false);
            sidebar.setAttribute('aria-hidden', String(mobile));
            sidebar.inert = mobile;
            menuButton.setAttribute('aria-expanded', String(!mobile));
        }

        function fallbackCopy(text) {
            const helper = document.createElement('textarea');
            helper.className = 'copy-helper';
            helper.value = text;
            helper.setAttribute('readonly', '');
            document.body.appendChild(helper);
            helper.select();
            const copied = document.execCommand('copy');
            helper.remove();
            if (!copied) throw new Error('Copy command was unavailable');
        }

        async function copyCode(elementOrButton) {
            let codeBlock;
            if (elementOrButton.tagName === 'PRE') {
                codeBlock = elementOrButton;
            } else if (elementOrButton.tagName === 'BUTTON') {
                codeBlock = elementOrButton.closest('.code-block').querySelector('pre');
            } else {
                codeBlock = elementOrButton;
            }

            try {
                if (navigator.clipboard && window.isSecureContext) {
                    await navigator.clipboard.writeText(codeBlock.textContent);
                } else {
                    fallbackCopy(codeBlock.textContent);
                }
                if (elementOrButton.tagName === 'BUTTON') {
                    const originalLabel = elementOrButton.textContent;
                    elementOrButton.textContent = 'Copied!';
                    window.setTimeout(() => {
                        elementOrButton.textContent = originalLabel;
                    }, 2000);
                }
                announceStatus('Copied to clipboard.');
            } catch (error) {
                console.error('Failed to copy:', error);
                announceStatus('Copy failed. Select the code and copy it manually.');
            }
        }

        function toggleFallback(fallbackId) {
            const fallbackElement = document.getElementById(fallbackId);
            const toggle = document.querySelector(`[data-fallback-toggle][aria-controls="${fallbackId}"]`);
            if (!fallbackElement || !toggle) return;
            const expanded = fallbackElement.hidden;
            fallbackElement.hidden = !expanded;
            toggle.setAttribute('aria-expanded', String(expanded));
            toggle.textContent = toggle.textContent.replace(
                expanded ? 'Click to expand' : 'Click to collapse',
                expanded ? 'Click to collapse' : 'Click to expand'
            );
        }

        function toggleQuiz(quizId) {
            const quiz = document.getElementById(quizId);
            const content = quiz.querySelector('.gut-check-content');
            const toggle = quiz.querySelector('.gut-check-toggle');
            const expanded = !content.classList.contains('expanded');
            content.classList.toggle('expanded', expanded);
            toggle.setAttribute('aria-expanded', String(expanded));
            toggle.textContent = expanded ? 'Hide Quiz' : 'Take Quiz';
            if (expanded) content.querySelector('input[type="radio"]')?.focus();
        }

        function selectQuizOption(quizId, optionIndex) {
            const quiz = document.getElementById(quizId);
            const options = quiz.querySelectorAll('.quiz-option');
            options.forEach((option, index) => {
                option.classList.toggle('selected', index === optionIndex);
                option.classList.remove('correct', 'incorrect');
            });
            const selectedInput = options[optionIndex]?.querySelector('input[type="radio"]');
            if (selectedInput) selectedInput.checked = true;
            const submitButton = quiz.querySelector('.quiz-submit');
            submitButton.disabled = false;
            const feedback = quiz.querySelector('.quiz-feedback');
            feedback.className = 'quiz-feedback';
            feedback.replaceChildren();
        }

        function readQuizCompletion() {
            try {
                return JSON.parse(localStorage.getItem('quiz-completed') || '{}');
            } catch (error) {
                console.warn('Quiz completion could not be read:', error);
                return {};
            }
        }

        function saveQuizCompletion(completed) {
            try {
                localStorage.setItem('quiz-completed', JSON.stringify(completed));
            } catch (error) {
                console.warn('Quiz completion could not be saved:', error);
            }
        }

        function addCompletedBadge(quiz) {
            const header = quiz.querySelector('.gut-check-header h4');
            if (!header.querySelector('.quiz-completed')) {
                const completedBadge = document.createElement('span');
                completedBadge.className = 'quiz-completed';
                completedBadge.textContent = '✓ Completed';
                header.appendChild(completedBadge);
            }
        }

        function submitQuiz(quizId, correctAnswer) {
            const quiz = document.getElementById(quizId);
            const options = quiz.querySelectorAll('.quiz-option');
            const feedbackDiv = quiz.querySelector('.quiz-feedback');
            const submitButton = quiz.querySelector('.quiz-submit');
            const selectedInput = quiz.querySelector('.quiz-option input[type="radio"]:checked');
            if (!selectedInput) return;

            const selectedIndex = Number(selectedInput.value);
            const isCorrect = selectedIndex === correctAnswer;
            options.forEach((option, index) => {
                option.classList.remove('correct', 'incorrect');
                if (index === correctAnswer) option.classList.add('correct');
                if (index === selectedIndex && !isCorrect) option.classList.add('incorrect');
            });
            submitButton.disabled = true;

            const title = document.createElement('div');
            title.className = 'quiz-feedback-title';
            title.textContent = isCorrect ? 'Correct answer' : 'Review the answer';
            const detail = document.createElement('div');
            detail.className = 'quiz-feedback-text';
            detail.textContent = isCorrect ? submitButton.dataset.correct : submitButton.dataset.incorrect;
            feedbackDiv.replaceChildren(title, detail);

            if (!isCorrect && submitButton.dataset.reviewSection) {
                const reviewButton = document.createElement('button');
                reviewButton.type = 'button';
                reviewButton.className = 'quiz-review-link';
                reviewButton.textContent = 'Review this section';
                reviewButton.addEventListener('click', () => scrollToSection(submitButton.dataset.reviewSection));
                feedbackDiv.appendChild(reviewButton);
            }

            feedbackDiv.className = `quiz-feedback show ${isCorrect ? 'correct' : 'incorrect'}`;
            if (isCorrect) {
                const completed = readQuizCompletion();
                completed[quizId] = true;
                saveQuizCompletion(completed);
                addCompletedBadge(quiz);
            }
            feedbackDiv.scrollIntoView({
                behavior: prefersReducedMotion() ? 'auto' : 'smooth',
                block: 'nearest'
            });
        }

        function scrollToSection(sectionId) {
            const section = document.getElementById(sectionId);
            if (!section) return;
            if (document.body.classList.contains('js-enabled')) {
                navigateToSection(sectionId);
            } else {
                section.scrollIntoView({ behavior: 'auto' });
            }
        }

        function initializeQuizzes() {
            const completed = readQuizCompletion();
            Object.keys(completed).forEach(quizId => {
                if (!completed[quizId]) return;
                const quiz = document.getElementById(quizId);
                if (quiz) addCompletedBadge(quiz);
            });
        }

        function updateThemeControl() {
            const toggle = document.getElementById('themeToggle');
            if (!toggle) return;
            const dark = document.documentElement.getAttribute('data-theme') === 'dark';
            toggle.setAttribute('aria-pressed', String(dark));
            toggle.setAttribute('aria-label', dark ? 'Switch to light theme' : 'Switch to dark theme');
        }

        function toggleTheme() {
            const current = document.documentElement.getAttribute('data-theme');
            document.documentElement.setAttribute('data-theme', current === 'dark' ? 'light' : 'dark');
            updateThemeControl();
        }


        document.addEventListener('click', event => {
            const link = event.target.closest('a[href^="#"]');
            if (!link) return;
            if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
            if (event.button !== 0) return;
            const id = link.getAttribute('href').slice(1);
            if (!sections.includes(id)) return;
            event.preventDefault();
            navigateToSection(id);
        });

        function handleHashNavigation() {
            const hash = window.location.hash.slice(1);
            if (hash === 'mainContent') {
                document.getElementById('mainContent')?.focus();
                return;
            }
            const target = hash && sections.includes(hash) ? hash : 'overview';
            navigateToSection(target, {
                historyMode: hash && sections.includes(hash) ? 'none' : 'replace'
            });
        }

        document.addEventListener('keydown', event => {
            if (event.key === 'Escape') {
                if (document.body.classList.contains('sidebar-open')) {
                    closeMobileSidebar({ restoreFocus: true });
                }
                return;
            }
            if (event.key === 'Tab' && document.body.classList.contains('sidebar-open')) {
                const sidebar = document.getElementById('sidebar');
                const focusable = [...sidebar.querySelectorAll(
                    'a[href], button:not(:disabled), [tabindex]:not([tabindex="-1"])'
                )].filter(element => !element.inert);
                if (focusable.length) {
                    const first = focusable[0];
                    const last = focusable[focusable.length - 1];
                    if (event.shiftKey && document.activeElement === first) {
                        event.preventDefault();
                        last.focus();
                    } else if (!event.shiftKey && document.activeElement === last) {
                        event.preventDefault();
                        first.focus();
                    }
                }
                return;
            }
            if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
            if (event.target.closest('input, textarea, select, button, a, summary, .table-wrap, [tabindex], [contenteditable="true"], [role="button"], [role="radio"], [role="region"]')) return;
            if (event.key === 'ArrowRight') {
                event.preventDefault();
                nextSection();
            } else if (event.key === 'ArrowLeft') {
                event.preventDefault();
                previousSection();
            }
        });

        function attachMissingCopyButtons() {
            document.querySelectorAll('.content-section pre').forEach((block) => {
                const wrapper = block.closest('.code-block');
                if (wrapper && wrapper.querySelector('.copy-btn')) return;
                const button = document.createElement('button');
                button.type = 'button';
                button.className = 'copy-btn';
                button.textContent = 'Copy';
                button.setAttribute('aria-label', 'Copy code to clipboard');
                button.addEventListener('click', () => copyCode(block));
                block.parentElement.insertBefore(button, block);
            });
        }

        document.addEventListener('DOMContentLoaded', () => {
            attachMissingCopyButtons();
            syncSidebarForViewport();
            initializeQuizzes();
            updateThemeControl();
            handleHashNavigation();
        });

        window.addEventListener('resize', syncSidebarForViewport);
        window.addEventListener('hashchange', handleHashNavigation);
        window.addEventListener('popstate', handleHashNavigation);

runtime.bind({toggleTheme,toggleSidebar,previousSection,nextSection,copyCode,toggleQuiz,selectQuizOption,submitQuiz,toggleFallback});

})();
}

/* metrics: content behavior ported from metrics.html; the shell owns navigation and theme. */
if (document.body.dataset.page === 'metrics') {
(function () {
"use strict";
const runtime = sectionRuntime('metrics.html');
const fetch = runtime.fetch;

const SITE = 'https://microsoft.github.io/aibast-agents-library/';
const DEFAULT_OWNER = 'microsoft', DEFAULT_REPO = 'aibast-agents-library';
let OWNER = DEFAULT_OWNER, REPO = DEFAULT_REPO;
const SVG_NS = 'http://www.w3.org/2000/svg';
const $ = id => document.getElementById(id);
const num = n => (n === null || n === undefined || isNaN(n)) ? '—' : Number(n).toLocaleString();
const percent = n => (n === null || n === undefined || isNaN(n)) ? '—' : `${Number(n).toLocaleString(undefined, { maximumFractionDigits: 1 })}%`;
const esc = s => String(s == null ? '' : s).replace(/[&<>"'`]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;','`':'&#96;'}[c]));
const bytes = b => !b ? '—' : b > 1e9 ? (b/1e9).toFixed(1)+' GB' : b > 1e6 ? (b/1e6).toFixed(1)+' MB' : (b/1e3).toFixed(0)+' KB';
const short = s => String(s || '').replace(/^@[^/]+\//, '');
const pretty = s => String(s || '').replace(/_/g, ' ');
const boundedPercent = (value, max) => {
  const amount = Number(value);
  const ceiling = Number(max);
  if (!Number.isFinite(amount) || !Number.isFinite(ceiling) || ceiling <= 0) return 0;
  return Math.max(0, Math.min(100, (amount / ceiling) * 100)).toFixed(2);
};

let M = null;

/* ---------------------------------------------------------------- loading */
async function getJSON(paths) {
  for (const p of paths) {
    try {
      const response = await fetch(p);
      if (response.ok) return await response.json();
    } catch (error) {
      /* Try the next public source, including the hosted fallback for file://. */
    }
  }
  return null;
}

function setRefreshBusy(busy) {
  const button = $('refresh');
  button.disabled = busy;
  button.setAttribute('aria-busy', String(busy));
  $('kpis').setAttribute('aria-busy', String(busy));
}

function setSnapshotRepository(repo) {
  const validPart = value => /^[A-Za-z0-9_.-]+$/.test(String(value || ''));
  OWNER = validPart((repo || {}).owner) ? repo.owner : DEFAULT_OWNER;
  REPO = validPart((repo || {}).name) ? repo.name : DEFAULT_REPO;
}

function appendAdminSetupNotice(parent) {
  parent.appendChild(document.createTextNode(' An administrator must configure METRICS_TOKEN with repository Administration: read permission and authorize the token for organization SSO. '));
  const link = document.createElement('a');
  link.href = 'docs/metrics-admin-setup.html';
  link.textContent = 'Admin setup checklist';
  parent.appendChild(link);
}

async function load() {
  setRefreshBusy(true);
  $('stamp-mode').textContent = 'Loading metrics snapshot…';
  try {
    M = await getJSON(['state/metrics.json', SITE + 'state/metrics.json']);
    if (!M) {
      $('kpis').innerHTML = '<div class="kpi error-card"><b>Metrics are unavailable.</b><div class="sub">Could not load <code>state/metrics.json</code>. Run <code>python scripts/build_metrics.py</code> locally or retry when the hosted snapshot is reachable.</div></div>';
      $('stamp-mode').textContent = 'Metrics snapshot unavailable';
      return;
    }
    setSnapshotRepository(M.repo);
    render();
    await liveTopUp();
  } catch (error) {
    $('kpis').innerHTML = '<div class="kpi error-card"><b>Metrics could not be rendered.</b><div class="sub">The snapshot was reached, but this dashboard could not process it. Refresh the page or report the issue.</div></div>';
    $('stamp-mode').textContent = 'Metrics rendering failed';
  } finally {
    setRefreshBusy(false);
  }
}

/* Client-side top-up keeps repository stars and package-wide CDN hits current
   between snapshots. Discussion signals remain snapshot-only aggregates. */
async function liveTopUp() {
  $('stamp-mode').innerHTML = '<span class="spin" aria-hidden="true"></span> Checking live sources…';
  const [repo, cdn] = await Promise.all([
    getJSON([(document.body.getAttribute('data-base') || './') + 'api/v1/github/repo.json']),  /* snapshot only: browsers never call api.github.com (rapp-static-api/1.1) */
    getJSON([`https://data.jsdelivr.com/v1/stats/packages/gh/${OWNER}/${REPO}?period=year`])
  ]);
  const live = [];
  M.repo = M.repo || {};
  if (repo) {
    M.repo.stars = repo.stargazers_count;
    M.repo.forks = repo.forks_count;
    M.repo.open_issues = repo.open_issues_count;
    live.push('GitHub');
  }
  if (cdn && cdn.hits) {
    const hits = cdn.hits.total || 0;
    if (Number.isFinite(M.totals.downloads) && Number.isFinite(M.totals.cdn_hits) && hits > M.totals.cdn_hits) {
      M.totals.downloads += (hits - M.totals.cdn_hits);
      M.totals.cdn_hits = hits;
    }
    live.push('jsDelivr');
  }
  renderKPIs();
  $('stamp-mode').textContent = live.length
    ? 'live top-up: ' + live.join(' + ')
    : 'snapshot only (live APIs unreachable)';
}

/* ----------------------------------------------------------------- render */
function render() {
  const t = M.totals;
  const generated = M.generated_at ? new Date(M.generated_at) : null;
  $('stamp-time').textContent = generated && !isNaN(generated)
    ? 'snapshot ' + generated.toLocaleString()
    : 'snapshot time unavailable';
  const tr = M.traffic || {};
  $('stamp-src').textContent = tr.live === false
    ? (tr.as_of ? `traffic figures as of ${String(tr.as_of).slice(0, 10)} (last authorized read)` : 'traffic never read — see below')
    : 'traffic read live';
  $('stamp-window').textContent = t.tracking_since
    ? `tracking since ${t.tracking_since} (${t.days_tracked} days)`
    : 'traffic tracking not started';
  const trafficGap = $('traffic-gap');
  trafficGap.replaceChildren();
  const trafficUnavailable = tr.live !== true;
  const trafficReason = tr.unavailable_reason;
  if (trafficUnavailable) {
    const callout = document.createElement('div');
    callout.className = 'callout';
    callout.setAttribute('role', 'note');
    const heading = document.createElement('b');
    heading.textContent = 'Live clone and page-view coverage is unavailable.';
    callout.appendChild(heading);
    callout.appendChild(document.createTextNode(
      trafficReason
        ? ` ${String(trafficReason)}`
        : ' The snapshot may reuse the last authorized traffic read rather than reporting live coverage.'
    ));
    appendAdminSetupNotice(callout);
    trafficGap.appendChild(callout);
  }
  renderKPIs();
  renderAchievementPoints();
  renderWorkshops();
  $('board-hint').textContent = `ranked across ${num(t.agents)} single-file agents`;
  renderChart();
  renderBoards();
  renderStacks();
  const lb = M.leaderboards || {};
  renderBars('vert-bars', (lb.verticals || []).slice(0, 14).map(v => ({ label: pretty(v.name), value: v.agents, extra: `${v.stacks} stacks` })));
  renderBars('cat-bars', (lb.categories || []).slice(0, 14).map(c => ({ label: pretty(c.name), value: c.agents, extra: `${num(c.lines)} lines` })));
  renderBars('tier-bars', Object.entries(lb.tiers || {}).map(([k, v]) => ({ label: k, value: v })));
  renderCDNFiles();
  renderFileLedger();
  renderPaths();
  renderReferrers();
  renderReleases();
  renderSources();
  hidePausedMetricSections();
}

// Metrics paused from display until their source works or carries signal.
// Data still collects in state/metrics.json; flip an entry to show it again.
const HIDDEN_METRICS = new Set([
  'agent_upvotes',          // Discussion sync is refused by the workflow token
  'achievements',           // one opt-in participant so far
  'workshop_adoption',      // per-workshop signals are almost all zero
  'repository_downloads',   // dominated by this repo's own CI clones
  'catalog_size'            // lines of code say nothing about use
]);
const showMetric = key => !HIDDEN_METRICS.has(key);

function hidePausedMetricSections() {
  document.querySelectorAll('[data-metric]').forEach(el => {
    if (!showMetric(el.dataset.metric)) el.hidden = true;
  });
}

function renderKPIs() {
  const t = M.totals, r = M.repo || {};
  const workshopTotals = (M.workshops || {}).totals || {};
  const achievementTotals = (M.achievements || {}).totals || {};
  const cards = [
    { primary: true, label: 'Agent downloads', value: num(t.agent_file_downloads), sub: 'observable immutable agent.py release-asset transfers' },
    { primary: true, metric: 'repository_downloads', label: 'AIBAST repository downloads', value: num(t.downloads), sub: `${num(t.clones)} repository clones (includes this repo's own CI) · ${num(t.cdn_hits)} CDN hits · ${num(t.release_downloads)} release assets` },
    { primary: true, metric: 'achievements', label: 'Verified achievement points', value: num(achievementTotals.points), sub: `${num(achievementTotals.participants)} opt-in public participants · ${num(achievementTotals.achievements)} badges · ${num(achievementTotals.starts)} starts · ${num(achievementTotals.workshop_completions)} workshop completions · ${num(achievementTotals.hard_completions)} hard completions` },
    { metric: 'agent_upvotes', label: 'Agent upvotes', value: num(t.agent_upvotes), sub: 'native rating-Discussion upvotes · one active signal per GitHub account and agent' },
    { metric: 'workshop_adoption', label: 'Workshop usage events', value: num(workshopTotals.usage_events), sub: `${num(workshopTotals.workshops)} advertised workshops · public event-count floor, not users` },
    { label: 'Repository stars', value: num(r.stars), sub: `${num(r.forks)} forks · ${num(r.open_issues)} open issues` },
    { label: 'Installer fetches', value: num(t.installer_downloads), sub: 'install.sh / .ps1 / .cmd served over the CDN — raw.githubusercontent installs are uncounted' },
    { label: 'Agents', value: num(t.agents), sub: `${num(t.stacks)} stacks · ${num(t.verticals)} verticals` },
    { metric: 'catalog_size', label: 'Catalog size', value: num(t.total_lines), sub: `lines of Python · ${num(t.total_kb)} KB across ${num(t.agents)} files` },
    { label: 'Unique cloners', value: num(t.clone_uniques_14d), sub: `last 14 days · ${num(t.clone_uniques_daily_sum)} daily-unique sum since ${t.tracking_since || '—'}` },
    { label: 'Page views', value: num(t.page_views), sub: `${num(t.view_uniques_14d)} unique visitors (14d)` }
  ].filter(card => !card.metric || showMetric(card.metric));
  $('kpis').innerHTML = cards.map(card =>
    `<article class="kpi${card.primary ? ' primary' : ''}">
       <div class="label">${esc(card.label)}</div>
       <div class="value">${card.value}</div>
       <div class="sub">${esc(card.sub)}</div>
     </article>`).join('');
}

function renderAchievementPoints() {
  const achievementMetrics = M.achievements || {};
  const totals = achievementMetrics.totals || {};
  const profiles = Array.isArray(achievementMetrics.profiles) ? achievementMetrics.profiles.slice() : [];
  const workshops = Array.isArray(achievementMetrics.workshops) ? achievementMetrics.workshops.slice() : [];
  const achievementRows = Array.isArray(achievementMetrics.achievements) ? achievementMetrics.achievements.slice() : [];
  const summary = [
    { label: 'Verified participants', value: totals.participants },
    { label: 'Achievement points', value: totals.points },
    { label: 'Verified badges', value: totals.achievements },
    { label: 'Verified starts', value: totals.starts },
    { label: 'Workshop completions', value: totals.workshop_completions },
    { label: 'Manual completions', value: totals.hard_completions },
    { label: 'Completion rate', value: percent(totals.completion_rate), formatted: true },
    { label: 'Achievement completion', value: percent(totals.achievement_completion_rate), formatted: true }
  ];
  $('achievements-summary').innerHTML = summary.map(item =>
    `<div class="workshop-stat"><b>${item.formatted ? item.value : num(item.value)}</b><span>${esc(item.label)}</span></div>`).join('');

  const coverage = achievementMetrics.coverage || {};
  const status = achievementMetrics.status || coverage.status || 'unavailable';
  const achievementCoverage = $('achievements-coverage');
  const coverageText = status === 'unavailable'
    ? 'Verified public achievement claims are unavailable in this snapshot. Null values are not verified zeros.'
    : `${status === 'partial' ? 'Partial' : 'Available'} verified achievement coverage · ${num((coverage.diagnostics || {}).accepted_achievements)} unique achievements from ${num(coverage.issues_scanned)} marker-matched public issues.`;
  achievementCoverage.textContent = achievementMetrics.carried_forward
    ? `Carried forward from ${achievementMetrics.as_of || 'the prior snapshot'} · ${coverageText}`
    : coverageText;
  if (status === 'unavailable') appendAdminSetupNotice(achievementCoverage);

  profiles.sort((left, right) =>
    (Number(right.points) || 0) - (Number(left.points) || 0)
    || (Number(right.achievement_count) || 0) - (Number(left.achievement_count) || 0)
    || (Number(right.workshop_completions) || 0) - (Number(left.workshop_completions) || 0)
    || (Number(right.hard_completions) || 0) - (Number(left.hard_completions) || 0)
    || String(left.login).localeCompare(String(right.login), undefined, { sensitivity: 'base' })
  );
  $('achievements-profile-hint').textContent = profiles.length
    ? `${num(profiles.length)} opt-in public profile${profiles.length === 1 ? '' : 's'}`
    : 'Profiles are public only after opt-in submission';
  const profileTable = $('achievements-leaderboard');
  profileTable.innerHTML = `<caption>Verified public achievement profiles ranked by points</caption>
    <thead><tr><th scope="col">GitHub login</th><th class="num" scope="col">Points</th><th class="num" scope="col">Badges</th><th class="num" scope="col">Starts</th><th class="num" scope="col">Workshop completions</th><th class="num" scope="col">Manual completions</th></tr></thead>
    <tbody>${profiles.length ? profiles.map(profile => {
      const login = String(profile.login || '');
      const profileUrl = /^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$/.test(login)
        ? `https://github.com/${encodeURIComponent(login)}`
        : `https://github.com/${OWNER}/${REPO}`;
      const achievementIds = Array.isArray(profile.achievement_ids)
        ? profile.achievement_ids
        : [];
      return `<tr>
        <td class="achievements-login"><a href="${profileUrl}" target="_blank" rel="noopener">${esc(login)}</a></td>
        <td class="num">${num(profile.points)}</td>
        <td class="num achievements-badges" title="${esc(achievementIds.join(', '))}">${num(profile.achievement_count)}</td>
        <td class="num">${num(profile.starts)}</td>
        <td class="num">${num(profile.workshop_completions)}</td>
        <td class="num">${num(profile.hard_completions)}</td>
      </tr>`;
    }).join('') : '<tr><td class="empty" colspan="6">No opt-in verified achievement profiles are available in this snapshot.</td></tr>'}</tbody>`;

  workshops.sort((left, right) =>
    (Number(right.points) || 0) - (Number(left.points) || 0)
    || (Number(right.achievements) || 0) - (Number(left.achievements) || 0)
    || (Number(right.workshop_completions) || 0) - (Number(left.workshop_completions) || 0)
    || (Number(right.hard_completions) || 0) - (Number(left.hard_completions) || 0)
    || (Number(right.starts) || 0) - (Number(left.starts) || 0)
    || String(left.display_name || left.slug).localeCompare(String(right.display_name || right.slug))
  );
  $('achievements-workshop-hint').textContent = workshops.length
    ? `${num(workshops.length)} canonical workshops; Grid Outage excluded`
    : 'Canonical workshop achievement rows are unavailable';
  const workshopTable = $('achievements-workshop-table');
  workshopTable.innerHTML = `<caption>Canonical workshops ranked by verified achievement points</caption>
    <thead><tr><th scope="col">Workshop</th><th class="num" scope="col">Points</th><th class="num" scope="col">Badges</th><th class="num" scope="col">Starts</th><th class="num" scope="col">Workshop completions</th><th class="num" scope="col">Manual completions</th><th class="num" scope="col">Achievement completion</th></tr></thead>
    <tbody>${workshops.length ? workshops.map(row => {
      const slug = String(row.slug || '');
      const quest = /^[a-z0-9-]+$/.test(slug)
        ? `solutions/${encodeURIComponent(slug)}/quest.html`
        : 'library.html';
      return `<tr>
        <td><a href="${quest}">${esc(row.display_name || pretty(row.slug))}</a><div class="rank-meta mono">${esc(row.agent_name || '')}</div></td>
        <td class="num">${num(row.points)}</td>
        <td class="num">${num(row.achievements)}</td>
        <td class="num">${num(row.starts)}</td>
        <td class="num">${num(row.workshop_completions)}</td>
        <td class="num">${num(row.hard_completions)}</td>
        <td class="num">${percent(row.achievement_completion_rate)}</td>
      </tr>`;
    }).join('') : '<tr><td class="empty" colspan="7">No canonical achievement workshop rows are available. Regenerate the metrics snapshot.</td></tr>'}</tbody>`;

  $('achievements-rollup-hint').textContent = achievementRows.length
    ? `${num(achievementRows.length)} canonical achievement IDs`
    : 'Canonical achievement rollup is unavailable';
  const achievementTable = $('achievements-rollup-table');
  achievementTable.innerHTML = `<caption>Verified claims by canonical achievement</caption>
    <thead><tr><th scope="col">Achievement</th><th class="num" scope="col">Points each</th><th class="num" scope="col">Claims</th><th class="num" scope="col">Participants</th><th class="num" scope="col">Workshops</th><th class="num" scope="col">Attainment</th></tr></thead>
    <tbody>${achievementRows.length ? achievementRows.map(row => `<tr>
      <td><span class="achievements-login">${esc(row.label || pretty(row.id))}</span><div class="rank-meta mono">${esc(row.id || '')}</div></td>
      <td class="num">${num(row.points)}</td>
      <td class="num">${num(row.claims)}</td>
      <td class="num">${num(row.participants)}</td>
      <td class="num">${num(row.workshops)}</td>
      <td class="num">${percent(row.attainment_rate)}</td>
    </tr>`).join('') : '<tr><td class="empty" colspan="6">No achievement rollup is available.</td></tr>'}</tbody>`;
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
    `<button type="button" class="tab${option.id === activeWorkshopSort ? ' active' : ''}" aria-pressed="${option.id === activeWorkshopSort}" aria-controls="workshop-table" data-workshop-sort="${option.id}">${option.label}</button>`).join('');
}

function renderWorkshops() {
  const workshops = M.workshops || {};
  const totals = workshops.totals || {};
  const rows = Array.isArray(workshops.rows) ? workshops.rows.slice() : [];
  const summary = [
    { label: 'Workshops', value: totals.workshops },
    { label: 'Usage events', value: totals.usage_events },
    { label: 'Agent upvotes', value: totals.agent_upvotes },
    { label: 'Views (14d)', value: totals.views_14d },
    { label: 'File downloads', value: totals.file_downloads },
    { label: 'Bundle downloads', value: totals.bundle_downloads },
    { label: 'Feedback reports', value: totals.feedback_reports }
  ];
  // Usage split: solutions that came from customer AIdeate and RAPP sessions vs. the original catalog.
  const bySource = workshops.by_source || {};
  if (bySource.field) summary.push({ label: `Usage, ${num(bySource.field.solutions)} from customer sessions`, value: bySource.field.usage_events });
  if (bySource.catalog) summary.push({ label: `Usage, ${num(bySource.catalog.solutions)} original catalog`, value: bySource.catalog.usage_events });
  $('workshop-summary').innerHTML = summary.map(item =>
    `<div class="workshop-stat"><b>${num(item.value)}</b><span>${esc(item.label)}</span></div>`).join('');
  $('workshop-hint').textContent = totals.workshops === undefined
    ? 'workshop metrics are not present in this snapshot'
    : `${num(totals.workshops)} catalog-advertised workshop quests`;

  const coverage = workshops.coverage || {};
  const workshopCoverage = $('workshop-coverage');
  const workshopViewStatus = (coverage.views || {}).status;
  const workshopViewsUnavailable = !workshopViewStatus || workshopViewStatus === 'unavailable';
  const coverageText = coverage.status === 'unavailable'
    ? 'Workshop public signals are unavailable in this snapshot. The advertised workshop rows remain present with unavailable values rather than fabricated zeros.'
    : coverage.status === 'partial'
      ? `Partial public coverage · views: ${(coverage.views || {}).status || 'unavailable'} · downloads: ${(coverage.downloads || {}).status || 'unavailable'} · feedback: ${(coverage.feedback || {}).status || 'unavailable'} · agent upvotes: ${(coverage.agent_upvotes || {}).status || 'unavailable'}.`
      : 'Workshop coverage metadata is not present in this snapshot.';
  workshopCoverage.textContent = workshops.carried_forward
    ? `Carried forward from ${workshops.as_of || 'the prior snapshot'} · ${coverageText}`
    : coverageText;
  if (coverage.status === 'unavailable' || workshopViewsUnavailable) {
    appendAdminSetupNotice(workshopCoverage);
  }
  renderWorkshopControls();

  const sort = ALL_WORKSHOP_SORTS.some(option => option.id === activeWorkshopSort)
    ? activeWorkshopSort
    : 'usage_events';
  rows.sort((left, right) =>
    (Number(right[sort]) || 0) - (Number(left[sort]) || 0)
    || (Number(right.usage_events) || 0) - (Number(left.usage_events) || 0)
    || String(left.display_name || left.slug).localeCompare(String(right.display_name || right.slug))
  );
  const table = $('workshop-table');
  const selected = ALL_WORKSHOP_SORTS.find(option => option.id === sort);
  if (!rows.length) {
    table.innerHTML = `<caption>Catalog-advertised workshop adoption signals</caption>
      <thead><tr><th scope="col">Workshop</th><th class="num" scope="col">Usage events</th><th class="num" scope="col">Agent upvotes</th><th class="num" scope="col">Views (14d)</th><th class="num" scope="col">Path uniques (14d)</th><th class="num" scope="col">File downloads</th><th class="num" scope="col">Bundle downloads</th><th class="num" scope="col">Feedback</th></tr></thead>
      <tbody><tr><td class="empty" colspan="8">No workshop rows are available. Regenerate the metrics snapshot from the current registry.</td></tr></tbody>`;
    return;
  }
  table.innerHTML = `<caption>Catalog-advertised workshops sorted by ${esc(selected.label)}</caption>
    <thead><tr><th scope="col">Workshop</th><th class="num" scope="col">Usage events</th><th class="num" scope="col">Agent upvotes</th><th class="num" scope="col">Views (14d)</th><th class="num" scope="col">Path uniques (14d)</th><th class="num" scope="col">File downloads</th><th class="num" scope="col">Bundle downloads</th><th class="num" scope="col">Feedback</th></tr></thead>
    <tbody>${rows.map(row => {
      const fallbackQuest = `solutions/${encodeURIComponent(row.slug)}/quest.html`;
      const quest = /^solutions\/[a-z0-9-]+\/quest\.html$/.test(row.quest_url || '')
        ? row.quest_url
        : fallbackQuest;
      return `<tr>
        <td><a href="${esc(quest)}">${esc(row.display_name || pretty(row.slug))}</a><div class="rank-meta mono">${esc(row.slug)}</div></td>
        <td class="num">${num(row.usage_events)}</td>
        <td class="num">${num(row.agent_upvotes)}<div class="rank-meta mono">${esc(row.agent_name || '')}</div></td>
        <td class="num">${num(row.views_14d)}</td>
        <td class="num">${num(row.view_uniques_14d)}</td>
        <td class="num">${num(row.file_downloads)}</td>
        <td class="num">${num(row.bundle_downloads)}</td>
        <td class="num">${num(row.feedback_reports)}<div class="rank-meta">${num(row.feedback_open)} open · ${num(row.feedback_closed)} closed</div></td>
      </tr>`;
    }).join('')}</tbody>`;
}

function chartToken(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

function appendSvg(parent, tag, attributes, text) {
  const node = document.createElementNS(SVG_NS, tag);
  Object.entries(attributes || {}).forEach(([name, value]) => node.setAttribute(name, String(value)));
  if (text !== undefined) node.textContent = text;
  parent.appendChild(node);
  return node;
}

function renderChart() {
  const data = (M.daily || []).slice(-60);
  const svg = $('chart');
  const colors = {
    clones: chartToken('--cp-accent'),
    views: chartToken('--cp-link'),
    cdn: chartToken('--cp-success'),
    grid: chartToken('--cp-border'),
    text: chartToken('--cp-text-soft')
  };
  svg.replaceChildren();
  appendSvg(svg, 'title', { id: 'chart-title' }, 'Traffic over time');
  appendSvg(svg, 'desc', { id: 'chart-desc' }, 'Daily repository clones, page views, and CDN hits for the latest available 60 days.');
  const W = 1000, H = 210, PAD = 28;
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  if (!data.length) {
    appendSvg(svg, 'text', { x: 12, y: 108, fill: colors.text, 'font-size': 13 }, 'No traffic history yet — the first authorized snapshot starts the series.');
    return;
  }
  const max = Math.max(1, ...data.map(d => Math.max(Number(d.clones) || 0, Number(d.views) || 0, Number(d.cdn) || 0)));
  const barWidth = (W - PAD * 2) / data.length;
  const y = value => H - PAD - ((Number(value) || 0) / max) * (H - PAD * 2);
  for (let i = 0; i <= 3; i += 1) {
    const gridY = PAD + i * (H - PAD * 2) / 3;
    const value = Math.round(max - i * max / 3);
    appendSvg(svg, 'line', { x1: PAD, y1: gridY, x2: W - PAD, y2: gridY, stroke: colors.grid, 'stroke-width': 1 });
    appendSvg(svg, 'text', { x: 4, y: gridY + 3, fill: colors.text, 'font-size': 9 }, String(value));
  }
  data.forEach((d, index) => {
    const x = PAD + index * barWidth;
    const width = Math.max(1.5, barWidth * .26);
    const series = [
      { value: d.clones, color: colors.clones, offset: 0, label: 'clones' },
      { value: d.views, color: colors.views, offset: width + 1, label: 'views' },
      { value: d.cdn, color: colors.cdn, offset: (width + 1) * 2, label: 'CDN hits' }
    ];
    series.forEach(item => {
      const amount = Number(item.value) || 0;
      if (!amount) return;
      const rect = appendSvg(svg, 'rect', {
        x: x + item.offset,
        y: y(amount),
        width,
        height: H - PAD - y(amount),
        fill: item.color,
        rx: 1
      });
      appendSvg(rect, 'title', {}, `${d.date}: ${amount} ${item.label}`);
    });
  });
  const step = Math.ceil(data.length / 8);
  data.forEach((d, index) => {
    if (index % step) return;
    appendSvg(svg, 'text', {
      x: PAD + index * barWidth,
      y: H - 6,
      fill: colors.text,
      'font-size': 9
    }, String(d.date || '').slice(5));
  });
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
  ...(showMetric('agent_upvotes') ? [AGENT_UPVOTE_BOARD] : []),
  ...BOARDS.slice(1).filter(board => board.id !== 'largest' || showMetric('catalog_size'))
];
let activeBoard = 'most_downloaded';

function renderBoards() {
  const tabs = $('tabs');
  tabs.innerHTML = ALL_BOARDS.map(board =>
    `<button type="button" class="tab${board.id === activeBoard ? ' active' : ''}" id="tab-${board.id}" role="tab" aria-selected="${board.id === activeBoard}" aria-controls="board" tabindex="${board.id === activeBoard ? '0' : '-1'}" data-board="${board.id}">${board.label}</button>`).join('');
  const panel = $('board');
  panel.setAttribute('aria-labelledby', `tab-${activeBoard}`);
  const cfg = ALL_BOARDS.find(board => board.id === activeBoard);
  const signalBoard = activeBoard === 'most_upvoted';
  const advertisedWorkshopAgents = new Set(
    ((M.workshops || {}).rows || [])
      .map(row => row.agent_name)
      .filter(Boolean)
  );
  const eligibleAgent = row => (
    row.catalog_kind !== 'solution'
    || advertisedWorkshopAgents.has(row.name)
  );
  const rows = (signalBoard
    ? (Array.isArray(M.agent_metrics) ? M.agent_metrics : [])
        .filter(eligibleAgent)
        .filter(row => Number(row[cfg.metric]) > 0)
        .sort((left, right) =>
          (Number(right[cfg.metric]) || 0) - (Number(left[cfg.metric]) || 0)
          || (Number(right.downloads) || 0) - (Number(left.downloads) || 0)
          || String(left.name).localeCompare(String(right.name)))
        .slice(0, 15)
    : ((M.leaderboards || {})[activeBoard] || [])
        .filter(eligibleAgent));
  if (!rows.length) {
    panel.innerHTML = activeBoard === 'most_downloaded'
      ? '<div class="empty">No agent release-asset downloads have been recorded yet.</div>'
      : signalBoard
        ? '<div class="empty">No canonical Discussion signals are available in this snapshot yet.</div>'
        : '<div class="empty">No data recorded yet for this leaderboard.</div>';
    return;
  }
  panel.innerHTML = rows.map((r, index) => {
    let value = r[cfg.metric];
    if (cfg.metric === 'added_at') value = String(value).slice(0, 10);
    else value = num(value);
    const tier = r.tier ? `<span class="pill">${esc(r.tier)}</span>` : '';
    const url = r.file ? `https://github.com/${OWNER}/${REPO}/blob/main/${encodeURI(r.file)}` : `https://github.com/${OWNER}/${REPO}`;
    const signalUrl = cfg.metric === 'upvotes'
      ? r.upvote_discussion_url
      : '';
    const signalLink = /^https:\/\/github\.com\/[^/]+\/[^/]+\/discussions\/\d+$/.test(signalUrl || '')
      ? ` · <a href="${esc(signalUrl)}" target="_blank" rel="noopener">Discussion ↗</a>`
      : '';
    return `<div class="rank-row">
      <div class="rank-n">${index + 1}</div>
      <div>
        <div class="rank-name"><a href="library.html#agent/${encodeURIComponent(r.name)}">${esc(r.display_name || short(r.name))}</a>${tier}</div>
        <div class="rank-meta"><span class="mono">${esc(r.name)}</span> · ${esc(pretty(r.category))}${r.stack ? ` · ${esc(pretty(r.stack))} stack` : ''} · <a href="${url}" target="_blank" rel="noopener">source ↗</a>${signalLink}</div>
      </div>
      <div class="rank-val">${value}<small>${esc(cfg.unit)}</small></div>
    </div>`;
  }).join('');
}

function activateBoard(boardId, focusTab) {
  if (!ALL_BOARDS.some(board => board.id === boardId)) return;
  activeBoard = boardId;
  renderBoards();
  if (focusTab) {
    const selected = $('tabs').querySelector('[aria-selected="true"]');
    if (selected) selected.focus();
  }
}

function renderStacks() {
  const rows = (M.leaderboards || {}).stacks || [];
  const table = $('stack-table');
  if (!rows.length) {
    table.innerHTML = '<caption>Deployable stack adoption and catalog size</caption><thead><tr><th scope="col">Stack</th><th scope="col">Vertical</th><th class="num" scope="col">Agents</th><th class="num" scope="col">Lines</th><th class="num" scope="col">Downloads</th></tr></thead><tbody><tr><td class="empty" colspan="5">No stacks are available in the catalog snapshot.</td></tr></tbody>';
    $('stack-hint').textContent = 'No deployable stacks in this snapshot';
    return;
  }
  const total = M.totals.stacks || rows.length;
  // The link goes to the catalog, so it states the catalog's own count.
  const solutions = M.totals.solutions;
  const libraryLink = solutions === undefined || solutions === null
    ? '<a href="library.html">browse the library</a>'
    : `<a href="library.html">${num(solutions)} solutions in the library</a>`;
  $('stack-hint').innerHTML = rows.length < total
    ? `the unit a customer actually deploys — top ${rows.length} of ${num(total)} stacks, ${libraryLink}`
    : `the unit a customer actually deploys — ${libraryLink}`;
  table.innerHTML =
    `<caption>Deployable stack adoption and catalog size</caption>
     <thead><tr><th scope="col">Stack</th><th scope="col">Vertical</th><th class="num" scope="col">Agents</th><th class="num" scope="col">Lines</th><th class="num" scope="col">Downloads</th></tr></thead>
     <tbody>${rows.map(s => `<tr>
       <td><a href="https://github.com/${OWNER}/${REPO}/tree/main/${encodeURI(s.path)}" target="_blank" rel="noopener">${esc(s.display_name)}</a></td>
       <td>${esc(pretty(s.vertical))}</td>
       <td class="num">${num(s.agents)}</td>
       <td class="num">${num(s.lines)}</td>
       <td class="num">${num(s.downloads)}</td></tr>`).join('')}</tbody>`;
}

function renderBars(target, rows) {
  const element = $(target);
  if (!rows.length) {
    element.innerHTML = '<div class="empty">No data is available for this breakdown.</div>';
    return;
  }
  const max = Math.max(...rows.map(r => Number(r.value) || 0), 1);
  element.innerHTML = rows.map(r => `<div class="bar-row">
      <div class="bar-label" title="${esc(r.label)}">${esc(r.label)}${r.extra ? ` <span class="bar-extra">· ${esc(r.extra)}</span>` : ''}</div>
      <div class="bar-track"><div class="bar-fill" style="width:${boundedPercent(r.value, max)}%"></div></div>
      <div class="bar-num">${num(r.value)}</div>
    </div>`).join('');
}

function renderCDNFiles() {
  const files = ((M.cdn || {}).files || []).slice(0, 12);
  if (!files.length) {
    $('cdn-files').innerHTML = '<div class="empty">No observed CDN file hits are available in this snapshot. <a href="#file-download-ledger">Open the full tracked-file ledger</a>.</div>';
    return;
  }
  const max = Math.max(...files.map(f => Number(f.hits) || 0), 1);
  $('cdn-files').innerHTML = files.map(f => `<div class="bar-row">
      <div class="bar-label" title="${esc(f.file)}">${esc(f.agent ? short(f.agent) : f.file.split('/').pop())}
        <span class="bar-extra">· ${esc(f.kind)}</span></div>
      <div class="bar-track"><div class="bar-fill" style="width:${boundedPercent(f.hits, max)}%"></div></div>
      <div class="bar-num">${num(f.hits)}</div>
    </div>`).join('') +
    `<p class="note note-summary">Total CDN traffic: ${num(M.cdn.total_hits)} hits · ${bytes(M.cdn.bandwidth)} served${M.cdn.rank ? ` · jsDelivr rank #${num(M.cdn.rank)}` : ''} · <a href="#file-download-ledger">open the full tracked-file ledger</a></p>`;
}

const FILE_LEDGER_PAGE_SIZE = 50;
let fileLedgerPage = 1;

function fileKindLabel(kind) {
  return kind === 'skill' ? 'Skill (SKILL.md)' : pretty(kind);
}

function renderFileLedgerControls(rows) {
  const select = $('file-ledger-kind');
  const selected = select.value || 'all';
  const kinds = Array.from(new Set(rows.map(row => row.kind).filter(Boolean))).sort();
  select.innerHTML = '<option value="all">All kinds</option>' + kinds.map(kind =>
    `<option value="${esc(kind)}">${esc(fileKindLabel(kind))}</option>`).join('');
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
    if (!query) return true;
    return [
      row.path,
      row.kind,
      row.agent_name,
      row.workshop_slug
    ].some(value => String(value || '').toLocaleLowerCase().includes(query));
  });
  filtered.sort((left, right) => {
    if (sort === 'path') return String(left.path).localeCompare(String(right.path));
    const leftKnown = Number.isFinite(left.downloads);
    const rightKnown = Number.isFinite(right.downloads);
    if (leftKnown !== rightKnown) return leftKnown ? -1 : 1;
    return (Number(right.downloads) || 0) - (Number(left.downloads) || 0)
      || String(left.path).localeCompare(String(right.path));
  });
  const pageCount = Math.max(1, Math.ceil(filtered.length / FILE_LEDGER_PAGE_SIZE));
  fileLedgerPage = Math.min(Math.max(1, fileLedgerPage), pageCount);
  const start = (fileLedgerPage - 1) * FILE_LEDGER_PAGE_SIZE;
  const visible = filtered.slice(start, start + FILE_LEDGER_PAGE_SIZE);
  const table = $('file-ledger-table');
  if (!rows.length) {
    table.innerHTML = '<caption>All tracked repository files and observable downloads</caption><thead><tr><th scope="col">Path</th><th scope="col">Kind</th><th scope="col">Mapped agent</th><th scope="col">Mapped workshop</th><th class="num" scope="col">Downloads</th><th scope="col">Status</th></tr></thead><tbody><tr><td class="empty" colspan="6">This snapshot predates the tracked-file ledger. Regenerate metrics to publish every repository file.</td></tr></tbody>';
  } else if (!visible.length) {
    table.innerHTML = '<caption>All tracked repository files and observable downloads</caption><thead><tr><th scope="col">Path</th><th scope="col">Kind</th><th scope="col">Mapped agent</th><th scope="col">Mapped workshop</th><th class="num" scope="col">Downloads</th><th scope="col">Status</th></tr></thead><tbody><tr><td class="empty" colspan="6">No tracked files match the current search and kind filter.</td></tr></tbody>';
  } else {
    table.innerHTML = `<caption>Tracked files ${start + 1}–${start + visible.length} of ${filtered.length} matching rows</caption>
      <thead><tr><th scope="col">Path</th><th scope="col">Kind</th><th scope="col">Mapped agent</th><th scope="col">Mapped workshop</th><th class="num" scope="col">Downloads</th><th scope="col">Status</th></tr></thead>
      <tbody>${visible.map(row => `<tr>
        <td><a href="https://github.com/${OWNER}/${REPO}/blob/main/${encodeURI(row.path)}" target="_blank" rel="noopener" class="mono">${esc(row.path)}</a></td>
        <td>${esc(fileKindLabel(row.kind))}</td>
        <td class="mono">${esc(row.agent_name || '—')}</td>
        <td>${esc(row.workshop_slug || '—')}</td>
        <td class="num">${num(row.downloads)}</td>
        <td>${esc(pretty(row.status || 'unknown'))}</td>
      </tr>`).join('')}</tbody>`;
  }
  const totalFiles = (metrics.totals || {}).files;
  const kindSummary = Object.entries((metrics.totals || {}).by_kind || {})
    .filter(([_kind, values]) => values.files)
    .map(([kindName, values]) =>
      `${fileKindLabel(kindName)}: ${num(values.downloads)} downloads across ${num(values.files)} files`)
    .join(' · ');
  $('file-ledger-summary').textContent = rows.length
    ? `${num(filtered.length)} matching of ${num(totalFiles ?? rows.length)} tracked files · source coverage: ${metrics.source_status || 'unknown'}${kindSummary ? ` · ${kindSummary}` : ''}`
    : 'Tracked-file metrics are unavailable in this snapshot.';
  $('file-ledger-page').textContent = `Page ${fileLedgerPage} of ${pageCount}`;
  $('file-ledger-prev').disabled = fileLedgerPage <= 1;
  $('file-ledger-next').disabled = fileLedgerPage >= pageCount;
}

function renderPaths() {
  const rows = (M.traffic || {}).paths || [];
  if (!rows.length) {
    $('paths').innerHTML = '<div class="empty">Path data needs a token-authenticated snapshot.</div>';
    return;
  }
  const max = Math.max(...rows.map(p => Number(p.count) || 0), 1);
  $('paths').innerHTML = rows.slice(0, 12).map(p => `<div class="bar-row">
      <div class="bar-label" title="${esc(p.path)}"><a href="https://github.com${esc(p.path)}" target="_blank" rel="noopener">${esc(p.path.replace(`/${OWNER}/${REPO}`, '') || '/')}</a></div>
      <div class="bar-track"><div class="bar-fill" style="width:${boundedPercent(p.count, max)}%"></div></div>
      <div class="bar-num">${num(p.count)}</div>
    </div>`).join('');
}

function renderReferrers() {
  const rows = (M.traffic || {}).referrers || [];
  if (!rows.length) {
    $('referrers').innerHTML = '<div class="empty">No referrer data is available in this snapshot.</div>';
    return;
  }
  const max = Math.max(...rows.map(r => Number(r.count) || 0), 1);
  $('referrers').innerHTML = rows.map(r => `<div class="bar-row">
      <div class="bar-label">${esc(r.referrer)}</div>
      <div class="bar-track"><div class="bar-fill" style="width:${boundedPercent(r.count, max)}%"></div></div>
      <div class="bar-num">${num(r.count)}</div>
    </div>`).join('');
}

function renderReleases() {
  const rel = M.releases || { releases: [] };
  if (!(rel.releases || []).length) {
    $('releases').innerHTML = '<div class="empty">No releases have been published.</div>';
    return;
  }
  $('releases').innerHTML = rel.releases.map(r => `<div class="rank-row">
      <div class="rank-n">▸</div>
      <div><div class="rank-name"><a href="https://github.com/${OWNER}/${REPO}/releases/tag/${encodeURIComponent(r.tag)}" target="_blank" rel="noopener">${esc(r.tag)}</a></div>
        <div class="rank-meta">${esc(r.name || '')} · ${String(r.published_at || '').slice(0, 10)} · ${(r.assets || []).length} assets</div></div>
      <div class="rank-val">${num(r.downloads)}<small>downloads</small></div>
    </div>`).join('');
}

function renderSources() {
  const rows = (M.sources || []).filter(s =>
    s.name !== 'GitHub Discussions' || showMetric('agent_upvotes'));
  $('sources').innerHTML = rows.length
    ? rows.map(s => `<div class="src-item"><b>${esc(s.name)}</b><span>${esc(s.metric)} — <a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.url.replace('https://', ''))}</a></span></div>`).join('')
    : '<div class="empty">No source metadata is available in this snapshot.</div>';
}

function syncThemeButton() {
  const button = $('themeToggle');
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  button.setAttribute('aria-pressed', String(isDark));
  button.textContent = isDark ? 'Use light theme' : 'Use dark theme';
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  syncThemeButton();
  if (M) renderChart();
}

const feedbackSchema = 'aibast-workshop-feedback/1.0';
function resolveFeedbackOwner(hostname) {
  const pagesHost = hostname.match(
    /^([a-z0-9](?:[a-z0-9-]{0,37}[a-z0-9])?)\.github\.io$/i
  );
  return pagesHost ? pagesHost[1] : 'microsoft';
}

function wireFeedback() {
  const issueOwner = resolveFeedbackOwner(location.hostname);
  const issueUrl = new URL(`https://github.com/${issueOwner}/aibast-agents-library/issues/new`);
  issueUrl.searchParams.set('title', '[Metrics] Dashboard feedback');
  issueUrl.searchParams.set('body', `<!-- aibast-workshop-feedback:v1 -->
Feedback schema: ${feedbackSchema}

Page: Library Metrics
Page URL: ${location.href.split('#')[0]}
Section or metric:
What happened:
What did you expect:

Snapshot time shown on page:
Browser and theme:`);
  $('reportIssue').href = issueUrl.toString();
}

$('tabs').addEventListener('click', event => {
  const tab = event.target.closest('button[role="tab"]');
  if (tab) activateBoard(tab.dataset.board, false);
});

$('tabs').addEventListener('keydown', event => {
  if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
  const tabs = Array.from($('tabs').querySelectorAll('button[role="tab"]'));
  const current = tabs.indexOf(event.target);
  if (current < 0) return;
  event.preventDefault();
  let next = current;
  if (event.key === 'ArrowLeft') next = (current - 1 + tabs.length) % tabs.length;
  if (event.key === 'ArrowRight') next = (current + 1) % tabs.length;
  if (event.key === 'Home') next = 0;
  if (event.key === 'End') next = tabs.length - 1;
  activateBoard(tabs[next].dataset.board, true);
});

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
syncThemeButton();
load();

})();
}

/* achievements: content behavior ported from achievements.html; the shell owns navigation and theme. */
if (document.body.dataset.page === 'achievements') {
(function () {
"use strict";
const runtime = sectionRuntime('achievements.html');
const fetch = runtime.fetch;

    (() => {
      const PROFILE_KEY = "aibast:achievement-profile:v1";
      const HIGHLIGHT_KEY = "aibast:achievement-highlight:v1";
      const BADGES = Object.freeze([
        { id: "started", claimId: "started", label: "Started", points: 5, description: "First meaningful workshop checkpoint." },
        { id: "local-proof", claimId: "local-proof", label: "Local proof", points: 15, description: "Locked local cases confirmed." },
        { id: "draft-builder", claimId: "draft-builder", label: "Draft builder", points: 20, description: "Reviewed unpublished Draft confirmed." },
        { id: "preview-proven", claimId: "preview-proven", label: "Preview proven", points: 25, description: "Every named Preview checkpoint confirmed." },
        { id: "workshop-complete", claimId: "workshop-completed", label: "Workshop complete", points: 35, description: "Every required checkpoint in the current Easy path." },
        { id: "hard-mode-complete", claimId: "hard-mode-completed", label: "Manual mode complete", points: 50, description: "Every manual browserfilm step marked complete." },
      ]);
      const BADGE_IDS = new Set(BADGES.map((badge) => badge.id));
      const CLAIM_ORDER = Object.freeze(BADGES.map((badge) => badge.claimId));
      const CLAIM_IDS = new Set(CLAIM_ORDER);
      let verifiedByWorkshop = new Map();

      function validTimestamp(value) {
        return typeof value === "string" && !Number.isNaN(Date.parse(value))
          ? value
          : null;
      }

      function count(value) {
        return Number.isInteger(value) && value >= 0 ? value : 0;
      }

      function sanitizeProfile(value) {
        const clean = { score: 0, workshops: {}, updatedAt: null };
        const source =
          value && typeof value === "object" && !Array.isArray(value) ? value : {};
        const workshops =
          source.workshops && typeof source.workshops === "object"
            ? source.workshops
            : {};
        Object.entries(workshops).forEach(([key, raw]) => {
          if (!raw || typeof raw !== "object") return;
          const slug = typeof raw.slug === "string" ? raw.slug : key;
          if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug)) return;
          const rawProgress =
            raw.progress && typeof raw.progress === "object" ? raw.progress : {};
          const rawAchievements =
            raw.achievements && typeof raw.achievements === "object"
              ? raw.achievements
              : {};
          const achievements = {};
          Object.entries(rawAchievements).forEach(([id, achievement]) => {
            if (!BADGE_IDS.has(id)) return;
            const earned =
              achievement === true ||
              (achievement &&
                typeof achievement === "object" &&
                achievement.earned === true);
            if (!earned) return;
            achievements[id] = {
              earned: true,
              earnedAt: validTimestamp(achievement?.earnedAt),
            };
          });
          clean.workshops[slug] = {
            slug,
            mode: raw.mode === "hard" ? "hard" : "easy",
            progress: {
              easyChecked: count(rawProgress.easyChecked),
              easyTotal: count(rawProgress.easyTotal),
              hardChecked: count(rawProgress.hardChecked),
              hardTotal: count(rawProgress.hardTotal),
              easyComplete: rawProgress.easyComplete === true,
              hardComplete: rawProgress.hardComplete === true,
              updatedAt: validTimestamp(rawProgress.updatedAt),
            },
            achievements,
          };
        });
        clean.score = Object.values(clean.workshops).reduce(
          (total, workshop) =>
            total +
            BADGES.reduce(
              (subtotal, badge) =>
                subtotal +
                (workshop.achievements[badge.id]?.earned ? badge.points : 0),
              0,
            ),
          0,
        );
        clean.updatedAt = validTimestamp(source.updatedAt);
        return clean;
      }

      function readProfile() {
        try {
          return sanitizeProfile(
            JSON.parse(localStorage.getItem(PROFILE_KEY) || "{}"),
          );
        } catch (_error) {
          return sanitizeProfile({});
        }
      }

      function writeProfile(value) {
        const profile = sanitizeProfile(value);
        profile.updatedAt = new Date().toISOString();
        localStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
        return profile;
      }

      function displaySlug(slug) {
        return slug
          .split("-")
          .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
          .join(" ");
      }

      function appendText(parent, tag, text, className = "") {
        const node = document.createElement(tag);
        node.textContent = text;
        if (className) node.className = className;
        parent.append(node);
        return node;
      }

      function isVerifiedSynced(slug, claimId) {
        return verifiedByWorkshop.get(slug)?.has(claimId) === true;
      }

      function renderLocal() {
        const profile = readProfile();
        const workshops = Object.values(profile.workshops);
        const earnedCount = workshops.reduce(
          (total, workshop) =>
            total +
            BADGES.filter((badge) => workshop.achievements[badge.id]?.earned)
              .length,
          0,
        );
        document.getElementById("totalScore").textContent = String(profile.score);
        document.getElementById("earnedSummary").textContent = earnedCount
          ? `${earnedCount} badge${earnedCount === 1 ? "" : "s"} earned across ${workshops.length} workshop${workshops.length === 1 ? "" : "s"}`
          : "No badges earned yet";

        const catalog = document.getElementById("badgeCatalog");
        catalog.replaceChildren();
        BADGES.forEach((badge) => {
          const earnedWorkshops = workshops.filter(
            (workshop) => workshop.achievements[badge.id]?.earned,
          );
          const verifiedWorkshops = earnedWorkshops.filter((workshop) =>
            isVerifiedSynced(workshop.slug, badge.claimId),
          );
          const card = document.createElement("article");
          card.className = "badge";
          card.dataset.earned = String(earnedWorkshops.length > 0);
          appendText(card, "strong", `${badge.label} · ${badge.points} points`);
          appendText(card, "span", badge.description);
          appendText(
            card,
            "span",
            earnedWorkshops.length
              ? `${verifiedWorkshops.length} Verified synced · ${earnedWorkshops.length - verifiedWorkshops.length} Local unsynced`
              : "Not earned",
          );
          catalog.append(card);
        });

        const list = document.getElementById("workshopList");
        list.replaceChildren();
        if (!workshops.length) {
          appendText(list, "div", "No local workshop progress yet.", "empty");
          return;
        }
        workshops
          .sort((left, right) => left.slug.localeCompare(right.slug))
          .forEach((workshop) => {
            const card = document.createElement("article");
            card.className = "workshop";
            const detail = document.createElement("div");
            const heading = document.createElement("h3");
            const link = document.createElement("a");
            link.href = `solutions/${workshop.slug}/quest.html`;
            link.textContent = displaySlug(workshop.slug);
            heading.append(link);
            detail.append(heading);
            const easy = workshop.progress;
            const activeChecked =
              workshop.mode === "hard" ? easy.hardChecked : easy.easyChecked;
            const activeTotal =
              workshop.mode === "hard" ? easy.hardTotal : easy.easyTotal;
            appendText(
              detail,
              "p",
              `${workshop.mode === "hard" ? "Hard" : "Easy"} progress: ${activeChecked} of ${activeTotal}`,
              "muted",
            );
            const progress = document.createElement("div");
            progress.className = "progress";
            progress.setAttribute("aria-hidden", "true");
            const bar = document.createElement("span");
            bar.style.width = activeTotal
              ? `${(activeChecked / activeTotal) * 100}%`
              : "0%";
            progress.append(bar);
            detail.append(progress);
            const status = document.createElement("div");
            appendText(
              status,
              "strong",
              easy.easyComplete ? "Easy complete" : "Easy in progress",
            );
            appendText(
              status,
              "span",
              easy.hardComplete ? "Hard complete" : "Hard not complete",
              "muted",
            );
            const syncList = document.createElement("ul");
            syncList.className = "sync-list";
            BADGES.filter(
              (badge) => workshop.achievements[badge.id]?.earned,
            ).forEach((badge) => {
              const verified = isVerifiedSynced(
                workshop.slug,
                badge.claimId,
              );
              appendText(
                syncList,
                "li",
                `${badge.label}: ${verified ? "Verified synced" : "Local unsynced"}`,
                verified ? "sync-verified" : "sync-local",
              );
            });
            status.append(syncList);
            card.append(detail, status);
            list.append(card);
          });
      }

      function publicRows(metrics) {
        const candidates = [
          metrics?.achievements,
          metrics?.achievement_points,
          metrics?.verified_achievements,
          metrics?.workshop_achievements,
        ].filter(Boolean);
        for (const candidate of candidates) {
          const rows =
            candidate.leaderboard ||
            candidate.leaderboards?.verified ||
            candidate.leaderboards?.profiles ||
            candidate.verified_profiles ||
            candidate.profiles;
          if (Array.isArray(rows)) return rows;
          if (rows && typeof rows === "object") return Object.values(rows);
        }
        const fallback =
          metrics?.leaderboards?.verified_achievements ||
          metrics?.leaderboards?.achievements;
        return Array.isArray(fallback) ? fallback : [];
      }

      function canonicalClaimIds(value) {
        let candidates = [];
        if (Array.isArray(value)) {
          candidates = value;
        } else if (typeof value === "string") {
          candidates = value.split(",").map((item) => item.trim());
        } else if (value && typeof value === "object") {
          const nested =
            value.achievements ||
            value.verified_achievements ||
            value.earned_achievements ||
            value.badge_ids;
          if (nested && nested !== value) {
            return canonicalClaimIds(nested);
          }
          candidates = Object.entries(value)
            .filter(([, earned]) => earned === true)
            .map(([id]) => id);
        }
        const found = new Set(
          candidates.filter(
            (id) => typeof id === "string" && CLAIM_IDS.has(id),
          ),
        );
        return CLAIM_ORDER.filter((id) => found.has(id));
      }

      function addVerifiedAchievements(slug, value) {
        if (
          typeof slug !== "string" ||
          !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug)
        ) {
          return;
        }
        const ids = canonicalClaimIds(value);
        if (!ids.length) return;
        const merged = verifiedByWorkshop.get(slug) || new Set();
        ids.forEach((id) => merged.add(id));
        verifiedByWorkshop.set(slug, merged);
      }

      function collectVerifiedForHighlight(rows, highlight) {
        verifiedByWorkshop = new Map();
        if (!highlight) return;
        rows.forEach((row) => {
          const username = String(
            row.github_username ||
              row.github_login ||
              row.username ||
              row.login ||
              row.account ||
              row.user ||
              "",
          )
            .replace(/^@/, "")
            .toLowerCase();
          if (username !== highlight) return;
          if (Array.isArray(row.badges)) {
            row.badges.forEach((badge) => {
              if (
                !badge ||
                typeof badge !== "object" ||
                typeof badge.workshop !== "string" ||
                typeof badge.achievement !== "string"
              ) {
                return;
              }
              addVerifiedAchievements(badge.workshop, [badge.achievement]);
            });
          }
          const directSlug =
            row.workshop_slug || row.workshop || row.solution_slug || row.slug;
          const directIds =
            row.achievements ||
            row.verified_achievements ||
            row.earned_achievements ||
            row.badge_ids;
          if (directSlug) addVerifiedAchievements(directSlug, directIds);

          [row.workshops, row.workshop_achievements].forEach((entries) => {
            if (!Array.isArray(entries)) return;
            entries.forEach((entry) => {
              if (!entry || typeof entry !== "object") return;
              addVerifiedAchievements(
                entry.workshop_slug ||
                  entry.workshop ||
                  entry.solution_slug ||
                  entry.slug,
                entry.achievements ||
                  entry.verified_achievements ||
                  entry.badge_ids,
              );
            });
          });

          [
            row.achievements_by_workshop,
            row.verified_achievements_by_workshop,
            !Array.isArray(row.workshops) &&
            row.workshops &&
            typeof row.workshops === "object"
              ? row.workshops
              : null,
            !directSlug &&
            row.achievements &&
            !Array.isArray(row.achievements) &&
            typeof row.achievements === "object"
              ? row.achievements
              : null,
            !Array.isArray(row.workshop_achievements) &&
            row.workshop_achievements &&
            typeof row.workshop_achievements === "object"
              ? row.workshop_achievements
              : null,
          ].forEach((mapping) => {
            if (!mapping || typeof mapping !== "object") return;
            Object.entries(mapping).forEach(([slug, ids]) => {
              addVerifiedAchievements(slug, ids);
            });
          });
        });
      }

      function verifiedWorkshopCompletionCount(row) {
        const canonical =
          row.workshops_completed ?? row.workshop_completions;
        const numeric = Number(canonical);
        if (Number.isFinite(numeric) && numeric >= 0) return numeric;
        if (Array.isArray(row.completed_workshops)) {
          return row.completed_workshops.length;
        }
        const fallback = Number(row.completed_workshops ?? row.completions ?? 0);
        return Number.isFinite(fallback) && fallback >= 0 ? fallback : 0;
      }

      function renderPublic(rows) {
        const root = document.getElementById("publicProfiles");
        root.replaceChildren();
        root.setAttribute("aria-busy", "false");
        const highlight = localStorage
          .getItem(HIGHLIGHT_KEY)
          ?.trim()
          .toLowerCase();
        collectVerifiedForHighlight(rows, highlight);
        renderLocal();
        if (!rows.length) {
          appendText(
            root,
            "p",
            "The current metrics snapshot does not include an opt-in verified achievement profile dataset.",
            "empty",
          );
          return;
        }
        const table = document.createElement("table");
        table.className = "leaderboard";
        table.innerHTML =
          "<caption>Opt-in public verified achievement profiles</caption><thead><tr><th scope=\"col\">GitHub profile</th><th scope=\"col\">Verified workshops</th><th scope=\"col\">Verified score</th></tr></thead>";
        const body = document.createElement("tbody");
        rows.forEach((row) => {
          const username = String(
            row.github_username ||
              row.github_login ||
              row.username ||
              row.login ||
              row.account ||
              row.user ||
              "",
          ).replace(/^@/, "");
          if (!username) return;
          const score = Number(
            row.verified_score ??
              row.verified_points ??
              row.score ??
              row.points ??
              0,
          );
          const completions = verifiedWorkshopCompletionCount(row);
          const tr = document.createElement("tr");
          if (highlight && username.toLowerCase() === highlight) {
            tr.className = "highlight";
          }
          const profileCell = document.createElement("td");
          const link = document.createElement("a");
          link.href = `https://github.com/${encodeURIComponent(username)}`;
          link.target = "_blank";
          link.rel = "noopener";
          link.textContent = `@${username}`;
          profileCell.append(link);
          appendText(tr, "td", Number.isFinite(completions) ? String(completions) : "0");
          appendText(tr, "td", Number.isFinite(score) ? String(score) : "0");
          tr.prepend(profileCell);
          body.append(tr);
        });
        table.append(body);
        root.append(table);
      }

      async function loadPublic() {
        verifiedByWorkshop = new Map();
        renderLocal();
        try {
          const response = await fetch("state/metrics.json");
          if (!response.ok) throw new Error(`HTTP ${response.status}`);
          renderPublic(publicRows(await response.json()));
        } catch (_error) {
          verifiedByWorkshop = new Map();
          renderLocal();
          const root = document.getElementById("publicProfiles");
          root.replaceChildren();
          root.setAttribute("aria-busy", "false");
          appendText(
            root,
            "p",
            "Public verified achievement profiles are unavailable in this metrics snapshot.",
            "empty",
          );
        }
      }

      const status = document.getElementById("dataStatus");
      document.getElementById("exportProfile").addEventListener("click", () => {
        const payload = JSON.stringify(readProfile(), null, 2);
        const blob = new Blob([payload], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "aibast-achievement-profile.json";
        link.click();
        URL.revokeObjectURL(url);
        status.textContent = "Privacy-filtered local profile exported.";
      });
      document.getElementById("importProfile").addEventListener("click", () => {
        document.getElementById("profileFile").click();
      });
      document.getElementById("profileFile").addEventListener("change", async (event) => {
        const [file] = event.target.files;
        if (!file) return;
        try {
          writeProfile(JSON.parse(await file.text()));
          renderLocal();
          status.textContent = "Local profile imported; unknown and sensitive fields were discarded.";
        } catch (_error) {
          status.textContent = "Import failed. Choose a valid JSON profile export.";
        } finally {
          event.target.value = "";
        }
      });
      document.getElementById("resetProfile").addEventListener("click", () => {
        if (!window.confirm("Reset the local achievement score, workshop progress, and badges on this device?")) return;
        localStorage.removeItem(PROFILE_KEY);
        renderLocal();
        status.textContent = "Local achievement profile reset.";
      });

      const highlightInput = document.getElementById("githubHighlight");
      highlightInput.value = localStorage.getItem(HIGHLIGHT_KEY) || "";
      document.getElementById("saveHighlight").addEventListener("click", () => {
        const username = highlightInput.value.trim().replace(/^@/, "");
        if (!/^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$/.test(username)) {
          status.textContent = "Enter a valid GitHub username to highlight.";
          return;
        }
        localStorage.setItem(HIGHLIGHT_KEY, username);
        status.textContent = "Public-profile highlight saved locally; no authentication was performed.";
        loadPublic();
      });
      document.getElementById("clearHighlight").addEventListener("click", () => {
        localStorage.removeItem(HIGHLIGHT_KEY);
        highlightInput.value = "";
        status.textContent = "Public-profile highlight cleared.";
        loadPublic();
      });

      document.getElementById("themeToggle").addEventListener("click", (event) => {
        const dark = document.documentElement.dataset.theme !== "dark";
        document.documentElement.dataset.theme = dark ? "dark" : "light";
        event.currentTarget.textContent = dark ? "Use light theme" : "Use dark theme";
        event.currentTarget.setAttribute("aria-pressed", String(dark));
      });

      renderLocal();
      loadPublic();
    })();

})();
}

/* why: content behavior ported from why.html; the shell owns navigation and theme. */
if (document.body.dataset.page === 'why') {
(function () {
"use strict";
const runtime = sectionRuntime('why.html');
const fetch = runtime.fetch;

/* Presentation mode for why.html.
   Off by default. Slides are cloned from <main> the first time it opens, so the
   deck always says exactly what the page says. Enter with the Present button,
   the P key, or ?present=1 (add &slide=N to open on one topic, which is how you
   jump straight to an objection in a meeting). Leave with Escape. */
(() => {
  const root = document.documentElement;
  const deck = document.getElementById("deck");
  const main = document.querySelector("[data-source-main]");
  let slides = [];
  let current = 0;
  let built = false;

  function build() {
    if (built) return;
    const title = { heading: null, nodes: [] };
    const groups = [];
    let group = title;
    for (const node of Array.from(main.children)) {
      if (node.classList.contains("actions")) continue;
      if (node.tagName === "H2") {
        group = { heading: node, nodes: [] };
        groups.push(group);
      } else {
        group.nodes.push(node);
      }
    }
    const all = [title, ...groups];
    deck.innerHTML = "";
    all.forEach((item, index) => {
      const slide = document.createElement("section");
      slide.className = "slide";
      slide.tabIndex = -1;
      slide.setAttribute("role", "group");
      slide.setAttribute("aria-roledescription", "slide");
      const label = item.heading
        ? item.heading.textContent.trim()
        : document.querySelector("h1").textContent.trim();
      slide.setAttribute("aria-label", (index + 1) + " of " + all.length + ": " + label);
      const inner = document.createElement("div");
      inner.className = "slide-inner";
      if (item.heading) {
        const eyebrow = document.createElement("p");
        eyebrow.className = "slide-eyebrow";
        eyebrow.textContent = "Why the RAPP Brainstem";
        inner.appendChild(eyebrow);
        inner.appendChild(item.heading.cloneNode(true));
      }
      item.nodes.forEach((node) => inner.appendChild(node.cloneNode(true)));
      slide.appendChild(inner);
      deck.appendChild(slide);
    });

    const bar = document.createElement("div");
    bar.className = "deck-bar";
    bar.innerHTML =
      '<button type="button" data-act="prev" aria-label="Previous slide">&#8592;</button>' +
      '<button type="button" data-act="next" aria-label="Next slide">&#8594;</button>' +
      '<div class="deck-dots" id="deck-dots" role="tablist" aria-label="Slides"></div>' +
      '<span class="deck-hint">&#8592; &#8594; move &middot; T theme &middot; Esc exits</span>' +
      '<span class="deck-counter" id="deck-counter" aria-live="polite"></span>' +
      '<button type="button" data-act="exit" aria-label="Leave presentation mode">Esc</button>';
    deck.appendChild(bar);
    bar.addEventListener("click", (event) => {
      const hit = event.target.closest("[data-act]");
      if (!hit) return;
      if (hit.dataset.act === "prev") show(current - 1);
      if (hit.dataset.act === "next") show(current + 1);
      if (hit.dataset.act === "exit") close();
    });

    slides = Array.from(deck.querySelectorAll(".slide"));
    const dots = bar.querySelector("#deck-dots");
    slides.forEach((slide, index) => {
      const dot = document.createElement("button");
      dot.type = "button";
      dot.setAttribute("role", "tab");
      dot.setAttribute("aria-label", slide.getAttribute("aria-label"));
      dot.addEventListener("click", () => show(index));
      dots.appendChild(dot);
    });
    built = true;
  }

  function show(index, focus) {
    if (!slides.length) return;
    const next = Math.max(0, Math.min(index, slides.length - 1));
    slides.forEach((slide, i) => {
      slide.classList.toggle("active", i === next);
      slide.classList.toggle("prev", i < next);
    });
    deck.querySelectorAll(".deck-dots button").forEach((dot, i) => {
      dot.setAttribute("aria-current", String(i === next));
    });
    const counter = deck.querySelector("#deck-counter");
    if (counter) counter.textContent = (next + 1) + " / " + slides.length;
    current = next;
    if (focus !== false) slides[next].focus({ preventScroll: true });
    const url = new URL(location.href);
    url.searchParams.set("present", "1");
    url.searchParams.set("slide", String(next + 1));
    history.replaceState(null, "", url);
  }

  function open(index) {
    build();
    root.setAttribute("data-present", "on");
    deck.setAttribute("aria-hidden", "false");
    main.setAttribute("aria-hidden", "true");
    show(index || 0);
  }

  function close() {
    root.removeAttribute("data-present");
    deck.setAttribute("aria-hidden", "true");
    main.removeAttribute("aria-hidden");
    const url = new URL(location.href);
    url.searchParams.delete("present");
    url.searchParams.delete("slide");
    history.replaceState(null, "", url);
    document.getElementById("present-launch").focus({ preventScroll: true });
  }

  const isOn = () => root.getAttribute("data-present") === "on";

  document.getElementById("present-launch").addEventListener("click", () => open(0));
  document.getElementById("present-action").addEventListener("click", () => open(0));

  document.addEventListener("keydown", (event) => {
    const typing = /^(INPUT|TEXTAREA|SELECT)$/.test(event.target.tagName) || event.target.isContentEditable;
    if (typing || event.metaKey || event.ctrlKey || event.altKey) return;
    if (!isOn()) {
      if (event.key === "p" || event.key === "P") { event.preventDefault(); open(0); }
      return;
    }
    if (event.key === "ArrowRight" || event.key === " " || event.key === "PageDown") {
      event.preventDefault(); show(current + 1);
    } else if (event.key === "ArrowLeft" || event.key === "PageUp") {
      event.preventDefault(); show(current - 1);
    } else if (event.key === "Home") {
      event.preventDefault(); show(0);
    } else if (event.key === "End") {
      event.preventDefault(); show(slides.length - 1);
    } else if (event.key === "Escape") {
      event.preventDefault(); close();
    } else if (event.key === "f" || event.key === "F") {
      event.preventDefault();
      if (document.fullscreenElement) document.exitFullscreen();
      else if (deck.requestFullscreen) deck.requestFullscreen().catch(() => {});
    } else if (event.key === "t" || event.key === "T") {
      event.preventDefault();
      const dark = root.getAttribute("data-theme") === "dark"
        || (!root.hasAttribute("data-theme") && matchMedia("(prefers-color-scheme: dark)").matches);
      root.setAttribute("data-theme", dark ? "light" : "dark");
    }
  });

  let touchStart = null;
  deck.addEventListener("touchstart", (event) => { touchStart = event.touches[0].clientX; }, { passive: true });
  deck.addEventListener("touchend", (event) => {
    if (touchStart === null) return;
    const dx = event.changedTouches[0].clientX - touchStart;
    if (Math.abs(dx) > 50) show(current + (dx < 0 ? 1 : -1));
    touchStart = null;
  });

  const params = new URLSearchParams(location.search);
  if (params.get("present") === "1") {
    const requested = parseInt(params.get("slide") || "1", 10);
    open(Number.isFinite(requested) ? requested - 1 : 0);
  }
})();

})();
}

/* pitch: content behavior ported from pitch-playbook.html; the shell owns navigation and theme. */
if (document.body.dataset.page === 'pitch') {
(function () {
"use strict";
const runtime = sectionRuntime('pitch-playbook.html');
const fetch = runtime.fetch;

function toggleTheme(){
  const isLight = document.documentElement.getAttribute('data-theme') === 'light';
  if (isLight) {
    document.documentElement.setAttribute('data-theme', 'dark');
    localStorage.setItem('rapp-pitch-theme', 'dark');
  } else {
    document.documentElement.setAttribute('data-theme', 'light');
    localStorage.setItem('rapp-pitch-theme', 'light');
  }
}

// Two modes: 'exec' (default — just the pitch) and 'rehearse' (full deck, including speaker prep)
const allSlides = Array.from(document.querySelectorAll('.slide'));
const dotsEl = document.getElementById('dots');
const counterEl = document.getElementById('counter');
let visibleSlides = [];
let current = 0;
let mode = localStorage.getItem('rapp-pitch-mode') || 'exec';
document.documentElement.setAttribute('data-mode', mode);

function applyMode(){
  visibleSlides = allSlides.filter(s => mode === 'rehearse' || !s.hasAttribute('data-rehearse-only'));
  allSlides.forEach(s => {
    if (visibleSlides.includes(s)) {
      s.style.display = '';
    } else {
      s.style.display = 'none';
      s.classList.remove('active', 'prev');
    }
  });
  buildDots();
}

function buildDots(){
  dotsEl.innerHTML = '';
  visibleSlides.forEach((_, i) => {
    const d = document.createElement('div');
    d.className = 'dot' + (i === current ? ' active' : '');
    d.onclick = () => showSlide(i);
    dotsEl.appendChild(d);
  });
}

function showSlide(n) {
  if (n < 0 || n >= visibleSlides.length) return;
  visibleSlides.forEach((s, i) => {
    s.classList.remove('active', 'prev');
    if (i === n) s.classList.add('active');
    else if (i < n) s.classList.add('prev');
  });
  current = n;
  document.querySelectorAll('.dot').forEach((d, i) => d.classList.toggle('active', i === n));
  counterEl.textContent = `${n + 1} / ${visibleSlides.length}${mode === 'rehearse' ? ' · R' : ''}`;
  history.replaceState(null, '', `#${n}`);
}

function next() { if (current < visibleSlides.length - 1) showSlide(current + 1); }
function prev() { if (current > 0) showSlide(current - 1); }

function toggleMode(){
  const prevActive = visibleSlides[current] || allSlides[0];
  mode = (mode === 'exec') ? 'rehearse' : 'exec';
  localStorage.setItem('rapp-pitch-mode', mode);
  document.documentElement.setAttribute('data-mode', mode);
  applyMode();
  const idx = visibleSlides.indexOf(prevActive);
  current = idx >= 0 ? idx : 0;
  showSlide(current);
}

function downloadAgent(url, filename) {
  fetch(url).then(r => r.blob()).then(b => {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(b);
    a.download = filename;
    a.click();
    URL.revokeObjectURL(a.href);
  });
}

applyMode();
const initialSlide = parseInt(location.hash.slice(1), 10);
showSlide(!isNaN(initialSlide) && initialSlide >= 0 && initialSlide < visibleSlides.length ? initialSlide : 0);

// Keyboard navigation
document.addEventListener('keydown', e => {
  if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') { e.preventDefault(); next(); }
  if (e.key === 'ArrowLeft' || e.key === 'PageUp') { e.preventDefault(); prev(); }
  if (e.key === 'Home') { e.preventDefault(); showSlide(0); }
  if (e.key === 'End') { e.preventDefault(); showSlide(visibleSlides.length - 1); }
  if (e.key === 't' || e.key === 'T') { e.preventDefault(); toggleTheme(); }
  if (e.key === 'r' || e.key === 'R') { e.preventDefault(); toggleMode(); }
});

// Touch / swipe
let touchX = 0;
document.addEventListener('touchstart', e => { touchX = e.touches[0].clientX; }, {passive:true});
document.addEventListener('touchend', e => {
  const dx = e.changedTouches[0].clientX - touchX;
  if (Math.abs(dx) > 50) { dx < 0 ? next() : prev(); }
});


runtime.bind({toggleTheme,toggleMode,prev,next});

})();
}
