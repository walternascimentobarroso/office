---
description: "Task list for unified API request refactor"
---

# Tasks: Unified API Request Structure

**Input**: Design documents from `/specs/005-unified-api-request/`
**Prerequisites**: plan.md, spec.md, and contracts definitions

## Phase 1: Setup

- [ ] T001 [P] Initialize task tracking for `005-unified-api-request` in `specs/005-unified-api-request/tasks.md`
- [ ] T002 [P] Add or verify repository-wide linter/pre-commit in `.pre-commit-config.yaml` (if missing) to enforce formatting and imports for this feature

---

## Phase 2: Foundational (Blocking Prerequisites)

- [ ] T003 [P] Create base schema file `src/schemas/base_report.py` with `CompanyModel`, `EmployeeModel`, and `BaseReportRequest` definitions
- [ ] T004 [P] Implement `year` defaulting behavior in `src/schemas/base_report.py` (`BaseReportRequest` validates optional year and sets current year when absent)
- [ ] T005 [P] Add strict request validation behavior in `src/schemas/base_report.py` (prefer `extra=Extra.forbid` or explicit extension path)
- [ ] T006 [P] Update common API contract documentation in `specs/005-unified-api-request/contracts/request-response.md` describing base request fields

**Checkpoint**: Base request shape in place; can begin report-specific schema work.

---

## Phase 3: User Story 1 - Unified Report Request Schema (P1)

**Goal**: All report endpoints accept shared base request with company+employee+month+year+holidays; support report-specific entries.

**Independent Test**: Validate that a minimal unified payload passes route validation for both `mapa_diario` and `mapa_km`.

### Implementation

- [ ] T007 [P] Create `src/schemas/mapa_diario.py` with `MapaDiarioEntry` and `MapaDiarioRequest(BaseReportRequest)` where `entries` type is list of `MapaDiarioEntry`
- [ ] T008 [P] Create `src/schemas/mapa_km.py` with `MapaKmEntry` and `MapaKmRequest(BaseReportRequest)` where `entries` type is list of `MapaKmEntry`
- [ ] T009 [US1] Update `src/api/routes/mapa_diario.py` to use `MapaDiarioRequest` as request model and pass parsed data to report service
- [ ] T010 [US1] Update `src/api/routes/mapa_km.py` to use `MapaKmRequest` as request model and pass parsed data to report service
- [ ] T011 [US1] Update `src/reports/mapa_diario/service.py`, replace `data.meta` with `data.company`; replace `data.meta.mes` with `data.month` and handle `data.year`
- [ ] T012 [US1] Update `src/reports/mapa_km/service.py`, replace `data.meta` with `data.company`; replace `data.meta.mes` with `data.month` and handle `data.year`; validate `vehicle_plate` when used
- [ ] T013 [US1] Update any shared service or helper using meta/month values: `src/services/month_service.py`, `src/services/holiday_service.py`, `src/core/utils.py`
- [ ] T014 [US1] Update `src/services/holiday_service.py` to consume `month` (and `year` optional) for holiday/weekend logic; ensure existing behavior remains intact
- [ ] T015 [US1] Add report-agnostic mapping transform (if needed) in `src/reports/base_report_service.py` or related mapping util to bridge old schema to new contract
- [ ] T016 [US1] Add or update API contract tests in `tests/contract/test_api_mapa_diario.py` and `tests/contract/test_api_mapa_km.py` for unified request structure (company, employee, month, holidays)
- [ ] T017 [US1] Add or update integration tests in `tests/integration/test_mapa_diario_generation.py` and `tests/integration/test_mapa_km_generation.py` to cover new `month`/`year`/`holidays` logic and `employee.vehicle_plate` for `mapa_km`

**Checkpoint**: Report endpoints fully migrated to unified API contract, service mapping updated.

---

## Phase 4: Polish & Cross-Cutting Concerns

- [ ] T018 [P] Audit all code paths for remaining `meta` usage (grep for `meta.` and fix relevant lines) and ensure no stale schema remains
- [ ] T019 [P] Update docs in `README.md` / API docs to show unified payload example for both reports
- [ ] T020 [P] Run static type check (mypy) and adjust models to satisfy typing and pydantic validation rules
- [ ] T021 [P] Perform system test in `tests/integration/test_edge_cases.py` verifying error responses for invalid `month`, `holidays`, or missing core fields
- [ ] T022 [P] Add a task for runtime compatibility test to verify old payload is rejected or adapter behavior is explicit (if compatibility path is required by product decision)

---

## Dependencies & Execution Order

- Phase 1: Setup (no dependencies) - can run immediately
- Phase 2: Foundational (T003..T006) - must complete before Phase 3
- Phase 3: User Story (T007..T017) - depends on Phase 2
- Phase 4: Polish (T018..T022) - after Phase 3

### Parallel Opportunities

- Schema tasks (`T003`, `T004`, `T007`, `T008`) are parallelizable across team members
- Route and service updates for `mapa_diario` and `mapa_km` can be parallel once base schema exists
- Test tasks may run in parallel after implementation tasks complete

---

## Definition of Done

- [ ] All task checkboxes complete
- [ ] Specs and plan updated in `specs/005-unified-api-request`
- [ ] All tests pass (`pytest`) with nothing failing for existing and new flows
- [ ] OpenAPI contract regenerated and includes new schema definitions
- [ ] No unresolved `meta` references remain
- [ ] Code reviewed and merged
