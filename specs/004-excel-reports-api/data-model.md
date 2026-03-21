# Data Model: Excel Reports API

**Date**: 2026-03-21  
**Purpose**: Define the data structures and relationships for the Excel report generation system.

## Entities

### ReportRequest (Base)
**Purpose**: Common structure for all report generation requests.  
**Attributes**:
- `meta`: MetaData (required) - Report metadata including month and company info
- `entries`: List[Entry] (optional, default []) - Array of activity entries to fill rows
- `holidays`: List[int] (optional, default []) - Days of month to highlight as holidays (1-31)

### MetaData
**Purpose**: Metadata for report header.  
**Attributes**:
- `empresa`: str (optional) - Company name
- `nif`: str (optional) - Company tax ID
- `mes`: Union[int, str] (required) - Month (1-12 for diario, Portuguese name for km)

### Entry
**Purpose**: Single activity entry for report rows.  
**Attributes**:
- `day`: Union[int, str] (optional) - Day of month
- `description`: str (optional) - Activity description
- `location`: str (optional) - Activity location
- `start_time`: str (optional) - Start time (HH:MM format)
- `end_time`: str (optional) - End time (HH:MM format)
- `percentagem`: int (optional) - Percentage (0-100)

### Funcionario (Mapa Diario only)
**Purpose**: Employee data for footer.  
**Attributes**:
- `nome_completo`: str (optional) - Full name
- `morada`: str (optional) - Address
- `nif`: str (optional) - Employee tax ID

### Vehicle (Mapa KM only)
**Purpose**: Vehicle data for footer.  
**Attributes**:
- `modelo`: str (optional) - Vehicle model
- `matricula`: str (optional) - License plate
- `kms`: int (optional) - Kilometers

### ExcelTemplate
**Purpose**: Template XLSX file structure.  
**Attributes**:
- `path`: str - File path to .xlsx template
- `header_cells`: Dict[str, str] - Mapping of field names to cell addresses (e.g., "empresa": "B2")
- `row_start`: int - Starting row number for dynamic entries
- `row_columns`: Dict[str, str] - Mapping of entry fields to column letters (e.g., "description": "C")
- `footer_cells`: Dict[str, str] - Mapping of footer fields to cell addresses
- `styles`: Dict[str, str] - Style definitions (e.g., "weekend": "#F0F0F0")

### GeneratedReport
**Purpose**: Output XLSX file representation.  
**Attributes**:
- `filename`: str - Generated filename with timestamp
- `content`: BytesIO - Binary Excel content
- `content_type`: str - "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

### ValidationError
**Purpose**: Structured error response for validation failures.  
**Attributes**:
- `error`: str - Error type ("ValidationError")
- `details`: Dict[str, List[str]] - Field-specific error messages

## Relationships

- ReportRequest contains MetaData, list of Entry, list of int (holidays)
- MapaDiarioRequest extends ReportRequest with Funcionario
- MapaKmRequest extends ReportRequest with Vehicle
- Report services use ExcelTemplate to generate GeneratedReport
- Validation errors produced during schema validation

## Validation Rules

- `mes`: For diario - int 1-12; for km - one of ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
- `holidays`: Each int must be 1-31, invalid values ignored
- `percentagem`: 0-100 if provided
- `entries`: Can be empty, each entry can have missing fields (left blank in Excel)

## Data Flow

1. JSON payload parsed into ReportRequest (diario/km variant)
2. Validation applied via Pydantic schemas
3. Report service maps data to ExcelTemplate structure
4. BaseExcelService generates GeneratedReport
5. API returns GeneratedReport as StreamingResponse