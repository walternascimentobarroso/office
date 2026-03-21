# Request-Response Contract: Excel Generation with Weekend Highlighting

## Request Contract

### Endpoint
`POST /api/excel/generate`

### Content-Type
`application/json`

### Schema
```json
{
  "type": "object",
  "properties": {
    "mes": {
      "type": "integer",
      "minimum": 1,
      "maximum": 12,
      "description": "Month number for weekend highlighting (1=January, 12=December)"
    },
    // ... existing fields ...
  },
  "required": ["mes"]  // NEW: mes is now required for highlighting
}
```

### Validation Rules
- `mes`: Must be integer 1-12; reject with 400 if invalid
- Existing fields: Unchanged validation

## Response Contract

### Success Response
- **Status**: 200 OK
- **Content-Type**: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- **Body**: Excel file with weekend rows highlighted

### Weekend Highlighting Behavior
- Rows 8-38 correspond to days 1-31
- Weekend days (Sat/Sun) have fill color applied to columns A, B, D, E, J
- Color matches configuration (derived from template A8)
- No data or formulas altered
- Invalid days for month (e.g., Feb 30) are not highlighted

### Example Request
```json
{
  "mes": 3,
  // ... other fields ...
}
```

### Example Response
Excel file with March weekends (e.g., days 1,2,8,9,15,16,22,23,29,30) highlighted in rows 8-38.