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

st.set_page_config(
    page_title="Rainfall Analysis",
    page_icon="🌧️",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500;600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.stApp { background-color: #eef2f7; }

#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 1.5rem;
    max-width: 1280px;
}

/* ── header ── */
.app-header {
    background: #0b1f3a;
    border-radius: 10px;
    padding: 1.1rem 2rem;
    margin-bottom: 1.2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.app-header-left { display: flex; align-items: center; gap: 1rem; }
.app-header-icon { font-size: 2rem; line-height: 1; }
.app-header-title {
    color: #ffffff;
    font-family: 'Syne', sans-serif;
    font-size: 1.55rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    margin: 0;
    line-height: 1.1;
}
.app-header-sub {
    color: #5d8ab0;
    font-size: 0.72rem;
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin: 0;
}
.app-header-badge {
    background: #1a3a5c;
    color: #7eb8e8;
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    letter-spacing: 0.08em;
    border: 1px solid #2a5a8c;
}

/* ── step panels ── */
.step-panel {
    background: #ffffff;
    border: 1px solid #d5dfe9;
    border-radius: 10px;
    padding: 1rem 1.4rem 1.2rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(11,31,58,0.07);
}
.step-header {
    display: flex;
    align-items: baseline;
    gap: 0.7rem;
    margin-bottom: 0.9rem;
    border-bottom: 2px solid #eef2f7;
    padding-bottom: 0.6rem;
}
.step-num {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    font-weight: 500;
    color: #2979c4;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    background: #e8f0fb;
    padding: 0.18rem 0.55rem;
    border-radius: 4px;
}
.step-title {
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: #0b1f3a;
    letter-spacing: -0.01em;
}

/* ── stat chips ── */
.stat-row { display: flex; gap: 0.6rem; flex-wrap: wrap; margin-top: 0.7rem; }
.stat-chip {
    background: #f0f5fc;
    border: 1px solid #c8d8ec;
    border-radius: 6px;
    padding: 0.38rem 0.75rem;
    font-size: 0.78rem;
    color: #3a5a7a;
    font-family: 'DM Mono', monospace;
}
.stat-chip b { color: #0b1f3a; font-weight: 600; }

/* ── result highlight ── */
.result-banner {
    background: #0b1f3a;
    border-radius: 8px;
    padding: 0.75rem 1.2rem;
    margin: 0.8rem 0;
    display: flex;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
}
.result-banner .rb-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: #5d8ab0;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.result-banner .rb-value {
    font-family: 'Syne', sans-serif;
    font-size: 1.4rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.02em;
    line-height: 1;
}
.result-banner .rb-pct {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: #4da6ff;
    letter-spacing: -0.03em;
    margin-left: auto;
}

/* ── inputs ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    border: 1px solid #c0d0e0 !important;
    border-radius: 6px !important;
    background: #f7fafd !important;
    font-family: 'DM Sans', sans-serif !important;
    color: #0b1f3a !important;
    font-size: 0.88rem !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: #2979c4 !important;
    box-shadow: 0 0 0 3px rgba(41,121,196,0.14) !important;
}
.stSelectbox > div > div {
    border: 1px solid #c0d0e0 !important;
    border-radius: 6px !important;
    background: #f7fafd !important;
    font-size: 0.88rem !important;
}
.stDateInput > div > div > input {
    border: 1px solid #c0d0e0 !important;
    border-radius: 6px !important;
    background: #f7fafd !important;
    font-size: 0.88rem !important;
}
label, .stSelectbox label, .stTextInput label,
.stNumberInput label, .stDateInput label {
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    color: #3a5a7a !important;
    letter-spacing: 0.02em !important;
    text-transform: uppercase !important;
}

/* ── buttons ── */
.stButton > button {
    border-radius: 6px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.86rem !important;
    padding: 0.45rem 1.1rem !important;
    border: 1px solid #c0d0e0 !important;
    background: #ffffff !important;
    color: #0b1f3a !important;
    transition: all 0.12s ease !important;
}
.stButton > button:hover {
    background: #eef2f7 !important;
    border-color: #2979c4 !important;
    color: #2979c4 !important;
}
.stButton > button[kind="primary"] {
    background: #0b1f3a !important;
    color: #ffffff !important;
    border-color: #0b1f3a !important;
    font-size: 0.9rem !important;
    padding: 0.55rem 1.6rem !important;
    letter-spacing: 0.02em;
}
.stButton > button[kind="primary"]:hover {
    background: #2979c4 !important;
    border-color: #2979c4 !important;
}

/* ── alerts ── */
div[data-testid="stAlert"] {
    border-radius: 7px !important;
    font-size: 0.88rem !important;
}

/* ── download btn ── */
.stDownloadButton > button {
    border-radius: 6px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.78rem !important;
    background: #f0f5fc !important;
    border: 1px dashed #94b4d4 !important;
    color: #0b1f3a !important;
}
.stDownloadButton > button:hover {
    background: #dde8f5 !important;
    border-color: #2979c4 !important;
}
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
for key in ("df", "station_name", "stations"):
    if key not in st.session_state:
        st.session_state[key] = None if key != "stations" else []

# ── header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <div class="app-header-left">
    <div class="app-header-icon">🌧️</div>
    <div>
      <p class="app-header-title">What are the odds-rain?</p>
      <p class="app-header-sub">Australian SILO Data · Rainfall Between Two Dates</p>
    </div>
  </div>
  <div class="app-header-badge">SILO API</div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 1
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="step-panel">
  <div class="step-header">
    <span class="step-num">Step 01</span>
    <span class="step-title">Connect & Load Station Data</span>
  </div>
</div>
""", unsafe_allow_html=True)

with st.container():
    c1, c2, c3, c4 = st.columns([2, 2, 1.2, 1.2])
    with c1:
        email = st.text_input("Email address", placeholder="you@example.com",
                              help="Required by SILO as an API key.")
    with c2:
        search_term = st.text_input("Search station", placeholder="e.g. Cairns, Townsville")
    with c3:
        start_date = st.date_input("Start date", value=date(1990, 1, 1), min_value=date(1889, 1, 1))
    with c4:
        end_date = st.date_input("End date", value=date.today())

    if st.button("🔍  Search Stations", disabled=not (email and search_term)):
        if "@" not in email:
            st.error("Please enter a valid email address.")
        else:
            with st.spinner(f"Searching for '{search_term}'…"):
                try:
                    stations = silo_search(search_term, email)
                    st.session_state.stations = stations
                    if not stations:
                        st.warning("No stations found. Try a shorter term.")
                except Exception as e:
                    st.error(f"Search failed: {e}")

    if st.session_state.stations:
        sc1, sc2 = st.columns([3, 1])
        with sc1:
            labels = [s["label"] for s in st.session_state.stations]
            selected_label = st.selectbox(f"Select station ({len(st.session_state.stations)} found)", labels)
            selected_station = next(s for s in st.session_state.stations if s["label"] == selected_label)
        with sc2:
            st.write("")
            st.write("")
            fetch = st.button("⬇️  Fetch Data", type="primary")

        if fetch:
            with st.spinner(f"Fetching data for {selected_station['name']}…"):
                try:
                    raw = silo_fetch(selected_station["id"],
                                     start_date.strftime("%Y%m%d"),
                                     end_date.strftime("%Y%m%d"), email)
                    df  = parse_silo(raw)
                    st.session_state.df = df
                    st.session_state.station_name = selected_station["name"]
                    years    = df["year"].unique()
                    ann_mean = df.groupby("year")["rain"].sum().mean()
                    ann_max  = df.groupby("year")["rain"].sum().max()
                    st.success(f"✅ Loaded **{selected_station['name']}**")
                    st.markdown(f"""
                    <div class="stat-row">
                      <div class="stat-chip"><b>{len(df):,}</b> days</div>
                      <div class="stat-chip"><b>{years.min()}–{years.max()}</b> period</div>
                      <div class="stat-chip">Annual mean <b>{ann_mean:.0f} mm</b></div>
                      <div class="stat-chip">Annual max <b>{ann_max:.0f} mm</b></div>
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Fetch failed: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 2
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="step-panel">
  <div class="step-header">
    <span class="step-num">Step 02</span>
    <span class="step-title">Rolling Window Analysis</span>
  </div>
</div>
""", unsafe_allow_html=True)

if st.session_state.df is None:
    st.info("Complete Step 1 to enable analysis.")
else:
    df    = st.session_state.df
    years = sorted(df["year"].unique())

    ca, cb, cc, cd = st.columns([1.2, 1.2, 1, 1])

    with ca:
        st.markdown("**Season start**")
        s1, s2 = st.columns(2)
        with s1: start_day = st.selectbox("Day",   list(range(1,32)), index=0,  key="sd")
        with s2: start_mon = st.selectbox("Month", MONTHS,            index=0,  key="sm")

    with cb:
        st.markdown("**Season end**")
        e1, e2 = st.columns(2)
        with e1: end_day = st.selectbox("Day",   list(range(1,32)), index=30, key="ed")
        with e2: end_mon = st.selectbox("Month", MONTHS,            index=11, key="em")

    with cc:
        threshold = st.number_input("Rainfall (mm) ≥", min_value=1.0, value=100.0, step=10.0)
        win_days  = st.number_input("Within (days)",   min_value=1,   value=30,    step=1)

    with cd:
        yr_from = st.selectbox("Year from", years, index=0)
        yr_to   = st.selectbox("Year to",   years, index=len(years)-1)

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
                st.warning("No data in that season/year range.")
            else:
                results = []
                for sy, grp in sub.sort_values("date").groupby("season_year"):
                    rolled = grp["rain"].rolling(window=int(win_days), min_periods=int(win_days)).sum()
                    mx = rolled.max()
                    if not np.isnan(mx):
                        results.append({"season_year": sy, "max_roll_mm": mx,
                                        "met_criteria": int(mx >= threshold)})

                if not results:
                    st.warning("Not enough days to compute rolling window.")
                else:
                    annual_max = pd.DataFrame(results)
                    rain       = annual_max["max_roll_mm"].values
                    n          = len(rain)
                    n_exceed   = int(np.sum(rain >= threshold))
                    pct        = n_exceed / n * 100

                    station = st.session_state.station_name or "Station"

                    # ── result banner ──────────────────────────────────────────
                    st.markdown(f"""
                    <div class="result-banner">
                      <div>
                        <div class="rb-label">Exceedance frequency</div>
                        <div class="rb-value">{n_exceed} of {n} years exceeded {threshold:.0f} mm in {int(win_days)} days</div>
                      </div>
                      <div class="rb-pct">{pct:.1f}%</div>
                    </div>
                    """, unsafe_allow_html=True)

                    # ── chart ──────────────────────────────────────────────────
                    NAVY   = "#0b1f3a"
                    BLUE   = "#2979c4"
                    BRIGHT = "#4da6ff"
                    MISS   = "#b8cfe8"
                    BG     = "#f7fafd"
                    GRID   = "#dde5ee"

                    fig, ax = plt.subplots(figsize=(14, 4.2))
                    fig.patch.set_facecolor(BG)
                    ax.set_facecolor(BG)

                    colours = [BRIGHT if r >= threshold else MISS
                               for r in annual_max["max_roll_mm"]]

                    bars = ax.bar(
                        annual_max["season_year"],
                        annual_max["max_roll_mm"],
                        color=colours, width=0.72, zorder=3,
                        linewidth=0, alpha=0.95
                    )

                    for bar, r in zip(bars, annual_max["max_roll_mm"]):
                        if r >= threshold:
                            bar.set_edgecolor(BLUE)
                            bar.set_linewidth(0.8)

                    ax.axhline(threshold, color=NAVY, lw=1.8, ls="--", zorder=4)
                    ax.text(
                        annual_max["season_year"].max() + 0.5,
                        threshold + rain.max() * 0.018,
                        f"▶  {threshold:.0f} mm",
                        color=NAVY, fontsize=9.5, va="bottom", fontweight="bold",
                        fontfamily="monospace"
                    )

                    for _, row in annual_max[annual_max["max_roll_mm"] >= threshold].iterrows():
                        ax.bar(row["season_year"], threshold,
                               color=BLUE, width=0.72, zorder=3, alpha=0.3, linewidth=0)

                    ax.set_xlabel("Season year", fontsize=10, color="#3a5a7a", labelpad=6)
                    ax.set_ylabel(f"Max {int(win_days)}-day rainfall  (mm)",
                                  fontsize=10, color="#3a5a7a", labelpad=6)
                    ax.tick_params(colors="#3a5a7a", labelsize=9)
                    if n > 30:
                        ax.tick_params(axis="x", rotation=45)

                    ax.grid(True, axis="y", color=GRID, lw=0.9, zorder=0)
                    ax.set_axisbelow(True)
                    for sp in ["top", "right", "left"]:
                        ax.spines[sp].set_visible(False)
                    ax.spines["bottom"].set_color(GRID)

                    ax.set_title(
                        f"{station}   ·   {slabel}   ·   {int(win_days)}-day window   ·   {yr_from}–{yr_to}",
                        fontsize=11, fontweight="bold", color=NAVY, pad=10
                    )

                    from matplotlib.patches import Patch
                    ax.legend(
                        handles=[
                            Patch(color=BRIGHT, edgecolor=BLUE, linewidth=0.8,
                                  label=f"≥ {threshold:.0f} mm  ({n_exceed} yrs)"),
                            Patch(color=MISS, label=f"< {threshold:.0f} mm  ({n-n_exceed} yrs)"),
                        ],
                        fontsize=9, loc="upper left",
                        framealpha=0.95, edgecolor=GRID, fancybox=False
                    )

                    fig.tight_layout(pad=1.2)
                    st.pyplot(fig)
                    plt.close(fig)

                    # ── export ────────────────────────────────────────────────
                    export = annual_max.copy()
                    export["window_days"]  = int(win_days)
                    export["threshold_mm"] = threshold
                    export["season"]       = slabel
                    st.download_button(
                        "💾  Export CSV",
                        data=export.to_csv(index=False),
                        file_name=f"rolling_window_{station.replace(' ','_')}.csv",
                        mime="text/csv"
                    )

        except Exception as e:
            st.error(f"Analysis error: {e}")
