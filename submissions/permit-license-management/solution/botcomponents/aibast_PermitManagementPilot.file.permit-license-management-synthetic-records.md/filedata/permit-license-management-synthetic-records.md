# Permit Management Agent — Complete Synthetic Records

> COMPLETE SYNTHETIC PILOT DATA. Every organization, person, identifier, date, measurement, cost, score, status, and schedule below is fictional. Use only these records; do not supplement them with external facts.

## Provenance

- Deterministic source: `agents/@aibast-agents-library/energy_stacks/permit_license_management_stack/permit_license_management_agent.py`
- Captured source SHA-256: `40d35799eb84340dd98c5cca3ac896c99401688ebfe2660ab2f7b4ef53ab40e5`
- Locked case file: `tests/demo_cases/permit-license-management.json`
- Locked case SHA-256: `239d11a0225004062d91ad2a19d9537fbbc38be042b1200a651a141ef97b5d95`
- Strict isolation: `true`

## Record index

- `AS_OF`
- `PORTFOLIO`
- `PERMITS`
- `STAKEHOLDERS`
- `APPLICATIONS`
- `REGULATORY_REQUIREMENTS`

## AS_OF

```json
"2026-03-02"
```

## PORTFOLIO

```json
{
  "active_permits": 240,
  "expiring_120_days": 63,
  "critical_days": 30,
  "renewal_investment_63": 2340000,
  "production_at_risk_63": 47000000
}
```

## PERMITS

```json
{
  "PRM-8101": {
    "facility": "Imperial Valley Solar",
    "type": "Air Quality",
    "authority": "County air pollution control district",
    "expiration_date": "2026-03-20",
    "renewal_lead_days": 90,
    "renewal_cost": 185000,
    "production_at_risk": 4200000,
    "renewal_path": "Expedited air quality renewal application prepared, ready for you to submit"
  },
  "PRM-8102": {
    "facility": "Reno Wind Farm",
    "type": "Environmental",
    "authority": "State environmental protection division",
    "expiration_date": "2026-03-24",
    "renewal_lead_days": 120,
    "renewal_cost": 140000,
    "production_at_risk": 3100000,
    "renewal_path": "Environmental permit vendor shortlisted (2-week turnaround); engagement request drafted"
  },
  "PRM-8103": {
    "facility": "Phoenix Solar",
    "type": "Water Use",
    "authority": "County water resources department",
    "expiration_date": "2026-03-28",
    "renewal_lead_days": 60,
    "renewal_cost": 95000,
    "production_at_risk": 2200000,
    "renewal_path": "County approval fast-track request drafted"
  },
  "PRM-8104": {
    "facility": "Bakersfield Solar",
    "type": "Hazmat",
    "authority": "County environmental health department",
    "expiration_date": "2026-03-30",
    "renewal_lead_days": 60,
    "renewal_cost": 80000,
    "production_at_risk": 1600000,
    "renewal_path": "Hazmat documentation compiled, ready to submit"
  },
  "PRM-8105": {
    "facility": "Tehachapi Wind",
    "type": "Avian Protection",
    "authority": "Federal wildlife agency",
    "expiration_date": "2026-03-31",
    "renewal_lead_days": 90,
    "renewal_cost": 60000,
    "production_at_risk": 1100000,
    "renewal_path": "Monitoring report assembled for the renewal filing"
  },
  "PRM-8106": {
    "facility": "Palm Springs Wind",
    "type": "Noise Variance",
    "authority": "County planning department",
    "expiration_date": "2026-03-31",
    "renewal_lead_days": 45,
    "renewal_cost": 45000,
    "production_at_risk": 700000,
    "renewal_path": "Variance renewal letter drafted"
  },
  "PRM-8107": {
    "facility": "Yuma Solar",
    "type": "Grading",
    "authority": "County building and grading office",
    "expiration_date": "2026-03-31",
    "renewal_lead_days": 45,
    "renewal_cost": 40000,
    "production_at_risk": 500000,
    "renewal_path": "Grading plan resubmittal package prepared"
  },
  "PRM-8108": {
    "facility": "Mojave Storage",
    "type": "Fire Code",
    "authority": "County fire authority",
    "expiration_date": "2026-03-31",
    "renewal_lead_days": 45,
    "renewal_cost": 40000,
    "production_at_risk": 400000,
    "renewal_path": "Fire code inspection request drafted"
  }
}
```

## STAKEHOLDERS

```json
[
  "Facility managers",
  "Legal"
]
```

## APPLICATIONS

```json
{
  "APP-7101": {
    "permit_name": "Reno Wind Farm Repowering Environmental Review",
    "facility": "Reno Wind Farm",
    "submitted_date": "2025-11-12",
    "authority": "State environmental protection division",
    "status": "under_review",
    "expected_decision": "2026-05-15",
    "comments_received": 4
  },
  "APP-7102": {
    "permit_name": "Imperial Valley Solar Phase 2 Conditional Use Permit",
    "facility": "Imperial Valley Solar",
    "submitted_date": "2026-01-20",
    "authority": "County planning commission",
    "status": "public_comment",
    "expected_decision": "2026-06-30",
    "comments_received": 12
  },
  "APP-7103": {
    "permit_name": "Phoenix Solar Battery Storage Building Permit",
    "facility": "Phoenix Solar",
    "submitted_date": "2026-02-10",
    "authority": "County water resources department",
    "status": "submitted",
    "expected_decision": "2026-04-15",
    "comments_received": 0
  }
}
```

## REGULATORY_REQUIREMENTS

```json
{
  "Air Quality": [
    "Dust control plan",
    "Annual emissions inventory",
    "Quarterly compliance reports"
  ],
  "Environmental": [
    "Habitat monitoring",
    "Annual environmental report",
    "Mitigation plan updates"
  ],
  "Water Use": [
    "Monthly water use reporting",
    "Annual allocation review",
    "Conservation plan"
  ],
  "Hazmat": [
    "Hazardous materials business plan",
    "Annual inventory certification",
    "Emergency response plan"
  ],
  "Avian Protection": [
    "Post-construction fatality monitoring",
    "Annual avian report",
    "Adaptive management plan"
  ],
  "Noise Variance": [
    "Quarterly noise monitoring",
    "Community complaint log"
  ],
  "Grading": [
    "Erosion control inspection",
    "Grading completion certification"
  ],
  "Fire Code": [
    "Annual fire inspection",
    "Battery hazard mitigation analysis"
  ]
}
```

## Derived planning figures (computed from the records above)

Snapshot date 2026-03-02. Portfolio: 240 active permits; 63 expiring in the next 120 days; total renewal investment
$2.34M across 63 permits; production at risk $47M if permits lapse.

| ID | Facility | Permit type | Expiration | Days left | Lead time | Lead time status | Renewal cost | Production at risk |
|---|---|---|---|---|---|---|---|---|
| PRM-8101 | Imperial Valley Solar | Air Quality | 2026-03-20 | 18 | 90 days | MISSED | $185,000 | $4.2M |
| PRM-8102 | Reno Wind Farm | Environmental | 2026-03-24 | 22 | 120 days | MISSED | $140,000 | $3.1M |
| PRM-8103 | Phoenix Solar | Water Use | 2026-03-28 | 26 | 60 days | MISSED | $95,000 | $2.2M |
| PRM-8104 | Bakersfield Solar | Hazmat | 2026-03-30 | 28 | 60 days | MISSED | $80,000 | $1.6M |
| PRM-8105 | Tehachapi Wind | Avian Protection | 2026-03-31 | 29 | 90 days | MISSED | $60,000 | $1.1M |
| PRM-8106 | Palm Springs Wind | Noise Variance | 2026-03-31 | 29 | 45 days | MISSED | $45,000 | $0.7M |
| PRM-8107 | Yuma Solar | Grading | 2026-03-31 | 29 | 45 days | MISSED | $40,000 | $0.5M |
| PRM-8108 | Mojave Storage | Fire Code | 2026-03-31 | 29 | 45 days | MISSED | $40,000 | $0.4M |

- All 8 are critical (< 30 days) and each is a `renewal_lead_time_missed` compliance gap.
- Emergency renewal package: Investment Required $685,000 for critical renewals; Production Protected $13.8M (combined
  facility capacity); stakeholder alerts drafted for facility managers and legal (Teams and Outlook drafts, not sent);
  daily monitoring with executive escalation recommended. Prepared actions: Imperial Valley expedited air quality renewal
  application prepared, ready to submit; Reno Wind environmental permit vendor shortlisted (2-week turnaround); Phoenix
  Solar county approval fast-track request drafted; Bakersfield hazmat documentation compiled, ready to submit.
- Applications already in progress: APP-7101 Reno Wind Farm under_review; APP-7102 Imperial Valley Solar Phase 2
  public_comment (12 comments, decision 2026-06-30); APP-7103 Phoenix Solar submitted.

## Record-use boundary

- Values are fixed synthetic evidence, not live telemetry or customer records.
- An absent identifier must remain absent; never substitute a different record.
- A recommendation or draft is not proof that an external action occurred.
