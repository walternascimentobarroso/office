# API Contract: Excel Generation Endpoint

**Endpoint**: `POST /generate-excel`  
**API Version**: 1.0  
**Content-Type**: `application/json` (request), `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` (response)  

## Request Contract

### Method & Path

```
POST /generate-excel
```

### Request Headers

```
Content-Type: application/json
Content-Length: [size]
```

### Request Body

**Content-Type**: `application/json`

**Schema**:
```json
{
  "meta": {
    "empresa": "string (optional)",
    "nif": "string (optional)",
    "mes": "string (optional)"
  },
  "entries": [
    {
      "day": "integer | string (optional)",
      "description": "string (optional)",
      "location": "string (optional)",
      "start_time": "string (optional)",
      "end_time": "string (optional)"
    }
  ]
}
```

**Constraints**:
- `meta` object is required (but can be empty: `{}`)
- `entries` array is required (but can be empty: `[]`)
- Unknown fields in `meta` or array items are ignored
- No field type coercion errors; type mismatches in non-optional fields should be validation errors

---

### Example Requests

**Example 1: Full Data**

```bash
curl -X POST http://localhost:8000/generate-excel \
  -H "Content-Type: application/json" \
  -d '{
    "meta": {
      "empresa": "Acme Corp",
      "nif": "123456789",
      "mes": "Março 2026"
    },
    "entries": [
      {
        "day": 1,
        "description": "Project kickoff meeting",
        "location": "Conference Room A",
        "start_time": "09:00",
        "end_time": "10:30"
      },
      {
        "day": 1,
        "description": "Development sprint",
        "location": "Desk",
        "start_time": "10:30",
        "end_time": "12:00"
      },
      {
        "day": 2,
        "description": "Client call",
        "location": "Virtual",
        "start_time": "14:00",
        "end_time": "15:00"
      }
    ]
  }'
```

**Example 2: Minimal Data**

```bash
curl -X POST http://localhost:8000/generate-excel \
  -H "Content-Type: application/json" \
  -d '{
    "meta": {},
    "entries": []
  }'
```

**Example 3: Partial Data with Missing Fields**

```bash
curl -X POST http://localhost:8000/generate-excel \
  -H "Content-Type: application/json" \
  -d '{
    "meta": {
      "empresa": "Tech Startup"
    },
    "entries": [
      {
        "day": 15,
        "description": "Code review"
      },
      {
        "day": 16,
        "description": "Testing",
        "location": "QA Lab"
      }
    ]
  }'
```

---

## Success Response Contract

### HTTP Status

```
200 OK
```

### Response Headers

```
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename="relatorio_[mes]_[timestamp].xlsx"
Content-Length: [size]
```

### Response Body

Binary XLSX file stream.

### Filename Convention

- Format: `relatorio_[mes]_[timestamp].xlsx`
- `[mes]`: Value from `meta.mes` field (sanitized, max 20 chars); defaults to "report" if not provided
- `[timestamp]`: ISO 8601 timestamp (e.g., 20260320T153045Z; always UTC)
- Example: `relatorio_Março2026_20260320T153045Z.xlsx`

---

### Example Response

```bash
HTTP/1.1 200 OK
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename="relatorio_Março2026_20260320T153045Z.xlsx"
Content-Length: 8912

[Binary XLSX file content...]
```

---

## Error Response Contract

### Error Response Format

```json
{
  "error": "ErrorType",
  "message": "Human-readable description",
  "status": 400 | 500,
  "details": [
    {
      "field": "field_name",
      "issue": "issue_description"
    }
  ]
}
```

---

### 400 Bad Request - Validation Error

**Status**: `400`

**Cause**: Invalid request body (missing required fields, type mismatch, etc.)

**Example**:

```bash
curl -X POST http://localhost:8000/generate-excel \
  -H "Content-Type: application/json" \
  -d '{"invalid": "structure"}'
```

**Response**:

```json
{
  "error": "ValidationError",
  "message": "Invalid request body",
  "status": 400,
  "details": [
    {
      "field": "meta",
      "issue": "field required"
    },
    {
      "field": "entries",
      "issue": "field required"
    }
  ]
}
```

---

### 400 Bad Request - Invalid JSON

**Status**: `400`

**Cause**: Request body is not valid JSON

**Example**:

```bash
curl -X POST http://localhost:8000/generate-excel \
  -H "Content-Type: application/json" \
  -d '{invalid json}'
```

**Response**:

```json
{
  "error": "JSONDecodeError",
  "message": "Request body is not valid JSON",
  "status": 400
}
```

---

### 500 Internal Server Error - Template Load Error

**Status**: `500`

**Cause**: Template file not found, corrupted, or invalid XLSX

**Example Response**:

```json
{
  "error": "TemplateLoadError",
  "message": "Template file cannot be loaded",
  "status": 500,
  "details": [
    {
      "field": "template",
      "issue": "File not found at templates/excel_template.xlsx"
    }
  ]
}
```

---

### 500 Internal Server Error - Mapping Error

**Status**: `500`

**Cause**: Mapping configuration files are invalid or missing

**Example Response**:

```json
{
  "error": "MappingError",
  "message": "Mapping configuration is invalid",
  "status": 500,
  "details": [
    {
      "field": "header_mapping",
      "issue": "Invalid JSON in templates/mappings/header_mapping.json"
    }
  ]
}
```

---

### 500 Internal Server Error - Generic

**Status**: `500`

**Cause**: Unexpected error during Excel generation (should be rare with proper error handling)

**Example Response**:

```json
{
  "error": "InternalServerError",
  "message": "An unexpected error occurred while generating Excel",
  "status": 500
}
```

---

## Behavioral Guarantees

### Idempotency

- **Deterministic Output**: Given the same JSON input (including timestamp field if any), the generated Excel file is bitwise identical
- **State Independent**: No request affects subsequent requests; service is stateless
- **Safe to Retry**: Retransmitting the same request results in the same output

### Performance

- **Timeout**: Requests should complete in under 30 seconds for normal inputs (up to 100 entries)
- **Concurrency**: Service can handle multiple concurrent requests without queue blocking
- **Resource Usage**: Response size scales with number of entries (~50KB base + ~5KB per entry average)

### Data Handling

- **No Persistence**: Generated files are not stored on server; only returned to client
- **No Validation Side Effects**: Validation errors do not modify server state
- **Formula Preservation**: All formulas from template are preserved and functional in output

---

## Versioning & Compatibility

### API Versioning

- Current version: 1.0
- Endpoint remains: `POST /generate-excel` (no version prefix in path for now)
- Future versions: Consider `/v2/generate-excel` if breaking changes needed

### Backward Compatibility

- Additional optional fields in `meta` or `entries` are silently ignored (forward compatible)
- New error types may be added with new HTTP status codes
- Response filename format may change (clients should not depend on specific format)

### Breaking Changes (would require v2)

- Removal of required fields
- Change in required HTTP headers
- Change in default behavior for missing fields

---

## Rate Limiting & Quotas

Currently not enforced but available for future implementation:

- Suggested: 100 requests/minute per IP
- Suggested: 1MB max request body size
- Suggested: 50MB max response file size

---

## Testing Checklist

- [ ] Valid request with full meta and 1 entry
- [ ] Valid request with empty meta and empty entries
- [ ] Valid request with partial meta and partial entries
- [ ] Missing `meta` field → 400 error
- [ ] Missing `entries` field → 400 error
- [ ] Invalid JSON → 400 error
- [ ] Unknown fields in `meta` → ignored, success
- [ ] Unknown fields in `entries` → ignored, success
- [ ] Empty string values → accepted
- [ ] Null values → accepted (treated same as missing)
- [ ] Extra data in response → None (binary only)
- [ ] Response headers present and correct
- [ ] Filename includes mes value if provided
- [ ] Filename includes timestamp
- [ ] Generated Excel file is valid and opens in Excel/Sheets
- [ ] Data appears in correct cells (Per mapping)
- [ ] Template formulas still active in output
- [ ] Concurrent requests produce identical outputs
