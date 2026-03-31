"""
Rainfall Analysis Tool — Streamlit Web App
Fetches data from the SILO API and runs rolling window frequency analysis.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import urllib.request
import urllib.parse
from io import StringIO
from datetime import date

st.set_page_config(page_title="What are the odds?", page_icon="🌧️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,400;0,500;0,600;1,400&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background-color: #f4f7fb; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.2rem; padding-bottom: 1.5rem; max-width: 1100px; }

/* ── big open header ── */
.big-header {
    padding: 0.2rem 0 0.8rem 0;
    margin-bottom: 0;
}
.big-header-top {
    display: flex; align-items: flex-start; justify-content: space-between;
}
.big-title {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 4.2rem; font-weight: 800;
    color: #0b1f3a; letter-spacing: -0.04em;
    line-height: 1; margin: 0;
}
.big-subtitle {
    font-family: 'DM Sans', sans-serif;
    font-style: italic;
    font-size: 1.3rem; font-weight: 400;
    color: #0b1f3a; letter-spacing: 0.01em;
    margin: 0.15rem 0 0 0.3rem;
    display: flex; align-items: center; gap: 0.4rem;
}
.big-subtitle-dots {
    color: #2979c4; letter-spacing: -0.05em; font-style: normal;
}
.silo-badge {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.82rem; font-weight: 500;
    color: #6a8aaa;
    margin-top: 0.4rem;
}

/* ── panel cards — target st.container(border=True) ── */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #fff !important;
    border: 1.5px solid #d0dcea !important;
    border-radius: 12px !important;
    padding: 0.9rem 1.4rem 1.0rem !important;
    margin-bottom: 0.7rem !important;
    box-shadow: 0 1px 4px rgba(11,31,58,0.06) !important;
}

/* ── panel section titles ── */
.panel-title {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 1.3rem; font-weight: 700;
    color: #2979c4; letter-spacing: -0.02em;
    margin: 0 0 0.9rem 0;
}
.panel-hint {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.82rem; color: #8aaac4; font-weight: 400;
    margin-left: 0.5rem;
}
.panel-eg {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.88rem; color: #2e7d4f; font-weight: 500;
    margin-left: 0.3rem;
}

/* ── sentence row — prose with inline inputs ── */
.sentence-row {
    display: flex; align-items: center;
    flex-wrap: wrap; gap: 0.5rem;
    font-size: 1rem; color: #0b1f3a; font-weight: 400;
    margin-bottom: 0.9rem;
    line-height: 2.4;
}
.sentence-row b { font-weight: 600; }
.sentence-label {
    font-size: 1rem; color: #0b1f3a;
    white-space: nowrap;
}

/* ── all inputs — white boxes ── */

/* Text inputs */
.stTextInput input {
    background: #ffffff !important;
    border: 1.5px solid #c8d8e8 !important;
    border-radius: 6px !important;
    color: #0b1f3a !important;
    font-size: 0.92rem !important;
}
.stTextInput input:focus {
    border-color: #2979c4 !important;
    box-shadow: 0 0 0 3px rgba(41,121,196,0.12) !important;
    outline: none !important;
}

/* Number inputs — target the inner input only, never the wrapper */
.stNumberInput input {
    background: #ffffff !important;
    color: #0b1f3a !important;
    font-size: 0.92rem !important;
}
/* Number input outer border via the div[data-baseweb] container */
.stNumberInput [data-baseweb="base-input"] {
    background: #ffffff !important;
    border: 1.5px solid #c8d8e8 !important;
    border-radius: 6px !important;
}
.stNumberInput [data-baseweb="base-input"]:focus-within {
    border-color: #2979c4 !important;
    box-shadow: 0 0 0 3px rgba(41,121,196,0.12) !important;
}

/* Selectbox — ONLY the outer control button, nothing inside */
.stSelectbox [data-baseweb="select"] > div:first-child {
    background: #ffffff !important;
    border: 1.5px solid #c8d8e8 !important;
    border-radius: 6px !important;
    color: #0b1f3a !important;
}
/* Remove the red Streamlit validation outline — do NOT touch child elements */
.stSelectbox [data-baseweb="select"] {
    border: none !important;
    outline: none !important;
}

/* Labels hidden per-widget via label_visibility="collapsed" — no CSS needed */

/* ── radio list — compact station picker ── */
div[data-testid="stRadio"] > div {
    flex-direction: column !important;
    gap: 0.15rem !important;
}
div[data-testid="stRadio"] label {
    display: flex !important;
    align-items: center !important;
    padding: 0.35rem 0.7rem !important;
    border-radius: 6px !important;
    border: 1px solid #e0eaf4 !important;
    background: #f7fafd !important;
    font-size: 0.88rem !important;
    color: #0b1f3a !important;
    cursor: pointer !important;
    transition: background 0.1s !important;
    font-family: 'DM Mono', monospace !important;
}
div[data-testid="stRadio"] label:hover {
    background: #e8f0fb !important;
    border-color: #2979c4 !important;
}
div[data-testid="stRadio"] label[data-checked="true"],
div[data-testid="stRadio"] input:checked + div {
    background: #e8f0fb !important;
    border-color: #2979c4 !important;
    font-weight: 600 !important;
}

/* ── site search row ── */
.site-row {
    display: flex; align-items: baseline;
    flex-wrap: wrap; gap: 0.6rem;
    font-size: 1rem; color: #0b1f3a;
    margin-bottom: 0.8rem;
    line-height: 2.4;
}

/* ── station selectbox after search ── */
.stSelectbox > div { margin-top: 0 !important; }

/* ── stat chips ── */
.stat-row { display: flex; gap: 0.6rem; flex-wrap: wrap; margin-top: 0.5rem; }
.stat-chip {
    background: #eef5ff; border: 1px solid #b8d0ec;
    border-radius: 6px; padding: 0.3rem 0.7rem;
    font-size: 0.8rem; color: #3a5a7a;
    font-family: 'DM Mono', monospace;
}
.stat-chip b { color: #0b1f3a; font-weight: 600; }

/* ── result banner — light ── */
.result-banner {
    background: #eef5ff; border: 1.5px solid #b8d4f0; border-radius: 8px; padding: 0.8rem 1.4rem;
    margin: 0.8rem 0; display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;
}
.rb-label { font-family: 'DM Mono', monospace; font-size: 0.7rem; color: #4a7aaa; letter-spacing: 0.08em; text-transform: uppercase; }
.rb-value { font-family: Arial, Helvetica, sans-serif; font-size: 1.3rem; font-weight: 800; color: #0b1f3a; letter-spacing: -0.02em; line-height: 1.2; }
.rb-pct   { font-family: Arial, Helvetica, sans-serif; font-size: 2.2rem; font-weight: 800; color: #2979c4; letter-spacing: -0.03em; margin-left: auto; }

/* ── primary button ── */
.stButton > button {
    border-radius: 8px !important; font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important; font-size: 0.88rem !important;
    padding: 0.45rem 1.2rem !important;
    border: 1px solid #c0d0e0 !important;
    background: #fff !important; color: #0b1f3a !important;
    transition: all 0.12s ease !important;
}
.stButton > button:hover { background: #eef2f7 !important; border-color: #2979c4 !important; color: #2979c4 !important; }
.stButton > button[kind="primary"] {
    background: #0b1f3a !important; color: #fff !important;
    border-color: #0b1f3a !important;
    font-size: 1rem !important; font-weight: 700 !important;
    padding: 0.65rem 2rem !important; border-radius: 8px !important;
    letter-spacing: 0.01em;
    display: block !important; margin: 0 auto !important;
}
.stButton > button[kind="primary"]:hover { background: #2979c4 !important; border-color: #2979c4 !important; }

/* Remove the blank-box gap: zero out the default top margin Streamlit adds to each stMarkdownContainer block */
.stMarkdownContainer { margin-top: 0 !important; margin-bottom: 0 !important; }
div[data-testid="stMarkdownContainer"] p { margin: 0 !important; }
/* Hide the element wrapper gap for inline prose rows */
[data-testid="column"] > div:first-child { gap: 0 !important; }
[data-testid="stMarkdownContainer"] > div:has(> div[style*="padding-top"]) { padding: 0 !important; margin: 0 !important; }

div[data-testid="stAlert"] { border-radius: 7px !important; font-size: 0.88rem !important; }
.stDownloadButton > button {
    border-radius: 6px !important; font-family: 'DM Mono', monospace !important;
    font-size: 0.78rem !important; background: #f0f5fc !important;
    border: 1px dashed #94b4d4 !important; color: #0b1f3a !important;
}
.stDownloadButton > button:hover { background: #dde8f5 !important; border-color: #2979c4 !important; }
</style>
""", unsafe_allow_html=True)

MONTHS     = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
SILO_EMAIL = "a@b.com"

# ── helpers ───────────────────────────────────────────────────────────────────

def silo_search(frag):
    url = (f"https://www.longpaddock.qld.gov.au/cgi-bin/silo/"
           f"PatchedPointDataset.php?format=name&nameFrag="
           f"{urllib.parse.quote(frag)}&username={urllib.parse.quote(SILO_EMAIL)}")
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
            label = name
            if state: label += f"  [{state}]"
            if lat and lon: label += f"  ({lat}, {lon})"
            stations.append({"id": sid, "name": name, "label": label})
        except ValueError:
            continue
    return stations


def silo_fetch(station_id, start, end):
    url = (f"https://www.longpaddock.qld.gov.au/cgi-bin/silo/"
           f"PatchedPointDataset.php"
           f"?station={station_id}&start={start}&finish={end}"
           f"&format=csv&comment=R&username={urllib.parse.quote(SILO_EMAIL)}")
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
        date_col = next((c for c in df.columns if c.startswith("date") or "yyyy" in c), None)
        rain_col = next((c for c in df.columns if "rain" in c and "source" not in c and "quality" not in c), None)
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
    mo, dy, yr = df["date"].dt.month, df["date"].dt.day, df["date"].dt.year
    crosses = (sm > em) or (sm == em and sd > ed)
    after_start = (mo > sm) | ((mo == sm) & (dy >= sd))
    before_end  = (mo < em) | ((mo == em) & (dy <= ed))
    mask = after_start & before_end if not crosses else after_start | before_end
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
for key, default in [("df", None), ("station_name", None), ("stations", []), ("last_search", ""), ("selected_station", None), ("search_error", None), ("search_input", ""), ("station_confirmed", False), ("station_chosen", None)]:
    if key not in st.session_state:
        st.session_state[key] = default

# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
col_title, col_badge = st.columns([6, 1])
with col_title:
    st.markdown("""
    <div class="big-header">
      <p class="big-title">What are the odds?</p>
      <p class="big-subtitle">
        <span class="big-subtitle-dots">· · · · · · · · ·</span>
        <em>of getting rain at</em>
      </p>
    </div>
    """, unsafe_allow_html=True)
with col_badge:
    st.markdown("<div style='padding-top:1.6rem;text-align:right'><span style='font-family:DM Sans,sans-serif;font-size:0.82rem;color:#6a8aaa;font-weight:500'>Silo API</span></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PANEL 1 — SITE
# ══════════════════════════════════════════════════════════════════════════════

def do_search():
    """Callback fired by text_input on_change — updates stations in session state."""
    term = st.session_state.search_input
    if term and term != st.session_state.last_search:
        st.session_state.last_search = term
        st.session_state.stations = []
        st.session_state.selected_station = None
        st.session_state.station_confirmed = False
        st.session_state.station_chosen = None
        try:
            found = silo_search(term)
            st.session_state.stations = found
        except Exception as e:
            st.session_state.search_error = str(e)

with st.container(border=True):
    t1, t2, t3, t4 = st.columns([1.2, 3.5, 1.0, 0.8])
    with t1:
        st.markdown('<p class="panel-title" style="margin-bottom:0.4rem">Site</p>', unsafe_allow_html=True)
    with t2:
        st.markdown('<p style="padding-top:0.55rem;font-size:0.82rem;color:#8aaac4">(Press return to search)</p>', unsafe_allow_html=True)
    with t3:
        st.markdown('<p style="padding-top:0.55rem;font-size:0.82rem;color:#8aaac4;text-align:right">Data from</p>', unsafe_allow_html=True)
    with t4:
        start_year = st.number_input("yr", label_visibility="collapsed", min_value=1889, max_value=date.today().year, value=1900, step=1)

    st.text_input(
        "station",
        label_visibility="collapsed",
        placeholder="e.g. Cairns, Emerald  —  type and press Enter to search",
        key="search_input",
        on_change=do_search
    )
    start_date = date(int(start_year), 1, 1)

    if st.session_state.get("search_error"):
        st.error(f"Search failed: {st.session_state.search_error}")
        st.session_state.search_error = None

    # Station dropdown — always rendered from session_state (already updated by callback)
    if st.session_state.stations:
        labels = [s["label"] for s in st.session_state.stations]
        if len(labels) == 1:
            selected_label = labels[0]
            st.success(f"Found: **{labels[0]}**")
        else:
            confirmed = st.session_state.get("station_confirmed", False)
            # station_chosen persists independently of the radio widget
            chosen = st.session_state.get("station_chosen")
            if not chosen or chosen not in labels:
                chosen = labels[0]

            if confirmed:
                # Collapsed — show chosen station and Change button
                c1, c2 = st.columns([6, 1])
                with c1:
                    st.success(f"📍 {chosen}")
                with c2:
                    if st.button("Change", key="change_btn"):
                        st.session_state.station_confirmed = False
                selected_label = chosen
            else:
                # Expanded radio list — open at previously chosen index
                current_index = labels.index(chosen) if chosen in labels else 0
                st.caption(f"**{len(labels)} stations found** — click to select:")
                def on_station_pick():
                    # Save the picked value to station_chosen before confirmed flips
                    st.session_state.station_chosen = st.session_state.station_select
                    st.session_state.station_confirmed = True
                selected_label = st.radio(
                    "Station",
                    options=labels,
                    index=current_index,
                    key="station_select",
                    label_visibility="collapsed",
                    on_change=on_station_pick
                )
                # Keep station_chosen in sync while list is open
                st.session_state.station_chosen = selected_label
        st.session_state.selected_station = next(
            s for s in st.session_state.stations if s["label"] == selected_label)


    elif st.session_state.last_search:
        st.warning("No stations found. Try a shorter search term.")

# resolve selected_station from session state
selected_station = st.session_state.get("selected_station", None)



# ══════════════════════════════════════════════════════════════════════════════
# PANEL 2 — SET UP QUERY
# ══════════════════════════════════════════════════════════════════════════════
with st.container(border=True):
    st.markdown('<p class="panel-title">Set up query</p>', unsafe_allow_html=True)

    # Row 1: "Explore how often >  [25]  mm rain  occurs over  [5]  days?"
    r1a, r1b, r1c, r1d, r1e, r1f, r1g = st.columns([2.0, 0.65, 0.7, 1.1, 0.65, 0.5, 1.5])
    with r1a:
        st.markdown("<div style='padding-top:0.45rem;font-size:1rem;color:#0b1f3a'>Explore how often &gt;</div>", unsafe_allow_html=True)
    with r1b:
        threshold = st.number_input("mm", label_visibility="collapsed", min_value=1, value=25, step=5)
    with r1c:
        st.markdown("<div style='padding-top:0.45rem;font-size:1rem;color:#0b1f3a'>mm rain</div>", unsafe_allow_html=True)
    with r1d:
        st.markdown("<div style='padding-top:0.45rem;font-size:1rem;color:#0b1f3a'>occurs over</div>", unsafe_allow_html=True)
    with r1e:
        win_days = st.number_input("days", label_visibility="collapsed", min_value=1, value=5, step=1)
    with r1f:
        st.markdown("<div style='padding-top:0.45rem;font-size:1rem;color:#0b1f3a'>days?</div>", unsafe_allow_html=True)
    with r1g:
        st.write("")

    # Row 2: "Between  [1]  [Jan]  and  [31]  [Dec]"
    r2a, r2b, r2c, r2d, r2e, r2f, r2g = st.columns([1.0, 0.8, 0.9, 0.6, 0.8, 0.9, 2.0])
    with r2a:
        st.markdown("<div style='padding-top:0.45rem;font-size:1rem;color:#0b1f3a'>Between</div>", unsafe_allow_html=True)
    with r2b:
        start_day = st.selectbox("sd", list(range(1, 32)), index=0, key="sd", label_visibility="collapsed")
    with r2c:
        start_mon = st.selectbox("sm", MONTHS, index=0, key="sm", label_visibility="collapsed")
    with r2d:
        st.markdown("<div style='padding-top:0.45rem;font-size:1rem;color:#0b1f3a'>and</div>", unsafe_allow_html=True)
    with r2e:
        end_day = st.selectbox("ed", list(range(1, 32)), index=30, key="ed", label_visibility="collapsed")
    with r2f:
        end_mon = st.selectbox("em", MONTHS, index=11, key="em", label_visibility="collapsed")
    with r2g:
        st.write("")

    st.write("")

    # Centred action button
    _, bcol, _ = st.columns([1.5, 3, 1.5])
    with bcol:
        if selected_station:
            go = st.button("Fetch data and run analysis", type="primary", use_container_width=True)
        else:
            st.button("Fetch data and run analysis", type="primary", disabled=True, use_container_width=True)
            go = False


if go and selected_station:
    with st.spinner(f"Fetching data for {selected_station['name']}…"):
        try:
            raw = silo_fetch(
                selected_station["id"],
                start_date.strftime("%Y%m%d"),
                date.today().strftime("%Y%m%d")
            )
            df  = parse_silo(raw)
            st.session_state.df           = df
            st.session_state.station_name = selected_station["name"]
        except Exception as e:
            st.error(f"Fetch failed: {e}")
            st.stop()

    # ── run analysis immediately after fetch ──────────────────────────────
    df    = st.session_state.df
    years = sorted(df["year"].unique())
    yr_from, yr_to = years[0], years[-1]
    ann_mean = df.groupby("year")["rain"].sum().mean()

    st.markdown(f"""<div class="stat-row">
      <div class="stat-chip">✅ <b>{selected_station['name']}</b></div>
      <div class="stat-chip"><b>{yr_from}–{yr_to}</b> period</div>
      <div class="stat-chip">Annual mean <b>{int(round(ann_mean))} mm</b></div>
    </div>""", unsafe_allow_html=True)

    try:
        sm = MONTHS.index(start_mon) + 1
        em = MONTHS.index(end_mon)   + 1
        sd_i, ed_i = int(start_day), int(end_day)
        slabel = season_label(sm, sd_i, em, ed_i)

        sub = assign_season_year(df, sm, sd_i, em, ed_i)
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
                station    = st.session_state.station_name or "Station"

                st.markdown(f"""<div class="result-banner">
                  <div>
                    <div class="rb-label">Exceedance frequency</div>
                    <div class="rb-value">{n_exceed} of {n} years exceeded {int(threshold)} mm in {int(win_days)} days</div>
                  </div>
                  <div class="rb-pct">{int(round(pct))}%</div>
                </div>""", unsafe_allow_html=True)

                NAVY   = "#0b1f3a"
                BLUE   = "#2979c4"
                BRIGHT = "#4da6ff"
                MISS   = "#b8cfe8"
                BG     = "#f7fafd"
                GRID   = "#dde5ee"

                fig, ax = plt.subplots(figsize=(14, 4.0))
                fig.patch.set_facecolor(BG)
                ax.set_facecolor(BG)

                colours = [BRIGHT if r >= threshold else MISS for r in annual_max["max_roll_mm"]]
                bars = ax.bar(annual_max["season_year"], annual_max["max_roll_mm"],
                              color=colours, width=0.72, zorder=3, linewidth=0, alpha=0.95)

                for bar, r in zip(bars, annual_max["max_roll_mm"]):
                    if r >= threshold:
                        bar.set_edgecolor(BLUE)
                        bar.set_linewidth(0.8)

                for _, row in annual_max[annual_max["max_roll_mm"] >= threshold].iterrows():
                    ax.bar(row["season_year"], threshold,
                           color=BLUE, width=0.72, zorder=2, alpha=0.25, linewidth=0)

                ax.axhline(threshold, color=NAVY, lw=1.8, ls="--", zorder=4)
                ax.text(annual_max["season_year"].max() + 0.5,
                        threshold + rain.max() * 0.018,
                        f"▶  {int(threshold)} mm",
                        color=NAVY, fontsize=9.5, va="bottom",
                        fontweight="bold", fontfamily="monospace")

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
                    fontsize=11, fontweight="bold", color=NAVY, pad=10)

                from matplotlib.patches import Patch
                ax.legend(handles=[
                    Patch(color=BRIGHT, edgecolor=BLUE, linewidth=0.8,
                          label=f"≥ {int(threshold)} mm  ({n_exceed} yrs)"),
                    Patch(color=MISS, label=f"< {int(threshold)} mm  ({n - n_exceed} yrs)"),
                ], fontsize=9, loc="upper left", framealpha=0.95, edgecolor=GRID, fancybox=False)

                fig.tight_layout(pad=1.1)
                st.pyplot(fig)

                # ── JPEG summary card — light theme ────────────────────────
                import io
                from matplotlib.patches import FancyBboxPatch, Rectangle
                summary_fig, summary_ax = plt.subplots(figsize=(10, 4.0))
                summary_fig.patch.set_facecolor("#ffffff")
                summary_ax.set_facecolor("#ffffff")
                summary_ax.set_xlim(0, 10)
                summary_ax.set_ylim(0, 4.0)
                summary_ax.axis("off")

                # Outer card border
                summary_ax.add_patch(FancyBboxPatch((0.08, 0.08), 9.84, 3.84,
                    boxstyle="round,pad=0.12", facecolor="#ffffff",
                    edgecolor="#c8d8ec", linewidth=1.5, zorder=0))

                # Top blue header bar
                summary_ax.add_patch(Rectangle((0.08, 3.3), 9.84, 0.62,
                    facecolor="#2979c4", zorder=1,
                    clip_path=None))

                # Rounded top of header — overlay white rounded rect to fake it
                summary_ax.add_patch(FancyBboxPatch((0.08, 3.28), 9.84, 0.68,
                    boxstyle="round,pad=0.12", facecolor="#2979c4",
                    edgecolor="none", zorder=1))

                # Header title
                summary_ax.text(5, 3.62, "What are the odds?   ·   Rain frequency summary",
                    ha="center", va="center", fontsize=12.5, fontweight="bold",
                    color="white", zorder=2)

                # Station name
                summary_ax.text(0.4, 2.95, station,
                    ha="left", va="center", fontsize=15, fontweight="bold",
                    color="#0b1f3a", zorder=2)

                # Season + Record on one line
                summary_ax.text(0.4, 2.6,
                    f"Season: {slabel}     Record: {yr_from}–{yr_to}",
                    ha="left", va="center", fontsize=10.5, color="#4a6e94", zorder=2)

                # Thin divider
                summary_ax.plot([0.4, 9.6], [2.38, 2.38], color="#d0dcea", lw=1.0, zorder=2)

                # Query
                summary_ax.text(0.4, 2.12,
                    f"Query:  ≥ {int(threshold)} mm rain within any {int(win_days)}-day window  ·  {slabel}",
                    ha="left", va="center", fontsize=10.5, color="#5a7a9a", zorder=2)

                # Big centred result text
                summary_ax.text(4.2, 1.28, f"{n_exceed} of {n} years",
                    ha="center", va="center", fontsize=21, fontweight="bold",
                    color="#0b1f3a", zorder=2)
                summary_ax.text(4.2, 0.72, "met or exceeded the threshold",
                    ha="center", va="center", fontsize=10, color="#6a8aaa", zorder=2)

                # Big percentage — right side
                summary_ax.text(8.8, 1.4, f"{int(round(pct))}%",
                    ha="center", va="center", fontsize=40, fontweight="bold",
                    color="#2979c4", zorder=2)
                summary_ax.text(8.8, 0.6, "exceedance frequency",
                    ha="center", va="center", fontsize=9, color="#8aaac4", zorder=2)

                # Vertical separator between result and pct
                summary_ax.plot([6.5, 6.5], [0.35, 1.85], color="#d0dcea", lw=1.0, zorder=2)

                summary_fig.tight_layout(pad=0)
                jpeg_buf = io.BytesIO()
                summary_fig.savefig(jpeg_buf, format="jpeg", dpi=150,
                                    bbox_inches="tight", facecolor="#ffffff")
                plt.close(summary_fig)
                jpeg_buf.seek(0)

                plt.close(fig)

                # ── downloads ─────────────────────────────────────────────
                dl1, dl2 = st.columns(2)
                with dl1:
                    export = annual_max.copy()
                    export["window_days"]  = int(win_days)
                    export["threshold_mm"] = threshold
                    export["season"]       = slabel
                    st.download_button(
                        "💾  Export CSV",
                        data=export.to_csv(index=False),
                        file_name=f"rolling_window_{station.replace(' ', '_')}.csv",
                        mime="text/csv"
                    )
                with dl2:
                    st.download_button(
                        "🖼️  Download summary image",
                        data=jpeg_buf,
                        file_name=f"rain_summary_{station.replace(' ', '_')}.jpg",
                        mime="image/jpeg"
                    )

    except Exception as e:
        st.error(f"Analysis error: {e}")

