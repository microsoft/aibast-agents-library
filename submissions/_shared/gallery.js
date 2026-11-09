/* Gallery view. Reads one document from the library's static API and lays it out the way the
   Copilot Studio Gallery shows a solution: hero, agent table, tags, Overview / Agents / Files,
   and a rail that offers the recorded demo before the download. No live GitHub calls, no
   cache-busting: the API's hashes are the freshness signal (rapp-static-api/1.1). */
(function () {
  "use strict";
  var body = document.body;
  var root = body.dataset.api ? body.dataset.api.replace(/api\/v1\/.*$/, "") : "../../";

  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (key) {
      if (key === "text") node.textContent = attrs[key];
      else if (key === "html") node.innerHTML = attrs[key];
      else node.setAttribute(key, attrs[key]);
    });
    (children || []).forEach(function (child) { if (child) node.appendChild(child); });
    return node;
  }
  function initials(name) {
    return name.split(/\s+/).slice(0, 2).map(function (w) { return w.charAt(0); }).join("").toUpperCase();
  }
  function chips(items, cls) {
    return el("div", { class: "g-chips" }, items.map(function (item) {
      return el("span", { class: "g-chip " + cls, text: item.name || item });
    }));
  }

  function renderSolution(doc) {
    var main = document.getElementById("solution");
    main.innerHTML = "";
    var agent = doc.agents[0];
    var counts = doc.counts;

    main.appendChild(el("a", { class: "g-back", href: "../index.html", text: "← Back to gallery" }));

    var meta = el("div", { class: "g-meta" }, [
      el("span", {}, [
        el("span", { class: "g-avatar", text: initials(doc.author.name) }),
        document.createTextNode("by "),
        el("strong", { text: doc.author.name })
      ]),
      el("span", { text: "Version " + doc.version }),
      el("span", { text: "Updated " + (doc.updated || "") })
    ]);
    var countsRow = el("div", { class: "g-counts" }, [
      el("span", { html: "<strong>" + counts.agents + "</strong> agent" }),
      el("span", { html: "<strong>" + counts.skills + "</strong> skills" }),
      el("span", { html: "<strong>" + counts.knowledge + "</strong> knowledge files" }),
      counts.tools ? el("span", { html: "<strong>" + counts.tools + "</strong> tools" }) : null
    ]);
    var head = el("div", { class: "g-hero-head" }, [
      el("p", { class: "g-kicker", text: "Agents" }),
      el("h1", { text: doc.name }),
      el("p", { class: "g-lead", text: doc.description }),
      meta,
      countsRow
    ]);
    var table = el("table", { class: "g-agent-table", "aria-label": "Agents and their components" }, [
      el("thead", {}, [el("tr", {}, [el("th", { text: "Agent" }), el("th", { text: "Skills" }), el("th", { text: "Knowledge" })])]),
      el("tbody", {}, [el("tr", {}, [
        el("td", {}, [el("strong", { text: agent.name }), el("div", { class: "g-counts", text: "Copilot Studio agent" })]),
        el("td", {}, [chips(agent.skills, "skill")]),
        el("td", {}, [chips(agent.knowledge, "knowledge")])
      ])])
    ]);
    var tags = el("div", { class: "g-tags" }, [doc.category ? el("span", { class: "g-tag category", text: doc.category }) : null].concat(
      doc.tags.map(function (tag) { return el("span", { class: "g-tag", text: tag }); })
    ));
    main.appendChild(el("section", { class: "g-hero" }, [head, el("div", { class: "g-agent-band" }, [table]), tags]));

    // Tabs
    var panels = {
      overview: el("div", { class: "g-panel g-readme", html: doc.readme_html }),
      agents: el("div", { class: "g-panel", hidden: "" }, [
        el("h2", { text: agent.name }),
        el("p", { class: "g-intro", text: "Template " + agent.template + ". Model: " + agent.model + ". The greeting below is what a visitor sees first." }),
        el("div", { class: "g-greeting", text: agent.greeting }),
        el("h3", { text: "Skills" })
      ].concat(agent.skills.map(function (skill) {
        return el("div", { class: "g-skill" }, [el("code", { text: skill.name }), el("p", { text: skill.description })]);
      })).concat([el("h3", { text: "Knowledge files" }), el("ul", {}, agent.knowledge.map(function (name) { return el("li", {}, [el("code", { text: name })]); }))])),
      files: el("div", { class: "g-panel", hidden: "" }, [
        el("p", { class: "g-intro", text: "The exploded unmanaged solution, exactly as the download packages it." }),
        el("ul", { class: "g-files" }, doc.files.map(function (name) { return el("li", { text: "solution/" + name }); }))
      ])
    };
    var tabs = el("div", { class: "g-tabs", role: "tablist" });
    [["overview", "Overview", null], ["agents", "Agents", counts.agents], ["files", "Files", counts.files]].forEach(function (spec, index) {
      var tab = el("button", { class: "g-tab", role: "tab", type: "button", "aria-selected": index === 0 ? "true" : "false", text: spec[1] });
      if (spec[2] !== null) tab.appendChild(el("small", { text: String(spec[2]) }));
      tab.addEventListener("click", function () {
        Array.prototype.forEach.call(tabs.children, function (t) { t.setAttribute("aria-selected", "false"); });
        tab.setAttribute("aria-selected", "true");
        Object.keys(panels).forEach(function (key) { panels[key].hidden = key !== spec[0]; });
      });
      tabs.appendChild(tab);
    });
    var left = el("div", {}, [tabs, panels.overview, panels.agents, panels.files]);

    // Rail: demo first, then download.
    var tryCard = el("div", { class: "g-card" }, [
      el("h3", { text: "Try it without deploying" }),
      el("p", { text: "Watch the agent answer each sample prompt in a recorded Microsoft 365 Copilot demo. Nothing to install, no environment needed." }),
      doc.try.page ? el("a", { class: "g-btn primary", href: root + doc.try.page, text: "Open the demo" }) : null,
      el("ul", { class: "g-try-list" }, doc.try.scenarios.map(function (href, i) {
        var skill = agent.skills[i];
        return el("li", {}, [el("a", { href: root + href, text: skill ? skill.name.replace(/-/g, " ") : "Scenario " + (i + 1) })]);
      }))
    ]);
    var trust = el("input", { type: "checkbox", id: "g-trust" });
    var download = el("a", { class: "g-btn secondary", href: doc.download.url, "aria-disabled": "true", text: "Download ZIP" });
    trust.addEventListener("change", function () { download.setAttribute("aria-disabled", trust.checked ? "false" : "true"); });
    var downloadCard = el("div", { class: "g-card" }, [
      el("h3", { text: "Import into your environment" }),
      el("label", { class: "g-trust", for: "g-trust" }, [trust, el("span", { text: "I'll review this sample and only import it if I trust the source. It is provided as-is and is not covered by Microsoft Support." })]),
      download,
      el("p", { class: "g-sha", text: doc.download.sha256 ? "sha256 " + doc.download.sha256 : "" }),
      el("p", { html: 'Unmanaged solution. <a href="README.md">README</a> · <a href="' + root + doc.source.folder + '">source folder</a>' })
    ]);
    main.appendChild(el("div", { class: "g-body" }, [left, el("aside", { class: "g-rail" }, [tryCard, downloadCard])]));
    document.title = doc.name + " - AIBAST Agents Library";
  }

  function renderIndex(index) {
    var grid = document.getElementById("gallery-grid");
    grid.innerHTML = "";
    index.solutions.forEach(function (card) {
      grid.appendChild(el("a", { class: "g-tile", href: card.slug + "/" }, [
        el("span", { class: "g-tag category", text: card.category || "Solution" }),
        el("h2", { text: card.name }),
        el("p", { text: card.description }),
        el("div", { class: "g-counts" }, [
          el("span", { html: "<strong>" + card.counts.agents + "</strong> agent" }),
          el("span", { html: "<strong>" + card.counts.skills + "</strong> skills" }),
          el("span", { html: "<strong>" + card.counts.knowledge + "</strong> knowledge files" })
        ])
      ]));
    });
    var count = document.getElementById("gallery-count");
    if (count) count.textContent = index.count + (index.count === 1 ? " solution" : " solutions");
  }

  var api = body.dataset.api;
  if (!api) return;
  fetch(api).then(function (r) { if (!r.ok) throw new Error(r.status + " " + api); return r.json(); })
    .then(function (doc) { if (doc.solutions) renderIndex(doc); else renderSolution(doc); })
    .catch(function (err) {
      var target = document.getElementById("solution") || document.getElementById("gallery-grid");
      if (target) target.innerHTML = '<p class="g-loading">Could not load ' + api + " (" + err.message + ").</p>";
    });
})();
