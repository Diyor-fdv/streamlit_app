# Centrum Air — Ground Handling Tasks (Portfolio Demo)

**Secure portfolio version.** No real DB or company data. The app generates synthetic data in-memory
but preserves the original UI and logic (tabs, filters, delay highlighting, etc.).

## Run locally
```bash
python -m venv .venv
.\.venv\Scripts\activate  # Windows
pip install -r requirements.txt
streamlit run app.py
```

### Demo login
- Username: `flight`
- Password: `task123`

## Files
- `app.py` — Streamlit app
- `settings.py` — colors, logo (local `logo.jpg`), demo credentials
- `utility.py` — HTML table renderer & helpers
- `filters.py` — aircraft/flight options (from mock data)
- `mock_data.py` — synthetic dataset generator & pivoting
- `logo.jpg` — local logo used in the UI
- `requirements.txt` — deps
- `.gitignore` — excludes secrets like `.env` (not used here), caches, venv, etc.

## Notes
- All aircraft & flight numbers are **randomized** each run.
- No external services. Safe to publish as a portfolio project.
