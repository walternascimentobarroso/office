# Feature Specification: Unified API Request Structure for Excel Reports

**Feature Branch**: `005-unified-api-request`  
**Created**: 2026-03-22  
**Status**: Draft  
**Input**: User description: "Update the API specification to use a unified request structure..."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Unified request schema for all report endpoints (Priority: P1)

A report consumer submits a request to any report endpoint using a shared payload shape containing `company`, `employee`, `month`, `entries`, and `holidays`.

**Why this priority**: This enables consistent integration for clients and reduces schema drift across reports.

**Independent Test**: Send valid payload to each report endpoint and verify orchestration/route-specific entry validation executes as expected.

**Acceptance Scenarios**:

1. **Given** the client sends a request with `company`, `employee`, `month`, `entries`, and `holidays`, **When** endpoint validation runs, **Then** request passes schema checks and reaches report-specific processing.
2. **Given** `employee.vehicle_plate` is omitted, **When** request is sent to `mapa_diario`, **Then** request is accepted and processed (vehicle_plate is optional except for `mapa_km`).

---

### User Story 2 - Enforced top-level month/year and English naming (Priority: P2)

A reporter submits requests with `month` at root and optional `year`, all fields in English terminology.

**Why this priority**: Guarantees temporal standardization and avoids localization ambiguity.

**Independent Test**: Validate with test suite that a request missing root `month` fails and request with integer `month` in 1..12 succeeds.

**Acceptance Scenarios**:

1. **Given** request has `month: 5` and `year: 2025`, **When** validated, **Then** passes if within valid ranges.
2. **Given** request has `month: 13`, **When** validated, **Then** fails with `month must be 1..12` error.

---

### User Story 3 - Validate holidays and report-specific entries (Priority: P3)

A report consumer provides `holidays` as array of day integers and `entries` according to report type schema.

**Why this priority**: Ensures robust data quality and report correctness.

**Independent Test**: Validate that `holidays: [0,32]` fails and each report-specific entry schema (mapa_diario vs mapa_km) applies correctly.

**Acceptance Scenarios**:

1. **Given** request has `holidays: [1, 15, 25]`, **When** validated, **Then** passes.
2. **Given** request has `holidays: [31, 32]`, **When** validated, **Then** fails with `holidays days must be in range 1..31`.

---

### Edge Cases

- Boundary month values: 0, 1, 12, 13
- Empty `entries` array vs missing `entries`
- Employee `vehicle_plate` present with `mapa_diario` (should be accepted but ignored if not needed)
- `year` omitted (should default to current year in server processing layer)
- Additional unknown top-level fields in request (behavior: either reject by strict schema or permit as future-safe extension via open schema)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: All report endpoints MUST accept a base request body with root keys: `company`, `employee`, `month`, `entries`, `holidays`.
- **FR-002**: All schemas MUST replace any legacy `meta` field with `company`.
- **FR-003**: `company` object MUST include `name`, `tax_id`, `address` as strings.
- **FR-004**: `employee` object MUST include `name`, `address`, `tax_id`; `vehicle_plate` is optional and required only for `mapa_km` logic.
- **FR-005**: `month` MUST be an integer between 1 and 12 at top-level.
- **FR-006**: `year` MUST be top-level and optional; if absent, report behavior defaults to current year in server logic.
- **FR-007**: `holidays` MUST be an array of integers where each value is 1..31.
- **FR-008**: `entries` MUST follow report-specific payload schema:
  - `mapa_diario`: daily activity entries structure; existing fields preserved for this report.
  - `mapa_km`: kilometer entries structure including `vehicle_plate` semantic use.
- **FR-009**: All rename rules and requests/response fields MUST maintain English naming consistency across endpoints.
- **FR-010**: System MUST fail validation for unsupported fields unless explicit extension mode is enabled (future-proof strategy).

### Key Entities *(include if feature involves data)*

- **Company**: Encapsulates clear business identity; required for requesting report generation. (name, tax_id, address)
- **Employee**: Contains worker identity and optional vehicle assignment details (vehicle_plate) for mileage reports.
- **ReportRequest**: The unified payload shape with top-level `month` and optional `year`; `entries` is variant for each report type.
- **Holidays**: Array of day-of-month integers (1..31) used by all reports for calendar adjustments.

### Assumptions

- Reporting API can enforce strict JSON schema validation at entrypoint and reject unknown keys unless an extension mode is toggled.
- `year` default behavior is handled in implementation, not required in request when absent.
- Existing report behavior for `mapa_diario` and `mapa_km` will be mapped to new `entries` contract and tested by existing integration tests.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of report API contract tests use the unified payload and pass schema checks for `company`, `employee`, `month`, `entries`, `holidays`.
- **SC-002**: 0% of valid requests are rejected due to naming mismatches when following the English naming scheme in both endpoints.
- **SC-003**: 100% of requests with invalid `month` or `holidays` values are rejected and return clear validation errors.
- **SC-004**: 100% of fields previously named `meta` are removed in generated OpenAPI contract and replaced by `company` in the new spec.

## API Contract

### Base request schema (all reports)

```json
{
  "company": {
    "name": "string",
    "tax_id": "string",
    "address": "string"
  },
  "employee": {
    "name": "string",
    "address": "string",
    "tax_id": "string",
    "vehicle_plate": "string"  // optional, used only by mapa_km
  },
  "month": 1,
  "year": 2026,  // optional
  "entries": [],
  "holidays": [1, 15, 25]
}
```

### Validation rules

- `company.name`, `company.tax_id`, `company.address` are required non-empty strings.
- `employee.name`, `employee.address`, `employee.tax_id` are required non-empty strings.
- `employee.vehicle_plate` is optional; for `mapa_km` it must be non-empty when report logic requires it.
- `month` is required; must be integer 1..12.
- `year` is optional; when provided, must be integer in a valid production-supported range (e.g., 2000..2100).
- `holidays` is required; array of integers each in 1..31; duplicates allowed or normalized by business rules; out of range values fail.
- `entries` is required; structure is validated by report-specific schema.
- Additional fields behavior: strict mode rejects unknown root keys; extension mode may allow unknown keys for future fields.

### Report-specific entries contract

- `mapa_diario` entries: list of objects with fields such as `day`, `work_code`, `hours`, `comment` (preserve existing report semantics).
- `mapa_km` entries: list of objects with fields such as `date`, `distance_km`, `origin`, `destination`, `project_code`.

## Example requests

### Mapa Diario

```json
{
  "company": {"name": "ACME Ltd", "tax_id": "123456789", "address": "1 Main St"},
  "employee": {"name": "Ana Silva", "address": "Rua ABC", "tax_id": "987654321"},
  "month": 4,
  "year": 2026,
  "entries": [
    {"day": 1, "work_code": "A", "hours": 8, "comment": "normal"},
    {"day": 2, "work_code": "B", "hours": 6}
  ],
  "holidays": [1, 25]
}
```

### Mapa KM

```json
{
  "company": {"name": "ACME Ltd", "tax_id": "123456789", "address": "1 Main St"},
  "employee": {"name": "Ana Silva", "address": "Rua ABC", "tax_id": "987654321", "vehicle_plate": "XYZ-1234"},
  "month": 4,
  "year": 2026,
  "entries": [
    {"date": "2026-04-01", "distance_km": 120, "origin": "Factory", "destination": "Client"},
    {"date": "2026-04-02", "distance_km": 80, "origin": "Client", "destination": "Factory"}
  ],
  "holidays": [1, 25]
}
```

