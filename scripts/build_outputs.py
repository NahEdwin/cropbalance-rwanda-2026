"""Recompute static baseline artifacts. Run at repository root."""
from pathlib import Path
import pandas as pd
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.engine import make_forecasts, scenario_forecasts, holdout_metrics
ROOT = Path(__file__).resolve().parents[1]
source = pd.read_csv(ROOT/'data/fbs_key_commodities_2017_2025.csv')
engine = make_forecasts(source)
scenario_forecasts(engine).round(3).to_csv(ROOT/'data/forecast_2026_baseline.csv',index=False)
engine['holdout_2025'].round(3).to_csv(ROOT/'data/validation_2025.csv',index=False)
print('WAPE:', holdout_metrics(engine['holdout_2025']))
print('Created data/forecast_2026_baseline.csv and data/validation_2025.csv')
