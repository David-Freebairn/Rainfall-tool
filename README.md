# 🌧️ What are the Odds?
### *of getting rain at...*

A rainfall frequency analysis tool built on Australian [SILO](https://www.longpaddock.qld.gov.au/silo/) climate data.

**Live app → [rainodds.streamlit.app](https://rainodds.streamlit.app)**

---

## What it does

Ask a simple question: **how often has X mm of rain fallen within Y consecutive days, during a chosen season, at a specific weather station?**

The app queries the SILO Patched Point Dataset — Australia's longest continuous daily rainfall record — and returns a year-by-year frequency analysis with a chart and downloadable summary.

---

## How to use it

1. **Type a station name** and press Enter (e.g. *Roma*, *Cairns*, *Longreach*)
2. **Select a station** from the results list
3. **Set up your query** — rainfall threshold (mm), window length (days), and season dates
4. Click **Fetch data and run analysis**
5. Download the results as a **CSV** or **summary image**

---

## Example queries

| Question | Settings |
|---|---|
| How often does 25mm fall in 5 days in summer? | 25mm / 5 days / 1 Dec – 28 Feb |
| How often does 100mm fall in 30 days at any time of year? | 100mm / 30 days / 1 Jan – 31 Dec |
| How often does 50mm fall in 7 days during the wet season? | 50mm / 7 days / 1 Oct – 31 Mar |

---

## Data source

Data is sourced from the **SILO Patched Point Dataset** via the Queensland Government's longpaddock API. Records extend back to 1889 for many stations. No API key or registration is required.

---

## Running locally

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/whatodds.git
cd whatodds

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run rainfall_app.py
```

---

## Files

| File | Description |
|---|---|
| `rainfall_app.py` | Main Streamlit application |
| `requirements.txt` | Python dependencies |
| `README.md` | This file |

---

## Dependencies

```
streamlit>=1.32.0
pandas>=2.0.0
numpy>=1.26.0
matplotlib>=3.8.0
```

---

*Built with [Streamlit](https://streamlit.io) · Data from [SILO](https://www.longpaddock.qld.gov.au/silo/) · Queensland Government*
