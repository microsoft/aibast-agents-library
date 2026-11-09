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
