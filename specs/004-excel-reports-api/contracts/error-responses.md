# API Contracts: Error Responses

**Date**: 2026-03-21  
**Purpose**: Define error response formats and scenarios for Excel report generation endpoints.

## Common Error Response Format

All error responses use JSON format with the following structure:

```json
{
  "error": "ErrorType",
  "message": "Human-readable error message",
  "details": {
    "field": ["Specific validation error messages"]
  }
}
```

## Error Scenarios

### 422 Validation Error
**Status**: 422  
**Cause**: Invalid JSON payload or schema violations.  
**Example**:
```json
{
  "error": "ValidationError",
  "message": "Request validation failed",
  "details": {
    "meta.mes": ["Must be between 1 and 12"],
    "holidays": ["All values must be integers between 1 and 31"]
  }
}
```

### 400 Bad Request
**Status**: 400  
**Cause**: Malformed JSON or missing Content-Type header.  
**Example**:
```json
{
  "error": "BadRequest",
  "message": "Invalid JSON format"
}
```

### 500 Internal Server Error
**Status**: 500  
**Cause**: Unexpected server errors (template missing, Excel generation failure).  
**Example**:
```json
{
  "error": "InternalError",
  "message": "Failed to generate report"
}
```

## Specific Validation Errors

### Mapa Diário
- `meta.mes`: Must be integer 1-12
- `entries[].percentagem`: Must be 0-100 if provided
- `holidays[]`: Must be integers 1-31, invalid values ignored but logged

### Mapa KM
- `meta.mes`: Must be valid Portuguese month name ("Janeiro", "Fevereiro", etc.)
- `entries[].percentagem`: Must be 0-100 if provided
- `holidays[]`: Must be integers 1-31, invalid values ignored but logged

## Error Handling Behavior

- Invalid holiday values are silently ignored (logged as warnings)
- Missing optional fields result in empty cells in Excel
- Template file not found results in 500 error
- Concurrent requests are handled independently (stateless)
- Large payloads (>1000 entries) may timeout but attempt processing