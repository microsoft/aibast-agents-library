---
name: rapp-brainstem
description: Give the user their RAPP Brainstem and operate its complete lifecycle without asking them to run commands.
---

# RAPP Brainstem

The Brainstem is the product. Keep setup plumbing invisible.

When the user says "Give me my Brainstem," asks to install RAPP, or asks you to
operate or maintain their Brainstem, own the complete local operation. Do not
send terminal instructions back to the user. The only acceptable handoffs are
unavoidable GitHub sign-in, operating-system elevation, tenant authorization,
and explicit approval for a destructive action.

GitHub Copilot is the golden path. Claude Code follows this same contract as a
compatibility path. Set the lifecycle actor to `github-copilot` when running in
Copilot and `claude-code` when running in Claude Code.

## Authority

1. Treat this installed marketplace plugin as the lifecycle trust anchor.
   Resolve the plugin root from this skill file on every request and execute
   its bundled `rapp_operator/rappctl.py` directly. Use only the adjacent
   `scripts/bootstrap.*` and `installer-lock.json`.
2. Do not download an operator, bootstrap script, or replacement lock from a
   public manifest. `rapp-operator.json` is informational, not bootstrap
   authority.
3. Never execute `~/.rapp/operator/rapp_operator/rappctl.py` or promote a
   marketplace bundle into a stable copied operator. Marketplace updates take
   effect because every lifecycle use resolves the currently installed plugin.
4. Treat the upstream `brainstem.py` and existing installer as Grail. Never edit
   either during setup, operation, repair, or maintenance.
5. Use `POST /chat` as the only Brainstem execution entry point. Do not add or
   call a competing management route.

## First decision: existing state or fresh setup

1. Check whether `~/.brainstem` exists before deciding to bootstrap.
2. If it exists, this is an existing install even when health is offline. Never
   run fresh bootstrap over it. Run the current plugin's bundled `rappctl.py
   status`, then follow **Existing installs** below.
3. Only when `~/.brainstem` is absent, probe
   `http://127.0.0.1:7071/health/public`. If another Brainstem is reachable,
   stop rather than adopting it.
4. If both state and health are absent, run the bootstrap bundled in this local
   plugin:
   - macOS/Linux: `scripts/bootstrap.sh --actor <actor>`
   - Windows: `scripts/bootstrap.ps1 -Actor <actor>`
   You execute it; the user does not.
5. Do not pre-create a Python plan. The bootstrap works before Python exists. It
   verifies the local plugin bundle, persists a pre-mutation envelope binding
   the actor, installer-lock digest, exact installer URL and hash, target
   rolling tag plus commit/tree/version, and operator hashes, then invokes the
   unchanged installer with `--no-launch --version`.
6. The bootstrap lock binds PID plus process creation identity. Any failure
   after mutation restores the prior absent `~/.brainstem` state by moving the
   exact bootstrap-owned partial tree into private quarantine (or removing only
   that exact tree if quarantine cannot be activated). It never deletes
   pre-existing state.
7. The newly installed Brainstem Python runs `rappctl.py` directly from the
   current plugin to reconcile the exact envelope. Stop on any mismatch or
   partial result.
8. A successful reconcile proves installation only. It deliberately records
   `pending-live-canary` and does not append live-verification evidence.
9. Use the Brainstem-managed Python for runtime start and verification:
   - macOS/Linux: `~/.brainstem/venv/bin/python`
   - Windows: `~/.brainstem/venv/Scripts/python.exe`
10. From the current plugin operator, run `plan start --actor <actor>`, read the
    returned `plan_hash`, then apply that exact plan with `apply <plan_hash>
    --approve <plan_hash>`.
11. The start apply proves public health and deliberately leaves live
   verification pending so first-run authentication can complete.
12. Open the local Brainstem sign-in experience when authentication is required
   and let the user complete GitHub device authorization.
13. After authentication, create and apply a separate `verify` plan. It must
   send a real canary through `POST /chat` using
   `{"user_input":"Confirm my Brainstem is alive and name one capability."}`.
14. Finish only when `/chat` returns a real response and the separate
   verification frame exists. Report the RAPPID, Brainstem version, verified
   evidence head, and the result.

The initial request to "Give me my Brainstem" is consent for this
non-destructive setup. Never infer consent for deleting resources, replacing
user state, publishing, or tenant-wide deployment.

## Existing installs

Before delegating any Brainstem request:

1. Resolve and run the current plugin's bundled `rappctl.py`; ignore any legacy
   copied operator under `~/.rapp/operator`.
2. Run `status`. Use its effective port for both health and `/chat`.
3. A healthy Brainstem with `runtime.state == "unknown-process"` is a supported
   manual install. Use `/chat` immediately without creating a PID record,
   stopping it, or adopting it. Lifecycle mutations remain fail-closed while
   that process runs. Once it is stopped externally, a planned `start` can
   establish sidecar ownership.
4. A legacy sidecar PID record or a safely owned process with environment drift
   may be replaced only through a planned sidecar-owned `restart`; do not run
   update, repair, rollback, or verification until the current environment
   binding is established.
5. If the existing install is offline and safely stopped, plan and apply
   `start`, then create and apply a separate `verify` plan. Never run fresh
   bootstrap merely because health is offline.
6. If installed state is incomplete, plan `repair` from the current plugin.
   Repair uses the exact reviewed commit when the checkout supports it; only a
   broken checkout without Git metadata may use the currently verified rolling
   tag, followed by commit/tree/version verification.
7. For an explicit update, use the exact reviewed commit. For rollback, use the
   historical exact commit selected from successful verification evidence; do
   not require its old rolling tag to resolve.
8. On Windows, run installer-backed operator mutations outside
   `~/.brainstem/venv` (for example with the base interpreter recorded by the
   venv) so transaction rollback can restore the complete venv. Runtime
   start/verify still uses only the managed interpreter.
9. Send the user's work to `POST /chat`; surface its `response` and a concise
   summary of useful `agent_logs`.

## RAPP/1 and ownership rules

- Every lifecycle mutation must be bound to an exact plan or bootstrap-envelope
  hash and written as append-only RAPP/1 evidence by `rappctl`. Bootstrap apply
  evidence remains explicitly unverified until the separate live canary.
- Never rewrite or delete evidence frames.
- Never put tokens, raw memory, prompts, environment values, or private file
  contents into a plan or frame.
- Never silently change `soul.md`, user agents, memory, or `.env`.
- A runtime rollback changes runtime code only. It is not permission to roll
  back user state.
- Plans bind a minimal child environment. Supported behavior overrides are
  recorded only by name, source, presence, and value hash; raw auth, voice,
  model, path, LAN, and port values never enter plans or evidence.
- Every operation verifies the complete protected-zone manifest digest and
  count. A newly created protected path is allowed only when explicitly
  enumerated in the plan. Bootstrap initialization remains a separate case.
- Stop on a corrupt frame chain, hash mismatch, failed health check, unknown
  process, or incomplete installer result. Never return a success-shaped
  fallback.
- Existing manual one-liner users remain supported. This AI-operated path
  verifies and invokes that installer; it does not replace it.
