# Implementation Plan: Excel Reports API

**Branch**: `004-excel-reports-api` | **Date**: 2026-03-21 | **Spec**: specs/004-excel-reports-api/spec.md
**Input**: Feature specification from `/specs/004-excel-reports-api/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Create a FastAPI service that generates multiple Excel reports (mapa-diario and mapa-km) using a modular, plugin-like architecture with shared services for common functionality. Each report follows a consistent pipeline: load template → fill data → apply styles → return file, ensuring deterministic output and easy extensibility.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI, openpyxl  
**Storage**: N/A (stateless, no persistence)  
**Testing**: pytest  
**Target Platform**: Linux server  
**Project Type**: web-service  
**Performance Goals**: <5 seconds response time for payloads up to 100 entries  
**Constraints**: Modular architecture with clear separation of concerns, deterministic output, JSON as source of truth, no database, no authentication  
**Scale/Scope**: Support for multiple report types with independent schemas, extensible to new reports

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Report Isolation: Does the plan ensure each report is self-contained with plugin-like structure? ✅ Yes - each report in separate module with own service, mapping, config, template
- Multiple Report Support: Does the architecture support independent schemas and behaviors for different report types? ✅ Yes - separate endpoints, schemas, and report modules
- Pipeline Consistency: Is the Excel generation following load template → fill data → apply styles → return file? ✅ Yes - BaseExcelService implements consistent pipeline
- Styling Reusability: Are weekend/holiday styling rules centralized and reusable? ✅ Yes - StyleService provides reusable styling methods
- Determinism: Will the system produce identical outputs for identical inputs? ✅ Yes - stateless design, no external dependencies affecting output
- JSON Source of Truth: Is JSON the single authoritative input source? ✅ Yes - all data derived from JSON payload
- Extensibility: Can new reports be added easily without major changes? ✅ Yes - plugin-like structure, add new report module without touching core
- Modularity: Does the design maintain clear separation of concerns and modular architecture? ✅ Yes - separate modules for API, schemas, reports, services, core

## Project Structure

### Documentation (this feature)

```text
specs/004-excel-reports-api/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── api/
│   └── routes/
│       ├── mapa_diario.py
│       └── mapa_km.py
├── schemas/
│   ├── mapa_diario.py
│   └── mapa_km.py
├── reports/
│   ├── mapa_diario/
│   │   ├── service.py
│   │   ├── mapping.json
│   │   ├── config.json
│   │   └── template.xlsx
│   └── mapa_km/
│       ├── service.py
│       ├── mapping.json
│       ├── config.json
│       └── template.xlsx
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

**Structure Decision**: Adopted modular architecture with /reports containing plugin-like report modules, /services for shared business logic, /schemas for validation, and /api/routes for endpoints. This aligns with constitution principles of report isolation, modularity, and clear separation of concerns.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations - design fully compliant with constitution principles.
