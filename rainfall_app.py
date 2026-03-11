"""
Rainfall Analysis Tool — Streamlit Web App
Fetches data from the SILO API and runs rolling window frequency analysis.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import urllib.request
import urllib.parse
from io import StringIO
from datetime import datetime, date

# ── page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Rainfall Analysis",
    page_icon="🌧️",
    layout="wide",
)

# ── custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

/* ── global reset ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* ── app background ── */
.stApp {
    background-color: #f0f4f8;
}

/* ── hide default streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}

/* ── custom header banner ── */
.app-header {
    background: #0f2744;
    border-radius: 12px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    display: flex;
    align-items: center;
    gap: 1.2rem;
}
.app-header-icon {
    font-size: 2.4rem;
    line-height: 1;
}
.app-header-title {
    color: #ffffff;
    font-size: 1.7rem;
    font-weight: 600;
    letter-spacing: -0.02em;
    margin: 0;
}
.app-header-sub {
    color: #7ea8cc;
    font-size: 0.85rem;
    font-weight: 400;
    margin: 0;
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

/* ── section cards ── */
.section-card {
    background: #ffffff;
    border: 1px solid #dde5ee;
    border-radius: 10px;
    padding: 1.6rem 2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 1px 4px rgba(15,39,68,0.06);
}
.section-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #7ea8cc;
    font-family: 'DM Mono', monospace;
    margin-bottom: 0.2rem;
}
.section-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #0f2744;
    margin-bottom: 1.2rem;
    letter-spacing: -0.01em;
}

/* ── stat chips ── */
.stat-row {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    margin-top: 1rem;
}
.stat-chip {
    background: #eef3f9;
    border: 1px solid #d0dcea;
    border-radius: 8px;
    padding: 0.55rem 1rem;
    font-size: 0.82rem;
    color: #0f2744;
    font-family: 'DM Mono', monospace;
}
.stat-chip span {
    font-weight: 600;
    color: #1a5fa8;
}

/* ── divider ── */
.section-divider {
    border: none;
    border-top: 1px solid #dde5ee;
    margin: 1.5rem 0;
}

/* ── inputs ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    border: 1px solid #c8d8e8 !important;
    border-radius: 7px !important;
    background: #f7fafd !important;
    font-family: 'DM Sans', sans-serif !important;
    color: #0f2744 !important;
    font-size: 0.9rem !important;
    padding: 0.5rem 0.75rem !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: #1a5fa8 !important;
    box-shadow: 0 0 0 3px rgba(26,95,168,0.12) !important;
}
.stSelectbox > div > div {
    border: 1px solid #c8d8e8 !important;
    border-radius: 7px !important;
    background: #f7fafd !important;
    font-family: 'DM Sans', sans-serif !important;
    color: #0f2744 !important;
}
.stDateInput > div > div > input {
    border: 1px solid #c8d8e8 !important;
    border-radius: 7px !important;
    background: #f7fafd !important;
}

/* ── labels ── */
label, .stSelectbox label, .stTextInput label,
.stNumberInput label, .stDateInput label {
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    color: #4a6580 !important;
    letter-spacing: 0.01em !important;
    margin-bottom: 0.15rem !important;
}

/* ── buttons ── */
.stButton > button {
    border-radius: 7px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    padding: 0.5rem 1.2rem !important;
    transition: all 0.15s ease !important;
    border: 1px solid #c8d8e8 !important;
    background: #ffffff !important;
    color: #0f2744 !important;
}
.stButton > button:hover {
    background: #eef3f9 !important;
    border-color: #1a5fa8 !important;
    color: #1a5fa8 !important;
}
.stButton > button[kind="primary"] {
    background: #0f2744 !important;
    color: #ffffff !important;
    border-color: #0f2744 !important;
}
.stButton > button[kind="primary"]:hover {
    background: #1a5fa8 !important;
    border-color: #1a5fa8 !important;
    color: #ffffff !important;
}

/* ── alerts ── */
.stSuccess {
    border-radius: 8px !important;
    border-left: 4px solid #2e8b57 !important;
    background: #f0faf4 !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stInfo {
    border-radius: 8px !important;
    border-left: 4px solid #1a5fa8 !important;
    background: #eef3f9 !important;
}
.stWarning {
    border-radius: 8px !important;
    border-left: 4px solid #c8811a !important;
}
.stError {
    border-radius: 8px !important;
    border-left: 4px solid #c0392b !important;
}

/* ── download button ── */
.stDownloadButton > button {
    border-radius: 7px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.82rem !important;
    background: #f0f4f8 !important;
    border: 1px dashed #a0b8cc !important;
    color: #0f2744 !important;
    letter-spacing: 0.02em !important;
}
.stDownloadButton > button:hover {
    background: #dde5ee !important;
    border-color: #1a5fa8 !important;
}

/* ── subheader overrides ── */
h2 { color: #0f2744 !important; font-weight: 600 !important; letter-spacing: -0.02em !important; }
h3 { color: #0f2744 !important; font-weight: 500 !important; font-size: 0.95rem !important; }
</style>
""", unsafe_allow_html=True)

MONTHS = ["Jan","Feb","Mar","Apr","May","Jun",
          "Jul","Aug","Sep","Oct","Nov","Dec"]

# ── helpers ───────────────────────────────────────────────────────────────────

def silo_search(frag, email):
    url = (f"https://www.longpaddock.qld.gov.au/cgi-bin/silo/"
           f"PatchedPointDataset.php?format=name&nameFrag="
           f"{urllib.parse.quote(frag)}&username={urllib.parse.quote(email)}")
    with urllib.request.urlopen(url, timeout=15) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    stations = []
    for line in raw.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "|" not in line:
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 2:
            continue
        try:
            sid   = int(parts[0])
            name  = parts[1].strip()
            state = parts[4].strip() if len(parts) > 4 else ""
            lat   = parts[2].strip() if len(parts) > 2 else ""
            lon   = parts[3].strip() if len(parts) > 3 else ""
            label = f"{name}"
            if state: label += f"  [{state}]"
            if lat and lon: label += f"  ({lat}, {lon})"
            stations.append({"id": sid, "name": name, "label": label})
        except ValueError:
            continue
    return stations


def silo_fetch(station_id, start, end, email):
    url = (f"https://www.longpaddock.qld.gov.au/cgi-bin/silo/"
           f"PatchedPointDataset.php"
           f"?station={station_id}"
           f"&start={start}&finish={end}"
           f"&format=csv&comment=R"
           f"&username={urllib.parse.quote(email)}")
    with urllib.request.urlopen(url, timeout=60) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    return raw


def parse_silo(text):
    lines = text.splitlines()
    header_idx = None
    for i, line in enumerate(lines):
        low = line.lower()
        if "daily_rain" in low or ("date" in low and "rain" in low and "," in low):
            header_idx = i
            break
    if header_idx is not None:
        df = pd.read_csv(StringIO("\n".join(lines[header_idx:])), comment="#")
        df.columns = [c.strip().lower().split("(")[0].strip() for c in df.columns]
        date_col = next((c for c in df.columns
                         if c.startswith("date") or "yyyy" in c), None)
        rain_col = next((c for c in df.columns
                         if "rain" in c and "source" not in c and "quality" not in c), None)
        if date_col is None or rain_col is None:
            raise ValueError(f"Could not find date/rain columns. Found: {list(df.columns)}")
        df["date"] = pd.to_datetime(df[date_col], errors="coerce")
        df = df.dropna(subset=["date"])
        df["year"] = df["date"].dt.year
        df = df.rename(columns={rain_col: "rain"})
        df["rain"] = pd.to_numeric(df["rain"], errors="coerce").fillna(0.0)
        df.loc[df["rain"] < 0, "rain"] = 0.0
        return df.sort_values("date").reset_index(drop=True)
    h = next(i for i, l in enumerate(lines) if "date" in l.lower() and "rain" in l.lower())
    cols = lines[h].split()
    data = [l for l in lines[h+1:] if l.strip() and not l.startswith("#")]
    df = pd.read_csv(StringIO("\n".join(data)), sep=r"\s+", names=cols, header=None)
    df["date"] = pd.to_datetime(df["date"].astype(str), format="%Y%m%d", errors="coerce")
    df = df.dropna(subset=["date"])
    df["year"] = df["date"].dt.year
    rain_col = next(c for c in df.columns if c.lower() == "rain")
    df = df.rename(columns={rain_col: "rain"})
    df["rain"] = pd.to_numeric(df["rain"], errors="coerce").fillna(0.0)
    df.loc[df["rain"] < 0, "rain"] = 0.0
    return df.sort_values("date").reset_index(drop=True)


def assign_season_year(df, sm, sd, em, ed):
    df = df.copy()
    mo = df["date"].dt.month
    dy = df["date"].dt.day
    yr = df["date"].dt.year
    crosses = (sm > em) or (sm == em and sd > ed)
    after_start = (mo > sm) | ((mo == sm) & (dy >= sd))
    before_end  = (mo < em) | ((mo == em) & (dy <= ed))
    if not crosses:
        mask = after_start & before_end
    else:
        mask = after_start | before_end
    df = df[mask].copy()
    mo2, dy2, yr2 = df["date"].dt.month, df["date"].dt.day, df["date"].dt.year
    if crosses:
        after = (mo2 > sm) | ((mo2 == sm) & (dy2 >= sd))
        df["season_year"] = np.where(after, yr2, yr2 - 1)
    else:
        df["season_year"] = yr2
    return df


def season_label(sm, sd, em, ed):
    return f"{sd} {MONTHS[sm-1]} – {ed} {MONTHS[em-1]}"


# ── session state ─────────────────────────────────────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = None
if "station_name" not in st.session_state:
    st.session_state.station_name = None
if "stations" not in st.session_state:
    st.session_state.stations = []

# ── header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <div class="app-header-icon">🌧️</div>
  <div>
    <p class="app-header-title">Rainfall Analysis Tool</p>
    <p class="app-header-sub">Australian SILO Climate Data · Rolling Window Frequency Analysis</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 — FETCH DATA
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="section-card">
  <p class="section-label">Step 01</p>
  <p class="section-title">Connect to SILO & Load Station Data</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])
with col1:
    email = st.text_input(
        "Email address",
        placeholder="you@example.com",
        help="Required by SILO as an API key per their terms of use."
    )
with col2:
    search_term = st.text_input(
        "Search station",
        placeholder="e.g. Cairns, Townsville, Darwin",
        help="Enter part of a station name to search"
    )

col_date1, col_date2, col_gap = st.columns([1, 1, 1])
with col_date1:
    start_date = st.date_input("Start date", value=date(1990, 1, 1), min_value=date(1889, 1, 1))
with col_date2:
    end_date = st.date_input("End date", value=date.today())

st.write("")
if st.button("🔍  Search Stations", disabled=not (email and search_term)):
    if "@" not in email:
        st.error("Please enter a valid email address.")
    else:
        with st.spinner(f"Searching for stations matching '{search_term}'…"):
            try:
                stations = silo_search(search_term, email)
                st.session_state.stations = stations
                if not stations:
                    st.warning("No stations found. Try a shorter term (e.g. 'Cairn' instead of 'Cairns Airport').")
            except Exception as e:
                st.error(f"Search failed: {e}")

# Station picker
if st.session_state.stations:
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.success(f"**{len(st.session_state.stations)}** station(s) found")
    labels = [s["label"] for s in st.session_state.stations]
    selected_label = st.selectbox("Select a station", labels)
    selected_station = next(s for s in st.session_state.stations if s["label"] == selected_label)

    st.write("")
    if st.button("⬇️  Fetch Rainfall Data"):
        start_str = start_date.strftime("%Y%m%d")
        end_str   = end_date.strftime("%Y%m%d")
        with st.spinner(f"Fetching data for {selected_station['name']}…"):
            try:
                raw = silo_fetch(selected_station["id"], start_str, end_str, email)
                df  = parse_silo(raw)
                st.session_state.df = df
                st.session_state.station_name = selected_station["name"]
                years = df["year"].unique()
                ann_mean = df.groupby("year")["rain"].sum().mean()
                st.success(f"Data loaded for **{selected_station['name']}**")
                st.markdown(f"""
                <div class="stat-row">
                  <div class="stat-chip">Records &nbsp;<span>{len(df):,} days</span></div>
                  <div class="stat-chip">Period &nbsp;<span>{years.min()}–{years.max()}</span></div>
                  <div class="stat-chip">Annual mean &nbsp;<span>{ann_mean:.1f} mm</span></div>
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Fetch failed: {e}")

st.write("")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — ROLLING WINDOW ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="section-card">
  <p class="section-label">Step 02</p>
  <p class="section-title">Rolling Window Frequency Analysis</p>
</div>
""", unsafe_allow_html=True)

if st.session_state.df is None:
    st.info("Complete Step 1 above to enable analysis.")
else:
    df = st.session_state.df
    years = sorted(df["year"].unique())

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown("**Season window**")
        sc1, sc2 = st.columns(2)
        with sc1:
            start_day = st.selectbox("Start day",   list(range(1, 32)), index=0,  key="sd")
            start_mon = st.selectbox("Start month", MONTHS,             index=0,  key="sm")
        with sc2:
            end_day   = st.selectbox("End day",     list(range(1, 32)), index=30, key="ed")
            end_mon   = st.selectbox("End month",   MONTHS,             index=11, key="em")

    with col_b:
        st.markdown("**Threshold criteria**")
        threshold = st.number_input("Rainfall (mm) ≥", min_value=1.0,   value=100.0, step=10.0)
        win_days  = st.number_input("Within (days)",   min_value=1,     value=30,    step=1)

    with col_c:
        st.markdown("**Year range**")
        yr_from = st.selectbox("From", years, index=0)
        yr_to   = st.selectbox("To",   years, index=len(years)-1)

    st.write("")
    if st.button("▶  Run Analysis", type="primary"):
        try:
            sm = MONTHS.index(start_mon) + 1
            em = MONTHS.index(end_mon)   + 1
            sd, ed = int(start_day), int(end_day)
            slabel = season_label(sm, sd, em, ed)

            sub = assign_season_year(df, sm, sd, em, ed)
            sub = sub[(sub["season_year"] >= yr_from) & (sub["season_year"] <= yr_to)]

            if sub.empty:
                st.warning("No data found for that season/year range.")
            else:
                results = []
                for sy, grp in sub.sort_values("date").groupby("season_year"):
                    rolled = grp["rain"].rolling(window=int(win_days), min_periods=int(win_days)).sum()
                    mx = rolled.max()
                    if not np.isnan(mx):
                        results.append({
                            "season_year": sy,
                            "max_roll_mm": mx,
                            "met_criteria": int(mx >= threshold)
                        })

                if not results:
                    st.warning("Not enough days to compute the rolling window.")
                else:
                    annual_max = pd.DataFrame(results)
                    rain       = annual_max["max_roll_mm"].values
                    n          = len(rain)
                    n_exceed   = int(np.sum(rain >= threshold))
                    pct        = n_exceed / n * 100

                    # ── result summary chips ───────────────────────────────────
                    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
                    st.markdown(f"""
                    <div class="stat-row">
                      <div class="stat-chip">Criterion &nbsp;<span>{threshold:.0f} mm in {int(win_days)} days</span></div>
                      <div class="stat-chip">Season &nbsp;<span>{slabel}</span></div>
                      <div class="stat-chip">Years assessed &nbsp;<span>{n}</span></div>
                      <div class="stat-chip">Years exceeded &nbsp;<span>{n_exceed}</span></div>
                      <div class="stat-chip">Exceedance frequency &nbsp;<span>{pct:.1f}%</span></div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.write("")

                    # ── chart ─────────────────────────────────────────────────
                    NAVY    = "#0f2744"
                    BLUE    = "#1a5fa8"
                    MISS    = "#c8d8e8"
                    BG      = "#f7fafd"
                    GRID    = "#dde5ee"

                    fig, ax = plt.subplots(figsize=(13, 4.8))
                    fig.patch.set_facecolor(BG)
                    ax.set_facecolor(BG)

                    colours = [NAVY if r >= threshold else MISS
                               for r in annual_max["max_roll_mm"]]
                    bars = ax.bar(
                        annual_max["season_year"],
                        annual_max["max_roll_mm"],
                        color=colours, width=0.72, zorder=3,
                        linewidth=0
                    )

                    # threshold line
                    ax.axhline(threshold, color=BLUE, lw=1.4, ls="--", zorder=4, alpha=0.85)
                    ax.text(
                        annual_max["season_year"].max() + 0.5,
                        threshold + rain.max() * 0.016,
                        f"{threshold:.0f} mm threshold",
                        color=BLUE, fontsize=9, va="bottom",
                        fontfamily="monospace"
                    )

                    # axes
                    ax.set_xlabel("Season year", fontsize=10, color="#4a6580", labelpad=8)
                    ax.set_ylabel(f"Max {int(win_days)}-day Rainfall (mm)", fontsize=10, color="#4a6580", labelpad=8)
                    ax.tick_params(colors="#4a6580", labelsize=9)
                    ax.tick_params(axis="x", rotation=45 if n > 30 else 0)

                    ax.grid(True, axis="y", color=GRID, lw=0.8, zorder=0)
                    ax.set_axisbelow(True)
                    for sp in ax.spines.values():
                        sp.set_color(GRID)
                    ax.spines["top"].set_visible(False)
                    ax.spines["right"].set_visible(False)

                    station = st.session_state.station_name or "Station"
                    ax.set_title(
                        f"{station}   ·   {slabel}   ·   {int(win_days)}-day rolling window   ·   {yr_from}–{yr_to}",
                        fontsize=11, fontweight="semibold", color=NAVY, pad=14
                    )

                    from matplotlib.patches import Patch
                    ax.legend(
                        handles=[
                            Patch(color=NAVY, label=f"≥ {threshold:.0f} mm  ({n_exceed} yrs)"),
                            Patch(color=MISS, label=f"< {threshold:.0f} mm  ({n - n_exceed} yrs)"),
                        ],
                        fontsize=9, loc="upper left",
                        framealpha=0.9, edgecolor=GRID,
                        fancybox=False
                    )

                    fig.tight_layout()
                    st.pyplot(fig)
                    plt.close(fig)

                    # ── download ──────────────────────────────────────────────
                    st.write("")
                    export = annual_max.copy()
                    export["window_days"]  = int(win_days)
                    export["threshold_mm"] = threshold
                    export["season"]       = slabel
                    csv = export.to_csv(index=False)
                    st.download_button(
                        "💾  Export results as CSV",
                        data=csv,
                        file_name=f"rolling_window_{station.replace(' ','_')}.csv",
                        mime="text/csv"
                    )

        except Exception as e:
            st.error(f"Analysis error: {e}")
