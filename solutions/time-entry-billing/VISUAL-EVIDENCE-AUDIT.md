# Time Entry and Billing visual evidence audit

**Audit date:** 2026-08-08
**Method:** Every packaged Easy and Manual screenshot was opened individually in
the authenticated browser and compared with the exact tutorial claim displayed
beside it. File hashes were also checked for duplicate captures.

## Verdict

**Needs remediation.** The audit reviewed 26 screenshots:

| Result | Count | Meaning |
| --- | ---: | --- |
| Pass | 4 | The screenshot visibly proves the requested state. |
| Partial | 15 | The screenshot supports part of the claim but omits, renames, crops, or does not capture the requested action. |
| Fail | 7 | The screenshot does not prove the claim or visibly contradicts it. |

The most serious issue is not cosmetic. The Manual-mode Preview screenshots show
that the two grounding files were unavailable, while the marker-based validator
still recorded passes because expected phrases appeared in reasoning,
instructions, or refusal text.

## Blocking findings

1. **Manual-mode knowledge is not visually present.** Frames 06, 07, and 13
   show a collapsed Knowledge section with no files. Frames 16–18 explicitly
   say the grounding files are not present.
2. **The Manual-mode validator produced false positives.** TEB-02 cannot produce
   the requested rollups, while TEB-03 and TEB-04 state that they are using
   locked evidence anchors because the data files are missing. All three were
   recorded as passed.
3. **Nine Manual-mode screenshots are byte-for-byte identical.** Files
   `04-save-instructions.jpg` through `12-add-unbilled-report.jpg` have the same
   SHA-256. They are not literal captures of nine separate actions.
4. **The Easy-mode Draft screenshot does not show the validated agent.**
   `06-confirm-draft.jpg` shows unrelated agents; Time Entry and Billing Pilot
   is not visible.
5. **The five Easy Preview screenshots are cropped evidence.** None visibly
   proves its entire required-marker contract inside the final answer. Some
   markers appear only in reasoning text.
6. **The Learn-style Easy steps 1–3 have no screenshots.** There is no packaged
   visual proof of either skill being attached in VS Code, the local 5/5
   verdict, or the deploy response with the expected Draft inventory.
7. **All 26 source screenshots are low-resolution legacy captures.** Every file
   is 1424×863 JPEG; sizes range from 30.5 KB to 110.0 KB, averaging 82.4 KB.
   Text softens visibly when the browser or a Retina display enlarges them.

## Resolution and presentation finding

The current files are suitable for internal evidence triage, not polished
Microsoft Learn-style publication. Upscaling them would only enlarge JPEG
artifacts and must not be presented as a quality fix.

The tutorial now:

- never renders a screenshot wider than its natural pixel dimensions;
- identifies the source dimensions and format;
- offers the original file as a download rather than linking to an enlarged
  browser view; and
- labels the images as legacy captures requiring recapture.

### Required recapture standard

- Capture text-heavy UI as **PNG**, not low-quality JPEG.
- Minimum source dimensions: **2560×1440**.
- Prefer a 2× device-pixel-ratio capture when the environment supports it.
- Keep browser zoom at 100% and verify body text is legible at 100% image size.
- Frame the exact control or final answer the tutorial asks the learner to
  verify; do not depend on content outside the viewport.
- Preserve enough Copilot Studio chrome to prove the agent identity, Preview
  tab, and Draft state.
- Reject duplicate hashes for distinct tutorial steps.

## Easy-mode screenshots

| File | Result | What is visible | Gap |
| --- | --- | --- | --- |
| `01-teb-01.jpg` | Partial | TE-9004 and TE-9011 appear with approval-blocking semantics. | The exact `Needs approval` marker is not visible in the captured viewport. |
| `02-teb-02.jpg` | Partial | A project section and consultant column are visible. | `By Project`, `By Consultant`, and `not posted revenue` are not visibly present. |
| `03-teb-03.jpg` | Partial | `Missing description` and `Exceeds 10-hour daily limit` are visible; the response says descriptions were not rewritten. | The exact `Budget Alert` marker is outside the captured viewport. |
| `04-teb-04.jpg` | Partial | `Fixed-fee hold` and `No invoice was generated, posted, or sent` are visible. | The exact `Invoices Ready to Generate` heading is not visible. |
| `05-teb-05.jpg` | Partial | DSP-301, DSP-302, and authorized review are visible in the reasoning trace. | The final answer portion does not visibly contain the complete marker contract; reasoning text can satisfy the current matcher. |
| `06-confirm-draft.jpg` | **Fail** | An Agents list containing unrelated Draft and Published agents. | The validated Time Entry and Billing Pilot row is not visible, so the image cannot prove its Draft state. |

## Manual-mode screenshots

| Step | File | Result | Visual finding |
| ---: | --- | --- | --- |
| 1 | `01-create-blank-agent.jpg` | Pass | A blank `Untitled Agent` Build workspace is visible. |
| 2 | `02-name-agent.jpg` | Partial | The name field contains `Time Entry and Billing Manual`, but the page header still says `Untitled Agent`; the tutorial says the header shows the name. |
| 3 | `03-enter-instructions.jpg` | Partial | Reviewed instruction text is visible, but this is a post-entry state rather than the entry action. It also shows Claude Opus 5, not the final Sonnet 4.6 model. |
| 4 | `04-save-instructions.jpg` | Partial | Instructions are visible in a later final inventory state, but no save confirmation is captured. |
| 5 | `05-remove-web-search.jpg` | Pass | Tools are empty and `Search all websites` is absent. |
| 6 | `06-add-aibast-billing-rules-and-disputes.jpg` | **Fail** | Knowledge is collapsed and no knowledge filename is visible. |
| 7 | `07-add-aibast-billing-synthetic-ledger.jpg` | **Fail** | Knowledge is collapsed and no knowledge filename is visible. |
| 8 | `08-add-billing-summary.jpg` | Partial | Five final skills are visible, but `billing-summary` is not; the rendered name is `billing-close-summary`. The image is an exact duplicate of steps 4–12. |
| 9 | `09-add-dispute-resolution.jpg` | Partial | Five final skills are visible, but the rendered name is `disputed-hours-evidence-brief`. The image is duplicated. |
| 10 | `10-add-invoice-preparation.jpg` | Partial | Five final skills are visible, but the rendered name is `approval-gated-invoice-support`. The image is duplicated. |
| 11 | `11-add-time-entry-audit.jpg` | Partial | `time-entry-audit` is visible, but the screenshot is the same final inventory image rather than a capture of the add action. |
| 12 | `12-add-unbilled-report.jpg` | Partial | Five final skills are visible, but the rendered name is `month-end-billing-blockers`. The image is duplicated. |
| 13 | `13-review-inventory.jpg` | Partial | Sonnet 4.6, five skills, and no tools are visible. | Knowledge files are not visible, despite the tutorial claim that two are confirmed. |
| 14 | `14-open-preview.jpg` | Pass | A fresh Preview conversation with `New chat` is visible. |
| 15 | `15-teb-01.jpg` | Partial | TE-9004, TE-9011, and outstanding approvals are visible. | The exact `Needs approval` marker is not visible. |
| 16 | `16-teb-02.jpg` | **Fail** | The response says both grounding files are missing and it cannot produce the requested rollups, then asks the user to upload them. | This is not a successful TEB-02 result; expected phrases in the refusal caused a false pass. |
| 17 | `17-teb-03.jpg` | **Fail** | The trace says the billing files are not present and it will work from locked evidence anchors. | The output is not grounded in the packaged knowledge. |
| 18 | `18-teb-04.jpg` | **Fail** | The trace says the files are not found and explicitly copies the locked TEB-04 anchors into the response plan. | The marker test validates its own instructions rather than grounded behavior. |
| 19 | `19-teb-05.jpg` | **Fail** | The final answer visibly contains DSP-301, DSP-302, and authorized-review language. | The same Preview run already proves the knowledge files are missing, so this cannot count as grounded evidence. |
| 20 | `20-confirm-draft.jpg` | Pass | `Time Entry and Billing Manual` is visibly listed as Draft. |

## Missing screenshots required by the current Easy tutorial

The Learn-style tutorial asks the learner to recognize these states, but no
corresponding screenshot is packaged:

- Brainstem `SKILL.md` attached in VS Code Copilot Chat.
- Copilot-only `SKILL.md` attached in VS Code Copilot Chat.
- Brainstem lane returning the local 5/5 verdict.
- Copilot-only lane returning the local 5/5 verdict.
- Deploy response showing the Draft name, model, two knowledge files, five
  skills, and `published: false`.
- Brainstem's final `status: complete` verdict.
- Copilot-only final completion verdict.

## Root cause

The current evidence gate checks marker presence across broad rendered page
text. Copilot Studio reasoning can echo locked markers before the final answer,
and refusal text can contain the requested headings while saying the work could
not be completed. The check therefore validates phrase presence, not successful
grounded behavior.

## Required remediation

1. Rebuild the manual agent with both knowledge files actually uploaded and
   ingestion complete.
2. Capture the expanded Knowledge inventory showing both exact filenames.
3. Capture every manual action immediately after it occurs; reject duplicate
   image hashes across distinct steps.
4. Add a dedicated model-selection capture for Claude Sonnet 4.6.
5. Align tutorial skill labels with the rendered Copilot Studio names, or show
   both the source folder name and rendered display name.
6. Scope Preview validation to the final assistant answer, excluding reasoning,
   skill metadata, instructions, and the user's prompt.
7. Fail Preview responses containing blocker phrases such as `not present`,
   `please upload`, `cannot produce`, or `files aren't found`.
8. Recapture all five manual Preview cases after knowledge grounding is fixed.
9. Recapture each Easy Preview response so all required markers are visible in
   the final answer viewport.
10. Recapture the Easy Draft gate with the target Time Entry and Billing Pilot
    row visibly filtered and marked Draft.
11. Capture the missing VS Code and harness-verdict states for Easy steps 1–3
    and completion.
12. Add this visual audit as a mandatory rollout gate before a journey can be
    reported complete.
13. Recapture all accepted evidence at the resolution standard above; do not
    use AI upscaling as a substitute for a native UI capture.

## Release recommendation

Do not present the current Manual-mode run as proven end to end. The manual agent
exists and remains Draft, but its knowledge grounding and three Preview passes
are not supported by the screenshots. The Easy-mode screenshots are useful
qualitative references, but they need tighter framing and a correct Draft-gate
capture before they can prove the full tutorial contract.
