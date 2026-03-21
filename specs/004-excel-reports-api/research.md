# Research: Excel Reports API

**Date**: 2026-03-21  
**Purpose**: Resolve technical unknowns and make architectural decisions for the modular Excel report system.

## Findings

### Decision: JSON Schema Definitions
**Decision**: Define detailed Pydantic schemas for both endpoints based on README examples and user requirements.  
**Rationale**: Ensures type safety, validation, and clear API contracts. Mapa-diario uses integer month (1-12) and optional funcionario object; mapa-km uses string month (Portuguese names) and required vehicle object for footer.  
**Alternatives Considered**: Use plain dicts (rejected for lack of validation), JSON Schema only (rejected for less Python integration).

### Decision: Template File Paths and Mapping Configurations
**Decision**: Templates at `templates/mapa_diario.xlsx` and `templates/mapa_km.xlsx`; mappings as JSON files in each report module defining cell addresses for header, rows, footer.  
**Rationale**: Keeps templates versioned with code, mappings configurable without code changes. Row mappings specify start row and column offsets.  
**Alternatives Considered**: Hardcoded paths (rejected for inflexibility), database storage (rejected for no DB constraint).

### Decision: Styling Rules and Colors
**Decision**: Weekends highlighted in light gray (#F0F0F0), holidays in light yellow (#FFFFE0). Applied only to column A, preserving formulas.  
**Rationale**: Standard accessible colors, column A focus prevents data corruption. Weekend detection based on month calendar, holidays from input array.  
**Alternatives Considered**: Template-defined colors (rejected for runtime reading violation), user-configurable colors (rejected for complexity).

### Decision: Error Response Formats
**Decision**: 422 for validation errors with JSON body `{"error": "ValidationError", "details": {...}}`; 500 for internal errors with generic message.  
**Rationale**: Standard HTTP codes, detailed validation feedback for developers, security-conscious error messages.  
**Alternatives Considered**: Custom error codes (rejected for REST standard violation), stack traces in response (rejected for security).

### Decision: Excel Filename Format
**Decision**: `relatorio_<mes>_<timestamp_utc>.xlsx` where mes is sanitized (numeric for diario, string for km).  
**Rationale**: Consistent naming, timestamp prevents overwrites, mes reflects input type.  
**Alternatives Considered**: Random UUIDs (rejected for less meaningful), no timestamp (rejected for collision risk).

### Decision: Implementation Flow Details
**Decision**: API routes validate with Pydantic, call report-specific service which instantiates BaseExcelService with template path, fills data via mappings, applies styles via StyleService, returns BytesIO via StreamingResponse.  
**Rationale**: Clean separation: validation in schemas, business logic in services, Excel ops in BaseExcelService.  
**Alternatives Considered**: Single monolithic service (rejected for modularity violation), async processing (rejected for no async requirement).

### Decision: Month Parsing and Validation
**Decision**: MonthService handles int (1-12) and Portuguese strings ("Janeiro", "Fevereiro", etc.), validates ranges.  
**Rationale**: Centralized logic, supports both report types, clear error messages.  
**Alternatives Considered**: Inline parsing (rejected for duplication), external library (rejected for minimal dependencies).

### Decision: Holiday Processing
**Decision**: HolidayService filters valid integers 1-31, ignores invalid entries with logging.  
**Rationale**: Robust input handling, prevents crashes, maintains determinism.  
**Alternatives Considered**: Strict validation with rejection (rejected for user experience), no filtering (rejected for safety).