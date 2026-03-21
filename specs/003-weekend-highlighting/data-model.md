# Data Model: Weekend Highlighting

## Entities

### Month Input
- **Type**: Integer
- **Range**: 1-12
- **Validation**: Must be present in JSON payload; reject if outside range or non-integer
- **Usage**: Determines which month to calculate weekends for

### Weekend Days
- **Type**: Set of integers
- **Range**: 1-31 (subset valid for the month)
- **Derivation**: Calculated from month and year using datetime/calendar
- **Validation**: Only includes days that are Saturdays or Sundays within the month's valid days
- **Usage**: Identifies which rows (days) to highlight in Excel

### Highlight Configuration
- **Type**: Dictionary
- **Keys**:
  - `weekend_fill`: String (hex color code, e.g., "FFD9D9D9")
- **Validation**: Must be valid hex color; required for styling
- **Usage**: Provides color for weekend row highlighting

## Relationships

- **Month Input** → **Weekend Days**: One-to-one derivation (month determines weekend set)
- **Highlight Configuration** → **Excel Styling**: Configuration drives styling application
- **Weekend Days** → **Excel Rows**: Set maps to row numbers (day 1 = row 8, etc.)

## Validation Rules

- Month must be 1-12; invalid values trigger 400 error
- Weekend days set cannot exceed month's maximum day (e.g., Feb 28/29)
- Color must be valid hex format; invalid config raises startup error
- All entities are stateless; no persistence required

## State Transitions

N/A - All entities are request-scoped and computed per request.