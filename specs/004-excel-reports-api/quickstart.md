# Quickstart: Excel Reports API

**Date**: 2026-03-21  
**Purpose**: Developer guide for integrating with the Excel report generation API.

## Prerequisites

- Python 3.11+
- FastAPI server running on localhost:8000
- curl or HTTP client

## Endpoints Overview

- `POST /reports/mapa-diario` - Generate daily activity report
- `POST /reports/mapa-km` - Generate kilometer tracking report

Both endpoints accept JSON payloads and return Excel files.

## Quick Examples

### Generate Mapa Diário Report

```bash
curl -X POST http://localhost:8000/reports/mapa-diario \
  -H "Content-Type: application/json" \
  -d '{
    "meta": {
      "empresa": "My Company",
      "mes": 3
    },
    "entries": [
      {
        "day": 1,
        "description": "Meeting",
        "percentagem": 100
      }
    ],
    "holidays": [5, 25]
  }' \
  -o report_diario.xlsx
```

### Generate Mapa KM Report

```bash
curl -X POST http://localhost:8000/reports/mapa-km \
  -H "Content-Type: application/json" \
  -d '{
    "meta": {
      "empresa": "My Company",
      "mes": "Março"
    },
    "entries": [
      {
        "day": 1,
        "description": "Trip",
        "percentagem": 100
      }
    ],
    "vehicle": {
      "modelo": "Car Model",
      "matricula": "AA-12-BB"
    },
    "holidays": [5, 25]
  }' \
  -o report_km.xlsx
```

## Schema Details

### Common Fields
- `meta`: Report metadata (company, month)
- `entries`: Array of activity records
- `holidays`: Array of holiday days (1-31)

### Mapa Diário Specific
- `meta.mes`: Integer 1-12
- `funcionario`: Employee details for footer

### Mapa KM Specific
- `meta.mes`: Portuguese month name ("Janeiro", "Fevereiro", etc.)
- `vehicle`: Vehicle details for footer

## Response Handling

- **Success (200)**: Excel file downloaded with filename like `relatorio_3_2026-03-21T10-30-00.xlsx`
- **Validation Error (422)**: JSON error details
- **Server Error (500)**: Generic error message

## Testing

```bash
# Health check
curl http://localhost:8000/health

# Invalid request (should return 422)
curl -X POST http://localhost:8000/reports/mapa-diario \
  -H "Content-Type: application/json" \
  -d '{"meta": {"mes": 13}}'
```

## Development

The API uses modular architecture:
- `/api/routes`: Endpoint handlers
- `/schemas`: Pydantic validation models
- `/reports`: Report-specific logic
- `/services`: Shared business services

Reports are plugin-like with independent templates and mappings.