# CropBalance Rwanda

**Forecasting Agricultural Demand and Domestic Production Coverage in Rwanda**

**NISR 2026 Big Data Hackathon**  
**Track 1: Agricultural Productivity**

**Team:** AnyX  
**Team Members:**
- NAHIMANA Edwin Chancelin
- VIVI Nzembi Aggee Loic

**Institution:** Kigali Independent University (ULK)

## 1. Project Overview

CropBalance Rwanda is a data-driven agricultural forecasting platform designed to support better planning and decision-making in Rwanda's agricultural sector.

The platform uses historical data from the National Institute of Statistics of Rwanda (NISR) to estimate domestic agricultural utilization and production for 2026. By comparing these estimates, the system helps identify potential production gaps, areas of import dependence and opportunities for improved storage and post-harvest management.

Our aim is to make agricultural statistics more accessible and useful to farmers' cooperatives, researchers, agricultural planners and institutions involved in strengthening Rwanda's food security.

## 2. Problem Statement

Agricultural production and domestic food needs do not always grow at the same rate. Changes in population, production levels, trade and post-harvest losses can affect the balance between locally produced food and domestic utilization.

Although NISR publishes valuable agricultural statistics, interpreting historical trends and assessing future production needs requires additional analysis.

CropBalance Rwanda addresses this gap by bringing historical agricultural data, forecasting methods and interactive planning scenarios into one platform.

## 3. Main Features

The application provides four main functions:

**Agricultural Outlook for 2026**

Estimates domestic production and utilization for 15 selected agricultural commodities. Results include production coverage, estimated differences between production and utilization, uncertainty ranges and downloadable tables.

**Commodity Analysis**

Allows users to explore historical trends from 2017 to 2025, compare production and utilization patterns, and examine forecasts for individual commodities.

**Scenario Analysis**

Enables users to examine how changes in population growth, agricultural production and food losses could affect estimated production coverage.

**Forecast Evaluation**

Compares different forecasting approaches using historical data and evaluates their performance against actual observations.

## 4. Data Sources

The project uses publicly available Food Balance Sheet statistics published by the National Institute of Statistics of Rwanda.

The following reports were used:

- Rwanda Food Balance Sheets 2017–2021
- Rwanda Food Balance Sheets 2022
- Rwanda Food Balance Sheets 2023–2024
- Rwanda Food Balance Sheets 2025

The dataset covers nine years, from 2017 to 2025, with 135 commodity-year observations for 15 selected commodities.

The main variables include agricultural production, imports, exports, stock changes, domestic supply, food utilization, processing, feed, seed, reported losses and per-capita food availability.

All quantities are expressed in thousand metric tonnes unless otherwise specified.

Detailed data references and extraction methods are available in [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md).

## 5. Forecasting Methodology

The forecasting process combines historical agricultural utilization, production trends and population-related assumptions to estimate conditions for 2026.

The methodology follows five main stages:

1. **Data preparation:** Extract and organize relevant agricultural statistics from NISR Food Balance Sheet reports, including checks for missing values and consistency.
2. **Historical analysis:** Examine changes in production, domestic utilization, per-capita food availability and other relevant indicators between 2017 and 2025.
3. **Model development:** Apply four forecasting approaches: last-year baseline, three-year moving average, damped linear trend and pooled random-forest regression.
4. **Model evaluation:** Use historical rolling forecasts to assess prediction errors and select suitable forecasting methods. The two selected models are combined using weights of 65% and 35%.
5. **Scenario forecasting:** Estimate 2026 domestic utilization and production under adjustable population-growth and production assumptions.

The platform compares forecast domestic production with forecast domestic utilization to assess indicative production coverage.

These estimates represent national-level planning scenarios rather than verified food shortages or marketable surpluses. Actual food availability also depends on imports, exports, stock changes and other market conditions.

### Model Performance

Forecast performance was evaluated using 2025 as a holdout year.

| Indicator | Model blend | Last-year baseline |
|---|---:|---:|
| Domestic utilization WAPE | 3.73% | 2.82% |
| Production WAPE | 5.47% | 5.39% |

*WAPE: Weighted Absolute Percentage Error. Lower values indicate smaller prediction errors.*

The last-year baseline achieved slightly lower errors than the blended model in this evaluation. This highlights the importance of comparing forecasting approaches rather than relying on model complexity alone.

Given the limited number of annual observations, the platform emphasizes transparent estimates, scenario analysis and clear communication of uncertainty.

Further methodological details are provided in [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md).

## 6. Technology Stack

CropBalance Rwanda was developed using the following technologies:

| Technology | Application |
|---|---|
| Python | Data processing and forecasting |
| Streamlit | Interactive web application |
| pandas and NumPy | Data preparation and analysis |
| scikit-learn | Machine learning and model evaluation |
| Altair | Data visualization |
| PyMuPDF | Extraction of data from source reports |

## 7. Project Structure

The repository is organized as follows:

| File or folder | Description |
|---|---|
| `app.py` | Main Streamlit application |
| `requirements.txt` | Python dependencies |
| `src/engine.py` | Forecasting, validation and scenario calculations |
| `data/` | Historical NISR data and forecast outputs |
| `scripts/` | Data extraction, processing and verification scripts |
| `tests/` | Automated tests |
| `docs/DATA_SOURCES.md` | Data sources and references |
| `docs/METHODOLOGY.md` | Forecasting methodology |
| `docs/PROJECT_ABSTRACT.md` | Project summary |
| `docs/JUDGING_DEMO.md` | Application demonstration |
| `DECLARATION.md` | Project originality, attribution and development disclosures |

## 8. Running the Application

The application can be run locally using Python.

**Install the dependencies:**

```bash
python -m pip install -r requirements.txt
```

**Launch the application:**

```bash
python -m streamlit run app.py
```

The application is accessible locally at:

`http://localhost:8501`

The forecast outputs can be reproduced by running:

```bash
python scripts/build_outputs.py
```

## 9. Relevance to National Priorities

CropBalance Rwanda addresses the NISR 2026 Big Data Hackathon's Agricultural Productivity track.

The project supports the broader objectives of Rwanda's National Strategy for Transformation 2 (NST2), Vision 2050 and the Fifth Strategic Plan for Agriculture Transformation (PSTA 5).

Its main areas of relevance include:

- Improving agricultural productivity and planning.
- Supporting evidence-based food security decisions.
- Identifying potential production and utilization imbalances.
- Informing post-harvest storage and loss-reduction strategies.
- Strengthening the practical use of national agricultural statistics.

## 10. Expected Contribution

CropBalance Rwanda provides a practical way to turn historical agricultural statistics into information that can support planning.

The platform is intended to help agricultural planners and other stakeholders better understand production trends, anticipate possible imbalances and evaluate alternative planning scenarios.

Its long-term potential includes supporting more efficient resource allocation, improved coordination across agricultural value chains and better-informed decisions on production, storage and food availability.

These outcomes depend on the availability of reliable data, continued model improvement and adoption by relevant stakeholders.

## 11. Limitations

The platform is a research prototype based on national annual statistics.

Its forecasts are exploratory estimates and should not be interpreted as official NISR forecasts or confirmed food shortages. The available historical series is relatively short, and forecasting uncertainty remains significant.

The current version does not provide farm-level or district-level production forecasts. Further development would benefit from additional agricultural survey data, weather information, commodity prices and more detailed geographical observations.

## 12. References and Acknowledgments

We acknowledge the National Institute of Statistics of Rwanda for making agricultural statistics publicly available and for organizing the 2026 Big Data Hackathon.

The project draws on NISR Food Balance Sheet publications covering 2017–2025. Additional references, software attribution and methodological documentation are included in the repository.

**Official references:**

- [National Institute of Statistics of Rwanda](https://statistics.gov.rw/)
- [NISR 2026 Big Data Hackathon](https://statistics.gov.rw/about/hackathon/2026-hackathon-competition)
- [Ministry of Agriculture and Animal Resources](https://www.minagri.gov.rw/)
- [Streamlit Documentation](https://docs.streamlit.io/)

---

**CropBalance Rwanda | Team AnyX | NISR Big Data Hackathon 2026**
