# Research & Design Decisions: Excel Generation API

**Feature**: Generate Excel from JSON  
**Date**: 20 March 2026  
**Phase**: Phase 0 - Research & Clarification  

## Findings

### 1. Template File Loading & Storage

**Decision**: Template stored in application resources directory under `templates/excel_template.xlsx`

**Rationale**: 
- Aligns with web service best practices (templates bundled with application)
- Ensures consistency between environments (no external file path configuration needed initially)
- Supports easy deployment and version control of templates with code

**Alternatives Considered**:
- Environment variable configuration: More flexible but adds complexity for initial implementation
- Admin upload endpoint: Beyond initial scope; can be added later as extension
- Hardcoded in code: Not practical for binary files

**Implementation Detail**: Template path is configurable via `src/core/config.py`, allowing future migration to environment variables or admin upload without code changes to core service.

---

### 2. Invalid Template Handling

**Decision**: Template validation occurs on service startup and per-request. Invalid templates return HTTP 500 error with descriptive message.

**Rationale**:
- Service startup validation catches misconfigured deployments early
- Per-request validation with graceful error messages supports debugging
- HTTP 500 indicates server error (not client fault) appropriate for template issues

**Validation Checks**:
- File exists and is readable
- File is valid XLSX format (openpyxl can parse it)
- File contains no circular formula references that would corrupt on write

**Error Response**:
```json
{
  "error": "TemplateLoadError",
  "message": "Template file cannot be loaded: [reason]",
  "status": 500
}
```

---

### 3. Excel Cell Mapping Strategy

**Decision**: Two-file mapping system with fixed header mapping and dynamic row mapping.

**Rationale**:
- Separates static configuration from template file (easier to update mappings without touching template)
- Explicit contracts make mapping behavior clear to developers
- Supports future multi-template scenarios

**Files**:
- `templates/mappings/header_mapping.json`: Fixed target cells for header fields
- `templates/mappings/rows_mapping.json`: Dynamic row configuration and column mapping

**Structure**:

```json
// header_mapping.json
{
  "empresa": "B1",
  "nif": "C4",
  "mes": "J3"
}

// rows_mapping.json
{
  "start_row": 8,
  "columns": {
    "day": "A",
    "description": "B",
    "location": "D",
    "start_time": "E",
    "end_time": "J"
  }
}
```

---

### 4. Formula & Formatting Preservation

**Decision**: Use openpyxl in value-only mode for data injection; preserve all template cell attributes.

**Rationale**:
- openpyxl automatically preserves formatting, formulas (in cells not written to), and styles
- Writing only to mapped cells ensures formulas in other columns remain untouched
- Deterministic behavior: same input always produces identical output

**Implementation**:
- Load template as read-only model
- Inject values only into mapped cells
- Write new workbook from modified model to BytesIO stream
- Return stream as response

---

### 5. Missing Field Handling

**Decision**: Skip missing fields in mapping; leave corresponding cells blank (unchanged from template).

**Rationale**:
- Robust error tolerance (requested in FR-009)
- Template may contain placeholder values that should persist if input is missing
- Blank cells are safer than defaults (no data ambiguity)

**Implementation**:
```python
# For each entry in entries array:
#   For each mapped column:
#     if field_value exists in input:
#       write value to cell
#     else:
#       continue (do not write anything)
```

---

### 6. Input Validation & Error Handling

**Decision**: Use Pydantic for strict schema validation; return HTTP 400 for invalid input with detailed error messages.

**Rationale**:
- Pydantic provides automatic validation with clear error reporting
- HTTP 400 signals client error (invalid input)
- Detailed error messages help developers fix input quickly

**Validation Rules**:
- `meta` object MUST be present and be an object (even if empty)
- `entries` array MUST be present and be an array (can be empty)
- Unknown fields in `meta` or `entry` are ignored (FR-010)
- Required fields within `meta` and `entries`: none (all optional for robustness)
- Type coercion: integers and strings are coerced; invalid types rejected

**Error Response**:
```json
{
  "error": "ValidationError",
  "message": "Invalid request body",
  "details": [
    {
      "field": "meta",
      "issue": "field required"
    }
  ],
  "status": 400
}
```

---

### 7. Response Format & Download

**Decision**: Return Excel file as binary attachment with Content-Disposition header; filename based on timestamp + metadata.

**Rationale**:
- Standard HTTP file download behavior
- Filename includes metadata (mes value if available) for user convenience
- Binary MIME type triggers browser download

**Response Headers**:
```
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename="relatorio_[mes]_[timestamp].xlsx"
```

---

### 8. Performance & Concurrency

**Decision**: Stateless async service using FastAPI and async/await; no caching of template content (fresh load per request).

**Rationale**:
- Ensures deterministic output (no cache coherency issues)
- Leverages FastAPI async for handling concurrent requests efficiently
- Aligns with constitution principle of statelessness
- Performance target (30s for 100 entries) is easily met with modern hardware

**Optimization Opportunities** (for future phases):
- Template file caching in memory after first load (safe with versioning)
- Batch processing endpoint for bulk generation
- Streaming responses for very large files

---

### 9. Logging & Monitoring

**Decision**: Structured logging (JSON format) for all key operations; metrics for success/error rates.

**Rationale**:
- Supports production debugging and SLA tracking
- Enable observability for performance monitoring

**Logged Events**:
- Request received (with input size)
- Template loaded (with checksum for version tracking)
- Fill operations (header filled, N rows filled)
- Response generated (file size)
- Error cases (validation failure, template error, etc.)

---

## Summary Table

| Aspect | Decision | Status |
|--------|----------|--------|
| Template storage | File-based in app resources | ✅ Confirmed |
| Invalid template | Return 500, validate on startup | ✅ Confirmed |
| Cell mapping | Two JSON files (header + rows) | ✅ Confirmed |
| Formulas | Preserve via openpyxl | ✅ Confirmed |
| Missing fields | Skip, leave cells unchanged | ✅ Confirmed |
| Validation | Pydantic with HTTP 400 errors | ✅ Confirmed |
| Response | Binary Excel + download headers | ✅ Confirmed |
| Concurrency | Stateless async service | ✅ Confirmed |
| Logging | Structured JSON logging | ✅ Confirmed |

All research questions have been resolved. Ready for Phase 1 design.
