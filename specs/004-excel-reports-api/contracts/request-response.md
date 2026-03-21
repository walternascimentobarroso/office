# API Contracts: Request/Response

**Date**: 2026-03-21  
**Purpose**: Define HTTP API contracts for Excel report generation endpoints.

## POST /reports/mapa-diario

**Purpose**: Generate Mapa Diário Excel report.

### Request
- **Method**: POST
- **Content-Type**: application/json
- **Body Schema**:
```json
{
  "meta": {
    "empresa": "string (optional)",
    "nif": "string (optional)",
    "mes": "integer (1-12, required)"
  },
  "entries": [
    {
      "day": "integer|string (optional)",
      "description": "string (optional)",
      "location": "string (optional)",
      "start_time": "string HH:MM (optional)",
      "end_time": "string HH:MM (optional)",
      "percentagem": "integer 0-100 (optional)"
    }
  ],
  "funcionario": {
    "nome_completo": "string (optional)",
    "morada": "string (optional)",
    "nif": "string (optional)"
  },
  "holidays": ["integer 1-31 (optional)"]
}
```

### Response (Success)
- **Status**: 200
- **Content-Type**: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
- **Content-Disposition**: attachment; filename="relatorio_3_2026-03-21T10-30-00.xlsx"
- **Body**: Binary XLSX content

### Example Request
```json
{
  "meta": {
    "empresa": "Minha Empresa",
    "nif": "123456789",
    "mes": 3
  },
  "entries": [
    {
      "day": 1,
      "description": "Reunião",
      "location": "Escritório",
      "start_time": "09:00",
      "end_time": "10:00",
      "percentagem": 75
    }
  ],
  "funcionario": {
    "nome_completo": "João Silva",
    "morada": "Rua Exemplo 100, Lisboa",
    "nif": "987654321"
  },
  "holidays": [5, 25]
}
```

## POST /reports/mapa-km

**Purpose**: Generate Mapa KM Excel report.

### Request
- **Method**: POST
- **Content-Type**: application/json
- **Body Schema**:
```json
{
  "meta": {
    "empresa": "string (optional)",
    "nif": "string (optional)",
    "mes": "string (Portuguese month name, required)"
  },
  "entries": [
    {
      "day": "integer|string (optional)",
      "description": "string (optional)",
      "location": "string (optional)",
      "start_time": "string HH:MM (optional)",
      "end_time": "string HH:MM (optional)",
      "percentagem": "integer 0-100 (optional)"
    }
  ],
  "vehicle": {
    "modelo": "string (optional)",
    "matricula": "string (optional)",
    "kms": "integer (optional)"
  },
  "holidays": ["integer 1-31 (optional)"]
}
```

### Response (Success)
- **Status**: 200
- **Content-Type**: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
- **Content-Disposition**: attachment; filename="relatorio_Marco_2026-03-21T10-30-00.xlsx"
- **Body**: Binary XLSX content

### Example Request
```json
{
  "meta": {
    "empresa": "Minha Empresa",
    "nif": "123456789",
    "mes": "Março"
  },
  "entries": [
    {
      "day": 1,
      "description": "Viagem",
      "location": "Cliente",
      "start_time": "08:00",
      "end_time": "18:00",
      "percentagem": 100
    }
  ],
  "vehicle": {
    "modelo": "Ford Focus",
    "matricula": "AA-12-BB",
    "kms": 15000
  },
  "holidays": [5, 25]
}
```