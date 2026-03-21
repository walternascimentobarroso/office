# Feature Specification: Excel Reports API

**Feature Branch**: `004-excel-reports-api`  
**Created**: 2026-03-21  
**Status**: Draft  
**Input**: User description: "Create a specification for a FastAPI service that generates multiple Excel reports. Endpoints: POST /reports/mapa-diario, POST /reports/mapa-km. Each endpoint accepts a specific JSON schema and returns an Excel file. Common behavior: Load report-specific template, Fill header, rows, and optional footer, Apply styling for weekends and holidays. Mapa Diário: month is numeric (1–12). Mapa KM: month is string (\"Março\", etc), includes vehicle in footer. Common input fields: meta, entries, holidays: list of days (1–31). Styling rules: Apply only to column A, Do not override formulas. Edge cases: Missing fields, Invalid month, Invalid holidays, Empty entries. Deliver: API contract, Request/response examples, Error scenarios"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate Mapa Diário Report (Priority: P1)

As an API client, I want to generate a Mapa Diário Excel report by sending a POST request to /reports/mapa-diario with JSON data containing meta (with numeric month), entries, and holidays, so that I receive a properly formatted Excel file with header, rows, footer, and weekend/holiday styling applied.

**Why this priority**: This is the primary report type and core functionality of the service, providing the most immediate business value.

**Independent Test**: Can be fully tested by sending a valid JSON payload to POST /reports/mapa-diario and verifying the returned Excel file contains the expected data in header/rows/footer and correct styling in column A for weekends and specified holidays.

**Acceptance Scenarios**:

1. **Given** a valid JSON payload with meta.month=3, entries with sample data, and holidays=[5,25], **When** POST to /reports/mapa-diario, **Then** receive Excel file with March data filled, weekends highlighted, and days 5/25 highlighted as holidays.
2. **Given** a valid JSON payload with empty entries array, **When** POST to /reports/mapa-diario, **Then** receive Excel file with header/footer filled but no rows added.
3. **Given** a valid JSON payload without holidays, **When** POST to /reports/mapa-diario, **Then** receive Excel file with only weekends highlighted in column A.

---

### User Story 2 - Generate Mapa KM Report (Priority: P2)

As an API client, I want to generate a Mapa KM Excel report by sending a POST request to /reports/mapa-km with JSON data containing meta (with string month), entries, holidays, and vehicle info, so that I receive a properly formatted Excel file with header, rows, footer including vehicle, and weekend/holiday styling applied.

**Why this priority**: This adds support for the second report type, expanding the service's capabilities while maintaining the same core generation logic.

**Independent Test**: Can be fully tested by sending a valid JSON payload to POST /reports/mapa-km and verifying the returned Excel file contains the expected data including vehicle in footer, correct month parsing from string, and proper styling.

**Acceptance Scenarios**:

1. **Given** a valid JSON payload with meta.month="Março", entries with sample data, holidays=[5,25], and vehicle details, **When** POST to /reports/mapa-km, **Then** receive Excel file with March data filled, vehicle in footer, weekends highlighted, and days 5/25 highlighted as holidays.
2. **Given** a valid JSON payload with meta.month="Janeiro", empty entries, and vehicle info, **When** POST to /reports/mapa-km, **Then** receive Excel file with January header, vehicle in footer, and appropriate weekend highlighting.

---

### User Story 3 - Handle Edge Cases and Errors (Priority: P3)

As an API client, I want the service to handle invalid inputs and edge cases gracefully by returning appropriate error responses, so that I can understand what went wrong and correct my requests.

**Why this priority**: Robust error handling ensures reliability and good developer experience, though it's secondary to core report generation functionality.

**Independent Test**: Can be fully tested by sending various invalid payloads to both endpoints and verifying appropriate HTTP status codes and error messages are returned.

**Acceptance Scenarios**:

1. **Given** JSON payload missing required meta.month, **When** POST to either endpoint, **Then** receive 422 status with validation error message.
2. **Given** JSON payload with invalid month (numeric >12 or invalid string), **When** POST to respective endpoint, **Then** receive 422 status with month validation error.
3. **Given** JSON payload with holidays containing invalid days (0, 32, non-integers), **When** POST to either endpoint, **Then** receive 422 status with holidays validation error.
4. **Given** malformed JSON, **When** POST to either endpoint, **Then** receive 422 status with JSON parsing error.

### Edge Cases

- Missing required fields (meta, meta.month) result in 422 validation errors
- Invalid month values (outside 1-12 for diario, invalid Portuguese month names for km) result in 422 errors
- Invalid holidays (non-integer, out of 1-31 range) are ignored with warnings logged
- Empty entries array produces Excel with header/footer but no data rows
- Very large entries arrays (>1000 items) may cause performance issues but should still work
- Special characters in text fields (entries.description, etc.) must be handled properly in Excel
- Concurrent requests should not interfere with each other due to stateless design

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide POST /reports/mapa-diario endpoint accepting JSON and returning Excel file
- **FR-002**: System MUST validate mapa-diario JSON schema: meta (required, with month as integer 1-12), entries (array), holidays (array of integers 1-31)
- **FR-003**: System MUST provide POST /reports/mapa-km endpoint accepting JSON and returning Excel file
- **FR-004**: System MUST validate mapa-km JSON schema: meta (required, with month as Portuguese month string), entries (array), holidays (array of integers 1-31), vehicle (object for footer)
- **FR-005**: System MUST load report-specific Excel template for each endpoint
- **FR-006**: System MUST fill header cells from meta data
- **FR-007**: System MUST fill data rows from entries array
- **FR-008**: System MUST fill footer cells from vehicle data (mapa-km only)
- **FR-009**: System MUST apply weekend highlighting to column A based on month
- **FR-010**: System MUST apply holiday highlighting to column A for specified days
- **FR-011**: System MUST not override any formulas or existing cell content during styling
- **FR-012**: System MUST return Excel file with appropriate filename including timestamp
- **FR-013**: System MUST handle missing optional fields by leaving corresponding cells empty
- **FR-014**: System MUST validate month values and return 422 for invalid months
- **FR-015**: System MUST validate holidays array and ignore invalid entries
- **FR-016**: System MUST handle empty entries arrays gracefully
- **FR-017**: System MUST return appropriate error responses for invalid requests

### Key Entities *(include if feature involves data)*

- **Report Request**: JSON payload containing meta (month, company info), entries (array of activity records), holidays (array of days), vehicle (object for km reports)
- **Excel Template**: Pre-defined XLSX file with placeholders for header, rows, and footer
- **Generated Report**: Output XLSX file with data filled and conditional styling applied
- **Validation Error**: Structured error response with field-specific validation messages

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: API endpoints respond with valid Excel files in under 5 seconds for payloads up to 100 entries
- **SC-002**: 100% of valid requests produce Excel files with correct data placement and formatting
- **SC-003**: System correctly applies weekend and holiday styling in 100% of generated reports
- **SC-004**: All specified edge cases return appropriate HTTP status codes and error messages
- **SC-005**: Service maintains 99.9% uptime for valid request patterns
