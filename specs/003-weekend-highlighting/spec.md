# Feature Specification: Weekend Highlighting in Excel Output

**Feature Branch**: `003-weekend-highlighting`  
**Created**: 2026-03-21  
**Status**: Draft  
**Input**: User description: "Extend the API specification to support weekend highlighting in the Excel output. New behavior: Input: - The field \"mes\" (month) is always a number between 1 and 12. Processing: 1. Determine the current year (use system year or configurable value). 2. For the given month: - Calculate which days are Saturdays and Sundays. 3. For each day in the Excel (rows 8 to 38): - Column A contains the day number (1–31). - If the day is a weekend: - Apply highlight color to the entire row. Affected columns: - A, B, D, E, J (only the columns we control) Rules: - Do NOT modify formula columns - Do NOT overwrite data - Only apply fill color Color: - Must match the color currently used in A8 - This color must be stored in configuration (not read dynamically every time) Edge cases: - Month with less than 31 days - Invalid month input - Missing \"mes\" field Deliver: - Clear description of styling logic - Example before/after behavior"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Weekend Day Highlighting (Priority: P1)

As a user generating Excel reports with calendar data, I want weekend days (Saturdays and Sundays) to be visually highlighted in the output so that I can easily distinguish working days from non-working days.

**Why this priority**: This is the core functionality requested, providing immediate visual value to users reviewing calendar-based Excel reports.

**Independent Test**: Can be fully tested by submitting a request with a month containing weekends, generating the Excel file, and verifying that the appropriate rows are highlighted while data integrity is preserved.

**Acceptance Scenarios**:

1. **Given** a valid month input with weekend days, **When** the Excel is generated, **Then** rows corresponding to Saturdays and Sundays are highlighted with the specified color.
2. **Given** a valid month input with no weekend days in the visible range, **When** the Excel is generated, **Then** no rows are highlighted.
3. **Given** an invalid month input, **When** the request is processed, **Then** an appropriate error is returned without generating the Excel.

---

### Edge Cases

- What happens when the month has fewer than 31 days (e.g., February has 28 or 29 days)?
- How does the system handle invalid month values (not 1-12)?
- What occurs when the "mes" field is missing from the input?
- How are leap years handled for February calculations?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept a "mes" field in the JSON input as an integer between 1 and 12 representing the month.
- **FR-002**: System MUST determine the current year using system time or a configurable value for weekend calculations.
- **FR-003**: System MUST calculate which days in the given month are Saturdays and Sundays.
- **FR-004**: System MUST apply highlight styling to entire rows (columns A, B, D, E, J) for weekend days in Excel rows 8-38.
- **FR-005**: System MUST use a fill color that matches the existing style in cell A8, stored in configuration.
- **FR-006**: System MUST NOT modify any formula columns or overwrite existing data during styling.
- **FR-007**: System MUST handle months with fewer than 31 days correctly, only highlighting valid days.
- **FR-008**: System MUST validate the "mes" field and return an error for invalid or missing values.
- **FR-009**: System MUST ensure styling does not break existing formulas or data integrity.

### Key Entities *(include if feature involves data)*

- **Month Input**: Represents the month number (1-12) provided in the JSON payload, used to determine weekend days.
- **Day Calculation**: Represents the logic for identifying Saturdays and Sundays within the specified month and year.
- **Highlight Configuration**: Represents the stored color configuration used for weekend highlighting, matching the A8 cell style.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Weekend days (Saturdays and Sundays) are visually highlighted in generated Excel files with the correct color.
- **SC-002**: No existing data, formulas, or cell values are altered by the highlighting process.
- **SC-003**: Highlighting is applied only to the specified columns (A, B, D, E, J) and rows (8-38).
- **SC-004**: System correctly handles all valid months (1-12) and edge cases like February in leap years.
- **SC-005**: Invalid month inputs result in clear error responses without file generation.
- **SC-006**: Highlighting configuration is loaded from static configuration, not dynamically from templates.
