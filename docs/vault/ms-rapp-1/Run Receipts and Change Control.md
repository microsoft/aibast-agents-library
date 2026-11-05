---
title: Run Receipts and Change Control
section: ms-rapp-1
status: published
hook: How does ms-rapp/1 keep an AI step auditable, and how does a new Step get into production?
source: "docs/ms-rapp1/; this vault's Security Considerations and Conformance and Drift notes"
---

# Run Receipts and Change Control

Two rules make RAPP Runtime fit an enterprise review: every run leaves a record, and the set of Steps changes only through review.

## The answer in brief

- A **Run Receipt** records each run: the Step, the model, the number of attempts and the usage.
- The **Step Catalog** holds only files that were reviewed and deployed. The runtime never writes or downloads a Step.
- A new Step is a pull request, not a new endpoint and not a new release of the engine.

## Run Receipts

A receipt answers the questions an auditor asks about one AI step:

| Question | Receipt field |
|---|---|
| Which capability ran? | the Step's route and the hash of its file |
| Which model answered? | the model name |
| Did the model's answer pass the Step's checks? | the number of attempts, and the last refusal if any |
| What did it cost? | the token usage |

Receipts record what ran, not the customer's content. Keep payloads out of logs unless the review approves them.

## Change Control

1. A Step is written as a file and opened as a pull request.
2. Review reads one file: its parameters, its result schema, its checks.
3. Merge and deploy put it in the Step Catalog. The next call uses it.

The engine never loads code from a browser, an upload or a model response. This is the same rule app stores apply to apps after review: new behavior arrives as reviewed code.

## When a Step goes back to review

A Step stays inside an existing review when it uses only what the service already uses: the same sign-in, the same model, no new outside system.
A Step that sends email, writes to a new data store or calls a new service is a new data flow and needs its own review.

See also [[RAPP Runtime]], [[Security Considerations]] and [[Conformance and Drift]].
