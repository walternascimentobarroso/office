# Developer Quick Start: Excel Generation API

**Feature**: Generate Excel from JSON  
**Phase**: Phase 1 - Design  
**Date**: 20 March 2026  

## Overview

This API accepts JSON metadata and time-entry data, generates a filled Excel file from a template, and returns it as a download. This guide covers:

- API endpoint and usage
- Request/response format
- Error handling
- Configuration
- Running locally
- Development setup

---

## Quick Start (30 seconds)

### 1. Start the Service

```bash
cd /path/to/project
python -m uvicorn src.main:app --reload
```

Service runs at `http://localhost:8000`

### 2. Make a Test Request

```bash
curl -X POST http://localhost:8000/generate-excel \
  -H "Content-Type: application/json" \
  -d '{
    "meta": {
      "empresa": "Test Company",
      "nif": "123456",
      "mes": "March 2026"
    },
    "entries": [
      {
        "day": 1,
        "description": "Meeting",
        "location": "Office",
        "start_time": "09:00",
        "end_time": "10:00"
      }
    ]
  }' \
  -o output.xlsx
```

Generated Excel file downloads to `output.xlsx`.

---

## API Reference

### Endpoint

```
POST /generate-excel
```

### Request Format

**Content-Type**: `application/json`

**Body**:
```json
{
  "meta": {
    "empresa": "string",     // Optional: Company name
    "nif": "string",         // Optional: Tax ID
    "mes": "string"          // Optional: Month/period
  },
  "entries": [
    {
      "day": "integer",               // Optional: Day of month
      "description": "string",        // Optional: Activity description
      "location": "string",           // Optional: Work location
      "start_time": "string",         // Optional: Start time
      "end_time": "string"            // Optional: End time
    }
  ]
}
```

**Notes**:
- All fields are optional
- Extra fields are ignored
- Missing fields are handled gracefully
- Both `meta` and `entries` must be present (can be empty)

### Response

**Success (200 OK)**:
- Content-Type: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- Body: Binary XLSX file
- Filename: `relatorio_[mes]_[timestamp].xlsx`

**Error (4xx/5xx)**:
- Content-Type: `application/json`
- Body: Error description

---

## Usage Examples

### Example 1: Full Data with Multiple Entries

```bash
curl -X POST http://localhost:8000/generate-excel \
  -H "Content-Type: application/json" \
  -d '{
    "meta": {
      "empresa": "Acme Corp",
      "nif": "PT123456789",
      "mes": "Março 2026"
    },
    "entries": [
      {
        "day": 1,
        "description": "Project planning",
        "location": "Conference Room",
        "start_time": "09:00",
        "end_time": "11:00"
      },
      {
        "day": 1,
        "description": "Development",
        "location": "Desk",
        "start_time": "14:00",
        "end_time": "17:00"
      },
      {
        "day": 2,
        "description": "Testing",
        "location": "QA Lab",
        "start_time": "10:00",
        "end_time": "13:00"
      }
    ]
  }' -o report.xlsx
```

### Example 2: Minimal Request (Empty)

```bash
curl -X POST http://localhost:8000/generate-excel \
  -H "Content-Type: application/json" \
  -d '{
    "meta": {},
    "entries": []
  }' -o blank_report.xlsx
```

### Example 3: Partial Data

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
        "start_time": "09:30",
        "end_time": "16:00"
      }
    ]
  }' -o partial_report.xlsx
```

Missing fields are left blank in the Excel file.

### Example 4: Python Client

```python
import requests
import json

url = "http://localhost:8000/generate-excel"
payload = {
    "meta": {
        "empresa": "My Company",
        "nif": "123456",
        "mes": "April 2026"
    },
    "entries": [
        {
            "day": 1,
            "description": "Client call",
            "location": "Zoom",
            "start_time": "14:00",
            "end_time": "15:00"
        }
    ]
}

response = requests.post(url, json=payload)

if response.status_code == 200:
    with open("output.xlsx", "wb") as f:
        f.write(response.content)
    print("Excel file generated successfully")
else:
    errors = response.json()
    print(f"Error: {errors}")
```

---

## Error Handling

### Missing Required Fields

**Request**:
```json
{
  "invalid": "payload"
}
```

**Response (400)**:
```json
{
  "error": "ValidationError",
  "message": "Invalid request body",
  "status": 400,
  "details": [
    {
      "field": "meta",
      "issue": "field required"
    }
  ]
}
```

### Template Not Found

**Response (500)**:
```json
{
  "error": "TemplateLoadError",
  "message": "Template file cannot be loaded",
  "status": 500
}
```

**Action**: Check that `templates/excel_template.xlsx` exists and is readable.

### Mapping Configuration Invalid

**Response (500)**:
```json
{
  "error": "MappingError",
  "message": "Mapping configuration is invalid",
  "status": 500
}
```

**Action**: Verify `templates/mappings/header_mapping.json` and `templates/mappings/rows_mapping.json` contain valid JSON.

---

## Configuration

### Environment Variables

```bash
TEMPLATE_PATH="/path/to/template.xlsx"           # Default: templates/excel_template.xlsx
HEADER_MAPPING_PATH="/path/to/header_mapping.json" # Default: templates/mappings/header_mapping.json
ROWS_MAPPING_PATH="/path/to/rows_mapping.json"     # Default: templates/mappings/rows_mapping.json
LOG_LEVEL="INFO"                                  # Default: INFO
```

### Template File

The template is a standard Excel file (XLSX) with:
- Pre-defined header area (cells B1, C4, J3 for meta fields)
- Pre-defined entry rows starting at row 8 (columns A, B, D, E, J)
- Optional formulas and formatting (preserved in output)

**To create/update template**:
1. Open Excel
2. Create/edit desired layout
3. Save as `.xlsx` (not macro-enabled)
4. Place at `templates/excel_template.xlsx`

### Mapping Files

**header_mapping.json** - Defines where meta fields are placed:

```json
{
  "empresa": "B1",
  "nif": "C4",
  "mes": "J3"
}
```

**rows_mapping.json** - Defines dynamic row data placement:

```json
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

## Installation & Setup

### Prerequisites

- Python 3.11+
- pip or poetry

### Install Dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt**:
```
fastapi==0.109.0
uvicorn==0.27.0
pydantic==2.5.0
openpyxl==3.11.0
python-multipart==0.0.6
```

### Project Structure

```
.
├── src/
│   ├── main.py                 # FastAPI app
│   ├── api/
│   │   └── routes/
│   │       └── excel.py        # /generate-excel endpoint
│   ├── models/
│   │   ├── request.py          # Pydantic models
│   │   └── response.py
│   ├── services/
│   │   └── excel_service.py    # Core service logic
│   ├── core/
│   │   ├── config.py           # Configuration
│   │   ├── mapping.py          # Mapping loader
│   │   └── exceptions.py       # Custom exceptions
│   └── logging_config.py       # Logging setup
├── templates/
│   ├── excel_template.xlsx
│   └── mappings/
│       ├── header_mapping.json
│       └── rows_mapping.json
├── tests/
│   ├── unit/
│   ├── integration/
│   └── contract/
├── requirements.txt
└── README.md
```

---

## Running the Service

### Development (with hot reload)

```bash
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI).

### Production

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.main:app
```

Or use Docker:

```bash
docker build -t excel-api .
docker run -p 8000:8000 excel-api
```

---

## Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test Suite

```bash
pytest tests/unit/             # Unit tests
pytest tests/integration/      # Integration tests
pytest tests/contract/         # API contract tests
```

### Run with Coverage

```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

---

## Common Issues

### Issue: "Template not found"

**Cause**: Template file path is incorrect or file doesn't exist.

**Fix**:
```bash
ls -la templates/excel_template.xlsx  # Check file exists
echo $TEMPLATE_PATH                   # Check environment variable
```

### Issue: "Mapping configuration invalid"

**Cause**: JSON in mapping files has syntax errors.

**Fix**:
```bash
cd templates/mappings
cat header_mapping.json | python -m json.tool  # Validate JSON
cat rows_mapping.json | python -m json.tool
```

### Issue: "Data not appearing in Excel"

**Cause**: Mapping cell addresses don't match template layout.

**Fix**:
1. Open template in Excel
2. Verify header fields are in cells B1, C4, J3
3. Verify row 8+ exists and columns A, B, D, E, J align with your data
4. Update mapping files if needed

### Issue: "Formulas disappeared from output"

**Cause**: Mapping overwrote formula cells.

**Fix**: Update mapping files to avoid cells with formulas. Leave formula cell addresses out of mapping.

---

## Next Steps

1. **Customize Template**: Edit `templates/excel_template.xlsx` to match your layout
2. **Update Mappings**: Adjust `header_mapping.json` and `rows_mapping.json` to your cell addresses
3. **Add Tests**: Write tests for your specific use cases
4. **Deploy**: Package and deploy to production environment
5. **Monitor**: Set up logging and monitoring for production instance

---

## Support & Documentation

- **API Docs**: [specs/002-generate-excel-from-json/contracts/](specs/002-generate-excel-from-json/contracts/)
- **Data Model**: [specs/002-generate-excel-from-json/data-model.md](specs/002-generate-excel-from-json/data-model.md)
- **Implementation Plan**: [specs/002-generate-excel-from-json/plan.md](specs/002-generate-excel-from-json/plan.md)
- **Research**: [specs/002-generate-excel-from-json/research.md](specs/002-generate-excel-from-json/research.md)

---

## FAQ

**Q: Can I use a macro-enabled template?**  
A: No, only standard .xlsx files are supported. Macros are not executed.

**Q: What if I need more than 100 entries?**  
A: Should work fine; performance may depend on your system and template complexity.

**Q: Can I use formulas in the template?**  
A: Yes, all formulas are preserved in the output. Just avoid mapping data to cells with formulas.

**Q: Is the output deterministic?**  
A: Yes, the same input always produces bitwise identical output.

**Q: Can I have authentication?**  
A: This API currently has no authentication. Add middleware (FastAPI middleware or reverse proxy) as needed.

**Q: Can I batch-generate multiple files?**  
A: Currently, make separate requests. Batch endpoint can be added in future versions.
