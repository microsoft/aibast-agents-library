# Workshop browser certification

This directory contains the fail-closed browser release gate for the 51
advertised industry workshops.

The gate:

- serves only immutable, hashed repository inputs;
- blocks unknown HTTP, external network, WebSocket, and service-worker access;
- validates catalog, registry, deployment, body, tab, and mode identity;
- binds the immutable HTML evidence inventory to live desktop and mobile DOMs;
- compares decoded source pixels, isolated rendering, overlays, pseudo-elements,
  clipping, masks, filters, transforms, and cross-mode evidence identity;
- records capture-buffer hashes for 102 screenshots and two generated contact
  sheets;
- runs an exact adversarial mutation contract; and
- re-hashes the repository, Git state, scripts, reports, manifest, screenshots,
  and contact sheets before writing the final attestation.

## Run the release gate

Node.js 22 or newer is required.

```bash
cd browser-audit
npm ci
npx playwright install chromium
npm run certify
```

`npm run certify` runs the exact mutation contract, the complete 51-workshop
audit, and the final current-state attestation in that order.

Run certification from a committed input state, then commit only the generated
certification outputs. The attester remains independently rerunnable from that
evidence commit only when the audited commit is its ancestor and every
cumulative changed path is a generated certification output. Any source,
workshop, registry, gate, rename-source, or other input change fails closed.

For investigation only:

```bash
AUDIT_SLUG=account-intelligence npm run audit
MUTATION_ONLY=css-filter npm run mutations
```

Targeted runs write isolated partial reports and are intentionally ineligible
for release attestation.
