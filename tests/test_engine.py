from pathlib import Path
import sys
import unittest
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.engine import make_forecasts, scenario_forecasts, holdout_metrics

class TestForecastEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = pd.read_csv(ROOT / 'data/fbs_key_commodities_2017_2025.csv')
        cls.engine = make_forecasts(cls.df)

    def test_data_coverage_and_maize_reference(self):
        self.assertEqual(len(self.df), 135)
        self.assertEqual(self.df.year.nunique(), 9)
        self.assertEqual(self.df.commodity.nunique(), 15)
        maize = self.df[(self.df.year==2024)&(self.df.commodity=='Maize')].iloc[0]
        self.assertEqual([maize.production_kt,maize.imports_kt,maize.exports_kt,maize.stock_change_kt,maize.domestic_supply_kt], [627,250,196,121,559])

    def test_baseline_forecast_has_finite_values(self):
        f = scenario_forecasts(self.engine)
        self.assertEqual(len(f), 15)
        for col in ['production_2026_kt','utilization_2026_kt','production_minus_use_kt','coverage_pct']:
            self.assertTrue(np.isfinite(f[col]).all())
        self.assertTrue((f.production_2026_kt>=0).all())
        self.assertTrue((f.utilization_2026_kt>0).all())

    def test_scenario_production_and_loss(self):
        before = scenario_forecasts(self.engine).set_index('commodity')
        after = scenario_forecasts(self.engine, production_change_pct=-20,
                                   selected_crop='Maize', loss_reduction_pct=20).set_index('commodity')
        self.assertAlmostEqual(after.loc['Maize','production_2026_kt']/before.loc['Maize','production_2026_kt'],0.8)
        self.assertAlmostEqual(after.loc['Rice (milled equivalent)','production_2026_kt'],before.loc['Rice (milled equivalent)','production_2026_kt'])
        self.assertTrue((after.utilization_2026_kt.sort_index()<=before.utilization_2026_kt.sort_index()).all())

    def test_model_reports_baseline_without_hiding_comparison(self):
        m = holdout_metrics(self.engine['holdout_2025'])
        self.assertLess(m['use_baseline_wape_pct'],m['use_wape_pct'])
        self.assertLess(m['production_baseline_wape_pct'],m['production_wape_pct'])

if __name__=='__main__':
    unittest.main()
