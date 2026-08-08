# Field Service Dispatch Agent — Complete Synthetic Records

> COMPLETE SYNTHETIC PILOT DATA. Every organization, person, identifier, date, measurement, cost, score, status, and schedule below is fictional. Use only these records; do not supplement them with external facts.

## Provenance

- Deterministic source: `agents/@aibast-agents-library/energy_stacks/field_service_dispatch_stack/field_service_dispatch_agent.py`
- Captured source SHA-256: `f6006d1be6da7dee92f23cb3acd9143e5c0be10ef85cc8271ef80750dbd3d2ba`
- Locked case file: `tests/demo_cases/field-service-dispatch.json`
- Locked case SHA-256: `185fda3b289e937edeabe433c7840536737549d554711bda50c20491957ae60a`
- Strict isolation: `true`

## Record index

- `TECHNICIANS`
- `SERVICE_REQUESTS`
- `GEOGRAPHIC_ZONES`

## TECHNICIANS

```json
{
  "TECH-201": {
    "name": "Carlos Rivera",
    "certifications": [
      "electrical_high_voltage",
      "transformer_maintenance",
      "confined_space"
    ],
    "zone": "West",
    "status": "available",
    "current_location": "Sacramento, CA",
    "jobs_today": 1,
    "max_jobs": 4,
    "efficiency_rating": 94,
    "years_experience": 12
  },
  "TECH-202": {
    "name": "Amy Blackwell",
    "certifications": [
      "wind_turbine",
      "electrical_high_voltage",
      "crane_operation"
    ],
    "zone": "Central",
    "status": "on_job",
    "current_location": "Sweetwater, TX",
    "jobs_today": 2,
    "max_jobs": 4,
    "efficiency_rating": 91,
    "years_experience": 8
  },
  "TECH-203": {
    "name": "Raj Patel",
    "certifications": [
      "gas_turbine",
      "combustion_systems",
      "electrical_high_voltage"
    ],
    "zone": "West",
    "status": "available",
    "current_location": "Bakersfield, CA",
    "jobs_today": 0,
    "max_jobs": 4,
    "efficiency_rating": 97,
    "years_experience": 15
  },
  "TECH-204": {
    "name": "Sarah Johansson",
    "certifications": [
      "pipeline_inspection",
      "welding_api1104",
      "hazmat"
    ],
    "zone": "Northeast",
    "status": "available",
    "current_location": "Scranton, PA",
    "jobs_today": 1,
    "max_jobs": 4,
    "efficiency_rating": 88,
    "years_experience": 6
  },
  "TECH-205": {
    "name": "Marcus Thompson",
    "certifications": [
      "electrical_high_voltage",
      "transformer_maintenance",
      "scada_systems"
    ],
    "zone": "Central",
    "status": "on_break",
    "current_location": "Denver, CO",
    "jobs_today": 2,
    "max_jobs": 4,
    "efficiency_rating": 92,
    "years_experience": 10
  }
}
```

## SERVICE_REQUESTS

```json
{
  "SR-4001": {
    "title": "Transformer oil leak - Ridgeline Substation",
    "priority": "high",
    "type": "corrective",
    "required_certs": [
      "transformer_maintenance",
      "electrical_high_voltage"
    ],
    "zone": "Central",
    "location": "Moffat County, CO",
    "equipment": "Substation Transformer B-12",
    "estimated_hours": 6,
    "status": "unassigned"
  },
  "SR-4002": {
    "title": "Quarterly turbine blade inspection - Sweetwater",
    "priority": "medium",
    "type": "preventive",
    "required_certs": [
      "wind_turbine"
    ],
    "zone": "Central",
    "location": "Nolan County, TX",
    "equipment": "Wind Turbine Alpha-7",
    "estimated_hours": 4,
    "status": "assigned"
  },
  "SR-4003": {
    "title": "Gas turbine fuel nozzle replacement",
    "priority": "high",
    "type": "corrective",
    "required_certs": [
      "gas_turbine",
      "combustion_systems"
    ],
    "zone": "West",
    "location": "Sacramento, CA",
    "equipment": "Gas Turbine GT-3A",
    "estimated_hours": 8,
    "status": "unassigned"
  },
  "SR-4004": {
    "title": "Pipeline cathodic protection survey",
    "priority": "medium",
    "type": "preventive",
    "required_certs": [
      "pipeline_inspection"
    ],
    "zone": "Northeast",
    "location": "Lackawanna County, PA",
    "equipment": "Gas Pipeline Segment NE-14",
    "estimated_hours": 5,
    "status": "unassigned"
  },
  "SR-4005": {
    "title": "Emergency: SCADA communication failure",
    "priority": "critical",
    "type": "emergency",
    "required_certs": [
      "scada_systems",
      "electrical_high_voltage"
    ],
    "zone": "Central",
    "location": "Denver, CO",
    "equipment": "Ridgeline Substation SCADA",
    "estimated_hours": 3,
    "status": "unassigned"
  }
}
```

## GEOGRAPHIC_ZONES

```json
{
  "West": {
    "states": [
      "CA",
      "NV",
      "OR",
      "WA"
    ],
    "technicians": 2,
    "open_requests": 1
  },
  "Central": {
    "states": [
      "TX",
      "CO",
      "OK",
      "KS",
      "NM"
    ],
    "technicians": 2,
    "open_requests": 3
  },
  "Northeast": {
    "states": [
      "PA",
      "NY",
      "NJ",
      "CT",
      "MA"
    ],
    "technicians": 1,
    "open_requests": 1
  }
}
```

## Record-use boundary

- Values are fixed synthetic evidence, not live telemetry or customer records.
- An absent identifier must remain absent; never substitute a different record.
- A recommendation or draft is not proof that an external action occurred.
