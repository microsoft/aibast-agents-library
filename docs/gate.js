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

  function gate() {
    if (invited()) return;
    var hide = document.querySelectorAll("[data-invite-only]");
    if (!hide.length) return;
    hide[0].parentNode.insertBefore(card(), hide[0]);
    for (var i = 0; i < hide.length; i++) hide[i].style.display = "none";
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", gate);
  else gate();
})();
