(async function () {
  "use strict";
  const script = document.querySelector("script[data-path-strip]");
  const root = new URL("../../", script.src);
  const current = new URL(location.href);
  // start.html?path=cowork names the Cowork walk-through; it is not a set of path answers.
  const saved = current.searchParams.get("path") === "cowork" ? null : current.searchParams.get("path");
  const request = location.pathname.endsWith("/request-info.html") && current.searchParams.has("text");
  if (!saved && !request) return;
  const answers = new URLSearchParams(saved || current.search);
  const make = (tag, text, href) => {
    const node = document.createElement(tag);
    node.textContent = text;
    if (href) node.href = href;
    return node;
  };
  const chooser = new URL("paths.html", root);
  answers.delete("screen");
  chooser.search = answers.toString();
  const change = new URL(chooser);
  change.searchParams.set("screen", "goal");
  let data;
  const region = make("aside", "");
  region.id = "your-path";
  region.setAttribute("aria-label", "Your path");
  region.style.cssText = "position:relative;z-index:101;padding:10px 16px;background:var(--cp-surface,Canvas);color:var(--cp-text,CanvasText);border-bottom:1px solid var(--cp-border,GrayText);font:14px/1.5 var(--cp-font,system-ui);display:flex;flex-wrap:wrap;gap:6px 16px;align-items:center";
  document.body.prepend(region);
  try {
    const response = await fetch(new URL("api/v1/paths.json", root));
    if (!response.ok) throw new Error("Path data returned " + response.status);
    data = await response.json();
    const route = data.routes.find(item => item.id === answers.get("goal"));
    const area = answers.get("area");
    if (request) {
      const summary = make("section", "");
      summary.id = "path-request-summary";
      summary.style.cssText = "margin:16px auto;padding:16px;max-width:760px;background:var(--cp-surface,Canvas);overflow-wrap:anywhere";
      const text = (answers.get("text") || "").slice(0, data.something_else.max_length);
      if (text) summary.append(make("p", "You were looking for: " + text));
      for (const q of data.questions) {
        const value = answers.get(q.id);
        if (value) summary.append(make("p", q.title + " " + (q.id === "area" ?
          data.solutions[value]?.name || value :
          value.split(",").map(id => q.answers.find(a => a.id === id)?.label || id).join(", "))));
      }
      const nearest = new URL(chooser);
      if (!route || route.area && !route.solutions.includes(area)) {
        nearest.searchParams.set("goal", "basics");
        nearest.searchParams.delete("area");
      }
      summary.append(make("p", "Copy these details into the request form below. They are not submitted automatically."),
        make("a", "Meanwhile, the closest we have is " + (route && (!route.area || route.solutions.includes(area)) ? route.label : data.routes.find(r => r.id === "basics").label), nearest.href));
      document.querySelector("main").prepend(summary);
    }
    if (!saved) { region.remove(); return; }
    if (!route || route.area && !route.solutions.includes(area)) throw new Error("These path answers are incomplete.");
    const have = (answers.get("have") || "").split(",");
    const missing = data.prerequisites.filter(item => route.needs.includes(item.id) && !have.includes(item.id));
    const steps = route.steps.map(step => ({label: step.label, url: step.url || data.solutions[area][step.destination]}));
    if (missing.length) steps.unshift({label: "Get the missing tools and access", url: missing[0].url});
    const number = Number(current.searchParams.get("pathStep"));
    if (!Number.isInteger(number) || number < 1 || number > steps.length) throw new Error("This path step is not valid.");
    const expected = new URL(steps[number - 1].url, root);
    const help = new URL(data.help.url, root);
    const helping = current.searchParams.get("pathHelp") === "1" && number === 1 &&
      missing.length && current.pathname === help.pathname && current.hash === help.hash;
    if (expected.pathname !== current.pathname && !helping) throw new Error("This page is not the selected path step.");
    region.append(make("span", `Your path: step ${number} of ${steps.length}`),
      make("a", "Back to my path", chooser.href),
      make("a", "Not what you wanted? Change my answers", change.href));
    if (helping || number < steps.length) {
      const next = new URL(steps[helping ? 0 : number].url, root);
      next.searchParams.set("path", answers.toString());
      next.searchParams.set("pathStep", String(helping ? 1 : number + 1));
      region.append(make("a", helping ? "Return to getting ready" : "Next step: " + steps[number].label, next.href));
    }
    document.addEventListener("click", event => {
      const anchor = event.target.closest("a[href]");
      if (!anchor || anchor.closest("#your-path")) return;
      const target = new URL(anchor.href);
      if (missing.length && target.pathname === help.pathname && target.hash === help.hash) {
        target.searchParams.set("path", answers.toString());
        target.searchParams.set("pathStep", "1");
        target.searchParams.set("pathHelp", "1");
        anchor.href = target.href;
        return;
      }
      const index = steps.findIndex(step => {
        const candidate = new URL(step.url, root);
        return candidate.origin === target.origin && candidate.pathname === target.pathname &&
          [...candidate.searchParams].every(([key, value]) => target.searchParams.get(key) === value);
      });
      if (index < 0) return;
      target.searchParams.set("path", answers.toString());
      target.searchParams.set("pathStep", String(index + 1));
      anchor.href = target.href;
    });
  } catch (error) {
    region.append(make("span", "Your path could not load: " + error.message),
      make("a", "Back to my path", chooser.href),
      make("a", "Change my answers", change.href));
  }
})();
