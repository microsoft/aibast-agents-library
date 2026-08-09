# Financial Regulatory Compliance Pilot — Synthetic Records

> SYNTHETIC PILOT DATA. Every organization, identifier, transaction, date, and
> person-like record below is fictional. The fixed snapshot date is
> 2026-08-07. Do not treat this content as customer data, regulatory advice, or
> evidence of a filing.

## Reporting entity

- Name: Northgate Asset Management LLP
- LEI: `549300XKQZ2P4NLK7T18`
- Status: investment firm and MiFID II Article 26 reporting entity
- Reporting mechanism: Unavista ARM
- Supervisory context: FCA (UK) / AFM (NL) passporting

## Executed-trade exception snapshot

The pilot contains 13 executed trades. These five have at least one compliance
or execution-quality exception.

| Trade | Instrument | Reported venue | Trader | Reporting evidence | Other evidence |
|---|---|---|---|---|---|
| TRD-88117 | SAP SE | XETR | T-2041 | field 57 Investment decision within firm is missing; source value is `T-2041` | ALGO-IS-DE documentation is expired |
| TRD-88129 | TotalEnergies SE | XETR | T-2107 | reported venue conflicts with reference data; verified execution venue is `XPAR` | none |
| TRD-88133 | Koninklijke Ahold Delhaize | XAMS | T-2107 | field 59 source value is `T-2107`; field 7 buyer LEI source value is `549300XKQZ2P4NLK7T18`; no ARM submission is recorded | execution-quality outlier; ALGO-IS-DE documentation is expired |
| TRD-88150 | Vodafone Group PLC | TQEX | T-2233 | reported venue conflicts with reference data; verified execution venue is `XLON` | execution-quality outlier |
| TRD-88162 | SAP SE | CHIX | T-2041 | report is complete | ALGO-IS-DE documentation is expired |

TRD-88133 is the canonical board-level example. It combines missing reporting
fields, an unsubmitted report, execution-quality evidence, and stale algorithm
documentation.

## Algorithm documentation

| Algorithm | Status on snapshot | Go-live state | Documentation evidence |
|---|---|---|---|
| ALGO-VWAP-EU | current | live | complete pack; validated 95 days ago |
| ALGO-IS-DE | expired | live | validated 402 days ago against a 365-day cycle |
| ALGO-POV-NL | never validated | goes live in 6 days | missing risk controls, kill-switch test, and conformance test |
| ALGO-DARK-EU | current | live | complete pack; validated 310 days ago |

## Trader certification snapshot

| Trader | Desk | Certification | Status | Next synthetic session |
|---|---|---|---|---|
| T-2041 | EU Equities | Algo Trading Certification | lapsed 12 days ago | 2026-08-19 |
| T-2233 | Credit | Market Abuse Regulation | lapsed 3 days ago | 2026-08-12 |
| T-2041 | EU Equities | MiFID II Knowledge & Competence | expires in 24 days | 2026-08-16 |
| T-2107 | EU Equities | Market Abuse Regulation | expires in 41 days | 2026-08-12 |
| T-2107 | EU Equities | MiFID II Knowledge & Competence | expires in 88 days | 2026-08-16 |

Supervisor contacts are role-based in this pilot:

- T-2041 and T-2107: Desk Supervisor — EU Equities
- T-2233: Desk Supervisor — Credit
