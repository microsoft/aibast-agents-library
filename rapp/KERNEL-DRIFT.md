# Kernel drift ledger

`rapp_brainstem/` and `install.sh` are vendored from the Grail kernel,
[kody-w/rapp-installer](https://github.com/kody-w/rapp-installer). Updates flow
one way: Grail → kernel-sync PR → this repository. This ledger names every
vendored file that differs from the pinned Grail commit and why, so drift is
always deliberate and visible. The species contract in
[`GRAIL-SPECIES.json`](GRAIL-SPECIES.json) (see [docs/GRAIL-SPECIES.md](../docs/GRAIL-SPECIES.md))
is the hard gate; this ledger is the explanation.

Rules:

- Every diverged path must appear here. `python scripts/grail_species.py drift <grail-dir> --ledger rapp/KERNEL-DRIFT.md`
  fails when one is missing, and the live species test runs that check.
- A fix that belongs to every Brainstem user goes to the Grail first and comes
  back through a kernel sync. Entries marked *upstream candidate* are waiting on that.
- Identity rewrites (repository URLs, support links, Pages origins) are permanent
  and expected; they are the only edits a distribution is entitled to make.

Pinned Grail: `kody-w/rapp-installer@49db80c8` (kernel 0.6.16). Refresh the pin
and re-run the drift report after each kernel sync.

| Path | Kind | Why it differs | Disposition |
|---|---|---|---|
| `install.sh` | modified | `BRAINSTEM_REPO_URL` / `BRAINSTEM_REPO_REF` / `BRAINSTEM_VERSION_URL` overrides (what preflight and the staging ring use), sparse partial-clone install, repair path, Ubuntu 24.04 and heartbeat fixes, Microsoft identity | **upstream candidate** — the override and repair work belongs in the Grail installer |
| `rapp_brainstem/brainstem.py` | modified | adds `GET /health/public` with CORS restricted to the two library Pages origins so the static catalog can show local readiness; support link points at this repository | route: upstream candidate; identity: permanent |
| `rapp_brainstem/agents/rar_rapp_learn_new_agent.py` | only vendored | AIBAST-shipped agent that teaches the RAR learn-new-agent flow | distribution content, stays here |
| `rapp_brainstem/tests/test_learn_new_agent.py` | only vendored | tests for the agent above | stays with the agent |
| `rapp_brainstem/tests/test_security_hardening.py` | modified | support-link identity and the `/health/public` CORS origins | follows the route |
| `rapp_brainstem/tests/test_model_selection.py`, `rapp_brainstem/tests/test_streaming.py` | modified | `sys.path` bootstrap so the suite runs from the repository root as well as from `rapp_brainstem/` | **upstream candidate** |
| `rapp_brainstem/tests/soul_defaults.sha256` | modified | checksum of the AIBAST `soul.md` below | follows `soul.md` |
| `rapp_brainstem/soul.md` | modified | Microsoft distribution identity in the default persona | permanent |
| `rapp_brainstem/index.html` | modified | opens the VS Code link in a new tab and accepts a `?prompt=` prefill from the catalog pages | **upstream candidate** |
| `rapp_brainstem/start.sh`, `rapp_brainstem/README.md` | modified | installer and support URLs point at this repository | permanent |
| `rapp_brainstem/start.ps1` | modified | UTF-8 byte-order mark (PowerShell 5.1 reads the file correctly with it) | **upstream candidate** |
| `rapp_brainstem/CONSTITUTION.md` | modified | AIBAST distribution disclaimer and downstream scope | permanent |
