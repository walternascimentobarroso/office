# Feature Specification: Generate Excel from JSON

**Feature Branch**: `002-generate-excel-from-json`  
**Created**: 20 March 2026  
**Status**: Draft  
**Input**: User description: "Create a specification for an API that generates an Excel file from structured JSON input.

Endpoint:
POST /generate-excel

Input JSON structure:
{
  \"meta\": {
    \"empresa\": string,
    \"nif\": string,
    \"mes\": string
  },
  \"entries\": [
    {
      \"day\": int,
      \"description\": string,
      \"location\": string,
      \"start_time\": string,
      \"end_time\": string
    }
  ]
}

Behavior:
- Load Excel template
- Fill header fields using fixed cell mapping
- Fill rows dynamically starting at row 8
- Each entry fills:
  - Column A → day
  - Column B → description
  - Column D → location
  - Column E → start_time
  - Column J → end_time
- Do NOT overwrite any formula columns

Output:
- Return Excel file as download

Requirements:
- Missing fields must not break execution
- Extra fields must be ignored
- Validate input structure

Edge cases:
- Empty entries array
- Partial data
- Invalid template

Deliver:
- API contract
- Example request/response
- Error handling strategy"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate Excel from Valid JSON (Priority: P1)

As an API consumer, I want to send valid JSON data to generate an Excel file with the data populated in the correct cells.

**Why this priority**: This is the core functionality that delivers the primary value of the API.

**Independent Test**: Can be fully tested by sending a POST request with valid JSON and verifying the returned Excel file contains the expected data in the specified cells.

**Acceptance Scenarios**:

1. **Given** a valid JSON payload with meta and entries, **When** POST to /generate-excel, **Then** returns an Excel file with header fields filled from meta and rows filled from entries.
2. **Given** a valid JSON payload, **When** POST to /generate-excel, **Then** the Excel file has data starting at row 8, with day in column A, description in B, location in D, start_time in E, end_time in J.

---

### User Story 2 - Handle Missing Fields Gracefully (Priority: P2)

As an API consumer, I want the API to handle missing fields in the JSON without failing, so that partial data can still generate a valid Excel file.

**Why this priority**: Ensures robustness and prevents failures due to incomplete data.

**Independent Test**: Can be tested by sending JSON with missing fields and verifying the API still returns an Excel file with available data filled.

**Acceptance Scenarios**:

1. **Given** JSON with missing meta fields, **When** POST to /generate-excel, **Then** returns Excel file with available meta data filled and missing fields left blank.
2. **Given** JSON with entries missing some fields, **When** POST to /generate-excel, **Then** returns Excel file with available entry data filled and missing fields left blank.

---

### User Story 3 - Handle Empty Entries (Priority: P3)

As an API consumer, I want the API to handle an empty entries array without failing, so that I can generate Excel files even when no entries are provided.

**Why this priority**: Handles edge case of no data to fill, ensuring API stability.

**Independent Test**: Can be tested by sending JSON with empty entries array and verifying the API returns a valid Excel file with only header data.

**Acceptance Scenarios**:

1. **Given** JSON with empty entries array, **When** POST to /generate-excel, **Then** returns Excel file with header filled and no rows added.

---

### Edge Cases

- What happens when entries array is empty? → Returns Excel with only header data.
- How does system handle partial data in entries? → Fills available fields, leaves missing ones blank.
- How does system handle invalid template? → [NEEDS CLARIFICATION: What constitutes invalid template and how to handle?]
- What if JSON has extra fields? → Ignores extra fields.
- What if JSON structure is invalid? → Returns error response.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept POST requests to /generate-excel endpoint with JSON body.
- **FR-002**: System MUST validate that input JSON has required top-level structure (meta object and entries array).
- **FR-003**: System MUST load the configured Excel template file.
- **FR-004**: System MUST fill header cells using fixed mapping from meta object (empresa, nif, mes to specific cells).
- **FR-005**: System MUST fill rows dynamically starting at row 8, one row per entry.
- **FR-006**: System MUST map entry fields to columns: day→A, description→B, location→D, start_time→E, end_time→J.
- **FR-007**: System MUST NOT overwrite any cells containing formulas.
- **FR-008**: System MUST return the generated Excel file as a downloadable response.
- **FR-009**: System MUST handle missing fields in JSON without breaking execution.
- **FR-010**: System MUST ignore extra fields in JSON.
- **FR-011**: System MUST validate input structure and return appropriate errors for invalid JSON.

### Key Entities *(include if feature involves data)*

- **Meta**: Contains company information with attributes empresa (string), nif (string), mes (string). Used to fill header fields.
- **Entry**: Represents a daily entry with attributes day (integer), description (string), location (string), start_time (string), end_time (string). Each entry fills one row in the Excel file.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: API generates Excel file in under 30 seconds for inputs with up to 100 entries.
- **SC-002**: System achieves 99% success rate for valid JSON inputs.
- **SC-003**: System handles invalid inputs without crashing and returns appropriate error responses.
- **SC-004**: 95% of users can successfully generate Excel files on first attempt with valid data.
