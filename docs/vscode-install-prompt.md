# Install the Brainstem from GitHub Copilot in VS Code

This is the recommended way to install the RAPP Brainstem. VS Code is not
required: the one-liner on the installer page is a fully supported alternative
that needs no VS Code. It is the best way to explore the AI frontier, because
Copilot installs the Brainstem, opens it in VS Code's browser and guides you
through it.

How to use it: open GitHub Copilot Chat in VS Code, switch to agent mode, paste
the prompt below and send it. The installer page
(https://microsoft.github.io/aibast-agents-library/docs/installer.html) has a
copy button that fills in the one-liner for the site you are on.

Don't have VS Code? Install it from https://code.visualstudio.com/ and set up
GitHub Copilot with https://code.visualstudio.com/docs/copilot/setup.

## Prompt

```text
Please install the RAPP Brainstem for me and show me how to use it. I don't want to type any commands myself, so do each step for me in VS Code.

1. Open a terminal in VS Code and run the installer one-liner for my computer:
   - macOS or Linux: curl -fsSL https://microsoft.github.io/aibast-agents-library/install.sh | bash
   - Windows (PowerShell): irm https://microsoft.github.io/aibast-agents-library/install.ps1 | iex
   If the installer asks me to sign in to GitHub, tell me in one short sentence what to do, then wait for me.
2. Wait until http://localhost:7071/health answers. Check every few seconds for up to five minutes. If it never answers, show me the last lines of the terminal output and suggest one fix.
3. Open http://localhost:7071 inside VS Code with the built-in browser (run the command "simpleBrowser.show" with that address).
4. Give me a short guided tour in plain words, one step at a time: what the Brainstem is, where I type a message, and where the agents live (the agents folder, and which agents are loaded). If your browser tools in VS Code can control that page, drive it for me: type a first message such as "What can you do?" and send it, then point out the answer and the agents. After each step, pause and let me try it myself before you go on.
Keep each message short. Do not change any files in the Brainstem itself.
```
