// Invite gate for the Brainstem one-liner.
// The install line is shown only to invited people. An invite link carries ?invite=<code>;
// the browser remembers it, so the invited person sees the line on every visit.
// Everyone else sees one "Request access" button. The installer itself is unchanged.
(function () {
  "use strict";
  // One setting: where access requests go (a Microsoft Form; answers stay in Microsoft's systems).
  var REQUEST_URL =
    "https://forms.cloud.microsoft/Pages/ResponsePage.aspx?id=v4j5cvGGr0GRqy180BHbR7RNABRLLw9Eq-9okV_7Z-hUOEY3QjQ3V1RJUk43OEs4WEkzTDZQUVdNMC4u";
  var KEY = "aibast-brainstem-invite";

  function invited() {
    var code = "";
    try { code = new URLSearchParams(location.search).get("invite") || ""; } catch (e) { code = ""; }
    code = code.replace(/[^A-Za-z0-9_-]/g, "").slice(0, 64);
    try {
      if (code) localStorage.setItem(KEY, code);
      return Boolean(code || localStorage.getItem(KEY));
    } catch (e) {
      return Boolean(code);
    }
  }

  function card() {
    var box = document.createElement("section");
    box.className = "invite-gate";
    box.style.cssText = "max-width:760px;margin:24px auto;padding:24px;border:1px solid var(--cp-border,#3a3f4b);border-radius:12px;text-align:center";
    box.setAttribute("aria-labelledby", "invite-gate-title");
    box.innerHTML =
      '<h2 id="invite-gate-title" style="margin:0 0 8px">The Brainstem is invite only</h2>' +
      "<p style=\"margin:0 0 16px\">We open it to a small group at a time so every new person gets real help. " +
      "Ask for access and we will send you your install link.</p>" +
      '<a class="hero-action primary" target="_blank" rel="noopener">Request access</a>';
    box.querySelector("a").href = REQUEST_URL;
    return box;
  }

  // The Brainstem one-liner as it appears in a command block (not the separate
  // community_rapp installer, which stays open).
  var LINE = /(curl|irm)\s[^\n]*?(?<!community_rapp\/)install\.(sh|ps1)/;

  function commandBlocks() {
    var found = [];
    var nodes = document.querySelectorAll("pre, code, .cmd, .command, .prompt, .code-block, [id$='-cmd']");
    for (var i = 0; i < nodes.length; i++) {
      var el = nodes[i];
      if (el.closest("[data-invite-only]")) continue;
      if (LINE.test(el.textContent || "")) found.push(el);
    }
    // Keep only the outermost matching block.
    return found.filter(function (el) {
      return !found.some(function (other) { return other !== el && other.contains(el); });
    });
  }

  function note() {
    var a = document.createElement("a");
    a.href = REQUEST_URL;
    a.target = "_blank";
    a.rel = "noopener";
    a.textContent = "Invite only: request access";
    return a;
  }

  function gate() {
    if (invited()) return;
    var marked = Array.prototype.slice.call(document.querySelectorAll("[data-invite-only]"));
    var blocks = commandBlocks();
    if (!marked.length && !blocks.length) return;
    var first = marked[0] || blocks[0];
    first.parentNode.insertBefore(card(), first);
    marked.forEach(function (el) { el.style.display = "none"; });
    blocks.forEach(function (el) {
      if (el !== first) el.parentNode.insertBefore(note(), el);
      el.style.display = "none";
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", gate);
  else gate();
})();
