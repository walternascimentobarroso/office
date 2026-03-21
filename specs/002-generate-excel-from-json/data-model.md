# Data Model: Excel Generation API

**Feature**: Generate Excel from JSON  
**Phase**: Phase 1 - Design  
**Date**: 20 March 2026  

## Entity & Schema Definitions

### 1. Meta Entity

**Purpose**: Contains company/report metadata that fills header fields in the Excel template.

**Fields**:

| Field | Type | Required | Description | Mapping |
|-------|------|----------|-------------|---------|
| `empresa` | string (1-255 chars) | Optional | Company/business name | Cell B1 |
| `nif` | string (1-20 chars) | Optional | Tax ID or similar identifier | Cell C4 |
| `mes` | string (1-20 chars) | Optional | Month/period identifier | Cell J3 |

**Validation Rules**:
- All fields are optional (robustness requirement)
- Extra fields are silently ignored
- Empty strings are accepted
- No special character validation (preserve user data as-is)

**Pydantic Schema**:
```python
class Meta(BaseModel):
    empresa: Optional[str] = None
    nif: Optional[str] = None
    mes: Optional[str] = None
    
    class Config:
        extra = "ignore"  # Ignore unknown fields
```

---

### 2. Entry Entity

**Purpose**: Represents a single daily/time-entry record that fills one row in the Excel template.

**Fields**:

| Field | Type | Required | Description | Column |Validation |
|-------|------|----------|-------------|--------|-----------|
| `day` | integer | Optional | Day of month (1-31) or day number | A | Can be any integer |
| `description` | string | Optional | Entry description/activity | B | Up to 255 chars |
| `location` | string | Optional | Physical location or work location | D | Up to 255 chars |
| `start_time` | string | Optional | Start time (format user-defined) | E | Recommended HH:MM or ISO format |
| `end_time` | string | Optional | End time (format user-defined) | J | Recommended HH:MM or ISO format |
| `percentagem` | integer | Optional | Percentage (0-100) | K | Must be between 0 and 100 |

**Validation Rules**:
- All fields are optional
- Extra fields are silently ignored
- No format validation (preserves user data flexibility)
- Type coercion: numbers are converted to strings for display
- `percentagem` must be an integer between 0 and 100 if provided

**Pydantic Schema**:
```python
class Entry(BaseModel):
    day: Optional[int | str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    percentagem: Optional[int] = None
    
    class Config:
        extra = "ignore"  # Ignore unknown fields
    
    @validator('percentagem')
    def percentagem_must_be_valid(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('percentagem must be between 0 and 100')
        return v
```

---

### 3. Request Payload Entity

**Purpose**: Top-level request structure for POST /generate-excel.

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `meta` | Meta object | Required | Company metadata (header fields) |
| `entries` | Array of Entry | Required | Time/activity entries (rows) |

**Validation Rules**:
- Both `meta` and `entries` must be present
- `meta` can be empty object `{}`
- `entries` can be empty array `[]`
- Request body must be valid JSON

**Pydantic Schema**:
```python
class GenerateExcelRequest(BaseModel):
    meta: Meta
    entries: list[Entry] = []
```

---

### 4. Response Entities

#### Success Response

**Content-Type**: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`

**Headers**:
```
Content-Disposition: attachment; filename="relatorio_[mes]_[timestamp].xlsx"
```

**Body**: Binary Excel file (XLSX format)

**HTTP Status**: 200

---

#### Error Response

**Purpose**: Standardized error response for all error cases.

**Structure**:
```json
{
  "error": "ErrorType",
  "message": "Human-readable error description",
  "status": 4xx or 5xx,
  "details": [optional additional context]
}
```

**Error Types**:

| Error Type | HTTP Status | Cause | Recovery |
|------------|------------|-------|----------|
| ValidationError | 400 | Invalid request body (missing fields, wrong types) | Fix request payload |
| TemplateLoadError | 500 | Template file not found or corrupted | Check server configuration |
| MappingError | 500 | Mapping configuration invalid | Check mapping files |
| InternalServerError | 500 | Unexpected error during generation | Retry; contact support if persistent |

**Pydantic Schema**:
```python
class ErrorDetail(BaseModel):
    field: str
    issue: str

class ErrorResponse(BaseModel):
    error: str
    message: str
    status: int
    details: Optional[list[ErrorDetail]] = None
```

---

## Relationships & State Transitions

### Request Processing Flow

```
┌─────────────────────┐
│ Receive JSON Request│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────┐
│ Validate against Pydantic Schema│
└──────────┬──────────────────────┘
           │
    ┌──────┴──────┐
    │             │
    ▼ (valid)     ▼ (invalid)
┌───────────┐  ┌─────────────┐
│Load       │  │Return 400   │
│Template   │  │Error        │
└─────┬─────┘  │Response     │
      │        └─────────────┘
      │ (success)
      ▼ (failure)
┌──────────────────┐   ┌──────────────────┐
│Return 500        │   │Fill Header Fields│
│TemplateLoadError │   │from Meta         │
└──────────────────┘   └────────┬─────────┘
                                 │
                    ┌────────────┴────────────┐
                    │ For each Entry in list: │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌──────────────────────┐
                    │Map Entry to Row      │
                    │Write values to cols  │
                    │A, B, D, E, J         │
                    └────────────┬─────────┘
                                 │
                    ┌────────────┴────────────┐
                    │More entries?           │
                    └────────────┬────────────┘
                                 │
                    ┌────────────┴─────────┐
                    ▼ (yes)                ▼ (no)
                 [Loop back]      ┌──────────────────┐
                                  │Write Excel to    │
                                  │BytesIO stream    │
                                  └────────┬─────────┘
                                           │
                                           ▼
                                  ┌──────────────────┐
                                  │Return 200 +      │
                                  │Excel file        │
                                  └──────────────────┘
```

---

## Data Integrity & Constraints

### Template Preservation Constraints

- **Read-Only Template**: Template file is never modified; fresh copy used per request
- **Formula Protection**: No cells containing formulas are overwritten (only mapped cells)
- **Formatting Preservation**: All original cell styling, number formats, merged ranges retained
- **Determinism**: Given identical inputs, output is bitwise identical

### Input Data Constraints

- **No SQL/formula injection risks**: User data is treated as literal values, not evaluated
- **No file path injection**: All file paths are hardcoded in configuration
- **No external network access**: Service is self-contained

---

## Extension Points

Future enhancements to data model:

1. **Multi-template Support**: Extend config to support different templates; add template selection field to request
2. **Conditional Formatting**: Add rules to Entry for conditional cell coloring
3. **Calculated Fields**: Allow formulas in Entry fields (e.g., duration = end_time - start_time)
4. **Batch Operations**: Add batch endpoint to generate multiple files; extend Entry with file ID mapping
5. **Template Versioning**: Track template versions; support version selection in request

---

## Summary

This data model supports the core requirement of mapping JSON input to Excel output while maintaining template integrity and supporting graceful handling of missing/extra fields. The schema is extensible for future template types and advanced features.
