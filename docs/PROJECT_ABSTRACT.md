# CropBalance Rwanda — competition abstract

**Track:** 1 — Agricultural Productivity  
**Team:** [EXACT REGISTERED TEAM NAME]  
**Year:** 2026  
**Project status:** working student research prototype, not a nationally endorsed forecasting service

## Problem

Agricultural planning requires an understanding of how expected production may compare with national domestic utilization of food crops, particularly where trade, storage and losses complicate the picture. Rwanda's NISR Food Balance Sheets provide detailed annual statistics, yet these data are not always accessible to users as an interactive forward-looking planning tool.

## Proposed solution

CropBalance Rwanda is an interactive Streamlit dashboard that converts 2017–2025 NISR Food Balance Sheet data into a transparent 2026 outlook for 15 selected agricultural and food commodities. Users can compare estimated domestic production with total domestic utilization, investigate historical trends and utilization components, download results and simulate hypothetical production, population and food-loss scenarios.

## Data and analysis

We extracted and reconciled 135 commodity-year records from four NISR publications, preserving source page references. We model per-capita human food availability, other domestic uses and production using several annual forecasting approaches, including a pooled random-forest benchmark. We show transparent 2025 holdout validation and report that a simple last-year baseline outperformed our model blend in that test. Indicative uncertainty ranges are explicitly labeled as non-calibrated. The tool avoids confusing a production-to-utilization gap with an actual food shortage.

## Practical value

The prototype could help public agricultural planners, cooperatives and researchers identify commodities for deeper investigation, explore storage and production scenarios, and communicate national supply-utilization trends. Actual interventions require seasonal, geographic, trade and stock data beyond the present model.

## Alignment to Rwandan priorities

The project supports the evidence-based agricultural productivity and post-harvest management agenda in NISR's **2026 hackathon Track 1**, with broad alignment to **NST2**, **Vision 2050** and the agricultural transformation themes of **PSTA 5**: modernizing production, climate resilience, inclusive markets and post-harvest management.

## Deliverables

Public source repository; deployed Streamlit application; source-derived data tables; model, validation and scenario scripts; documentation of limitations and citations; originality and AI-use declaration.

### Sources

- [NISR, 2026 Hackathon Competition](https://statistics.gov.rw/about/hackathon/2026-hackathon-competition)
- NISR, *Rwanda Food Balance Sheets 2017–2021* (May 2023), *2022* (September 2023), *2023–2024* (September 2025), and *2025* (September 2026).
- [MINAGRI, PSTA 5 Abridged Version](https://www.minagri.gov.rw/fileadmin/user_upload/Minagri/Publications/Policies_and_strategies/PSTA_5_Abridged_version_Final.pdf)
