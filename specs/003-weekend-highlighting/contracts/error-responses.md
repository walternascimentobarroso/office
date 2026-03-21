# Error Responses: Weekend Highlighting

## 400 Bad Request - Invalid Month

### Condition
`mes` field is missing, not an integer, or outside 1-12 range.

### Response
```json
{
  "error": "InvalidMonth",
  "message": "The 'mes' field must be an integer between 1 and 12.",
  "details": {
    "provided_value": "<actual_value>",
    "expected_range": "1-12"
  }
}
```

### Example
```json
{
  "error": "InvalidMonth",
  "message": "The 'mes' field must be an integer between 1 and 12.",
  "details": {
    "provided_value": "13",
    "expected_range": "1-12"
  }
}
```

## Existing Errors
All existing error responses remain unchanged.