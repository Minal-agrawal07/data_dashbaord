# AI Dashboard Builder

Describe charts in plain English. AI writes the SQL, picks the right visualization, and renders it — no BI tools, no SQL knowledge required.

## Quick Start

### 1. Set your Anthropic API key

```bash
cp backend/.env backend/.env
# Edit backend/.env and add your ANTHROPIC_API_KEY
```

Or export it directly:
```bash
export ANTHROPIC_API_KEY=your_key_here
```

### 2. Run everything

```bash
cd data_dashboard
./start.sh
```

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### 3. Add your CSV files

Drop any `.csv` files into the `csvs/` folder. Schema is auto-detected within seconds.

```
data_dashboard/
└── csvs/
    ├── sales.csv          ← already included (sample data)
    ├── customers.csv      ← already included (sample data)
    ├── website_traffic.csv← already included (sample data)
    └── your_data.csv      ← drop yours here
```

### 4. Ask for a chart

Go to http://localhost:3000/builder and type:

> "Show me monthly revenue by category as a bar chart for Q1 2024"

> "Top 10 customers by total spend"

> "Website sessions by channel over time as a line chart"

---

## Manual Setup (if `start.sh` doesn't work)

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## How It Works

```
Your English query
       ↓
Stage 1: Intent Parser (Claude)
       ↓ extracts metrics, dimensions, time range, chart type
Stage 2: Schema Matcher
       ↓ maps your terms to actual CSV column names (fuzzy search)
Stage 3: SQL Generator (Claude)
       ↓ writes DuckDB SQL using your file paths directly
Stage 4: Chart Type Selector
       ↓ picks bar/line/pie/kpi/table based on rules
Stage 5: Chart Config Generator (Claude)
       ↓ generates ECharts JSON config
Rendered chart + SQL shown
```

DuckDB reads CSV files directly — no database import or setup needed.

---

## Sample Queries to Try

With the included sample data:

| Query | Data source |
|-------|-------------|
| "Monthly total revenue by category" | sales.csv |
| "Top 5 categories by total sales as a bar chart" | sales.csv |
| "Revenue by region as a pie chart" | sales.csv |
| "Customers by plan type" | customers.csv |
| "Active vs inactive customers by region" | customers.csv |
| "Website sessions over time as a line chart" | website_traffic.csv |
| "Conversions by channel as a bar chart" | website_traffic.csv |
| "Average bounce rate by page" | website_traffic.csv |
Total revenue

---

## Project Structure

```
data_dashboard/
├── csvs/                    ← your CSV files go here
├── backend/
│   ├── main.py              ← FastAPI app + all API routes
│   ├── pipeline/
│   │   ├── intent_parser.py ← NL → structured intent (Claude)
│   │   ├── schema_matcher.py← fuzzy column name matching
│   │   ├── sql_generator.py ← intent → DuckDB SQL (Claude)
│   │   ├── chart_selector.py← rule-based chart type picker
│   │   └── chart_config.py  ← SQL results → ECharts config (Claude)
│   ├── catalog/
│   │   ├── crawler.py       ← reads CSV schema via DuckDB
│   │   ├── watcher.py       ← watches csvs/ for new files
│   │   └── db.py            ← SQLite read/write
│   ├── query/
│   │   ├── executor.py      ← DuckDB query execution + caching
│   │   └── validator.py     ← SELECT-only enforcement
│   └── catalog.db           ← auto-created SQLite database
└── frontend/
    ├── app/
    │   ├── page.tsx          ← home page
    │   ├── builder/page.tsx  ← chart builder
    │   └── setup/page.tsx    ← data source viewer
    └── components/
        ├── NLInput.tsx       ← natural language input
        ├── ChartRenderer.tsx ← ECharts wrapper (bar/line/pie/kpi/table)
        └── SQLPanel.tsx      ← collapsible SQL viewer + editor
```



python -m pipeline.dashboard_planner: to run dashboard file to create most imp que from csv 
nd can ignore these files : dashboard generator nd dashboar executor nd savechartfiledashbaord : as these r incompelte to run through concurrency 
