# Testing Data

Compression tests, density measurements, workability assessments.

## Test Types

### Compression Testing (ASTM C39)
- 4x8 inch cylinders
- Test at 7 days and 28 days
- Minimum target: 1000 PSI

### Density Testing (ASTM C138)
- Fresh concrete density
- Target: 65 PCF

### Slump Testing (ASTM C143)
- Workability assessment
- Target: 4-6 inch slump

## Data Format

Store test results in markdown tables:

```markdown
| Mix ID | Test Date | Age (days) | Strength (PSI) | Density (PCF) |
|--------|-----------|------------|----------------|---------------|
| MIX-001 | 2026-02-15 | 7 | 850 | 64.2 |
| MIX-001 | 2026-03-08 | 28 | 1150 | 64.5 |
```

## Testing Schedule

- Week 1: Make test cylinders for initial mix
- Week 2: 7-day compression tests
- Week 5: 28-day compression tests
- Week 6: Final mix selection
