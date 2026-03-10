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
    page_title="Rainfall Analysis Tool",
    page_icon="🌧️",
    layout="wide",
)

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
    # try CSV format
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
    # fallback whitespace
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

# ── title ─────────────────────────────────────────────────────────────────────
st.title("🌧️ Rainfall Analysis Tool")
st.caption("Australian SILO climate data — Rolling window frequency analysis")
st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 — FETCH DATA
# ══════════════════════════════════════════════════════════════════════════════
st.header("Step 1 — Get Data from SILO")

col1, col2 = st.columns([1, 1])

with col1:
    email = st.text_input(
        "Your email address",
        placeholder="you@example.com",
        help="Required by SILO. Your email is used as the API key per their terms of use."
    )

with col2:
    search_term = st.text_input(
        "Search for a station",
        placeholder="e.g. Cairns, Townsville, Darwin",
        help="Enter part of a station name to search"
    )

col_date1, col_date2, col_search_btn = st.columns([1, 1, 1])
with col_date1:
    start_date = st.date_input("Start date", value=date(1990, 1, 1), min_value=date(1889, 1, 1))
with col_date2:
    end_date = st.date_input("End date", value=date.today())

# Search button
if st.button("🔍 Search Stations", disabled=not (email and search_term)):
    if "@" not in email:
        st.error("Please enter a valid email address.")
    else:
        with st.spinner(f"Searching for stations matching '{search_term}'..."):
            try:
                stations = silo_search(search_term, email)
                st.session_state.stations = stations
                if not stations:
                    st.warning("No stations found. Try a shorter search term (e.g. 'Cairn' instead of 'Cairns Airport').")
            except Exception as e:
                st.error(f"Search failed: {e}")

# Station picker
if st.session_state.stations:
    st.success(f"{len(st.session_state.stations)} station(s) found")
    labels = [s["label"] for s in st.session_state.stations]
    selected_label = st.selectbox("Select a station", labels)
    selected_station = next(s for s in st.session_state.stations if s["label"] == selected_label)

    if st.button("⬇️ Fetch Rainfall Data"):
        start_str = start_date.strftime("%Y%m%d")
        end_str   = end_date.strftime("%Y%m%d")
        with st.spinner(f"Fetching data for {selected_station['name']}..."):
            try:
                raw = silo_fetch(selected_station["id"], start_str, end_str, email)
                df  = parse_silo(raw)
                st.session_state.df = df
                st.session_state.station_name = selected_station["name"]
                years = df["year"].unique()
                ann_mean = df.groupby("year")["rain"].sum().mean()
                st.success(
                    f"✅ Loaded **{len(df):,} days** for **{selected_station['name']}**  |  "
                    f"{years.min()}–{years.max()}  |  Annual mean: **{ann_mean:.1f} mm**"
                )
            except Exception as e:
                st.error(f"Fetch failed: {e}")

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — ROLLING WINDOW ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
st.header("Step 2 — Rolling Window Analysis")
st.caption("How often did X mm fall within Y consecutive days during a season?")

if st.session_state.df is None:
    st.info("⬆️ Fetch data in Step 1 to enable analysis.")
else:
    df = st.session_state.df
    years = sorted(df["year"].unique())

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.subheader("Season window")
        sc1, sc2 = st.columns(2)
        with sc1:
            start_day = st.selectbox("Start day",   list(range(1, 32)), index=0,  key="sd")
            start_mon = st.selectbox("Start month", MONTHS,             index=0,  key="sm")
        with sc2:
            end_day   = st.selectbox("End day",     list(range(1, 32)), index=30, key="ed")
            end_mon   = st.selectbox("End month",   MONTHS,             index=11, key="em")

    with col_b:
        st.subheader("Criteria")
        threshold = st.number_input("Rainfall (mm) ≥", min_value=1.0,   value=100.0, step=10.0)
        win_days  = st.number_input("In (days)",        min_value=1,     value=30,    step=1)

    with col_c:
        st.subheader("Year range")
        yr_from = st.selectbox("From", years, index=0)
        yr_to   = st.selectbox("To",   years, index=len(years)-1)

    if st.button("▶️ Run Analysis", type="primary"):
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
                        results.append({
                            "season_year": sy,
                            "max_roll_mm": mx,
                            "met_criteria": int(mx >= threshold)
                        })

                if not results:
                    st.warning("Not enough days to compute rolling window.")
                else:
                    annual_max = pd.DataFrame(results)
                    rain       = annual_max["max_roll_mm"].values
                    n          = len(rain)
                    n_exceed   = int(np.sum(rain >= threshold))
                    pct        = n_exceed / n * 100

                    # ── result box ────────────────────────────────────────────
                    st.success(
                        f"**{threshold:.0f} mm in {int(win_days)} days**  ({slabel})  ➤  "
                        f"**{n_exceed} of {n} years  =  {pct:.1f}%**"
                    )

                    # ── chart ─────────────────────────────────────────────────
                    fig, ax = plt.subplots(figsize=(12, 4.5))
                    fig.patch.set_facecolor("#dde6ef")
                    ax.set_facecolor("#e8f0f8")

                    colours = ["#000000" if r >= threshold else "#e07b4f"
                               for r in annual_max["max_roll_mm"]]
                    ax.bar(annual_max["season_year"], annual_max["max_roll_mm"],
                           color=colours, width=0.8, alpha=0.9, zorder=3)

                    ax.axhline(threshold, color="#333333", lw=1.6, ls="--", zorder=4)
                    ax.text(annual_max["season_year"].max() + 0.4,
                            threshold + rain.max() * 0.015,
                            f"Threshold  {threshold:.0f} mm",
                            color="#000000", fontsize=10, va="bottom")

                    ax.set_xlabel("Season year", fontsize=11)
                    ax.set_ylabel(f"Max {int(win_days)}-day Rainfall (mm)", fontsize=11)
                    ax.grid(True, axis="y", color="#a0b8cc", lw=0.6, zorder=0)
                    for sp in ax.spines.values():
                        sp.set_color("#8aaabb")
                    ax.tick_params(colors="#000000", labelsize=10)
                    if n > 30:
                        ax.tick_params(axis="x", rotation=45)

                    station = st.session_state.station_name or "Station"
                    ax.set_title(
                        f"{station}   —   {slabel}   {int(win_days)}-day rolling window   ({yr_from}–{yr_to})",
                        fontsize=13, fontweight="bold", color="#000000"
                    )

                    # legend
                    from matplotlib.patches import Patch
                    ax.legend(handles=[
                        Patch(color="#000000", label=f"≥ {threshold:.0f} mm  ({n_exceed} years)"),
                        Patch(color="#e07b4f", label=f"< {threshold:.0f} mm  ({n - n_exceed} years)"),
                    ], fontsize=10, loc="upper left")

                    fig.tight_layout()
                    st.pyplot(fig)
                    plt.close(fig)

                    # ── download CSV ──────────────────────────────────────────
                    export = annual_max.copy()
                    export["window_days"]  = int(win_days)
                    export["threshold_mm"] = threshold
                    export["season"]       = slabel
                    csv = export.to_csv(index=False)
                    st.download_button(
                        "💾 Download results as CSV",
                        data=csv,
                        file_name=f"rolling_window_{station.replace(' ','_')}.csv",
                        mime="text/csv"
                    )

        except Exception as e:
            st.error(f"Analysis error: {e}")
