# NISR data sources and traceability

The project uses **only source data extracted from four original Rwanda Food Balance Sheet PDF reports supplied by the team**. National Institute of Statistics of Rwanda (NISR) is the data publisher. No district-level or farmer-specific datasets are used.

## Original PDFs used in extraction

| Years | NISR publication | Exact filename expected in a local `reports/` directory | PDF reader pages (1-indexed) |
|---|---|---|---|
| 2017–2021 | *Rwanda Food Balance Sheets 2017–2021* (May 2023) | `Rwanda Food Balance Sheets 2017-2021_Final.pdf` | 65–94; six commodity-table pages per year |
| 2022 | *Rwanda Food Balance Sheets Dashboard 2022* (Sept. 2023) | `Rwanda Food Balance Sheets 2022_Final_0.pdf` | 18–21 |
| 2023 | *Rwanda Food Balance Sheets 2023–2024* (Sept. 2025), Annex 2A | `Rwanda_Food_Balace Sheet_2023_24_.pdf` | 34–36 |
| 2024 | Same 2023–2024 report, Annex 1A | `Rwanda_Food_Balace Sheet_2023_24_.pdf` | 24–26 |
| 2025 | *Rwanda Food Balance Sheets 2025* (Sept. 2026), Annex 1 | `Food Balance Sheets 2025 Report.pdf` | 31–34 |

The above page numbers refer to the number displayed in a **PDF viewer**, not the section-specific printed page at the bottom of the report. The exact PDF page for every commodity-year row appears in `data/fbs_key_commodities_2017_2025.csv` as `source_pdf_page`.

## Rebuild the dataset

The original four reports are intentionally not included in the public ZIP to avoid duplicating large source documents. If you have the original PDFs, copy them to a folder named `reports` at the repository root, keeping the exact filenames above. Then, from a terminal at the repository root:

```bash
python -m pip install pandas PyMuPDF
python scripts/extract_fbs.py --reports-dir reports --output data/fbs_key_commodities_2017_2025.csv
```

The extractor checks for all 15 commodities across 9 years (135 rows). It validates the supply identity within rounding tolerance and checks a manually verified 2024 maize row:

> NISR FBS 2024, PDF page 24: maize production 627 kt, imports 250 kt, exports 196 kt, reported stock change 121 kt, domestic supply 559 kt.

It also validates the utilization balance. Differences of up to three thousand tonnes are tolerated because the original tables are rounded to whole thousand tonnes.

## Variables and methodology notes

- **Units:** `kt` means **1,000 metric tonnes**. `food_kt` is the amount allocated to human food in NISR's supply and utilization accounts. `per_capita_food_kg` refers to the report's food supply quantity per person per year, not observed intake in individual households.
- **Stock change:** follows the NISR convention: **production + imports − exports − stock changes = domestic supply**. Positive stock change is an accumulation; negative is a stock withdrawal.
- **Domestic utilization:** the sum of food, processing, feed, seed, recorded losses and other uses is approximately equal to domestic supply. Small differences reflect rounded published values.
- **Missing SSR and IDR:** the 2017–2021 annex does not report these columns in the selected extracted tables. They are left empty rather than invented; these columns appear from 2022 onward.
- **2024 population header:** the NISR 2023–2024 annex prints `13,500` (thousand) for **both** years. However, 2024 reported food volumes divided by published per-capita kg suggest roughly 13.8 million in 2024, versus roughly 13.5 million in 2023. This dataset does **not alter the published cells**. The model derives an approximate historical denominator from multiple higher-volume foods and explains it; official demographic projections should replace this approach in future work.
- **Categories:** rice is given in **milled equivalent**, groundnuts in **shelled equivalent**, and product groupings include processed products, as indicated by the NISR row labels. Values therefore should not be casually equated with raw-harvest mass.
- **NISR FBS losses:** reported loss quantities relate to the food-balance methodology and should **not** be presented as a comprehensive measure of retail and household food waste.
- **Source quality:** public official statistical reports, but their food-balance figures are estimated and may be revised. There are just nine annual observations per commodity.

## Attribution and reuse

Data source: © National Institute of Statistics of Rwanda. Published reports: *Rwanda Food Balance Sheets 2017–2021; 2022; 2023–2024; 2025*. Website: https://statistics.gov.rw/.

NISR's current website generally states **Creative Commons Attribution 4.0 (CC BY 4.0) unless otherwise indicated**, while individual publications may state other terms (e.g., the 2023–2024 report has its own copyright notice). The team must follow any report-specific conditions and the hackathon intellectual-property agreement. This project contains extracted selected figures with clear source attribution, not copies of the full PDF reports.
