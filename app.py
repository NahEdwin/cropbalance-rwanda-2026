"""CropBalance Rwanda | NISR 2026 Big Data Hackathon.

Entry point for Streamlit Community Cloud: app.py
"""
from __future__ import annotations

from pathlib import Path
import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from src.engine import make_forecasts, scenario_forecasts, holdout_metrics

st.set_page_config(
    page_title="CropBalance Rwanda | 2026 crop outlook",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  .block-container {padding-top: 1.3rem; padding-bottom: 3.5rem; max-width: 1250px;}
  .hero {background:linear-gradient(110deg,#113b32,#215a48); padding:27px 30px;
         border-radius:18px; color:white; margin:7px 0 22px 0;}
  .hero h1 {color:#fff!important;font-size:2.15rem!important;letter-spacing:-.025em;margin:0 0 .25rem 0;}
  .hero p {color:#e0efe6!important;margin:0;font-size:1.05rem;max-width:940px;}
  .eyebrow {color:#a9ddbe!important;font-size:.76rem!important;font-weight:750;letter-spacing:.14em;}
  div[data-testid="stMetric"] {background:#f5f8f4; color:#1b2c27!important; padding:15px 18px; border:1px solid #e5ebe4; border-radius:13px;}
  div[data-testid="stMetricLabel"] {font-weight:600; color:#1b2c27!important;}
  div[data-testid="stMetricLabel"] *, div[data-testid="stMetricValue"], div[data-testid="stMetricValue"] * {color:#1b2c27!important;}
  .note {border-left:3px solid #35745c; padding:10px 14px; background:#f6f9f5; color:#1b2c27; border-radius:0 8px 8px 0;}
</style>
""", unsafe_allow_html=True)

ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "data" / "fbs_key_commodities_2017_2025.csv"

@st.cache_data(show_spinner="Building verified NISR forecasts and holdout validation…")
def load_and_model():
    source = pd.read_csv(DATA_FILE)
    engine = make_forecasts(source)
    return source, engine

source, engine = load_and_model()

st.markdown("""
<div class="hero">
  <div class="eyebrow">NISR BIG DATA HACKATHON 2026 | AGRICULTURAL PRODUCTIVITY</div>
  <h1>CropBalance Rwanda</h1>
  <p>2026 agricultural production and domestic utilization outlook using NISR Food Balance Sheet data. Compare commodities, examine forecasts and explore planning scenarios.</p>
</div>
""", unsafe_allow_html=True)
st.caption("National-level analysis | 15 selected commodities | Historical data: 2017-2025")

with st.sidebar:
    st.markdown("## Scenario lab")
    st.caption("Explore how population growth, production and food-loss assumptions affect the 2026 outlook.")
    population_growth = st.slider("Assumed 2026 population growth", 0.0, 4.0, 2.2, 0.1, format="%.1f%%",
                                  help="Scenario assumption applied to estimated human-food use; not an official population projection.")
    target_crop = st.selectbox("Apply production change to", ["All commodities"] + sorted(source.commodity.unique().tolist()))
    prod_change = st.slider("Production change relative to forecast", -30, 30, 0, 5, format="%d%%")
    loss_reduction = st.slider("Assumed reduction in recorded food losses", 0, 50, 0, 5, format="%d%%",
                               help="Scenario assumption, not an observed change in losses.")
    st.divider()
    st.markdown("**Data and forecast**")
    st.caption("Source: NISR Food Balance Sheets, 2017-2025. Quantities are in thousand metric tonnes (kt).")
    st.caption("Models: persistence, 3-year mean, damped trend and pooled random forest; chosen with rolling backtests.")
    st.caption("Forecast ranges are indicative and not calibrated confidence intervals.")

outlook = scenario_forecasts(engine, population_growth, prod_change, loss_reduction, target_crop)
by_crop = outlook.set_index("commodity")
metrics = holdout_metrics(engine["holdout_2025"])

c1, c2, c3, c4 = st.columns(4)
c1.metric("Selected commodities", len(outlook))
c2.metric("2026 population scenario", f"{float(outlook.assumed_population_2026_millions.iloc[0]):.2f}M")
c3.metric("2026 production coverage", f"{100*outlook.production_2026_kt.sum()/outlook.utilization_2026_kt.sum():.0f}%")
c4.metric("2026 domestic utilization", f"{outlook.utilization_2026_kt.sum():,.0f} kt")

st.caption("Production coverage and domestic utilization totals refer to the 15 selected commodities.")

view1, view2, view3, view4 = st.tabs([
    "National outlook", "Commodity explorer", "Forecast checks", "Data & method"
])

with view1:
    st.markdown("### Production relative to estimated domestic use, 2026")
    st.caption("Negative values indicate production below estimated domestic utilization. Trade and stock changes also affect food availability.")
    chart_df = outlook[["commodity", "production_minus_use_kt"]].copy()
    chart_df["direction"] = np.where(chart_df.production_minus_use_kt >= 0, "Above estimated use", "Below estimated use")
    barchart = alt.Chart(chart_df).mark_bar(cornerRadiusEnd=3).encode(
        y=alt.Y("commodity:N", sort=alt.SortField(field="production_minus_use_kt", order="ascending"), title=None, axis=alt.Axis(labelLimit=230)),
        x=alt.X("production_minus_use_kt:Q", title="Production minus estimated domestic utilization (thousand metric tonnes)"),
        color=alt.Color("direction:N", scale=alt.Scale(domain=["Below estimated use", "Above estimated use"], range=["#bc5d39", "#2c8067"]), legend=None),
        tooltip=[alt.Tooltip("commodity:N", title="Commodity"),
                 alt.Tooltip("production_minus_use_kt:Q", title="Difference (kt)", format="+,.1f")],
    ).properties(height=445)
    st.altair_chart(barchart, use_container_width=True)

    st.markdown("#### Commodity-level outlook for 2026")
    show = outlook[["commodity", "production_2026_kt", "utilization_2026_kt", "production_minus_use_kt", "coverage_pct", "assessment"]].copy()
    show = show.rename(columns={"commodity":"Commodity", "production_2026_kt":"Production (kt)",
                                "utilization_2026_kt":"Domestic use (kt)", "production_minus_use_kt":"Production - use (kt)",
                                "coverage_pct":"Coverage (%)", "assessment":"Indicative assessment"})
    st.dataframe(show, use_container_width=True, hide_index=True, column_config={
        "Production (kt)": st.column_config.NumberColumn(format="%.1f"),
        "Domestic use (kt)": st.column_config.NumberColumn(format="%.1f"),
        "Production - use (kt)": st.column_config.NumberColumn(format="%+.1f"),
        "Coverage (%)": st.column_config.NumberColumn(format="%.1f%%"),
    })
    st.download_button("Download 2026 scenario as CSV", outlook.to_csv(index=False).encode("utf-8"),
                       file_name="cropbalance_2026_scenario.csv", mime="text/csv", key="download_outlook")

    st.markdown("#### Planning implications")
    left, right = st.columns(2)
    with left:
        st.markdown("**When domestic production is below modeled use**")
        st.write("Planners might review imports, seasonal crop yields, access to seed and inputs, storage capacity, and how food is allocated between household use, processing and feed.")
    with right:
        st.markdown("**When modeled production exceeds use**")
        st.write("Cooperatives and planners could explore storage, processing and marketing options, after checking expected trade flows, geographic distribution and seasonal timing.")
    st.caption("Production-use differences do not independently establish import requirements, food shortages or marketable surpluses.")

with view2:
    st.markdown("### Explore one commodity")
    selected = st.selectbox("Commodity", sorted(source.commodity.unique().tolist()), index=5)
    s = by_crop.loc[selected]
    hist = engine["history"][engine["history"].commodity == selected].sort_values("year")

    d1, d2, d3, d4 = st.columns(4)
    d1.metric("2026 production", f"{s.production_2026_kt:,.0f} kt")
    d2.metric("2026 estimated use", f"{s.utilization_2026_kt:,.0f} kt")
    d3.metric("Production - use", f"{s.production_minus_use_kt:+,.0f} kt")
    d4.metric("Production coverage", f"{s.coverage_pct:,.0f}%")

    hlong = hist[["year", "production_kt", "domestic_supply_kt"]].melt(
        id_vars="year", value_vars=["production_kt", "domestic_supply_kt"],
        var_name="series", value_name="kt")
    hlong["series"] = hlong.series.map({"production_kt":"Production", "domestic_supply_kt":"Domestic utilization"})
    fpoints = pd.DataFrame({"year": [2026, 2026], "series": ["Production", "Domestic utilization"],
                            "kt": [s.production_2026_kt, s.utilization_2026_kt]})
    lines_all = pd.concat([hlong, fpoints], ignore_index=True)
    hue = alt.Scale(domain=["Production", "Domestic utilization"], range=["#2b795b", "#c48d41"])
    lines = alt.Chart(lines_all).mark_line(point=True, strokeWidth=2.5).encode(
        x=alt.X("year:O", title="Year", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("kt:Q", title="Thousand metric tonnes (kt)", scale=alt.Scale(zero=False)),
        color=alt.Color("series:N", scale=hue, title=None),
        tooltip=["series:N", "year:O", alt.Tooltip("kt:Q", format=",.1f")],
    )
    bands = pd.DataFrame({
        "series":["Production", "Domestic utilization"],
        "year":[2026, 2026],
        "lower":[s.production_low_kt, s.utilization_low_kt],
        "upper":[s.production_high_kt, s.utilization_high_kt],
    })
    rules = alt.Chart(bands).mark_rule(strokeWidth=6, opacity=.35).encode(
        x=alt.X("year:O"), y=alt.Y("lower:Q"), y2="upper:Q", color=alt.Color("series:N",scale=hue),
        tooltip=["series:N", alt.Tooltip("lower:Q", format=",.1f"), alt.Tooltip("upper:Q", format=",.1f")],
    )
    st.altair_chart((rules + lines).properties(height=350), use_container_width=True)
    st.caption("2017-2025: observed NISR statistics | 2026: modeled scenario | Forecast ranges are indicative, not calibrated confidence intervals.")

    if s.assessment == "Below use across indicative range":
        summary = "Domestic production is projected below total domestic utilization across the indicative ranges. Consider productivity, trade and stock planning."
    elif s.assessment == "Above use across indicative range":
        summary = "Modeled production exceeds utilization across the indicative ranges. Review storage, trade and processing possibilities."
    else:
        summary = "The indicative production and utilization ranges overlap; the direction of the gap is uncertain."
    st.markdown(f"<div class='note'><strong>Planning interpretation:</strong> {summary}</div>", unsafe_allow_html=True)

    sub1, sub2 = st.columns([1.15, 1])
    with sub1:
        st.markdown("#### 2025 domestic-use components")
        last = hist.iloc[-1]
        components = pd.DataFrame({"Component":["Food", "Processing", "Loss", "Feed", "Seed", "Other uses"],
                                   "kt":[last.food_kt, last.processed_kt, last.loss_kt, last.feed_kt, last.seed_kt, last.other_kt]})
        components = components[components.kt > 0]
        if len(components):
            pie = alt.Chart(components).mark_arc(innerRadius=65).encode(
                theta=alt.Theta("kt:Q"), color=alt.Color("Component:N"),
                tooltip=["Component:N", alt.Tooltip("kt:Q", title="Volume (kt)", format=",.0f")]
            ).properties(height=280)
            st.altair_chart(pie, use_container_width=True)
        st.caption("Rounded published components can differ slightly from total use. Negative residual/other-use entries are omitted from the pie.")
    with sub2:
        st.markdown("#### Model transparency")
        st.write(f"**Production:** {s.production_selected_models}")
        st.write(f"**Per-capita food:** {s.percap_selected_models}")
        st.write(f"**Other domestic uses:** {s.nonfood_selected_models}")
        st.write(f"**Reference annual recorded loss:** {s.loss_reference_kt:,.1f} kt (2023–2025 mean)")
        st.write(f"**Selected scenario population:** {s.assumed_population_2026_millions:,.2f} million")
        st.caption("Models are selected by one-year-ahead error in 2022–2025; the pooled random forest competes against three statistical baselines.")

with view3:
    st.markdown("### Forecast validation against 2025 observations")
    st.write("Forecasts for 2025 were generated from **2017-2024 data**, with model selection based on earlier backtests. Predictions were then compared against NISR's published 2025 figures.")
    v1, v2, v3, v4 = st.columns(4)
    v1.metric("Use error | blended", f"{metrics['use_wape_pct']:.1f}%")
    v2.metric("Use error | baseline", f"{metrics['use_baseline_wape_pct']:.1f}%")
    v3.metric("Production error | blended", f"{metrics['production_wape_pct']:.1f}%")
    v4.metric("Production error | baseline", f"{metrics['production_baseline_wape_pct']:.1f}%")
    st.info("The last-year baseline achieved lower errors than the blended model in the 2025 validation. Both results are presented to support model comparison.")
    st.caption("Error metric: weighted absolute percentage error (WAPE); lower is better. The domestic-use evaluation uses observed 2025 implied population to isolate model error and does not assess population-forecast accuracy.")

    val = engine["holdout_2025"].copy()
    t = st.radio("Choose measure", ["Domestic utilization", "Production"], horizontal=True)
    if t == "Domestic utilization":
        x, y, bas = "actual_use_kt", "pred_use_kt", "baseline_use_kt"
    else:
        x, y, bas = "actual_production_kt", "pred_production_kt", "baseline_production_kt"
    vlong = val[["commodity", x, y, bas]].rename(columns={x:"Observed", y:"Forecast blend", bas:"Last-year baseline"}).melt(
        id_vars="commodity", var_name="Series", value_name="kt")
    selected_comp = st.selectbox("Check a commodity", sorted(val.commodity.tolist()), index=5)
    vc = vlong[vlong.commodity == selected_comp]
    st.altair_chart(alt.Chart(vc).mark_bar().encode(x=alt.X("Series:N", title=None, axis=alt.Axis(labelAngle=0)),
        y=alt.Y("kt:Q", title="Thousand metric tonnes (kt)"), color="Series:N",
        tooltip=["Series:N",alt.Tooltip("kt:Q", format=",.1f")]).properties(height=265), use_container_width=True)
    st.dataframe(val[["commodity", "actual_use_kt", "pred_use_kt", "actual_production_kt", "pred_production_kt", "use_abs_pct_error", "production_abs_pct_error"]].round(2),
                 use_container_width=True, hide_index=True)
    st.download_button("Download 2025 holdout test", val.to_csv(index=False).encode("utf-8"),
                       file_name="cropbalance_2025_holdout.csv", mime="text/csv", key="download_validation")

with view4:
    st.markdown("### Sources and reproducibility")
    st.caption("The 2026 outlook consists of scenario-based estimates for planning, not official NISR projections.")
    st.markdown("""
    **Primary sources:** National Institute of Statistics of Rwanda (NISR),
    *Rwanda Food Balance Sheets 2017–2021* (May 2023),
    *Rwanda Food Balance Sheets Dashboard 2022* (September 2023),
    *Rwanda Food Balance Sheets 2023–2024* (September 2025), and
    *Rwanda Food Balance Sheets 2025* (September 2026).

    The `data/` folder contains transcribed annual commodity records. `scripts/extract_fbs.py`
    reproduces the extraction from the original PDFs; `src/engine.py` contains all forecasting logic.
    Refer to `docs/DATA_SOURCES.md` for the exact PDF page locations.

    **Forecast recipe:** Three basic annual methods and a pooled random forest are
    compared on one-year-ahead historical years. We estimate per-capita human food use,
    non-food domestic utilization and production separately. Estimated 2026 population
    is an **editable assumption**, not an official population projection.
    """)
    st.latex(r"\text{Modeled domestic use}_{2026}=\text{Food kg/cap}_{2026}\times\text{Population (millions)}_{2026}+\text{Other uses (kt)}_{2026}")
    st.latex(r"\text{Production coverage (\%)}=100\times\frac{\text{Domestic production}}{\text{Domestic utilization}}")
    st.caption("With food supply in kg/person/year and population in millions, their product is thousand metric tonnes (kt).")
    st.markdown("#### Main limitations")
    st.markdown("""
    - Nine annual observations per commodity do not support reliable long-horizon ML or district-level predictions.
    - Trade, stocks and geographic distribution are not modeled prospectively. Lower domestic production than utilization is **not** a verified food shortage.
    - The uncertainty bands are heuristic and must not be interpreted as calibrated prediction intervals.
    - The 2024 FBS population header appears inconsistent with commodity quantities divided by per-capita use. We derive implied population and disclose the discrepancy.
    - Crop processing equivalence matters (e.g., rice is reported in milled equivalent); compare categories with care.
    - The analysis uses national statistics and does not estimate individual household demand or specific farm harvests.
    - Model comparisons include a pooled ML benchmark, but the holdout shows that the statistical baseline can be stronger.
    """)
    st.download_button("Download cleaned NISR history", source.to_csv(index=False).encode("utf-8"),
                       file_name="cropbalance_nisr_2017_2025.csv", mime="text/csv", key="download_history")
    st.caption("Source attribution: © National Institute of Statistics of Rwanda. NISR website generally states CC BY 4.0 unless otherwise indicated. Source report terms should also be respected.")
    st.caption("Implementation: Python, Streamlit, pandas, Altair, NumPy and scikit-learn. Source attribution and development disclosures are available in the repository documentation.")

st.divider()
st.caption("CropBalance Rwanda | Team AnyX | NISR Big Data Hackathon 2026 | Data: NISR Food Balance Sheets (2017-2025)")
