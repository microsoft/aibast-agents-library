---
name: energy-regulatory-reporting-data-validation
description: Use when a Data Analyst asks to screen source-data quality before certification.
---
# Regulatory Reporting Agent: Data Validation

## Route

Use the `data_validation` operation. The canonical persona prompt is:

> Which report data is incomplete or below quality threshold?

## Procedure

1. Read the synthetic knowledge records and controls.
2. Call or reproduce only the `data_validation` operation behavior.
3. Lead with source-backed identifiers and evidence.
4. State uncertainty and the required authorized review.
5. End with the operation's no-write boundary.

## Required evidence

- Data collection incomplete
- Data quality score below threshold
- authorized report owner

Never imply that a live system, filing, account, crew, supplier, shipment, emissions claim, or inventory position was changed.
