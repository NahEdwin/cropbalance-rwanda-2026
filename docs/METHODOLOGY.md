# Forecasting and validation methodology

## Research question

**How might Rwanda's annual domestic utilization of 15 agricultural/food commodities in 2026 compare with expected domestic production, and how might selected assumptions change that comparison?**

We **do not** attempt to estimate actual national calorie deficiency, household purchasing power, production by district or harvest-time market prices. This is an early-stage **planning demonstrator** built from NISR national Food Balance Sheets.

## NISR source data

Four NISR reports contain 2017–2025 annual data. Selected food balance rows include production, imports, exports, stock change, domestic supply, food use, non-food uses and reported loss. Commodity naming conventions have been preserved in the source CSV. NISR reports all tonnage as **thousand metric tonnes (kt)**. See [DATA_SOURCES.md](DATA_SOURCES.md) for report pages and checks.

For each commodity and year:

```
domestic_supply_kt = production_kt + imports_kt - exports_kt - stock_change_kt
nonfood_use_kt   = max(0, domestic_supply_kt - food_kt)
```

In national FBS accounting, total domestic utilization approximately equals total domestic supply, allowing for rounding. Note that this *includes* processing, seed, feed, measured losses and other uses. It is distinct from edible household food demand.

## Historical population denominator

For a commodity with sizable published food supply, `food_kt / per_capita_food_kg` yields the implied population in millions, since kt = million kg. We calculate the **median** across commodities where food use is at least 100 kt and published per-capita use at least 10 kg/year. This robustly reduces the effect of one-decimal kg rounding.

| Year | Approximate implied population (million) |
|---|---:|
| 2017 | 11.81 |
| 2018 | 12.09 |
| 2019 | 12.38 |
| 2020 | 12.66 |
| 2021 | 12.95 |
| 2022 | 13.25 |
| 2023 | 13.50 |
| 2024 | 13.80 |
| 2025 | 14.10 |

These figures are **inferred from FBS**, not a replacement for official census projections. The published 2024 table header is inconsistent with several 2024 data rows; the original published cells are preserved.

For 2026, the prototype applies a **user-editable population growth assumption**. The default 2.2% is chosen as a round scenario reflecting recent implied changes and **is not stated as an official 2026 population forecast**.

## Three forecast targets

We model, separately, for each commodity:

1. **Human-food availability per capita** (kg/person/year).
2. **Other domestic uses** (kt), i.e., domestic supply minus human food use, including processing, feed, seed, loss, and other uses.
3. **Domestic production** (kt).

To calculate 2026 quantities:

```
population_2026_million = implied_population_2025_million * (1 + assumed_growth_pct/100)
food_2026_kt          = forecast_food_per_capita_kg * population_2026_million
utilization_2026_kt   = food_2026_kt + forecast_nonfood_use_kt
production_gap_kt     = forecast_production_kt - utilization_2026_kt
production_coverage_% = 100 * forecast_production_kt / utilization_2026_kt
```

The multiplication above is dimensionally correct: `(kg/person) × (million persons) = million kg = thousand tonnes`.

## Candidate forecasting methods

Given only nine annual records per commodity, we compare simple forecasting baselines to one pooled ML model instead of assuming a deep-learning system is justified:

- **Last-year persistence:** next year equals the previous year's recorded value.
- **Three-year average:** next year equals the average of the previous three values.
- **Damped trend:** linear trend estimated from the last five years (or as many as available), projected forward at half-strength and limited to a ±30% one-year movement (with a 1-unit guard for very small series).
- **Pooled random forest:** a 90-tree scikit-learn RandomForestRegressor trained on *year-on-year log growth* from all 15 commodities for each target. Features are lag levels and normalized lag ratios, recent variation, recent slopes and target year. Trees use max depth 5, minimum 4 samples per leaf, and fixed seed 26. Training rows use only years **strictly before the forecast year**. Predictions are converted back into the source units.

The random forest shares statistical information across commodities but has limited annual history. Its inclusion is an exploratory benchmark, not proof that ML is superior.

## Model selection and validation

- Rolling one-year-ahead backtests produce forecasts for 2022, 2023, 2024 and 2025 using only the data available **before** each predicted year.
- In each commodity and target, models are ranked by mean absolute percentage error across the available selection years. The two best are averaged as 65% best and 35% second-best.
- For the **independent 2025 holdout demonstration**, model types are selected using 2022–2024 backtest results **only**, and forecast 2025 with data through 2024. They are compared to actual published 2025 quantities.
- For the final **2026 prospective forecast**, the updated model selection may use all four backtest years 2022–2025, and models train on full 2017–2025 history.
- Holdout utilization evaluation uses the **actual historical inferred 2025 population** to isolate per-capita utilization-model error. It therefore does **not** validate a prospective 2025 population forecast.

Evaluation metric:

`WAPE = 100 × Σ|forecast − actual| / Σ|actual|`

| Genuine 2025 holdout, 15 commodities | Blend WAPE | Last-year baseline WAPE |
|---|---:|---:|
| Total domestic utilization | 3.73% | **2.82%** |
| Production | 5.47% | **5.39%** |

**Interpretation:** the model blend is **worse than persistence** in this holdout. This is an important empirical limitation, disclosed to judges. We do not assert that ML improves accuracy. Further work should add higher-frequency seasonal agricultural statistics and more independent prospective evaluation years.

The evaluation uses an aggregate WAPE weighted toward high-volume commodities, and performance on small or volatile crops may be much worse. Per-crop errors are provided in `data/validation_2025.csv` and the app's **Forecast checks** tab.

## Uncertainty and classification

The app uses **heuristic ranges** motivated by five years of observed annual changes, not statistically calibrated confidence/prediction intervals. For each commodity and series, the fractional band is:

`clip(0.08 + 0.65 × SD(annual percentage changes), 0.10, 0.45)`

Bounds are estimated production/utilization multiplied by `(1 ± fractional band)`. We label it an **indicative range** and explicitly state that it cannot support statements such as “there is an 80% probability of a shortage”.

- *Below use across indicative range:* even the high production bound lies below the low utilization bound.
- *Above use across indicative range:* even the low production bound exceeds the high utilization bound.
- *Overlap / uncertain:* neither condition is met.

These categories describe only the simplified production-to-use **accounting comparison**. They do not identify observed shortages, marketable surpluses or import quantities.

## Interactive scenarios

1. **Population growth (%):** changes the projected human-food use portion, holding other use forecasts fixed.
2. **Production change (%):** hypothetical increase/decrease in forecast production, applied to all commodities or one selected commodity; it does not claim a real projected drought or productivity intervention.
3. **Loss reduction (%):** reduces projected total utilization by the selected share of the mean annual *NISR-recorded loss quantity* in 2023–2025, per commodity. This represents a stylized reduction in reported production-to-retail supply-chain losses; it is not an evaluated intervention nor a forecast of savings for households.

Scenarios are arithmetic what-if analyses. They are not causal impact estimates.

## Main methodological limitations

1. **Very short annual time series:** 9 observations/crop, limited precision; statistical and ML forecasts are sensitive to shocks.
2. **No prospective trade-and-stock forecasting:** domestic utilization can exceed production without an actual shortage because imported goods or stock withdrawals may bridge the gap.
3. **National average and commodity-product categories:** the reports are not disaggregated to seasonal or district-level conditions, and some groups are in processed equivalents (e.g., milled rice).
4. **Incomplete forward production drivers:** no 2026 rainfall, cultivated area, fertilizer, irrigation, price or seasonal data are modeled.
5. **Population assumption:** historical denominator is inferred from FBS and future growth is user-adjusted; official NISR demographic projections should replace it.
6. **2024 population anomaly:** the report header appears internally inconsistent; see data sources.
7. **Loss measurement:** recorded FBS loss is not a comprehensive measure of consumer retail/household waste.
8. **Holdout results:** the simplest baseline is slightly stronger; do not market the method as superior AI accuracy.
9. **Uncalibrated ranges:** do not use planning bands for a probability statement or production procurement decision without additional evidence.

## Future improvements beyond hackathon prototype

Add NISR Seasonal Agricultural Survey crop/season observations, official population projections, MINAGRI prices and trade statistics, climate indicators and validated district crop production. Evaluate across more years and seasons, quantify probabilistic calibration, and interview user institutions before policy use.
