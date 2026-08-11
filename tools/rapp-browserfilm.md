# rapp-browserfilm

`rapp-browserfilm` turns a sequence of real browser screenshots into a labeled,
auditable GIF and contact sheet.

It exists because browser walkthroughs are release evidence, not decoration.
Every frame must come from the actual authenticated environment.

## Capture workflow

1. Drive the real browser with `rapp-copilot-in-chrome`.
2. Save a screenshot after each meaningful action.
3. Copy the frames into `solutions/<slug>/screenshots/`.
4. Create a `browserfilm.json` manifest:

   ```json
   {
     "schema": "rapp-browserfilm/1.0",
     "watermark": "rapp-browserfilm · environment · synthetic pilot",
     "frames": [
       {
         "file": "01-home.jpg",
         "label": "1 · Open the target environment",
         "duration_ms": 1600
       }
     ]
   }
   ```

5. Build the assets:

   ```text
   python3 tools/rapp-browserfilm.py \
     solutions/<slug>/screenshots/browserfilm.json \
     solutions/<slug>/screenshots/manual-mode-walkthrough.gif \
     --contact-sheet solutions/<slug>/screenshots/manual-mode-contact-sheet.jpg
   ```

The script requires Pillow. Frames are normalized to one size and receive:

- a step label,
- frame count,
- progress bar,
- and a `rapp-browserfilm` provenance watermark.

## Evidence rules

- Never use mock screens.
- Never capture customer data or credentials.
- Prefer synthetic or sandbox environments.
- Capture the final response for at least one canonical acceptance prompt.
- Capture the publish action only after explicit approval.
- Keep the raw frames and manifest beside the GIF so the walkthrough can be
  rebuilt and audited.
