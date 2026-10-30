"""Extract selected food-balance commodity rows from NISR annual report PDFs.

Usage (requires PyMuPDF):
    python -m pip install PyMuPDF pandas
    python scripts/extract_fbs.py --reports-dir reports --output data/fbs_key_commodities_2017_2025.csv

The four reports must have their original filenames. See docs/DATA_SOURCES.md.
All values retain NISR units, 1,000 metric tonnes unless specified otherwise.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path
import pandas as pd

CROPS = {
    "Maize": "Maize and products",
    "Rice (milled equivalent)": "Rice & Prod (Milled Equivalent)",
    "Sorghum": "Sorghum and products",
    "Wheat": "Wheat and products",
    "Dry beans": "Beans, Dry & Products",
    "Irish potatoes": "Potatoes and products",
    "Cassava": "Cassava and products",
    "Sweet potatoes": "Sweet potatoes",
    "Bananas": "Bananas",
    "Plantains": "Plantains",
    "Soybeans": "Soyabeans & Products",
    "Groundnuts": "Groundnuts (Shelled Eq)",
    "Tomatoes": "Tomatoes and products",
    "Onions": "Onions, Dry",
    "Milk (excluding butter)": "Milk - Excluding Butter",
}

# Pages 1-indexed and reflect exact printed PDF pages, not report-internal section numbering.
REPORT_RANGES = {
    2017: ("Rwanda Food Balance Sheets 2017-2021_Final.pdf", 65, 70, 15),
    2018: ("Rwanda Food Balance Sheets 2017-2021_Final.pdf", 71, 76, 15),
    2019: ("Rwanda Food Balance Sheets 2017-2021_Final.pdf", 77, 82, 15),
    2020: ("Rwanda Food Balance Sheets 2017-2021_Final.pdf", 83, 88, 15),
    2021: ("Rwanda Food Balance Sheets 2017-2021_Final.pdf", 89, 94, 15),
    2022: ("Rwanda Food Balance Sheets 2022_Final_0.pdf", 18, 21, 17),
    2023: ("Rwanda_Food_Balace Sheet_2023_24_.pdf", 34, 36, 17),
    2024: ("Rwanda_Food_Balace Sheet_2023_24_.pdf", 24, 26, 17),
    2025: ("Food Balance Sheets 2025 Report.pdf", 31, 34, 17),
}

COLS = [
    "production_kt", "imports_kt", "exports_kt", "stock_change_kt",
    "domestic_supply_kt", "processed_kt", "loss_kt", "feed_kt",
    "seed_kt", "other_kt", "food_kt", "per_capita_food_kg",
    "per_capita_calories_kcal_day", "per_capita_protein_g_day",
    "per_capita_fats_g_day", "reported_ssr_pct", "reported_idr_pct",
]
NUMBER = re.compile(r"^-?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?$")


def parse_number(text: str) -> float | None:
    text = text.strip().replace("\u00a0", "").replace("\u202f", "")
    if text in ("-", "–", "—"):
        return None
    if NUMBER.fullmatch(text):
        return float(text.replace(",", ""))
    raise ValueError(f"Expected a numeric cell, got {text!r}")


def extract(reports_dir: Path) -> pd.DataFrame:
    try:
        import fitz
    except ImportError as e:
        raise RuntimeError("Install PyMuPDF first: python -m pip install PyMuPDF") from e

    cache = {}
    out = []
    for year, (fname, start, end, ncols) in REPORT_RANGES.items():
        p = reports_dir / fname
        if fname not in cache:
            if not p.is_file():
                raise FileNotFoundError(f"Missing source PDF: {p}")
            cache[fname] = fitz.open(p)
        doc = cache[fname]
        rows = {}
        for page_num in range(start, end + 1):
            raw_lines = doc[page_num - 1].get_text(sort=False).splitlines()
            lines = [line.strip() for line in raw_lines if line.strip()]
            for key, raw_name in CROPS.items():
                for i, line in enumerate(lines):
                    if line == raw_name:
                        if key in rows:
                            raise ValueError(f"Duplicate {key} in year {year}")
                        cells = [parse_number(v) for v in lines[i + 1: i + 1 + ncols]]
                        if len(cells) != ncols:
                            raise ValueError(f"Truncated {key} row for year {year}")
                        row = dict(zip(COLS[:ncols], cells))
                        for c in COLS[ncols:]:
                            row[c] = None
                        row.update(year=year, commodity=key, original_item_name=raw_name,
                                   source_report=fname, source_pdf_page=page_num)
                        rows[key] = row
                        break
        missing = sorted(set(CROPS) - set(rows))
        if missing:
            raise ValueError(f"Year {year}: missing {missing}")
        out.extend(rows.values())

    df = pd.DataFrame(out)
    first = ["year", "commodity", "original_item_name"]
    last = ["source_report", "source_pdf_page"]
    df = df[first + COLS + last].sort_values(["commodity", "year"]).reset_index(drop=True)
    for col in COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def validate(df: pd.DataFrame) -> None:
    assert df.shape[0] == 15 * 9, (df.shape, 'Rows must cover 15 commodities x 9 years')
    assert not df.duplicated(["year", "commodity"]).any()
    for c in ["production_kt", "imports_kt", "exports_kt", "domestic_supply_kt", "food_kt", "loss_kt"]:
        assert df[c].notna().all(), f"Missing {c}"
        assert (df[c] >= 0).all(), f"Negative {c}"
    # NISR balances are reported rounded to thousand tonnes and may differ by 1-2 kt.
    supply_error = df.production_kt + df.imports_kt - df.exports_kt - df.stock_change_kt - df.domestic_supply_kt
    uses_error = (df.processed_kt + df.loss_kt + df.feed_kt + df.seed_kt + df.other_kt + df.food_kt) - df.domestic_supply_kt
    assert supply_error.abs().max() <= 3, f"Supply balance mismatch: {df.loc[supply_error.abs().idxmax()].to_dict()}"
    assert uses_error.abs().max() <= 3, f"Utilization balance mismatch: {df.loc[uses_error.abs().idxmax()].to_dict()}"
    # Reference row checked from original PDF (Rwanda FBS 2024, page 24).
    m = df[(df.year == 2024) & (df.commodity == "Maize")].iloc[0]
    assert [m.production_kt, m.imports_kt, m.exports_kt, m.stock_change_kt, m.domestic_supply_kt] == [627, 250, 196, 121, 559]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reports-dir", type=Path, default=Path("reports"))
    parser.add_argument("--output", type=Path, default=Path("data/fbs_key_commodities_2017_2025.csv"))
    args = parser.parse_args()
    result = extract(args.reports_dir)
    validate(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False, float_format="%.3f")
    print(f"Extracted {len(result)} validated rows to {args.output}")
    print("Covered years:", sorted(result.year.unique()))
    print("Covered commodities:", ", ".join(sorted(result.commodity.unique())))

if __name__ == "__main__":
    main()
