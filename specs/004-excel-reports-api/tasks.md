---

description: "Task list template for feature implementation"
---

# Tasks: Excel Reports API

**Input**: Design documents from `/specs/004-excel-reports-api/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test scenarios are explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below follow the modular structure from plan.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization with FastAPI and openpyxl

- [X] T001 Setup FastAPI project with openpyxl dependency in pyproject.toml
- [X] T002 [P] Create basic FastAPI app structure in src/main.py
- [X] T003 [P] Add health endpoint GET /health in src/main.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Create folder structure: src/api/routes/, src/schemas/, src/reports/, src/services/, src/core/ in src/
- [X] T005 [P] Create Pydantic schemas MapaDiarioRequest and MapaKmRequest in src/schemas/mapa_diario.py and src/schemas/mapa_km.py
- [X] T006 [P] Implement BaseExcelService with generate(), fill_header(), fill_rows(), fill_footer(), apply_styles() in src/services/base_excel_service.py
- [X] T007 [P] Implement StyleService with apply_weekend(), apply_holiday() in src/services/style_service.py
- [X] T008 [P] Implement MonthService with support for int and string months in src/services/month_service.py
- [X] T009 [P] Implement HolidayService with convert holidays list to set and validate values in src/services/holiday_service.py
- [X] T010 [P] Create core utilities and exceptions in src/core/config.py, src/core/exceptions.py, src/core/utils.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Generate Mapa Diário Report (Priority: P1) 🎯 MVP

**Goal**: Enable generation of Mapa Diário Excel reports with header, rows, footer, and weekend/holiday styling

**Independent Test**: Can be fully tested by POST to /reports/mapa-diario with valid JSON and verifying returned Excel has correct data and styling

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T011 [P] [US1] Contract test for POST /reports/mapa-diario endpoint in tests/contract/test_api_mapa_diario.py
- [X] T012 [P] [US1] Integration test for Mapa Diário report generation in tests/integration/test_mapa_diario_generation.py

### Implementation for User Story 1

- [X] T013 [P] [US1] Create report module structure in src/reports/mapa_diario/
- [X] T014 [P] [US1] Implement MapaDiarioService in src/reports/mapa_diario/service.py
- [X] T015 [P] [US1] Create mapping.json for header, rows, footer mappings in src/reports/mapa_diario/mapping.json
- [X] T016 [P] [US1] Create config.json for report configuration in src/reports/mapa_diario/config.json
- [X] T017 [P] [US1] Create template.xlsx placeholder in src/reports/mapa_diario/template.xlsx
- [X] T018 [US1] Implement API route POST /reports/mapa-diario in src/api/routes/mapa_diario.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Generate Mapa KM Report (Priority: P2)

**Goal**: Enable generation of Mapa KM Excel reports with header, rows, footer including vehicle data, and weekend/holiday styling

**Independent Test**: Can be fully tested by POST to /reports/mapa-km with valid JSON and verifying returned Excel has correct data, vehicle footer, and styling

### Tests for User Story 2 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T019 [P] [US2] Contract test for POST /reports/mapa-km endpoint in tests/contract/test_api_mapa_km.py
- [X] T020 [P] [US2] Integration test for Mapa KM report generation in tests/integration/test_mapa_km_generation.py

### Implementation for User Story 2

- [X] T021 [P] [US2] Create report module structure in src/reports/mapa_km/
- [X] T022 [P] [US2] Implement MapaKmService in src/reports/mapa_km/service.py
- [X] T023 [P] [US2] Create mapping.json for header, rows, footer mappings in src/reports/mapa_km/mapping.json
- [X] T024 [P] [US2] Create config.json for report configuration in src/reports/mapa_km/config.json
- [X] T025 [P] [US2] Create template.xlsx placeholder in src/reports/mapa_km/template.xlsx
- [X] T026 [US2] Implement API route POST /reports/mapa-km in src/api/routes/mapa_km.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Handle Edge Cases and Errors (Priority: P3)

**Goal**: Ensure robust error handling for invalid inputs, missing fields, and edge cases with appropriate error responses

**Independent Test**: Can be fully tested by sending various invalid payloads to both endpoints and verifying correct HTTP status codes and error messages

### Tests for User Story 3 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T027 [P] [US3] Contract tests for error scenarios in tests/contract/test_api_errors.py
- [X] T028 [P] [US3] Integration tests for edge cases in tests/integration/test_edge_cases.py

### Implementation for User Story 3

- [X] T029 [US3] Add comprehensive error handling to API routes in src/api/routes/mapa_diario.py and src/api/routes/mapa_km.py
- [X] T030 [US3] Enhance Pydantic schemas with custom validators in src/schemas/mapa_diario.py and src/schemas/mapa_km.py
- [X] T031 [US3] Add error response formatting in src/core/exceptions.py
- [X] T032 [US3] Update services to handle edge cases gracefully in src/services/base_excel_service.py and report services

**Checkpoint**: All user stories should now be independently functional with robust error handling

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Handle Edge Cases and Errors (Priority: P3)

**Goal**: Ensure robust error handling for invalid inputs, missing fields, and edge cases with appropriate error responses

**Independent Test**: Can be fully tested by sending various invalid payloads to both endpoints and verifying correct HTTP status codes and error messages

### Tests for User Story 3 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T027 [P] [US3] Contract tests for error scenarios in tests/contract/test_api_errors.py
- [ ] T028 [P] [US3] Integration tests for edge cases in tests/integration/test_edge_cases.py

### Implementation for User Story 3

- [ ] T029 [US3] Add comprehensive error handling to API routes in src/api/routes/mapa_diario.py and src/api/routes/mapa_km.py
- [ ] T030 [US3] Enhance Pydantic schemas with custom validators in src/schemas/mapa_diario.py and src/schemas/mapa_km.py
- [ ] T031 [US3] Add error response formatting in src/core/exceptions.py
- [ ] T032 [US3] Update services to handle edge cases gracefully in src/services/base_excel_service.py and report services

**Checkpoint**: All user stories should now be independently functional with robust error handling

---

## Phase 6: Testing & Validation

**Purpose**: Comprehensive testing of all scenarios and validation of the complete system

- [ ] T033 [P] Unit tests for all services in tests/unit/test_services.py
- [ ] T034 [P] Unit tests for schemas and validation in tests/unit/test_schemas.py
- [ ] T035 [P] Unit tests for core utilities in tests/unit/test_core.py
- [ ] T036 Test valid data scenarios for both reports
- [ ] T037 Test missing fields handling
- [ ] T038 Test invalid holidays processing
- [ ] T039 Test different month formats (int/string)
- [ ] T040 Test empty entries arrays
- [ ] T041 Test concurrent requests (statelessness)
- [ ] T042 Performance test with 100 entries payload

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and documentation

- [ ] T043 [P] Add comprehensive logging throughout the application
- [ ] T044 [P] Add OpenAPI documentation enhancements
- [ ] T045 [P] Code cleanup and refactoring for consistency
- [ ] T046 [P] Update README with new endpoints
- [ ] T047 [P] Add type hints throughout codebase
- [ ] T048 Run quickstart.md validation and update if needed
- [ ] T049 Final integration test of complete system

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Testing (Phase 6)**: Depends on all user stories being complete
- **Polish (Phase 7)**: Depends on testing completion

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - No dependencies on US1
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May enhance US1/US2 but independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Schemas before services
- Services before routes
- Core implementation before error handling
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Report module components marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Contract test for POST /reports/mapa-diario endpoint in tests/contract/test_api_mapa_diario.py"
Task: "Integration test for Mapa Diário report generation in tests/integration/test_mapa_diario_generation.py"

# Launch all report components for User Story 1 together:
Task: "Create report module structure in src/reports/mapa_diario/"
Task: "Implement MapaDiarioService in src/reports/mapa_diario/service.py"
Task: "Create mapping.json for header, rows, footer mappings in src/reports/mapa_diario/mapping.json"
Task: "Create config.json for report configuration in src/reports/mapa_diario/config.json"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Complete testing and polish → Final system

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Mapa Diário)
   - Developer B: User Story 2 (Mapa KM)
   - Developer C: User Story 3 (Error handling) + Testing
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence