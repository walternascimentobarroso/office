# Research: Weekend Highlighting Implementation

## Performance Goals Clarification

**Decision**: Target response time <500ms for Excel generation with highlighting (including weekend calculation and styling).

**Rationale**: Balances user experience with server load; aligns with typical web service latency expectations; openpyxl operations are fast for small sheets.

**Alternatives Considered**:
- <200ms: Too restrictive, may require premature optimization
- <2s: Too lenient, degrades UX for interactive use
- No target: Leaves ambiguity for testing and monitoring

## Weekend Color Determination

**Decision**: Inspect template file manually to extract RGB values from cell A8 fill color, store as hex string in configuration (e.g., "FFD9D9D9").

**Rationale**: Complies with constitution principle 11 (no runtime reading); ensures deterministic output; manual inspection is one-time setup cost.

**Alternatives Considered**:
- Hardcode a default gray color: May not match template, violates "match A8" requirement
- Runtime inspection: Violates constitution, introduces template dependency
- User-provided color in request: Adds complexity, not requested

## Year Determination for Weekend Calculation

**Decision**: Use current system year (datetime.date.today().year) for all calculations.

**Rationale**: Simplifies implementation; assumes reports are for current year; avoids adding year field to API.

**Alternatives Considered**:
- Configurable year in config file: Adds unnecessary configuration complexity
- Year field in JSON input: Changes API contract without clear benefit
- Always use 2026: Hardcoded, not maintainable

## Date Calculation Best Practices

**Decision**: Use Python's datetime and calendar modules for weekend detection.

**Rationale**: Standard library, reliable, handles leap years correctly; calendar.monthrange() for days in month.

**Alternatives Considered**:
- Third-party libraries (e.g., dateutil): Unnecessary dependency for simple use case
- Manual calculation: Error-prone, reinventing wheel
- Precomputed weekend sets: Overkill for monthly calculations

## Excel Styling with openpyxl

**Decision**: Use openpyxl.PatternFill with fgColor for background fill on specified columns.

**Rationale**: Direct support in openpyxl; preserves existing styles; applies only fill without affecting borders/fonts.

**Alternatives Considered**:
- Conditional formatting: More complex, may conflict with existing template formatting
- Cell-by-cell styling: Inefficient, harder to maintain
- Pandas styling: Not applicable, using openpyxl directly

## Configuration Management

**Decision**: Extend existing config.py with weekend_fill key, loaded as dict.

**Rationale**: Consistent with project patterns; easy to access; supports future styling extensions.

**Alternatives Considered**:
- Environment variables: Less structured for color values
- Separate config file: Overkill for single value
- Inline constants: Harder to change without code deploy