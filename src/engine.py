"""Transparent annual forecasting engine for the CropBalance Rwanda prototype.

All volumes are 1,000 metric tonnes (kt); food per capita is kg/person/year.
Series have only nine observations, so statistical baselines are compared to a
regularized pooled random forest. Forecast uncertainty bands are heuristic,
not calibrated prediction intervals. See docs/METHODOLOGY.md.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

YEARS = list(range(2017, 2026))
BACKTEST_YEARS = (2022, 2023, 2024, 2025)
TARGETS = ("production_kt", "per_capita_food_kg", "nonfood_use_kt")
MODELS = ("Last year", "3-year average", "Damped trend", "Pooled random forest")


def prepared_data(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["year"] = out["year"].astype(int)
    out["nonfood_use_kt"] = (out.domestic_supply_kt - out.food_kt).clip(lower=0)
    assert not out.duplicated(["year", "commodity"]).any()
    return out.sort_values(["commodity", "year"]).reset_index(drop=True)


def implied_population_millions(df: pd.DataFrame) -> pd.Series:
    """Median implied population among large food categories to reduce rounding noise.

    In NISR FBS, 1 kt = 1m kg. Thus food_kt / kg_per_person = people in millions.
    This is a reconstruction for visualization, NOT an official population projection.
    """
    valid = df[(df.food_kt >= 100) & (df.per_capita_food_kg >= 10)].copy()
    valid["pop"] = valid.food_kt / valid.per_capita_food_kg
    pop = valid.groupby("year")["pop"].median().sort_index()
    assert len(pop) == 9
    return pop


def _simple_forecast(values: np.ndarray, model: str) -> float:
    values = np.asarray(values, dtype=float)
    if len(values) < 3:
        return max(0.0, float(values[-1]))
    if model == "Last year":
        return max(0.0, float(values[-1]))
    if model == "3-year average":
        return max(0.0, float(np.mean(values[-3:])))
    if model == "Damped trend":
        hist = values[-min(5, len(values)):]
        if len(hist) < 3:
            return max(0.0, float(values[-1]))
        slope = float(np.polyfit(np.arange(len(hist)), hist, 1)[0])
        estimate = float(values[-1] + 0.5 * slope)
        # Limit one-year trend extrapolation when annual series are short.
        upper = values[-1] * 1.30 + 1.0
        lower = max(0.0, values[-1] * 0.70 - 1.0)
        return float(np.clip(estimate, lower, upper))
    raise ValueError(model)


def _ml_features(values: np.ndarray, target_year: int) -> list[float]:
    v = np.asarray(values, dtype=float)
    if len(v) < 3:
        raise ValueError("Need 3 historical observations")
    a, b, c = v[-3:]
    mean3 = float(np.mean(v[-3:]))
    std3 = float(np.std(v[-3:]))
    s = max(mean3, 0.5)
    return [
        float(np.log1p(max(0, c))),
        float(c / s), float(b / s), float(a / s),
        float(std3 / s), float((c - b) / s),
        float((c - a) / (2 * s)),
        float((target_year - 2017) / 10),
    ]


def _series_dict(df: pd.DataFrame, target: str) -> dict[str, dict[int, float]]:
    return {
        commodity: {int(y): float(val) for y, val in zip(group.year, group[target])}
        for commodity, group in df.groupby("commodity")
    }


def _pooled_ml_fit(series: dict[str, dict[int, float]], target_year: int):
    """Train on rows strictly earlier than the target year; no temporal leakage."""
    X, y = [], []
    for _, vals in series.items():
        for year in sorted(vals):
            if year >= target_year or year < 2020:
                continue
            years = list(range(2017, year))
            if not all(yr in vals for yr in years):
                continue
            hist = np.array([vals[yr] for yr in years], dtype=float)
            eps = 0.5
            growth = np.log((max(vals[year], 0.0) + eps) / (max(hist[-1], 0.0) + eps))
            X.append(_ml_features(hist, year))
            y.append(float(np.clip(growth, -0.75, 0.75)))
    if len(X) < 15:
        return None
    model = RandomForestRegressor(
        n_estimators=90, min_samples_leaf=4, max_depth=5,
        max_features=0.8, random_state=26, n_jobs=1,
    )
    model.fit(X, y)
    return model


def _model_predictions(series: dict[str, dict[int, float]], target_year: int) -> dict[str, dict[str, float]]:
    rf = _pooled_ml_fit(series, target_year)
    forecasts = {}
    for crop, values in series.items():
        hist_years = sorted(y for y in values if y < target_year)
        arr = np.asarray([values[y] for y in hist_years], dtype=float)
        if len(arr) < 3:
            raise ValueError(f"Insufficient history: {crop}, {target_year}")
        p = {m: _simple_forecast(arr, m) for m in MODELS[:-1]}
        if rf is not None:
            growth = float(rf.predict([_ml_features(arr, target_year)])[0])
            p[MODELS[-1]] = float(max(0.0, (arr[-1] + 0.5) * np.exp(growth) - 0.5))
        else:
            p[MODELS[-1]] = p["3-year average"]
        forecasts[crop] = p
    return forecasts


def _top_models(backtest: pd.DataFrame, commodity: str, target: str, last_year: int) -> list[str]:
    chosen = backtest[
        (backtest.commodity == commodity)
        & (backtest.target == target)
        & (backtest.year <= last_year)
    ]
    if len(chosen) == 0:
        return ["3-year average", "Last year"]
    scores = {}
    for model, sub in chosen.groupby("model"):
        scores[model] = float(np.mean(np.abs(sub.forecast - sub.actual) / np.maximum(sub.actual, 1.0)))
    return sorted(scores, key=lambda m: (scores[m], MODELS.index(m)))[:2]


def _ensemble(predictions: dict[str, float], winners: list[str]) -> float:
    return max(0.0, 0.65 * predictions[winners[0]] + 0.35 * predictions[winners[1]])


def _validation_pivot(bt: pd.DataFrame, year: int, last_selection_year: int) -> pd.DataFrame:
    """Rebuild predictions for a holdout with models chosen on earlier holdouts."""
    bt_year = bt[bt.year == year]
    rows = []
    for (crop, target), sub in bt_year.groupby(["commodity", "target"]):
        chosen = _top_models(bt, crop, target, last_selection_year)
        by_model = {r.model: float(r.forecast) for r in sub.itertuples()}
        rows.append({"commodity": crop, "target": target,
                     "actual": float(sub.actual.iloc[0]),
                     "forecast": _ensemble(by_model, chosen),
                     "baseline": by_model["Last year"],
                     "selected_models": "+".join(chosen)})
    return pd.DataFrame(rows)


def make_forecasts(source: pd.DataFrame) -> dict[str, Any]:
    data = prepared_data(source)
    population = implied_population_millions(data)
    all_series = {target: _series_dict(data, target) for target in TARGETS}

    bt_rows = []
    for target, series in all_series.items():
        for holdout_year in BACKTEST_YEARS:
            predictions = _model_predictions(series, holdout_year)
            for crop, all_predictions in predictions.items():
                actual = series[crop][holdout_year]
                for model, pred in all_predictions.items():
                    bt_rows.append(dict(target=target, year=holdout_year, commodity=crop,
                                        model=model, forecast=pred, actual=actual))
    bt = pd.DataFrame(bt_rows)

    # 2025 is a genuine out-of-sample evaluation year for model choice: the two
    # models are selected on 2022, 2023 and 2024 only.
    val25 = _validation_pivot(bt, year=2025, last_selection_year=2024)
    val_wide = val25.pivot(index="commodity", columns="target", values=["actual", "forecast", "baseline"])
    val_data = []
    for crop in sorted(data.commodity.unique()):
        actual_need = float(data[(data.commodity == crop) & (data.year == 2025)].domestic_supply_kt.iloc[0])
        forecast_food = float(val_wide.loc[crop, ("forecast", "per_capita_food_kg")]) * population.loc[2025]
        baseline_food = float(val_wide.loc[crop, ("baseline", "per_capita_food_kg")]) * population.loc[2025]
        pred_need = forecast_food + float(val_wide.loc[crop, ("forecast", "nonfood_use_kt")])
        baseline_need = baseline_food + float(val_wide.loc[crop, ("baseline", "nonfood_use_kt")])
        actual_prod = float(val_wide.loc[crop, ("actual", "production_kt")])
        pred_prod = float(val_wide.loc[crop, ("forecast", "production_kt")])
        baseline_prod = float(val_wide.loc[crop, ("baseline", "production_kt")])
        val_data.append(dict(commodity=crop, year=2025,
                             actual_use_kt=actual_need, pred_use_kt=pred_need,
                             baseline_use_kt=baseline_need,
                             actual_production_kt=actual_prod, pred_production_kt=pred_prod,
                             baseline_production_kt=baseline_prod,
                             use_abs_pct_error=100*abs(pred_need-actual_need)/max(1, actual_need),
                             production_abs_pct_error=100*abs(pred_prod-actual_prod)/max(1, actual_prod)))
    validation = pd.DataFrame(val_data)

    predictions26 = {target: _model_predictions(series, 2026) for target, series in all_series.items()}
    last_data = data[data.year == 2025].set_index("commodity")
    out = []
    for crop in sorted(data.commodity.unique()):
        pred = {}
        models = {}
        for target in TARGETS:
            winners = _top_models(bt, crop, target, 2025)
            pred[target] = _ensemble(predictions26[target][crop], winners)
            models[target] = " + ".join(winners)
        hist = data[data.commodity == crop].sort_values("year")
        # Recent published FBS loss rates; descriptive scenario anchor, not ML.
        loss = float(hist.loss_kt.tail(3).mean())
        # Scenario-independent heuristic ranges calibrated only to observed annual
        # variability. They are NOT statistical prediction intervals.
        prod_growth = hist.production_kt.pct_change().replace([np.inf, -np.inf], np.nan).dropna().tail(5)
        use_growth = hist.domestic_supply_kt.pct_change().replace([np.inf, -np.inf], np.nan).dropna().tail(5)
        band_prod = float(np.clip(0.08 + 0.65 * prod_growth.std(ddof=0), 0.10, 0.45))
        band_use = float(np.clip(0.08 + 0.65 * use_growth.std(ddof=0), 0.10, 0.45))
        out.append({
            "commodity": crop, "production_forecast_kt": pred["production_kt"],
            "food_per_capita_forecast_kg": pred["per_capita_food_kg"],
            "nonfood_use_forecast_kt": pred["nonfood_use_kt"],
            "loss_reference_kt": loss,
            "production_band_frac": band_prod, "utilization_band_frac": band_use,
            "production_selected_models": models["production_kt"],
            "percap_selected_models": models["per_capita_food_kg"],
            "nonfood_selected_models": models["nonfood_use_kt"],
            "published_2025_prod_kt": float(last_data.loc[crop, "production_kt"]),
            "published_2025_domestic_util_kt": float(last_data.loc[crop, "domestic_supply_kt"]),
            "published_2025_loss_kt": float(last_data.loc[crop, "loss_kt"]),
        })
    raw_forecasts = pd.DataFrame(out)
    return {"history": data, "population_millions": population,
            "backtest": bt, "holdout_2025": validation, "raw_forecasts": raw_forecasts}


def scenario_forecasts(engine: dict, population_growth_pct: float = 2.2,
                       production_change_pct: float = 0.0,
                       loss_reduction_pct: float = 0.0,
                       selected_crop: str = "All commodities") -> pd.DataFrame:
    """Return one transparent 2026 scenario, showing all assumptions."""
    base = engine["raw_forecasts"].copy()
    p2025 = float(engine["population_millions"].loc[2025])
    p2026 = p2025 * (1 + population_growth_pct / 100)
    base["food_forecast_kt"] = base.food_per_capita_forecast_kg * p2026
    base["baseline_utilization_kt"] = base.food_forecast_kt + base.nonfood_use_forecast_kt
    base["potential_loss_savings_kt"] = base.loss_reference_kt * loss_reduction_pct / 100
    base["utilization_2026_kt"] = (base.baseline_utilization_kt - base.potential_loss_savings_kt).clip(lower=0)
    mask = np.ones(len(base), dtype=bool) if selected_crop == "All commodities" else (base.commodity == selected_crop)
    base["production_2026_kt"] = base.production_forecast_kt * (1 + np.where(mask, production_change_pct, 0.0) / 100)
    base["production_minus_use_kt"] = base.production_2026_kt - base.utilization_2026_kt
    base["coverage_pct"] = np.where(base.utilization_2026_kt>0, 100*base.production_2026_kt / base.utilization_2026_kt, np.nan)
    base["production_low_kt"] = base.production_2026_kt * (1 - base.production_band_frac)
    base["production_high_kt"] = base.production_2026_kt * (1 + base.production_band_frac)
    base["utilization_low_kt"] = base.utilization_2026_kt * (1 - base.utilization_band_frac)
    base["utilization_high_kt"] = base.utilization_2026_kt * (1 + base.utilization_band_frac)
    base["assessment"] = np.select([
        base.production_high_kt < base.utilization_low_kt,
        base.production_low_kt > base.utilization_high_kt,
    ], ["Below use across indicative range", "Above use across indicative range"],
        default="Overlap / uncertain")
    base["assumed_population_2026_millions"] = p2026
    return base.sort_values("production_minus_use_kt").reset_index(drop=True)


def total_wape(observed: pd.Series, predicted: pd.Series) -> float:
    return float(100 * np.sum(np.abs(observed - predicted)) / max(1.0, np.sum(np.abs(observed))))


def holdout_metrics(validation: pd.DataFrame) -> dict[str, float]:
    return {
        "use_wape_pct": total_wape(validation.actual_use_kt, validation.pred_use_kt),
        "use_baseline_wape_pct": total_wape(validation.actual_use_kt, validation.baseline_use_kt),
        "production_wape_pct": total_wape(validation.actual_production_kt, validation.pred_production_kt),
        "production_baseline_wape_pct": total_wape(validation.actual_production_kt, validation.baseline_production_kt),
    }
