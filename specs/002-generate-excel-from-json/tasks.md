# Implementation Tasks: Generate Excel from JSON API

**Feature**: Generate Excel from JSON  
**Branch**: `002-generate-excel-from-json`  
**Date**: 21 March 2026  
**Spec**: [specs/002-generate-excel-from-json/spec.md](spec.md)  

---

## Phase 1: Project Setup & Dependencies

Setup phase: Initialize project structure, install dependencies, configure development environment.

- [ ] T001 Create project directory structure per plan in src/api/routes, src/models, src/services, src/core
- [ ] T002 [P] Create Python project files: src/__init__.py, src/models/__init__.py, src/services/__init__.py, src/core/__init__.py
- [ ] T003 Declare runtime and dev dependencies in pyproject.toml (e.g. FastAPI, uvicorn, openpyxl, pydantic; pytest, pytest-cov in dependency group dev) and manage installs with uv
- [ ] T004 [P] Create .gitignore for Python project (venv, __pycache__, *.pyc, .pytest_cache, .coverage)
- [ ] T005 Create pyproject.toml for project metadata and build configuration in project root
- [ ] T006 [P] Create development environment setup script in .specify/scripts/bash/setup-excel-api.sh with venv initialization
- [ ] T007 Create pytest.ini for test configuration in project root (covering tests/ directory)

---

## Phase 2: Foundational Components

Foundational phase: Core infrastructure that supports all user stories (no user story dependencies).

### Configuration & Exception Handling

- [ ] T008 Create custom exception classes in src/core/exceptions.py: TemplateLoadError, MappingError, ExcelWriteError, ValidationError, InternalServerError
- [ ] T009 [P] Create configuration module in src/core/config.py with template path, mapping path initialization, and startup validation
- [ ] T010 [P] Create logging configuration in src/logging_config.py with structured JSON logging setup

### Data Models & Validation

- [ ] T011 Create request models in src/models/request.py: Meta (empresa, nif, mes), Entry (day, description, location, start_time, end_time), GenerateExcelRequest
- [ ] T012 [P] Create response models in src/models/response.py: error response schema (error type, message, status, details)
- [ ] T013 Create request validation tests in tests/unit/test_models.py: test Meta model, test Entry model, test GenerateExcelRequest validation with missing/extra fields

### Mapping System

- [ ] T014 [P] Create header_mapping.json in templates/mappings/ with fields: empresa→B1, nif→C4, mes→J3
- [ ] T015 Create rows_mapping.json in templates/mappings/ with start_row=8 and column mapping: day→A, description→B, location→D, start_time→E, end_time→J
- [ ] T016 Create mapping loader in src/core/mapping.py: load_header_mapping(), load_rows_mapping() functions with validation
- [ ] T017 [P] Create mapping validation tests in tests/unit/test_mapping.py: test header mapping load, test rows mapping load, test invalid JSON handling

### Template Management

- [ ] T018 Create sample Excel template in templates/excel_template.xlsx with header row (row 1-7) and empty rows starting at row 8 with column headers
- [ ] T019 Document template structure in specs/002-generate-excel-from-json/template-guide.md: header cell locations, column headers, formula preservation instructions

---

## Phase 3: User Story 1 - Generate Excel from Valid JSON (P1)

Core functionality: Accept valid JSON, fill template with data, return Excel file.

### Excel Service Core Implementation

- [ ] T020 [US1] Create excel_service.py in src/services/ with ExcelService class and __init__ method (dependency injection for config)
- [ ] T021 [P] [US1] Implement load_template() method in ExcelService: load XLSX file, handle template load errors
- [ ] T022 [US1] Implement _fill_header() method in ExcelService: iterate header mapping, assign meta field values to cells
- [ ] T023 [P] [US1] Implement _fill_rows() method in ExcelService: loop through entries array, calculate row indices, assign values to mapped columns starting at row 8
- [ ] T024 [US1] Implement _write_to_stream() method in ExcelService: write modified workbook to BytesIO stream, return stream
- [ ] T025 [P] [US1] Implement generate() async method in ExcelService: orchestrate load_template → _fill_header → _fill_rows → _write_to_stream

### API Endpoint Implementation

- [ ] T026 [US1] Create FastAPI app in src/main.py with app initialization, CORS configuration, logging setup
- [ ] T027 [P] [US1] Create POST /generate-excel endpoint in src/api/routes/excel.py: accept GenerateExcelRequest, call excel_service.generate(), return FileResponse
- [ ] T028 [US1] Implement response headers in excel.py endpoint: Content-Type (application/vnd.openxmlformats-officedocument.spreadsheetml.sheet), Content-Disposition with filename convention
- [ ] T029 [P] [US1] Implement filename generation logic in excel.py: format "relatorio_[mes]_[ISO-timestamp].xlsx" with sanitization

### Service Tests

- [ ] T030 [US1] Create unit tests in tests/unit/test_excel_service.py: test_load_template_success, test_load_template_not_found, test_fill_header_all_fields
- [ ] T031 [P] [US1] Create unit tests for _fill_rows: test single entry, test multiple entries, verify row indices calculated correctly
- [ ] T032 [US1] Create unit tests for generate: test end-to-end with valid full data, verify output is valid XLSX
- [ ] T033 [P] [US1] Create integration tests in tests/integration/test_api_endpoint.py: test POST /generate-excel with valid payload, verify response status 200
- [ ] T034 [US1] Add integration test: verify returned file is valid XLSX and can be opened

### Acceptance Tests (User Story 1)

- [ ] T035 [P] [US1] Create acceptance test: send valid JSON with meta fields {empresa, nif, mes} and 1 entry, verify Excel has correct data in mapped cells
- [ ] T036 [US1] Create acceptance test: verify entry data starts at row 8 with correct column mapping (A=day, B=description, D=location, E=start_time, J=end_time)

---

## Phase 4: User Story 2 - Handle Missing Fields Gracefully (P2)

Robustness: Gracefully handle partial/incomplete data.

### Missing Field Handling

- [ ] T037 [P] [US2] Modify _fill_header() in ExcelService to skip None/missing meta fields (do not write to cell if value is None)
- [ ] T038 [US2] Modify _fill_rows() in ExcelService to skip None/missing entry fields (do not write to cell if value is None)
- [ ] T039 [P] [US2] Update models in src/models/request.py: verify all fields are Optional[str] | Optional[int], no required fields except top-level meta/entries

### Robustness Tests

- [ ] T040 [US2] Create unit tests in tests/unit/test_excel_service.py: test_fill_header_missing_fields, test_fill_rows_missing_fields
- [ ] T041 [P] [US2] Create integration tests: POST with missing meta fields, verify success, verify only provided fields populated
- [ ] T042 [US2] Create integration tests: POST with entries missing fields (e.g., no location, no start_time), verify success, verify partial data filled

### Acceptance Tests (User Story 2)

- [ ] T043 [P] [US2] Acceptance test: send JSON with meta={empresa only}, entries=[{day, description only}], verify Excel has only provided data, no errors
- [ ] T044 [US2] Acceptance test: send JSON with all fields missing values (meta={}, entries=[{}]), verify Excel returns success with blank template

---

## Phase 5: User Story 3 - Handle Empty Entries (P3)

Edge case stability: Handle zero entries gracefully.

### Empty Array Handling

- [ ] T045 [P] [US3] Verify _fill_rows() in ExcelService handles empty entries array correctly (no-op, no rows added)
- [ ] T046 [US3] Add validation in models or ExcelService: entries array validation (can be empty, but must be array)

### Edge Case Tests

- [ ] T047 [P] [US3] Create integration test: POST with entries=[], verify success, verify Excel has header data only
- [ ] T048 [US3] Create integration test: POST with empty meta and empty entries, verify success, verify base template returned

### Acceptance Tests (User Story 3)

- [ ] T049 [P] [US3] Acceptance test: send JSON {meta: {empresa: "Test"}, entries: []}, verify Excel generated with header only
- [ ] T050 [US3] Acceptance test: verify generated file is valid and opens in Excel/Sheets

---

## Phase 6: Error Handling & Validation

Cross-cutting: Input validation, error responses, edge cases.

### Input Validation

- [ ] T051 Create request validation in excel.py endpoint: validate GenerateExcelRequest Pydantic model
- [ ] T052 [P] Create error handling in excel.py: catch ValidationError, return 400 with error details
- [ ] T053 Create error handling for template errors: catch TemplateLoadError/MappingError, return 500 with error message
- [ ] T054 [P] Create catch-all error handler in main.py: log unexpected errors, return 500 InternalServerError

### Extra Fields Handling

- [ ] T055 Verify Pydantic models have `extra = "ignore"` config in Meta and Entry classes to ignore unknown fields
- [ ] T056 [P] Create test: POST with extra fields (e.g., meta={empresa, nif, mes, unknown_field}), verify success, extra fields ignored

### Invalid JSON Handling

- [ ] T057 Create error handling in excel.py for malformed JSON: catch JSONDecodeError, return 400
- [ ] T058 [P] Create test: POST with invalid JSON, verify 400 error response

### Invalid Template Handling

- [ ] T059 Create validation in src/core/config.py: check template file exists and is valid XLSX at startup
- [ ] T060 [P] Create test: simulate missing template, verify service fails to start with clear error

### Invalid Mapping Handling

- [ ] T061 Create validation in src/core/mapping.py: validate mapping files are valid JSON and contain required keys
- [ ] T062 [P] Create error test: invalid mapping JSON, verify 500 MappingError response

### Cell Address Validation

- [ ] T063 Create validation in mapping loader: validate cell addresses are valid (e.g., B1, C4, J3 format)
- [ ] T064 [P] Create test: invalid cell address in mapping, verify error during service init

---

## Phase 7: Performance & Determinism

Performance verification, output consistency.

### Performance Tests

- [ ] T065 Create performance test in tests/integration/: generate Excel with 100 entries, measure time, verify <30 seconds
- [ ] T066 [P] Create performance baseline: document typical response times for 10, 50, 100 entries

### Determinism Tests

- [ ] T067 Create determinism test: send identical request twice, verify generated files are bitwise identical (hash comparison)
- [ ] T068 [P] Create test: verify timestamp in filename changes between requests but Excel content is deterministic

### Concurrency Tests

- [ ] T069 Create test: send 10 concurrent requests with same payload, verify all succeed and produce identical Excel content
- [ ] T070 [P] Create test: send concurrent requests with different payloads, verify each produces correct data without interference

---

## Phase 8: Formula & Formatting Preservation

Template integrity: Verify formulas and formatting remain intact.

### Formula Preservation Tests

- [ ] T071 Create Excel template in templates/excel_template.xlsx with sample formulas (e.g., SUM formula in total row)
- [ ] T072 [P] Create test: generate Excel, open output, verify formulas are intact and functional (if possible to detect)

### Formatting Preservation Tests

- [ ] T073 Create Excel template with cell formatting (bold headers, colors, number formats)
- [ ] T074 [P] Create test: generate Excel, verify formatting is preserved in output

### Cell Content Verification

- [ ] T075 Create openpyxl-based test: read output Excel, iterate cells, verify formula cells are not overwritten
- [ ] T076 [P] Create test: verify template cells not in mapping remain unchanged

---

## Phase 9: Contract & API Tests

API contract compliance.

### Request/Response Contract Tests

- [ ] T077 [P] Create contract test in tests/contract/test_api_contract.py: verify endpoint returns 200 with correct Content-Type header
- [ ] T078 Create contract test: verify response has Content-Disposition header with attachment filename

### Error Response Contract Tests

- [ ] T079 [P] Create contract test: POST with missing meta, verify 400 response with error JSON structure
- [ ] T080 Create contract test: POST with missing entries, verify 400 response with error details

### HTTP Status Code Tests

- [ ] T081 [P] Create test suite in tests/contract/: verify all documented HTTP status codes (200, 400, 500)
- [ ] T082 Create test: verify error responses include json body with error, message, status fields

---

## Phase 10: Documentation & Developer Experience

Documentation, examples, deployment guides.

### API Documentation

- [ ] T083 Add OpenAPI/Swagger docstrings to /generate-excel endpoint in src/api/routes/excel.py
- [ ] T084 [P] Add example request/response in docstring for Swagger UI
- [ ] T085 Create API docs generation: verify `GET /docs` endpoint displays Swagger UI with endpoint documentation

### Code Documentation

- [ ] T086 [P] Add docstrings to ExcelService methods: load_template, fill_header, fill_rows, generate
- [ ] T087 Add docstrings to Pydantic models: Meta, Entry, GenerateExcelRequest with field descriptions

### Developer Guide

- [ ] T088 [P] Create DEVELOPMENT.md in project root: setup instructions, running tests, running server
- [ ] T089 Create REQUEST_EXAMPLES.md with cURL and Python examples for all scenarios (valid, missing fields, empty)

### Logging & Monitoring

- [ ] T090 [P] Add logging statements in ExcelService: log template load, header fill, rows fill, stream write
- [ ] T091 Add logging statements in excel.py endpoint: log request received (input size), response generated (file size)
- [ ] T092 [P] Add error logging: log validation errors, template errors with context

---

## Phase 11: Deployment & Production Readiness

Deployment, configuration, production checks.

### Docker Support (Optional)

- [ ] T093 [P] Create Dockerfile for application containerization (Python 3.11 base, install dependencies with uv, uvicorn run)
- [ ] T094 Create docker-compose.yml for local development (optional)

### Configuration for Production

- [ ] T095 [P] Create .env.example with template paths, log level, other config options
- [ ] T096 Add environment variable reading in src/core/config.py for deployment
- [ ] T097 [P] Create production deployment guide in DEPLOYMENT.md: environment setup, health checks, monitoring

### Health & Liveness Checks

- [ ] T098 [P] Add GET /health endpoint in main.py: check template accessibility, return 200 if healthy, 500 if not
- [ ] T099 Create health check test: verify endpoint returns expected status

---

## Phase 12: Polish & Cross-Cutting Concerns

Final quality, cleanup, validation.

### Code Quality

- [ ] T100 [P] Run pytest with coverage: `pytest --cov=src`, target >80% coverage
- [ ] T101 Fix any linting issues: format code with black or similar
- [ ] T102 [P] Add type hints to all functions in src/ (use mypy or pyright for validation)

### Final Integration Tests

- [ ] T103 Create end-to-end test: startup service, send request with full data, verify success and file content
- [ ] T104 [P] Create smoke test suite: run all critical tests before deployment

### README & Project Documentation

- [ ] T105 [P] Create comprehensive README.md: project overview, quick start, API reference link, development setup
- [ ] T106 Create ARCHITECTURE.md: explain service design, layering, data flow, constitution alignment

### Verification Checklist

- [ ] T107 [P] Verify all user stories (P1, P2, P3) have passing acceptance tests
- [ ] T108 Verify all functional requirements (FR-001 through FR-011) are implemented and tested
- [ ] T109 [P] Verify success criteria (SC-001 through SC-004) are met: performance, success rate, error handling, usability
- [ ] T110 Verify no formula or formatting loss in template output

### Dependency Security Scan

- [ ] T111 [P] Run Codacy analysis: check for vulnerabilities in project dependencies (e.g. pyproject.toml / uv.lock)
- [ ] T112 Update vulnerable dependencies if any identified

---

## Dependency Graph & Execution Strategy

### Critical Path (Must Complete First)

1. **T001-T007**: Project setup (enables all other work)
2. **T008-T017**: Configuration, exceptions, models, mapping system (foundation)
3. **T018**: Template creation (required for service functionality)
4. **T020-T029**: Excel service core and API endpoint (core feature)
5. **T035-T036**: Acceptance tests for P1 (verify core works)

### Parallel Work Streams (Can Run Simultaneously)

**After Phase 2 (T001-T017):**

- **Stream A**: Core implementation (T020-T026 U1 implementation)
- **Stream B**: Test infrastructure (T030-T034, T040-T044, T047-T050)
- **Stream C**: Error handling (T051-T064)
- **Stream D**: Documentation (T083-T092)

**After Core Functionality (T020-T036):**

- P2 implementation (T037-T044) and P3 implementation (T045-T050) can run in parallel
- Performance tests (T065-T070) can run once core is complete
- Formula preservation (T071-T076) can run with latest template

### MVP Scope (Minimum Viable Product)

Deliver working P1 functionality with basic testing:

1. T001-T007: Setup
2. T008-T019: Foundation
3. T020-T029: Core service
4. T026-T029: API endpoint
5. T030-T036: Unit and acceptance tests for P1
6. T083-T085: API documentation
7. T100-T101: Code quality

**Deliverable**: `/generate-excel` endpoint working for valid JSON with full data, returns Excel file.

---

## Quality Gates & Sign-Off

### Before Merge to Main

- [ ] All Phase 1-5 tasks (P1, P2, P3) passing: 100% user story coverage
- [ ] All Phase 6 tasks (error handling) passing: 100% error path coverage
- [ ] All Phase 8 tasks (formula preservation) passing: determinism verified
- [ ] Code coverage >80% (Phase 12 T100)
- [ ] Type hints complete (Phase 12 T102)
- [ ] No security vulnerabilities (Phase 12 T111)

### Before Production Deployment

- [ ] All tasks completed (Phase 1-12)
- [ ] Performance benchmarks met (Phase 7 T065)
- [ ] Concurrency tests passing (Phase 7 T069)
- [ ] Docker image built and tested (Phase 11 optional)
- [ ] Health check endpoint operational (Phase 11 T099)
- [ ] Documentation complete and reviewed (Phase 10 & Phase 12)

---

## Statistics

- **Total Tasks**: 112
- **P1 User Story Tasks**: ~36
- **P2 User Story Tasks**: ~12
- **P3 User Story Tasks**: ~10
- **Cross-cutting Tasks**: ~54 (setup, error handling, testing, performance, docs)
- **Critical Path**: ~15 tasks
- **Estimated Duration**: 40-60 developer hours (full team)
- **MVP Duration**: 16-24 developer hours (P1 + setup + basic tests)

---

## Notes for Implementation

- **Formula Preservation**: Ensure mapping never includes cells with active formulas; test output with Excel formula auditor
- **Determinism**: Document any timestamping; use ISO format consistently
- **Template Versioning**: Consider adding template version field for future multi-template support
- **Mapping Flexibility**: Current mapping is static; future versions can support dynamic/scoped mappings per template
- **Error Recovery**: Implement request retry logic on client side for transient errors (5xx)
- **Logging Levels**: Use DEBUG for per-cell writes, INFO for request/response, ERROR for failures
