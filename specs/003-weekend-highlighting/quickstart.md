# Quickstart: Weekend Highlighting in Excel Output

## Overview
The Excel generation API now supports automatic weekend highlighting. Provide a `mes` field (1-12) in your request to highlight Saturday and Sunday rows with a configured color.

## Basic Usage

### Request
```json
{
  "mes": 3,
  // ... your existing payload ...
}
```

### Response
Excel file with weekends in March highlighted.

## Configuration
The highlight color is configured in `src/core/config.py`:
```python
WEEKEND_FILL = "FFD9D9D9"  # Light gray - matches template A8
```

## Affected Columns
Highlighting applies only to columns A, B, D, E, J (data columns).

## Troubleshooting

### No Highlighting Appears
- Verify `mes` is 1-12 integer
- Check config has valid hex color
- Ensure month has weekends (e.g., February may have few)

### Invalid Month Error
- `mes` must be 1-12
- Field is required

### Performance Issues
- Highlighting adds ~50ms to generation
- Monitor for large sheets

## Example Output
For `mes: 3` (March 2026):
- Highlighted days: 1,2,8,9,15,16,22,23,29,30
- Rows: 8-9, 15-16, 22-23, 29-30, 36-37