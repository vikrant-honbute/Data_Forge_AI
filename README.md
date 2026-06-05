# DataForge AI

## Quickstart

1. Create a virtual environment:
   - Windows (PowerShell): `python -m venv .venv`
   - macOS/Linux: `python -m venv .venv`
2. Activate the environment:
   - Windows (PowerShell): `.venv\Scripts\Activate.ps1`
   - macOS/Linux: `source .venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Add `GROQ_API_KEY` to `.env`.
5. Run profiling: `python scripts/run_on_csv.py`
6. Run full pipeline: `python scripts/run_full.py`
