# Tasks: Weekend Highlighting

**Input**: Design documents from `/specs/003-weekend-highlighting/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Included as requested in feature specification for validation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root

## Dependencies

- Setup tasks complete before Foundational
- Foundational tasks complete before User Story tasks
- User Story tasks complete before Polish & Testing

## Parallel Execution Examples

- Setup tasks can run in parallel (different config files)
- Foundational tasks: DateService and validation can run in parallel
- US1 tasks: ExcelService updates can be parallel if split by method

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Configure weekend highlighting color and extend configuration

- [X] T001 Extract weekend highlight color from template A8 in src/core/config.py
- [X] T002 Add weekend_fill configuration key to src/core/config.py

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core services and validation for weekend calculation

- [X] T003 Create DateService class in src/services/date_service.py
- [X] T004 Implement get_weekend_days method in src/services/date_service.py
- [X] T005 Add mes field validation to src/models/request.py
- [X] T006 Update request contract validation in src/api/routes/excel.py

## Phase 3: User Story 1 - Weekend Day Highlighting

**Purpose**: Implement weekend row highlighting in Excel generation

- [X] T007 [US1] Extend ExcelService with weekend_days parameter in src/services/excel_service.py
- [X] T008 [US1] Add apply_weekend_style method to ExcelService in src/services/excel_service.py
- [X] T009 [US1] Update generate_excel flow to calculate and apply weekend styling in src/services/excel_service.py
- [X] T010 [US1] Implement PatternFill styling for columns A,B,D,E,J in src/services/excel_service.py

## Final Phase: Polish & Cross-Cutting Concerns

**Purpose**: Testing, error handling, and validation

- [X] T011 Add unit tests for DateService in tests/unit/test_date_service.py
- [X] T012 Add integration test for weekend highlighting in tests/integration/test_api_endpoint.py
- [X] T013 Add contract test for mes validation in tests/contract/test_api_endpoint.py
- [X] T014 Test month with 28 days (February) highlighting in tests/unit/test_excel_service.py
- [X] T015 Test month with 31 days highlighting in tests/unit/test_excel_service.py
- [X] T016 Test month starting on weekend highlighting in tests/unit/test_excel_service.py
- [X] T017 Verify no data/formula changes in tests/unit/test_excel_service.py
- [X] T018 Update quickstart documentation if needed in specs/003-weekend-highlighting/quickstart.md