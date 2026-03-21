# Error Handling Strategy

**Feature**: Generate Excel from JSON  
**Phase**: Phase 1 - Design  
**Date**: 20 March 2026  

## Error Taxonomy

Errors are categorized by source and severity:

### Client Errors (HTTP 4xx)

#### ValidationError (400)

**Scope**: Invalid request structure or data types

**Triggers**:
- Missing required fields (`meta`, `entries`)
- Unexpected field types (e.g., `entries` is string instead of array)
- Invalid JSON syntax in request body
- Constraint violations (though data is generally permissive)

**Response**:
```json
{
  "error": "ValidationError",
  "message": "Invalid request body",
  "status": 400,
  "details": [
    {
      "field": "entries",
      "issue": "Expected array, got string"
    }
  ]
}
```

**Recovery**: Client must fix request and retry.

---

### Server Errors (HTTP 5xx)

#### TemplateLoadError (500)

**Scope**: Template file cannot be accessed or parsed

**Triggers**:
- Template file not found at configured path
- Template file is not valid XLSX format
- File permissions prevent reading
- File is corrupted or truncated

**Timing**:
- Detected per-request when template is loaded
- Also detected at service startup (fail-fast); service does not start if template inaccessible

**Response**:
```json
{
  "error": "TemplateLoadError",
  "message": "Template file cannot be loaded: File not found at templates/excel_template.xlsx",
  "status": 500
}
```

**Recovery**: 
- Check template file exists at configured path
- Verify file is valid XLSX
- Check server file permissions
- Restart service after fix

---

#### MappingError (500)

**Scope**: Mapping configuration files are invalid or missing

**Triggers**:
- Mapping JSON files not found
- Mapping JSON files contain invalid JSON syntax
- Mapping references invalid cell addresses (e.g., "ZZZ99999")
- Mapping references cells that would cause conflicts

**Timing**: Detected per-request when mapping is loaded

**Response**:
```json
{
  "error": "MappingError",
  "message": "Mapping configuration is invalid: Invalid JSON in templates/mappings/header_mapping.json",
  "status": 500
}
```

**Recovery**:
- Verify mapping files exist and contain valid JSON
- Review cell address syntax
- Consult mapping schema in research.md
- Restart service after fix

---

#### ExcelWriteError (500)

**Scope**: Error during Excel file generation or writing

**Triggers**:
- openpyxl internal error during cell writing
- Out of memory during large file generation
- Disk space exhausted (for temporary files)
- Circular formula references detected in template

**Timing**: Detected during fill operations

**Response**:
```json
{
  "error": "ExcelWriteError",
  "message": "Error generating Excel file: [detailed reason]",
  "status": 500
}
```

**Recovery**:
- Check server memory and disk space
- Review template for circular formulas
- Retry request (may be transient resource issue)
- Contact support if persistent

---

#### InternalServerError (500)

**Scope**: Unexpected error (catch-all for unhandled exceptions)

**Triggers**:
- Unhandled exception in service code
- External dependency failure (if any added later)

**Timing**: Can occur at any point during request processing

**Response**:
```json
{
  "error": "InternalServerError",
  "message": "An unexpected error occurred while generating Excel. Please try again later.",
  "status": 500
}
```

**Recovery**:
- Retry request
- Check server logs for stack trace
- Contact support if persistent

---

## Error Handling Strategy by Component

### API Layer (routes/excel.py)

**Responsibility**: Catch Pydantic validation errors and HTTP-layer errors

```python
@app.post("/generate-excel")
async def generate_excel(request: GenerateExcelRequest) -> FileResponse:
    try:
        # Service call
        file_stream = await excel_service.generate(request)
        return FileResponse(file_stream, media_type=EXCEL_MIME_TYPE, ...)
    except ValueError as e:
        return JSONResponse(status_code=400, content={...})
    except Exception as e:
        return JSONResponse(status_code=500, content={...})
```

**Catches**:
- Pydantic validation errors → 400
- Business logic errors → 400 or 500 (delegated to service)
- Unexpected errors → 500

---

### Service Layer (services/excel_service.py)

**Responsibility**: Handle template/mapping loading, fill operations, detect business logic errors

**Model**:
```python
class ExcelService:
    async def generate(self, request: GenerateExcelRequest) -> BytesIO:
        try:
            template = await self._load_template()  # May raise TemplateLoadError
            mapping = await self._load_mapping()    # May raise MappingError
            workbook = self._fill_header(template, request.meta, mapping)
            workbook = self._fill_rows(workbook, request.entries, mapping)
            return self._write_to_stream(workbook)      # May raise ExcelWriteError
        except (TemplateLoadError, MappingError, ExcelWriteError) as e:
            raise  # Re-raise for API layer to catch
        except Exception as e:
            raise InternalServerError(f"Unknown error: {e}")
```

**Catches**:
- File I/O errors → TemplateLoadError/MappingError
- JSON parsing errors → MappingError
- openpyxl errors → ExcelWriteError
- Unexpected errors → InternalServerError

---

### Core/Config Layer

**Responsibility**: Detect configuration errors early

```python
class Config:
    def __init__(self):
        self.template_path = os.getenv("TEMPLATE_PATH", "templates/excel_template.xlsx")
        self._validate_template_accessible()  # Fail-fast at startup
    
    def _validate_template_accessible(self):
        if not os.path.exists(self.template_path):
            raise TemplateLoadError(f"Template not found: {self.template_path}")
```

**Validates at Startup**:
- Template file exists and is readable
- Mapping files exist and valid JSON
- All configured paths are accessible

**Benefit**: Service startup fails loudly if configuration is broken, preventing deployment of broken instances.

---

## Logging & Observability

Every error is logged with context for debugging:

```python
logger.error(
    "Template load failed",
    exc_info=True,
    extra={
        "template_path": config.template_path,
        "request_id": request_id,
        "duration_ms": elapsed_ms
    }
)
```

**Logged for all errors**:
- Timestamp (ISO 8601)
- Error type and message
- Request ID (for tracing)
- Stack trace (for 5xx errors)
- Relevant context (file path, input size, etc.)

---

## HTTP Status Code Mapping

| Scenario | HTTP Status | Error Type |
|----------|------------|-----------|
| Missing required field in request | 400 | ValidationError |
| Invalid JSON in request | 400 | JSONDecodeError |
| Unknown field in request | 200 (success) | N/A - ignored |
| Template file not found | 500 | TemplateLoadError |
| Mapping file not found | 500 | MappingError |
| Template parsing error | 500 | TemplateLoadError |
| Excel generation error | 500 | ExcelWriteError |
| Unexpected server error | 500 | InternalServerError |

---

## Retry Strategy Recommendations

**For clients**:

| Error | Retryable | Backoff | Max Attempts |
|-------|-----------|---------|--------------|
| 400 (ValidationError) | No | N/A | 0 (fix & retry) |
| 500 (TemplateLoadError) | Yes | Exponential | 3 |
| 500 (MappingError) | Yes | Exponential | 3 |
| 500 (ExcelWriteError) | Yes | Exponential | 3 |
| 500 (InternalServerError) | Yes | Exponential | 3 |

**Backoff Schedule**:
- Attempt 1: Immediate
- Attempt 2: 1 second delay
- Attempt 3: 4 second delay

---

## Future Error Handling Enhancements

1. **Rate Limiting**: Add 429 Too Many Requests error type
2. **Request Size Limits**: Add 413 Payload Too Large error
3. **Custom Validation Rules**: Add domain-specific validation errors
4. **Webhook Notifications**: Alert operations team on 5xx errors
5. **Error Analytics**: Track error rates by type for SLA monitoring

---

## Testing Error Cases

**Unit Tests**:
- [ ] ValidationError triggered by missing `meta`
- [ ] ValidationError triggered by invalid JSON
- [ ] TemplateLoadError when template not found
- [ ] MappingError when mapping files invalid
- [ ] ExcelWriteError on corrupted workbook state
- [ ] InternalServerError on unexpected exception

**Integration Tests**:
- [ ] Retry after 500 error recovers successfully
- [ ] Concurrent requests with one returning 500 doesn't affect others
- [ ] Error response contains proper HTTP headers
- [ ] Error response is valid JSON

**Smoke Tests**:
- [ ] Service starts successfully (config validation passes)
- [ ] Health check succeeds (template/mapping accessible)
- [ ] Valid request returns 200 without errors
