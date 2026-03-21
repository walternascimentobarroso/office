# Implementation Plan: Weekend Highlighting

**Branch**: `003-weekend-highlighting` | **Date**: 2026-03-21 | **Spec**: [specs/003-weekend-highlighting/spec.md](specs/003-weekend-highlighting/spec.md)
**Input**: Feature specification from `/specs/003-weekend-highlighting/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Extend the Excel generation API to support weekend highlighting. Calculate weekend days for a given month using Python datetime, apply fill color to specified columns in weekend rows, ensuring no data or formula modification. Use configuration for color storage.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI, openpyxl  
**Storage**: N/A  
**Testing**: pytest  
**Target Platform**: Linux server  
**Project Type**: web-service  
**Performance Goals**: NEEDS CLARIFICATION (response time for Excel generation with highlighting)  
**Constraints**: Preserve existing formulas and data; apply styles only to fill; no runtime style reading  
**Scale/Scope**: Single request processing, up to 31 rows highlighting

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Gates Passed:**
- Principle 9: Conditional styling based on business rules (weekend calculation)
- Principle 10: Deterministic styling (same input → same highlights)
- Principle 11: No runtime style reading (color from config)
- Principle 12: Configurable reusable styles (weekend_fill in config)
- Principle 13: Preserve data integrity (no data/formula changes)
- Principle 14: Weekend highlighting rule (Saturdays/Sundays highlighted)

No violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/003-weekend-highlighting/
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
├── models/
│   ├── request.py
│   └── response.py
├── services/
│   ├── excel_service.py
│   ├── date_service.py  # NEW
│   └── config.py
├── core/
│   ├── business_calendar.py
│   ├── config.py
│   └── exceptions.py
├── api/
│   └── routes/
│       └── excel.py
└── templates/
    └── mappings/

tests/
├── unit/
│   ├── test_date_service.py  # NEW
│   └── test_excel_service.py
├── integration/
│   └── test_api_endpoint.py
└── contract/
```

**Structure Decision**: Single project structure maintained. New components added to existing services/ and core/ directories. DateService added as new service for weekend calculations. StyleConfig integrated into existing config.py.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
