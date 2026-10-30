"""Preflight: check required files, source data and forecasts. Read-only."""
from pathlib import Path
import csv,sys
ROOT=Path(__file__).resolve().parents[1]
required=['app.py','requirements.txt','README.md','DECLARATION.md','docs/METHODOLOGY.md',
'docs/DATA_SOURCES.md','docs/SUBMISSION_STEPS.md','data/fbs_key_commodities_2017_2025.csv',
'data/forecast_2026_baseline.csv','data/validation_2025.csv','src/engine.py']
missing=[f for f in required if not (ROOT/f).is_file()]
if missing:
    print('MISSING FILES:',missing);sys.exit(1)
with (ROOT/'data/fbs_key_commodities_2017_2025.csv').open(encoding='utf-8') as f:
    rows=list(csv.DictReader(f))
assert len(rows)==135,len(rows)
assert len({r['year'] for r in rows})==9
assert len({r['commodity'] for r in rows})==15
print('READY FOR REVIEW: all required files present and data has 135 rows.')
print('REMINDER: team must complete name, declaration, publish GitHub and deploy Streamlit before NISR submission.')
