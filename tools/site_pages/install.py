"""The Install page, written for the person who has never opened a terminal.

One promise, one line, one button. The command for the visitor's own computer is chosen for them
(Homebrew, rustup, VS Code and Docker Desktop all learned this); everything else sits below the
fold in plain words. The installer scripts themselves stay at their root addresses and are never
generated here. Styles use the shared tokens only."""

import html

PAGES_BASE = "https://microsoft.github.io/aibast-agents-library/"
MAC_CMD = f"curl -fsSL {PAGES_BASE}install.sh | bash"
WIN_CMD = f"irm {PAGES_BASE}install.ps1 | iex"
COPILOT_PROMPT = ("Go and read https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/docs/start/skill.md "
                  "and set up my Brainstem for me.")
OFFICE_HOURS_SIGNUP = ("https://forms.cloud.microsoft/Pages/ResponsePage.aspx?id="
                       "v4j5cvGGr0GRqy180BHbR7RNABRLLw9Eq-9okV_7Z-hUQVBKS0NWREVQWFZKVVk4VFRWV05KNlZaWS4u")
GET_HELP_FORM = ("https://forms.cloud.microsoft/Pages/ResponsePage.aspx?id="
                 "v4j5cvGGr0GRqy180BHbR7RNABRLLw9Eq-9okV_7Z-hURVhJVVozNURGOE85SkI4VkFaOVhLTTNLUC4u")


def e(value):
    return html.escape(str(value), quote=True)


STYLE = """<style>
.in-hero{text-align:center;padding:56px 0 24px}
.in-hero .kick{color:var(--cp-accent);font-weight:700;letter-spacing:.08em;text-transform:uppercase;font-size:12px}
.in-hero h1{font-size:clamp(34px,5vw,56px);line-height:1.05;margin:12px auto 16px;max-width:820px;letter-spacing:-.02em}
.in-hero .lede{font-size:19px;color:var(--cp-text-muted);max-width:680px;margin:0 auto}
.in-box{max-width:820px;margin:28px auto 0;background:var(--cp-surface);border:1px solid var(--cp-border);border-radius:var(--cp-radius-lg,12px);padding:20px;text-align:left}
.in-os{display:flex;gap:6px;margin-bottom:12px}
.in-os button{border:1px solid var(--cp-border);background:transparent;color:var(--cp-text-muted);padding:7px 14px;border-radius:999px;font:inherit;font-size:14px;cursor:pointer}
.in-os button[aria-selected="true"]{background:var(--cp-text);color:var(--cp-bg);border-color:var(--cp-text);font-weight:600}
.in-cmd{display:grid;grid-template-columns:1fr auto;gap:12px;align-items:center;background:var(--cp-bg);border:1px solid var(--cp-border);border-radius:var(--cp-radius,8px);padding:14px 16px}
.in-cmd code{font-size:17px;line-height:1.5;word-break:break-all;color:var(--cp-text)}
.in-cmd code::before{content:"$ ";color:var(--cp-text-muted)}
.in-cmd[data-os="windows"] code::before{content:"> "}
.in-copy{background:var(--cp-accent);color:var(--cp-accent-fg,#0b0f1a);border:0;border-radius:var(--cp-radius,8px);padding:14px 22px;font:inherit;font-weight:700;font-size:16px;cursor:pointer;white-space:nowrap}
.in-copy:hover{filter:brightness(1.08)}
.in-hint{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;color:var(--cp-text-muted);font-size:14px;margin:12px 2px 0}
.in-hint a{color:var(--cp-link)}
.in-then{margin:18px 0 0;padding-top:16px;border-top:1px solid var(--cp-border);display:flex;gap:14px;align-items:center;flex-wrap:wrap}
.in-then strong{font-size:15px}
.in-then code{background:var(--cp-bg);border:1px solid var(--cp-border);border-radius:6px;padding:3px 8px}
.in-live{display:none;margin-top:14px;padding:12px 14px;border-radius:var(--cp-radius,8px);background:var(--cp-bg);border:1px solid var(--cp-accent);color:var(--cp-text)}
.in-live.on{display:flex;gap:10px;align-items:center;justify-content:space-between;flex-wrap:wrap}
.in-live .btn{padding:8px 14px}
.in-alt{max-width:820px;margin:14px auto 0;text-align:center;color:var(--cp-text-muted);font-size:15px}
.in-alt details{margin-top:10px;text-align:left;background:var(--cp-surface);border:1px solid var(--cp-border);border-radius:var(--cp-radius,8px);padding:12px 16px}
.in-alt summary{cursor:pointer;color:var(--cp-text);font-weight:600}
.in-alt .in-cmd{margin-top:10px}
.in-alt .in-cmd code{font-size:15px}
.in-alt .in-cmd code::before{content:""}
.in-sec{max-width:1000px;margin:64px auto 0}
.in-sec h2{font-size:28px;letter-spacing:-.01em;margin:0 0 6px}
.in-honest{margin-top:40px}.in-honest .card{padding:22px 26px;border-color:var(--cp-accent);min-height:0;display:block}.in-honest h2{font-size:20px}.in-honest .sub{margin:0;line-height:1.55}.in-honest a{color:var(--cp-link)}
.in-sec .sub{color:var(--cp-text-muted);font-size:17px;margin:0 0 22px}
.in-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.in-grid .card{padding:22px}
.in-grid h3{margin:0 0 8px;font-size:18px}
.in-grid p{margin:0;color:var(--cp-text-muted);line-height:1.5}
.in-grid .num{display:inline-grid;place-items:center;width:34px;height:34px;border-radius:50%;background:var(--cp-accent);color:var(--cp-accent-fg,#0b0f1a);font-weight:800;margin-bottom:12px}
.in-facts{display:grid;grid-template-columns:repeat(2,1fr);gap:12px 28px}
.in-facts div{display:flex;gap:12px;align-items:flex-start;padding:14px 0;border-top:1px solid var(--cp-border)}
.in-facts b{color:var(--cp-text)}
.in-facts span{color:var(--cp-text-muted)}
.in-facts .tick{color:var(--cp-accent);font-weight:800}
.in-path{display:grid;grid-template-columns:repeat(3,1fr);gap:0;border:1px solid var(--cp-border);border-radius:var(--cp-radius-lg,12px);overflow:hidden}
.in-path > div{padding:22px;border-left:1px solid var(--cp-border)}
.in-path > div:first-child{border-left:0;background:var(--cp-surface)}
.in-path .tag{margin-bottom:10px}
.in-path h3{margin:0 0 6px;font-size:17px}
.in-path p{margin:0;color:var(--cp-text-muted);line-height:1.5}
.in-help{display:grid;grid-template-columns:1.2fr 1fr;gap:16px}
.in-help .card{padding:22px}
.in-help h3{margin:0 0 8px}
.in-help p{color:var(--cp-text-muted);line-height:1.5;margin:0 0 14px}
.in-foot-space{height:72px}
@media (max-width:860px){.in-grid,.in-path,.in-help,.in-facts{grid-template-columns:1fr}.in-path > div{border-left:0;border-top:1px solid var(--cp-border)}.in-cmd{grid-template-columns:1fr}.in-copy{width:100%}.in-hero{padding-top:36px}}
</style>"""

SCRIPT = """<script>
(function(){
  var isWin = /Windows/i.test(navigator.userAgent);
  var box = document.getElementById('in-box');
  var tabs = box.querySelectorAll('.in-os button');
  var cmd = box.querySelector('.in-cmd');
  var hints = {mac: 'Works on macOS and Linux. Installs Python 3.11 for you if it is missing.',
               windows: 'Run it in PowerShell. Installs Python, Git and the GitHub CLI for you if they are missing.'};
  var downloads = {mac: ['../install.command', 'install.command'], windows: ['../install.cmd', 'install.cmd']};
  function pick(os){
    tabs.forEach(function(b){ b.setAttribute('aria-selected', b.dataset.os === os ? 'true' : 'false'); });
    cmd.setAttribute('data-os', os);
    box.querySelector('#brainstem-cmd').hidden = os !== 'mac';
    box.querySelector('#brainstem-win-cmd').hidden = os !== 'windows';
    box.querySelector('#in-hint-text').textContent = hints[os];
    var dl = document.getElementById('download-link');
    dl.setAttribute('href', downloads[os][0]); dl.setAttribute('download', downloads[os][1]);
    dl.textContent = 'download ' + downloads[os][1] + ' and double-click it';
  }
  tabs.forEach(function(b){ b.addEventListener('click', function(){ pick(b.dataset.os); }); });
  pick(isWin ? 'windows' : 'mac');
  document.querySelectorAll('[data-copy]').forEach(function(btn){
    btn.addEventListener('click', function(){
      var target = document.getElementById(btn.getAttribute('data-copy'));
      var text = target.hidden ? '' : target.textContent;
      if (!text) { var alt = document.getElementById(btn.getAttribute('data-copy-alt') || ''); text = alt ? alt.textContent : ''; }
      navigator.clipboard.writeText(text.trim()).then(function(){
        var old = btn.textContent; btn.textContent = 'Copied'; setTimeout(function(){ btn.textContent = old; }, 1600);
      });
    });
  });
  // A Brainstem already running on this computer: say so quietly. The opaque probe never logs an error.
  var live = document.getElementById('in-live');
  fetch('http://localhost:7071/health/public', {mode: 'no-cors', cache: 'no-cache'}).then(function(){ live.classList.add('on'); }).catch(function(){});
})();
</script>"""


def build(site, page):
    count = len(site.solutions())
    body = f"""
<section class="in-hero wrap">
  <div class="kick">Experimental · Rapid prototyping · Runs on your computer</div>
  <h1>Your own AI. On your computer. One line.</h1>
  <p class="lede">The Brainstem is a small, experimental AI server for rapid prototyping. It lives on your laptop and uses the
  GitHub Copilot you already have. Paste one line, sign in, and talk to any of the {count} agents in this library. Your AI is a folder of files you own.</p>

  <div class="in-box" id="in-box">
    <div class="in-os" role="tablist" aria-label="Your computer">
      <button type="button" role="tab" data-os="mac" aria-selected="true">macOS or Linux</button>
      <button type="button" role="tab" data-os="windows" aria-selected="false">Windows</button>
    </div>
    <div class="in-cmd" data-os="mac">
      <code id="brainstem-cmd">{e(MAC_CMD)}</code><code id="brainstem-win-cmd" hidden>{e(WIN_CMD)}</code>
      <button type="button" class="in-copy" data-copy="brainstem-cmd" data-copy-alt="brainstem-win-cmd">Copy the line</button>
    </div>
    <div class="in-hint"><span id="in-hint-text">Works on macOS and Linux. Installs Python 3.11 for you if it is missing.</span>
      <span>No terminal? <a id="download-link" href="../install.command" download="install.command">download install.command and double-click it</a></span></div>
    <div class="in-then"><strong>Then open</strong> <code>http://localhost:7071</code> <span>and say hello. That is the whole install.</span></div>
    <div class="in-live" id="in-live"><span>A Brainstem is already running on this computer.</span>
      <a class="btn pri" href="http://localhost:7071" target="_blank" rel="noopener">Open the chat</a></div>
  </div>

  <div class="in-alt">Rather have Copilot do it for you?
    <details><summary>Paste one sentence into GitHub Copilot Chat in VS Code (agent mode)</summary>
      <p style="margin:8px 0 0;color:var(--cp-text-muted)">Copilot reads the setup guide and does every step while you watch. You never type a command.</p>
      <div class="in-cmd"><code id="copilot-prompt">{e(COPILOT_PROMPT)}</code>
        <button type="button" class="in-copy" data-copy="copilot-prompt">Copy the sentence</button></div>
    </details></div>
</section>

<section class="in-sec wrap in-honest">
  <div class="card">
    <h2>What this is, and is not</h2>
    <p class="sub">An experimental project from a v-team in the Artificial Intelligence Business Applications Specialist Team (AIBAST). It is for learning the agent pattern and proving a prototype fast. It is not an officially supported Microsoft product, and nothing here is production software: expect rough edges, and tell us about them through the <a href="{e(GET_HELP_FORM)}" target="_blank" rel="noopener">Get help form</a>. Every agent ships with sample data only. When a prototype earns it, the <a href="../learn/guide/">production guide</a> is the path into Copilot Studio and Microsoft 365.</p>
  </div>
</section>

<section class="in-sec wrap">
  <h2>What you get</h2>
  <p class="sub">A working prototype you can change by editing a text file.</p>
  <div class="in-grid">
    <article class="card"><h3>A chat that runs on your machine</h3><p>Open it in your browser. Ask it anything. It answers with GitHub Copilot's models, and your conversation stays on your computer.</p></article>
    <article class="card"><h3>{count} agents ready to drop in</h3><p>Every solution in this library ships as one Python file. Put it in the <code>agents</code> folder and the Brainstem can use it on the next message.</p> <p style="margin-top:10px"><a href="../">Browse the agents</a></p></article>
    <article class="card"><h3>An AI you can read</h3><p>Its personality is <code>soul.md</code>. Its skills are files in <code>agents/</code>. Change a sentence and it changes. Copy the folder and it follows you.</p></article>
  </div>
</section>

<section class="in-sec wrap">
  <h2>Sixty seconds, three steps</h2>
  <p class="sub">No account to create. No key to paste. No settings screen.</p>
  <div class="in-grid">
    <article class="card"><span class="num">1</span><h3>Paste the line</h3><p>Into Terminal on a Mac, or PowerShell on Windows. It installs what it needs and starts the Brainstem.</p></article>
    <article class="card"><span class="num">2</span><h3>Sign in with GitHub</h3><p>A browser window asks you once. Your GitHub Copilot does the thinking, so there is nothing else to pay for or configure.</p></article>
    <article class="card"><span class="num">3</span><h3>Pick an agent and talk</h3><p>Start with hello. Then drop in an agent from the library and ask it to do its job with the sample data it carries.</p></article>
  </div>
</section>

<section class="in-sec wrap">
  <h2>Safe to try</h2>
  <p class="sub">Everything it does is visible, and leaving is one folder.</p>
  <div class="in-facts">
    <div><span class="tick">✓</span><span><b>Nothing to configure.</b> No API keys, no cloud account. It uses the GitHub Copilot sign-in you already have.</span></div>
    <div><span class="tick">✓</span><span><b>Installs its own Python.</b> If Python 3.11 is missing, the installer adds it. It never touches other projects.</span></div>
    <div><span class="tick">✓</span><span><b>Stays on your computer.</b> Only the model calls go to GitHub Copilot. Sample data only, never your organisation's data.</span></div>
    <div><span class="tick">✓</span><span><b>Leaves cleanly.</b> Everything lives in one folder, <code>~/.brainstem</code>. Delete it and it is gone.</span></div>
  </div>
</section>

<section class="in-sec wrap">
  <h2>When you outgrow your laptop</h2>
  <p class="sub">The same agent file moves up without being rewritten.</p>
  <div class="in-path">
    <div><span class="tag">Start here</span><h3>The Brainstem</h3><p>Local. Learn the pattern, prove the idea, show it to a customer the same day.</p></div>
    <div><span class="tag">Next</span><h3>The Hippocampus</h3><p>The same agents with persistent memory, running on Azure when more than one person needs them.</p></div>
    <div><span class="tag">Then</span><h3>Copilot Studio and Microsoft 365</h3><p>Publish into Teams and Microsoft 365 Copilot. <a href="../learn/guide/">The production guide</a> walks the fourteen steps.</p></div>
  </div>
</section>

<section class="in-sec wrap">
  <h2>People who can help</h2>
  <p class="sub">Real humans, every week.</p>
  <div class="in-help">
    <article class="card"><h3>AIBAST agents and prototyping office hours</h3>
      <p>Thursdays, 12:30 to 1:30 PM ET, on Teams. Bring a question about the Brainstem or a library agent, a use case you want to prototype, or a build you are stuck on. Sign-up uses your Microsoft account.</p>
      <a class="btn pri" href="{e(OFFICE_HOURS_SIGNUP)}" target="_blank" rel="noopener">Sign up</a></article>
    <article class="card"><h3>Stuck right now?</h3>
      <p>Tell us what you saw and we will get you unstuck. Nervous about PowerShell? <a href="../learn/practice/">Practice on a pretend Windows 11 computer first</a>. Nothing there touches your real PC.</p>
      <a class="btn" href="{e(GET_HELP_FORM)}" target="_blank" rel="noopener">Get help</a></article>
  </div>
</section>
<div class="in-foot-space"></div>
"""
    return {"install/index.html": page(
        site, title="Install the Brainstem",
        description="Your own AI on your computer in one line, powered by the GitHub Copilot you already have.",
        body=body, depth=1, active="Install", path="install/", extra_head=STYLE + SCRIPT.replace("<script>", "<script defer>", 1),
        page_type="install")}
