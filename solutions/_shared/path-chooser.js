(async function () {
  "use strict";
  const chooser = document.getElementById("chooser");
  const screen = document.getElementById("screen");
  let data;
  try {
    const response = await fetch("api/v1/paths.json");
    if (!response.ok) throw new Error("Path data returned " + response.status);
    data = await response.json();
  } catch (error) {
    document.getElementById("load-status").textContent =
      "The questions could not load. Choose a path below or reload the page. " + error.message;
    return;
  }
  const params = () => new URLSearchParams(location.search);
  const el = (tag, text, attributes = {}) => {
    const node = document.createElement(tag);
    if (text) node.textContent = text;
    for (const [key, value] of Object.entries(attributes)) node.setAttribute(key, value);
    return node;
  };
  const button = (text, action, className = "answer") => {
    const node = el("button", text, {type: "button", class: className});
    node.onclick = action;
    return node;
  };
  const link = (text, href, className = "") => el("a", text, {href, class: className});
  const routeFor = p => data.routes.find(route => route.id === p.get("goal"));
  const have = p => (p.get("have") || "").split(",").filter(value => value && value !== "none");
  function go(changes) {
    const p = params();
    for (const [key, value] of Object.entries(changes)) {
      if (value === null) p.delete(key);
      else p.set(key, value);
    }
    history.pushState(null, "", "?" + p);
    render();
  }
  function plan(p) {
    const route = routeFor(p);
    const area = p.get("area");
    if (!route || (route.area && !route.solutions.includes(area))) return null;
    const missing = data.prerequisites.filter(item => route.needs.includes(item.id) && !have(p).includes(item.id));
    const steps = route.steps.map(step => ({
      label: step.label,
      url: step.url || data.solutions[area][step.destination]
    }));
    if (missing.length) steps.unshift({
      label: "Get the missing tools and access",
      url: missing[0].url
    });
    return {route, missing, steps};
  }
  function question(id) {
    const q = data.questions.find(item => item.id === id);
    screen.append(el("h1", q.title, {tabindex: "-1"}));
    return q;
  }
  function somethingElse() {
    screen.append(button(data.something_else.label, () =>
      go({screen: "request", from: document.getElementById("screen").dataset.view}), "quiet"));
  }
  function summary(p) {
    const dl = el("dl");
    for (const q of data.questions) {
      const answer = p.get(q.id);
      if (!answer) continue;
      const label = q.id === "area" ? data.solutions[answer]?.name || answer :
        answer.split(",").map(value => q.answers.find(a => a.id === value)?.label || value).join(", ");
      dl.append(el("dt", q.title), el("dd", label));
    }
    return dl;
  }
  function render() {
    const p = params();
    const route = routeFor(p);
    let view = p.get("screen");
    if (!["goal", "have", "area", "all", "request"].includes(view)) {
      view = !route ? "goal" : route.needs.length && !p.has("have") ? "have" :
        route.area && !route.solutions.includes(p.get("area")) ? "area" : "preview";
    }
    screen.replaceChildren();
    screen.dataset.view = view;
    screen.className = view === "preview" ? "preview" : view === "goal" ? "opener" : "";
    document.getElementById("intro").textContent = data.intro;
    const sequence = ["goal", ...(route?.needs.length ? ["have"] : []), ...(route?.area ? ["area"] : [])];
    document.getElementById("progress").textContent = sequence.includes(view) ?
      `Question ${sequence.indexOf(view) + 1} of ${route ? sequence.length : 3}` : "";
    const back = document.getElementById("back");
    back.hidden = view === "goal";
    back.onclick = () => {
      const previous = view === "request" || view === "all" ? p.get("from") || "goal" :
        view === "preview" ? sequence.at(-1) :
        sequence.includes(view) ? sequence[Math.max(0, sequence.indexOf(view) - 1)] : "goal";
      go({screen: previous});
    };
    document.getElementById("browse").onclick = event => {
      event.preventDefault();
      go({screen: "all", from: view});
    };
    if (view === "goal") {
      const q = question("goal");
      const answers = el("div", "", {class: "answers"});
      for (const answer of q.answers) {
        const choice = button(answer.label, () => {
        const same = p.get("goal") === answer.id;
        go({goal: answer.id, have: same ? p.get("have") : null,
          area: same ? p.get("area") : null, screen: null});
        });
        choice.setAttribute("aria-pressed", String(p.get("goal") === answer.id));
        answers.append(choice);
      }
      screen.append(answers);
      somethingElse();
    } else if (view === "have") {
      const q = question("have");
      const form = el("form");
      const choices = el("div", "", {class: "choices"});
      for (const answer of q.answers) {
        const label = el("label", "", {class: "check"});
        const input = el("input", "", {type: "checkbox", name: "have", value: answer.id});
        input.checked = (p.get("have") || "").split(",").includes(answer.id);
        input.onchange = () => {
          for (const other of choices.querySelectorAll("input")) {
            if (other !== input && (answer.id === "none" || other.value === "none")) other.checked = false;
          }
          const values = [...choices.querySelectorAll("input:checked")].map(node => node.value);
          const current = params();
          if (values.length) current.set("have", values.join(","));
          else current.delete("have");
          history.replaceState(null, "", "?" + current);
        };
        label.append(input, document.createTextNode(answer.label));
        choices.append(label);
      }
      form.append(choices, el("button", "Continue", {type: "submit", class: "primary"}));
      form.onsubmit = event => {
        event.preventDefault();
        if (!params().has("have")) {
          choices.setAttribute("role", "alert");
          if (!form.querySelector(".selection-error")) form.prepend(el("p", "Choose what you have, or None of these yet.", {class: "selection-error"}));
          return;
        }
        go({screen: null});
      };
      screen.append(form);
      somethingElse();
    } else if (view === "area") {
      question("area");
      const search = el("input", "", {type: "search", placeholder: "Search industry, role or agent", "aria-label": "Search industry, role or agent"});
      const results = el("div", "", {class: "results", "aria-label": "Suggested agents"});
      const count = el("p", "", {class: "intro", role: "status"});
      const chosen = p.get("area");
      if (chosen && data.solutions[chosen]) screen.append(el("p", "Your previous choice: " + data.solutions[chosen].name));
      const matches = () => {
        const words = search.value.toLowerCase().trim().split(/\s+/);
        const items = route.solutions.filter(slug => {
          const item = data.solutions[slug];
          return words.every(word => [item.name, ...item.industries, ...item.personas].join(" ").toLowerCase().includes(word));
        });
        results.replaceChildren();
        for (const slug of items.slice(0, 4)) {
          const item = data.solutions[slug];
          results.append(button(item.name + " - " + item.industries.join(", "), () => go({area: slug, screen: null})));
        }
        count.textContent = items.length > 4 ? `Showing 4 of ${items.length}. Type more to narrow the list.` : "";
        if (!items.length) results.append(button(data.something_else.no_match, () => go({screen: "request", from: "area"}), "quiet"));
      };
      search.oninput = matches;
      screen.append(search, results, count);
      matches();
      somethingElse();
    } else if (view === "all") {
      screen.append(el("h1", "Every path", {tabindex: "-1"}));
      const choices = el("div", "", {class: "answers"});
      for (const item of data.routes) choices.append(button(item.label, () => {
        const same = p.get("goal") === item.id;
        go({goal: item.id, have: same ? p.get("have") : null,
          area: same ? p.get("area") : null, screen: null});
      }));
      screen.append(choices);
      somethingElse();
    } else if (view === "request") {
      screen.append(el("h1", data.something_else.title, {tabindex: "-1"}), summary(p));
      const form = el("form");
      const input = el("input", "", {type: "text", name: "text", maxlength: String(data.something_else.max_length), required: "", "aria-describedby": "request-hint", "aria-label": "What were you looking for?"});
      input.value = (p.get("text") || "").slice(0, data.something_else.max_length);
      input.oninput = () => {
        const current = params();
        current.set("text", input.value);
        history.replaceState(null, "", "?" + current);
      };
      form.append(el("p", data.something_else.hint, {id: "request-hint"}), input,
        el("p", "Continue to the public request form. Your text and answers will appear there; copy them into the form."),
        el("button", "Continue to request form", {type: "submit", class: "primary"}));
      form.onsubmit = event => {
        event.preventDefault();
        if (!input.value.trim()) { input.setCustomValidity("Describe the task you were looking for."); input.reportValidity(); return; }
        const query = params();
        query.set("text", input.value.trim());
        query.delete("screen");
        query.delete("from");
        location.href = data.something_else.destination + "?" + query;
      };
      input.addEventListener("input", () => input.setCustomValidity(""));
      screen.append(form);
      const nearest = plan(p);
      const fallback = new URLSearchParams(p);
      if (!nearest) {
        fallback.set("goal", "basics");
        fallback.delete("area");
      }
      fallback.delete("screen");
      screen.append(link("Meanwhile, the closest we have is " + (nearest?.route.label || data.routes.find(r => r.id === "basics").label), "?" + fallback, "secondary"));
    } else {
      const selected = plan(p);
      screen.append(el("h1", "Here is your path", {tabindex: "-1"}));
      const content = el("div", "", {class: "route-content"});
      const details = el("div");
      const requirements = el("div");
      details.append(el("p", selected.route.label + (selected.route.area ? ": " + data.solutions[p.get("area")].name : "")));
      if (selected.route.intro) details.append(el("p", selected.route.intro));
      details.append(el("p", selected.route.outcome + " " + selected.route.time + "."));
      const steps = el("ol", "", {class: "route-list"});
      for (const step of selected.steps) {
        const li = el("li", step.label, {"data-destination": step.url});
        steps.append(li);
      }
      details.append(steps);
      if (selected.missing.length) {
        const missing = el("div", "", {class: "missing"});
        for (const item of selected.missing) missing.append(el("p", "Missing: " + item.label + ". " + item.how));
        const help = new URL(data.help.url, location.href);
        const saved = new URLSearchParams(p);
        saved.delete("screen");
        help.searchParams.set("path", saved.toString());
        help.searchParams.set("pathStep", "1");
        help.searchParams.set("pathHelp", "1");
        missing.append(link(data.help.label, help.href));
        requirements.append(missing);
      }
      requirements.append(el("h2", "What you need"));
      const needs = el("ul", "", {class: "needs"});
      for (const item of selected.route.checklist) needs.append(el("li", item));
      requirements.append(needs);
      content.append(details, requirements);
      screen.append(content);
      const first = new URL(selected.steps[0].url, location.href);
      const saved = new URLSearchParams(p);
      saved.delete("screen");
      first.searchParams.set("path", saved.toString());
      first.searchParams.set("pathStep", "1");
      const other = new URLSearchParams(p);
      other.set("screen", "all");
      other.set("from", "preview");
      screen.append(link("Start step 1", first.href, "primary"),
        button("Change my answers", () => go({screen: "goal"}), "quiet secondary"),
        link("Other paths", "?" + other, "secondary"));
    }
    document.getElementById("fallback").hidden = true;
    chooser.hidden = false;
    screen.querySelector("h1")?.focus({preventScroll: true});
  }
  window.addEventListener("popstate", render);
  render();
})();
