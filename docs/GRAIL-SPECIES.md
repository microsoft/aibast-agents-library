# Grail species regression

The AIBAST Agents Library vendors the RAPP Brainstem kernel in
`rapp_brainstem/`. Kernel updates flow down from the Grail
(`kody-w/rapp-installer`) through sanctioned kernel-sync pull requests, but the
vendored copy is allowed to grow on its own. The species test keeps the two
compatible while they diverge.

## What the test guarantees

`tests/test_grail_species.py` diffs the vendored kernel against the pinned
Grail shape in `rapp/GRAIL-SPECIES.json`. The suite fails when the vendored
kernel drops or changes any of:

- a Flask route the Grail exposes (`METHOD PATH`)
- a `BasicAgent` method or its signature
- the agent discovery rule (`*_agent.py`, flat, no subdirectories)
- a `sys.modules` import shim (`agents.basic_agent`, `utils.azure_file_storage`, ...)
- the default port (`7071`) or the `/chat` response field (`response`)
- an install-layout constant from `install.sh` (`~/.brainstem`, `venv/`,
  `src/rapp_brainstem`, `src/rapp_brainstem/agents`)

Additions are allowed: new routes, environment keys, agent files, and
installer overrides are how the business fork grows.

Run it:

```bash
python -m unittest -v tests/test_grail_species.py
GRAIL_SPECIES_LIVE=1 python -m unittest tests/test_grail_species.py   # also diff against Grail@main
```

Live mode reports items the Grail has that we lack as "pending kernel sync"
and does not fail on them; it fails only when the vendored kernel breaks a
shared item.

## Refreshing the pin after a kernel sync

After a sanctioned kernel-sync pull request lands, regenerate the pin from the
Grail in the same change:

```bash
python scripts/grail_species.py fetch-grail /tmp/grail --ref main
python scripts/grail_species.py shape /tmp/grail/rapp_brainstem \
    --installer /tmp/grail/install.sh --source /tmp/grail/SOURCE.json \
    > rapp/GRAIL-SPECIES.json
python scripts/grail_species.py diff rapp/GRAIL-SPECIES.json \
    <(python scripts/grail_species.py shape rapp_brainstem --installer install.sh)
```

The pin records the Grail commit it was generated from under `source`.

## What "layer over top" means

A Grail install and an AIBAST install share one layout on the machine:
`~/.brainstem`, the `venv/` inside it, `src/rapp_brainstem/`, and the flat
`agents/` directory discovered by the same glob. Because the species test keeps
those constants and the kernel contract identical, either installer can run
over the other's install and the result is still one working Brainstem with the
user's agents intact.
