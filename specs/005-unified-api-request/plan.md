# Implementation Plan: Unified API Request Structure

**Branch**: `005-unified-api-request` | **Date**: 2026-03-22 | **Spec**: specs/005-unified-api-request/spec.md
**Input**: Feature specification from `/specs/005-unified-api-request/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Refactor the existing Excel report API to use a unified base request schema (company/employee/month/entries/holidays + optional year) while preserving report-specific entry rules for `mapa_diario` and `mapa_km`. Update schemas, services, and routes with minimal structure breakage, and ensure holiday/weekend behavior remains intact.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI, openpyxl, pydantic  
**Storage**: N/A (stateless, no persistence)  
**Testing**: pytest  
**Target Platform**: Linux/macOS server  
**Project Type**: web-service  
**Performance Goals**: <5 seconds response for payloads with up to 100 entries  
**Constraints**: deterministic reports, modular architecture, JSON as source of truth, no DB/auth  
**Scale/Scope**: existing `mapa_diario` and `mapa_km` endpoints; foundation for additional reports

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Report Isolation: Does the plan ensure each report is self-contained with plugin-like structure? ✅ Yes - report modules remain independent and schema mapping is report-specific.
- Multiple Report Support: Does the architecture support independent schemas and behaviors for different report types? ✅ Yes - base request + report-specific child schemas.
- Pipeline Consistency: Is the Excel generation following load template → fill data → apply styles → return file? ✅ Yes - no changes to existing pipeline.
- Styling Reusability: Are weekend/holiday styling rules centralized and reusable? ✅ Yes - unchanged existing style service and calendar logic.
- Determinism: Will the system produce identical outputs for identical inputs? ✅ Yes - using fixed transformations and no external non-determinism.
- JSON Source of Truth: Is JSON the single authoritative input source? ✅ Yes - unified request JSON with strict schema.
- Extensibility: Can new reports be added easily without major changes? ✅ Yes - the shared base request supports plugins via report-specific entries.
- Modularity: Does the design maintain clear separation of concerns and modular architecture? ✅ Yes - adding base schema only improves consistency.
- API Domain Naming: Are all request fields explicit domain names (no generic field names)? ✅ Yes - `company`, `employee`, `month`, `year`, `entries`, `holidays`.
- Company Metadata: Is the metadata field named "company" (not "meta")? ✅ Yes.
- Top-Level Time Fields: Does the request schema include top-level "month" and optionally "year"? ✅ Yes.
- Future-Proof Contract: Does the plan allow new reports and fields without disruptive refactoring? ✅ Yes, via report-specific entries + optional extension mode.

## Project Structure

### Documentation (this feature)

```text
specs/005-unified-api-request/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md
```

### Source Code (repository root)

```text
src/
├── api/
│   └── routes/
│       ├── mapa_diario.py
│       └── mapa_km.py
├── schemas/
│   ├── base_report.py   # new base schema
│   ├── mapa_diario.py
│   └── mapa_km.py
├── reports/
│   ├── mapa_diario/
│   └── mapa_km/
├── services/
│   ├── base_excel_service.py
│   ├── style_service.py
│   ├── month_service.py
│   └── holiday_service.py
└── core/
    ├── config.py
    ├── exceptions.py
    └── utils.py

tests/
├── contract/
├── integration/
└── unit/
```

**Structure Decision**: Keep existing modular architecture and route mapping; add a shared schema module for base request types and update service payload handoffs.

## Phase 1: Shared Schema Refactor

### Task 1.1 - Create shared base schema

- `src/schemas/base_report.py`:
  - `CompanyModel(name: str, tax_id: str, address: str)`
  - `EmployeeModel(name: str, address: str, tax_id: str, vehicle_plate: Optional[str] = None)`
  - `BaseReportRequest(month: conint(ge=1, le=12), year: Optional[conint(ge=2000, le=2100)] = None, company: CompanyModel, employee: EmployeeModel, holidays: conlist(conint(ge=1, le=31), min_items=0), entries: list[Any])`
  - `@validator("year", always=True)` defaults to current year if absent.
  - strict field mode: no extra keys unless `extra = Extra.ignore` in extension mode.

### Task 1.2 - Update API/route dependencies for new base schema

- `src/api/routes/mapa_diario.py` and `src/api/routes/mapa_km.py` to use `BaseReportRequest` in signatures.
- Ensure each route also validates report-specific entries via `MapadiarioReportRequest` / `MapaKmReportRequest` schema.

## Phase 2: Report-Specific Schemas

### Task 2.1 - MapaDiarioRequest

- `src/schemas/mapa_diario.py`:
  - `MapaDiarioEntry` fields (existing domain fields requiring English names)
  - `MapaDiarioRequest(BaseReportRequest)` with `entries: conlist(MapaDiarioEntry, min_items=1)`
  - ensure `employee.vehicle_plate` remains optional and accepted.

### Task 2.2 - MapaKmRequest

- `src/schemas/mapa_km.py`:
  - `MapaKmEntry` fields (`date`, `distance_km`, `origin`, `destination`, `project_code` etc.)
  - `MapaKmRequest(BaseReportRequest)` with `entries: conlist(MapaKmEntry, min_items=1)`
  - add optional `vehicle_plate` but require non-empty on business layer if metrics need vehicle context.

## Phase 3: Service Refactor

### Task 3.1 - Upgrade report services to company/month/year

- `src/reports/mapa_diario/service.py` and `src/reports/mapa_km/service.py`:
  - Replace any `meta` references with `request.company`
  - Use `request.month` and `request.year`
  - If `year` is None, use `month_service.get_current_year()` fallback.

### Task 3.2 - Holiday/weekend logic validation

- `src/services/holiday_service.py` / `month_service.py`:
  - Ensure `holidays` range validation still enforced (1..31).
  - Confirm `holiday` processing still merges with weekend shading from `style_service`.
  - Add tests for edge cases: holidays outside month boundaries, weekend overrides with holidays.

## Phase 4: Route & API updates

### Task 4.1 - Update `src/api/routes` endpoints

- `@app.post("/mapa_diario")` request model from old schema to `MapaDiarioRequest`.
- `@app.post("/mapa_km")` request model to `MapaKmRequest`.
- Update export to explicit response model if needed.

### Task 4.2 - Update API docs and contracts

- Regenerate OpenAPI docs / `specs/005-unified-api-request/contracts/request-response.md`.
- Add contract section for base request JSON and report-specific entries.

## Phase 5: Compatibility & Testing

### Task 5.1 - Existing logic compatibility

- Keep existing report pipelines in `src/reports/...` unchanged except for the `company` and `month` field mapping.
- Add adapter in route layer if old request structure still accepted for backward compatibility optionally (if needed by requirement, not required but advisable).

### Task 5.2 - Tests

- Update unit tests in `tests/unit/test_schemas.py` (or new file): base schema, MapaDiarioRequest, MapaKmRequest.
- Integration tests in `tests/integration/test_mapa_diario_generation.py` and `tests/integration/test_mapa_km_generation.py`:
  - verify new request structure flows correctly.
  - verify `month` range enforcement and default `year` behavior.
  - verify `holidays` value constraints and weekend behavior unchanged.

### Task 5.3 - Contract tests

- Update contract tests in `tests/contract/test_api_mapa_diario.py` and `tests/contract/test_api_mapa_km.py` to exercise unified request and error semantics.

## Complexity Tracking

No constitution violations identified; plan remains aligned with objectives and modular architecture.

---

## Deliverables

- `specs/005-unified-api-request/plan.md` (this file)
- `specs/005-unified-api-request/spec.md` (existing)
- `specs/005-unified-api-request/checklists/requirements.md` (existing)
- `src/schemas/base_report.py` + updated report schemas
- Updated `src/reports/*/service.py` and `src/api/routes/*.py`
- Updated tests in `tests/unit/`, `tests/integration/`, `tests/contract/`
- Updated contracts in `specs/005-unified-api-request/contracts/`
