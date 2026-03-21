# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Create a RESTful API endpoint (`POST /generate-excel`) that accepts structured JSON containing company metadata and time-entry data, then generates a filled Excel file using a configurable template and cell mapping system. The service will validate input, load a pre-built Excel template, fill header fields from metadata, populate rows dynamically starting at row 8, preserve all template formulas and formatting, and return the generated file as a downloadable response. The implementation will prioritize robustness (graceful handling of missing fields), deterministic output, and template immutability in accordance with the project constitution.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI (HTTP API framework), openpyxl (Excel template handling), Pydantic (input validation)  
**Storage**: File-based templates (XLSX templates stored in application resources)  
**Testing**: pytest with pytest-cov for coverage  
**Target Platform**: Linux server (cloud-native deployment)  
**Project Type**: Web service (REST API)  
**Performance Goals**: Generate Excel file in under 30 seconds for up to 100 entries (SC-001)  
**Constraints**: <30s response time per request, response must be deterministic (bitwise identical for same inputs)  
**Scale/Scope**: Initial scope: 1 template type, 1 mapping configuration, stateless service

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Principle Alignment Verification**:

✅ **P1 - JSON is source of truth**: Design includes Pydantic models for strict input validation; all transformations derive from JSON payload.

✅ **P2 - Template-driven generation**: Architecture loads template once per request and generates fresh output without mutation; no file state carried across requests.

✅ **P3 - Fixed header + dynamic rows**: Mapping system supports both fixed cell addresses (header_mapping.json) and dynamic row ranges (rows_mapping.json with start_row=8).

✅ **P4 - Preserve formulas/formatting**: openpyxl preserves cell attributes automatically; mapping explicitly avoids overwriting formula columns.

✅ **P5 - Explicit mapping contract**: Mapping files document static vs dynamic targets; code enforces contract during fill operations.

✅ **P6 - Deterministic output**: Stateless service with fixed template + deterministic mapping produces bitwise identical output for same inputs.

✅ **P7 - Statelessness**: No session state, all context from request payload and template files; caching (if added) will be safe replicate-only.

✅ **P8 - Production-ready code**: Plan includes unit tests, error handling, logging, type validation via Pydantic, and extension points (mapping file configuration).

**Gate Status**: PASS - No violations identified.

## Project Structure

### Documentation (this feature)

```text
specs/002-generate-excel-from-json/
├── plan.md              # This file (implementation plan)
├── research.md          # Phase 0 - Research findings (to be created)
├── data-model.md        # Phase 1 - Data entities and schemas (to be created)
├── contracts/           # Phase 1 - API contracts and interfaces (to be created)
│   ├── request-response.md
│   └── error-responses.md
├── quickstart.md        # Phase 1 - Developer quick start guide (to be created)
└── tasks.md             # Phase 2 - Actionable tasks (to be created by /speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── api/
│   └── routes/
│       └── excel.py              # POST /generate-excel endpoint
├── models/
│   ├── request.py                # Pydantic request schemas (Meta, Entry, Request)
│   └── response.py               # Pydantic response schemas (error models)
├── services/
│   └── excel_service.py          # Core service: load_template, fill_header, fill_rows
├── core/
│   ├── config.py                 # Template path, mapping path configuration
│   ├── mapping.py                # Mapping system initialization
│   └── exceptions.py             # Custom exception classes
└── main.py                       # FastAPI app initialization

templates/
├── excel_template.xlsx           # Base Excel template file
└── mappings/
    ├── header_mapping.json       # Fixed header cell mapping
    └── rows_mapping.json         # Dynamic rows mapping

tests/
├── unit/
│   ├── test_excel_service.py    # Unit tests for excel_service
│   ├── test_models.py           # Unit tests for request validation
│   └── test_mapping.py          # Unit tests for mapping system
├── integration/
│   └── test_api_endpoint.py     # Integration tests for /generate-excel
└── contract/
    └── test_api_contract.py     # API contract validation tests
```

**Structure Decision**: Single project structure with clear separation of concerns (API layer, services, models, core utilities). Templates and mappings are configuration-driven for flexibility. Tests are organized by type (unit, integration, contract) for clarity and maintainability.

## Complexity Tracking

No violations identified; all constitution principles are addressable within the planned scope.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
