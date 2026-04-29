# Financial Dashboard 2026

Interactive financial intelligence dashboard built with Plotly Dash.  
Colour palette: **Dark Green + Gold/Amber** — GreenStars brand identity.

---

## Features

| Section | What it shows |
|---|---|
| **8 KPI Cards** | Total Expenses, Income, Net Position, Budget Utilization %, Overhead, Project Spend, Active Projects, Avg Monthly Burn |
| **Story Banner** | Auto-generated narrative connecting the financial dots |
| **Monthly Burn Chart** | Stacked bars by category + trend line |
| **Category Pie** | Spend mix donut |
| **Project Budget vs Expenses** | Grouped bar: Budget / Expenses / Income per project |
| **Income vs Expenses** | Per-project net position |
| **Top 12 Accounts** | Horizontal ranked bar with colour thresholds |
| **Budget Gauge** | Utilization speedometer with safe/warn/danger zones |
| **Overhead Treemap** | Drill into overhead line items |
| **Cumulative Spend** | Monthly + cumulative dual-axis |
| **Transaction Table** | Filterable, sortable drill-down of every expense |

### Filters (all linked)
- Month (Jan–Apr 2026)
- Project
- Expense Category
- Reset button

---

## Local Setup

```bash
# 1. Clone
git clone https://github.com/Julesmugabo/Greendashboard.git
cd Greendashboard

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
python app.py
# → Open http://localhost:8050
```

---

## Deploy to Render

1. Push this repo to GitHub  
2. Go to [render.com](https://render.com) → **New Web Service**  
3. Connect your GitHub repo  
4. Render auto-detects `render.yaml` — just click **Deploy**  
5. Your dashboard will be live at `https://greenstars-dashboard.onrender.com`

**Manual settings (if not using render.yaml):**
- **Build Command:** `pip install -r requirements.txt`  
- **Start Command:** `gunicorn app:server -b 0.0.0.0:$PORT --timeout 120 --workers 2`  
- **Environment:** Python 3  

---

## File Structure

```
Greendashboard/
├── app.py              ← Main Dash application
├── data_loader.py      ← Data loading (GitHub URL → local fallback)
├── requirements.txt    ← Python dependencies
├── render.yaml         ← Render deployment config
├── Procfile            ← Gunicorn start command
├── .gitignore
├── README.md
└── data/
    └── Financial_data_-2026_-New.xlsx
```

---

## Data Source

- **Primary:** GitHub raw URL (auto-fetched on startup)  
- **Fallback:** `data/Financial_data_-2026_-New.xlsx` (bundled in repo)

The data loader tries the GitHub URL first. If unreachable (network issues, etc.), it automatically uses the local copy so the dashboard always works.
