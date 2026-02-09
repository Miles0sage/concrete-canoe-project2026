# Contributing

## Git Workflow

1. Pull latest: `git pull origin main`
2. Create a branch: `git checkout -b feature/your-feature`
3. Make changes
4. Run tests: `pytest tests/ -v`
5. Commit: `git commit -m "Description of changes"`
6. Push: `git push origin feature/your-feature`
7. Create Pull Request on GitHub

## Coding Standards

- Python: Follow PEP 8
- All functions must have docstrings
- Figures: 300 DPI minimum, saved to `reports/figures/`
- Data: Export to CSV in `data/`
- Reports: Markdown in `reports/`

## Adding a New Design

1. Add to the `DESIGNS` list in the relevant script
2. Run analysis to generate figures and data
3. Add tests in `tests/test_integration.py`
4. Update comparison table in README

## Review Process

- All changes should be reviewed by at least one team member
- Tests must pass before merging
- Update documentation if behavior changes
